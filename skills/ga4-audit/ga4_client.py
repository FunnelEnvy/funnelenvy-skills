#!/usr/bin/env python3
"""
GA4 API Client - Direct access to GA4 Data and Admin APIs.

Designed as the primary data source for the ga4-audit skill, with
analytics-mcp as fallback when credentials are unavailable.

Requires: requests (pip install requests)

Credentials (checked in order):
    1. GA4_ACCESS_TOKEN env var (pre-obtained token)
    2. GA4_CREDENTIALS_PATH env var (path to service account or OAuth JSON)
    3. GOOGLE_APPLICATION_CREDENTIALS env var (Google ADC standard)

Exit codes:
    0 - Success (JSON output on stdout)
    1 - General error
    2 - No credentials found (signal to fall back to MCP)
    3 - Auth failed (credentials exist but token exchange failed)

Usage:
    python ga4_client.py account-summaries
    python ga4_client.py property-details --property-id 123456789
    python ga4_client.py custom-dimensions --property-id 123456789
    python ga4_client.py run-report --property-id 123456789 --request '{...}'
    python ga4_client.py run-report --property-id 123456789 --request-file request.json
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print(
        "Error: 'requests' package required. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(1)


# ============================================================================
# Constants
# ============================================================================

ADMIN_API_BASE = "https://analyticsadmin.googleapis.com/v1beta"
DATA_API_BASE = "https://analyticsdata.googleapis.com/v1beta"
TOKEN_URL = "https://oauth2.googleapis.com/token"
GA4_SCOPES = "https://www.googleapis.com/auth/analytics.readonly"

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NO_CREDS = 2
EXIT_AUTH_FAILED = 3


# ============================================================================
# Authentication
# ============================================================================

def _load_credentials_file(path):
    """Load and validate a credentials JSON file. Returns parsed dict."""
    try:
        with open(path) as f:
            creds = json.load(f)
    except FileNotFoundError:
        error(f"Credentials file not found: {path}", EXIT_AUTH_FAILED)
    except json.JSONDecodeError:
        error(f"Credentials file is not valid JSON: {path}", EXIT_AUTH_FAILED)

    cred_type = creds.get("type")
    if cred_type not in ("service_account", "authorized_user"):
        error(
            f"Unsupported credential type '{cred_type}' in {path}. "
            "Expected 'service_account' or 'authorized_user'.",
            EXIT_AUTH_FAILED,
        )
    return creds


def _build_jwt(service_account):
    """Build a JWT for service account token exchange (no external deps)."""
    import base64
    import hashlib
    import hmac

    # RS256 requires the cryptography or PyJWT library for RSA signing.
    # To keep deps minimal, we use the oauth2 token endpoint with assertion.
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError:
        error(
            "Service account auth requires the 'cryptography' package. "
            "Install with: pip install cryptography\n"
            "Alternatively, use an OAuth refresh token or set GA4_ACCESS_TOKEN.",
            EXIT_AUTH_FAILED,
        )

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iss": service_account["client_email"],
        "scope": GA4_SCOPES,
        "aud": TOKEN_URL,
        "iat": now,
        "exp": now + 3600,
    }

    def b64url(data):
        return base64.urlsafe_b64encode(
            json.dumps(data, separators=(",", ":")).encode()
        ).rstrip(b"=").decode()

    segments = f"{b64url(header)}.{b64url(payload)}"

    private_key = serialization.load_pem_private_key(
        service_account["private_key"].encode(), password=None
    )
    signature = private_key.sign(segments.encode(), padding.PKCS1v15(), hashes.SHA256())
    sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

    return f"{segments}.{sig_b64}"


def _token_from_service_account(creds):
    """Exchange service account JWT for access token."""
    jwt = _build_jwt(creds)
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": jwt,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        error(
            f"Service account token exchange failed ({resp.status_code}): {resp.text}",
            EXIT_AUTH_FAILED,
        )
    return resp.json()["access_token"]


def _token_from_refresh_token(creds):
    """Exchange OAuth refresh token for access token."""
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": creds["client_id"],
            "client_secret": creds["client_secret"],
            "refresh_token": creds["refresh_token"],
        },
        timeout=30,
    )
    if resp.status_code != 200:
        error(
            f"Refresh token exchange failed ({resp.status_code}): {resp.text}",
            EXIT_AUTH_FAILED,
        )
    return resp.json()["access_token"]


def resolve_access_token():
    """Resolve an access token from environment or credential files.

    Returns the token string or calls sys.exit with appropriate code.
    """
    # 1. Direct access token
    token = os.environ.get("GA4_ACCESS_TOKEN")
    if token:
        return token

    # 2. GA4_CREDENTIALS_PATH
    creds_path = os.environ.get("GA4_CREDENTIALS_PATH")
    if creds_path:
        creds = _load_credentials_file(creds_path)
        if creds["type"] == "service_account":
            return _token_from_service_account(creds)
        return _token_from_refresh_token(creds)

    # 3. GOOGLE_APPLICATION_CREDENTIALS (Google ADC standard)
    adc_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if adc_path:
        creds = _load_credentials_file(adc_path)
        if creds["type"] == "service_account":
            return _token_from_service_account(creds)
        return _token_from_refresh_token(creds)

    # No credentials found
    error(
        "No GA4 credentials found. Set one of:\n"
        "  GA4_ACCESS_TOKEN - Direct access token\n"
        "  GA4_CREDENTIALS_PATH - Path to service account or OAuth JSON\n"
        "  GOOGLE_APPLICATION_CREDENTIALS - Google ADC standard",
        EXIT_NO_CREDS,
    )


# ============================================================================
# API Helpers
# ============================================================================

def error(msg, exit_code=EXIT_ERROR):
    """Print error to stderr and exit."""
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def api_get(url, token, params=None):
    """Make authenticated GET request. Returns parsed JSON."""
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=60,
    )
    if resp.status_code == 401:
        error("Authentication failed (401). Token may be expired.", EXIT_AUTH_FAILED)
    if resp.status_code == 403:
        error(
            f"Permission denied (403). Ensure the account has access to this resource.\n{resp.text}",
            EXIT_AUTH_FAILED,
        )
    if resp.status_code != 200:
        error(f"API request failed ({resp.status_code}): {resp.text}")
    return resp.json()


def api_post(url, token, body):
    """Make authenticated POST request. Returns parsed JSON."""
    resp = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=120,
    )
    if resp.status_code == 401:
        error("Authentication failed (401). Token may be expired.", EXIT_AUTH_FAILED)
    if resp.status_code == 403:
        error(
            f"Permission denied (403). Ensure the account has access to this property.\n{resp.text}",
            EXIT_AUTH_FAILED,
        )
    if resp.status_code != 200:
        error(f"API request failed ({resp.status_code}): {resp.text}")
    return resp.json()


def paginate_get(url, token, items_key, page_size=200):
    """Paginate a GET endpoint that uses pageToken/pageSize."""
    all_items = []
    page_token = None
    while True:
        params = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token
        data = api_get(url, token, params=params)
        all_items.extend(data.get(items_key, []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return all_items


# ============================================================================
# Subcommands
# ============================================================================

def cmd_account_summaries(token, _args):
    """List all accessible account summaries."""
    summaries = paginate_get(
        f"{ADMIN_API_BASE}/accountSummaries", token, "accountSummaries"
    )
    output = {"accountSummaries": summaries}
    print(json.dumps(output, indent=2))


def cmd_property_details(token, args):
    """Get details for a specific property."""
    if not args.property_id:
        error("--property-id is required for property-details")
    data = api_get(f"{ADMIN_API_BASE}/properties/{args.property_id}", token)
    print(json.dumps(data, indent=2))


def cmd_custom_dimensions(token, args):
    """List custom dimensions and metrics for a property."""
    if not args.property_id:
        error("--property-id is required for custom-dimensions")

    dimensions = paginate_get(
        f"{ADMIN_API_BASE}/properties/{args.property_id}/customDimensions",
        token,
        "customDimensions",
    )
    metrics = paginate_get(
        f"{ADMIN_API_BASE}/properties/{args.property_id}/customMetrics",
        token,
        "customMetrics",
    )
    output = {"customDimensions": dimensions, "customMetrics": metrics}
    print(json.dumps(output, indent=2))


def cmd_run_report(token, args):
    """Run a GA4 report."""
    if not args.property_id:
        error("--property-id is required for run-report")

    # Load request body from --request or --request-file
    if args.request_file:
        try:
            with open(args.request_file) as f:
                request_body = json.load(f)
        except FileNotFoundError:
            error(f"Request file not found: {args.request_file}")
        except json.JSONDecodeError:
            error(f"Request file is not valid JSON: {args.request_file}")
    elif args.request:
        try:
            request_body = json.loads(args.request)
        except json.JSONDecodeError:
            error("--request value is not valid JSON")
    else:
        error("Either --request or --request-file is required for run-report")

    url = f"{DATA_API_BASE}/properties/{args.property_id}:runReport"
    data = api_post(url, token, request_body)
    print(json.dumps(data, indent=2))


# ============================================================================
# CLI
# ============================================================================

COMMANDS = {
    "account-summaries": cmd_account_summaries,
    "property-details": cmd_property_details,
    "custom-dimensions": cmd_custom_dimensions,
    "run-report": cmd_run_report,
}


def build_parser():
    parser = argparse.ArgumentParser(
        description="GA4 API Client for ga4-audit skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "command",
        choices=COMMANDS.keys(),
        help="API operation to perform",
    )
    parser.add_argument(
        "--property-id",
        help="GA4 property ID (numeric)",
    )
    parser.add_argument(
        "--request",
        help="JSON request body for run-report (inline string)",
    )
    parser.add_argument(
        "--request-file",
        help="Path to JSON file containing run-report request body",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    token = resolve_access_token()
    COMMANDS[args.command](token, args)


if __name__ == "__main__":
    main()
