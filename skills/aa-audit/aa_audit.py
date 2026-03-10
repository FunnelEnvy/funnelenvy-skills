#!/usr/bin/env python3
"""
AA Audit - Adobe Analytics performance profiler.

Pulls site performance data from the AA 2.0 Reporting API and outputs
structured JSON to stdout. Designed to be invoked by the aa-audit SKILL.md,
which interprets the JSON and writes performance-profile.md.

Requires: requests (pip install requests)

Credentials (env vars):
    ADOBE_AA_CLIENT_ID
    ADOBE_AA_CLIENT_SECRET
    ADOBE_AA_ORG_ID

Usage:
    python3 aa_audit.py --config /path/to/config.json [--days 90] [--no-compare]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print("Error: 'requests' package required. Install with: pip install requests",
          file=sys.stderr)
    sys.exit(1)


# ============================================================================
# Config Loading
# ============================================================================

REQUIRED_CONFIG_KEYS = ["company_id", "report_suite"]

STANDARD_DIMENSIONS = {
    "page_fallback": "variables/page",
    "channel": "variables/lasttouchchannel",
    "channel_detail": "variables/lasttouchchanneldetail",
    "device": "variables/mobiledevicetype",
    "entry_page": "variables/entrypage",
    "new_returning": "variables/visitnumber",
}

STANDARD_METRICS = [
    "metrics/visits",
    "metrics/visitors",
    "metrics/bounces",
    "metrics/bouncerate",
]


def load_config(path: Optional[str] = None) -> dict:
    """Load and validate client config from file.

    Resolution order:
    1. --config CLI flag (path argument)
    2. ADOBE_AA_CONFIG env var pointing to file path
    3. Fail with clear error
    """
    config_path = path or os.environ.get("ADOBE_AA_CONFIG")
    if not config_path:
        print("Error: No config file specified. Use --config /path/to/config.json "
              "or set ADOBE_AA_CONFIG env var.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(config_path):
        print(f"Error: Config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    missing = [k for k in REQUIRED_CONFIG_KEYS if k not in config]
    if missing:
        print(f"Error: Config missing required keys: {', '.join(missing)}",
              file=sys.stderr)
        sys.exit(1)

    return config


# ============================================================================
# AA API Client
# ============================================================================

class AAClient:
    """Adobe Analytics 2.0 API client with OAuth and generic reporting."""

    TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"
    SCOPES = "openid,AdobeID,read_organizations,additional_info.projectedProductContext"

    def __init__(self, config: dict):
        self.company_id = config["company_id"]
        self.rsid = config["report_suite"]
        self.config = config

        self.client_id = os.environ.get("ADOBE_AA_CLIENT_ID")
        self.client_secret = os.environ.get("ADOBE_AA_CLIENT_SECRET")
        self.org_id = os.environ.get("ADOBE_AA_ORG_ID")

        if not self.client_id or not self.client_secret:
            print("Error: ADOBE_AA_CLIENT_ID and ADOBE_AA_CLIENT_SECRET env vars required.",
                  file=sys.stderr)
            sys.exit(1)

        self.base_url = f"https://analytics.adobe.io/api/{self.company_id}"
        self._token: Optional[str] = None

    def get_token(self) -> str:
        """Get OAuth access token from Adobe IMS."""
        if self._token:
            return self._token

        resp = requests.post(self.TOKEN_URL, data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.SCOPES,
        })

        if resp.status_code != 200:
            print(f"Error: Token request failed ({resp.status_code}): {resp.text}",
                  file=sys.stderr)
            sys.exit(1)

        self._token = resp.json()["access_token"]
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "x-api-key": self.client_id,
            "x-proxy-global-company-id": self.company_id,
            "Content-Type": "application/json",
        }

    def run_report(
        self,
        dimension: str,
        metrics: List[str],
        date_range: str,
        limit: int = 50,
        segment_ids: Optional[List[str]] = None,
        search: Optional[str] = None,
    ) -> dict:
        """Run a ranked report and return full response including summaryData.

        Args:
            dimension: AA dimension ID (e.g., variables/page)
            metrics: List of metric IDs (e.g., ["metrics/visits", "metrics/bounces"])
            date_range: ISO date range "YYYY-MM-DDTHH:MM:SS.mmm/YYYY-MM-DDTHH:MM:SS.mmm"
            limit: Max rows to return
            segment_ids: Optional list of segment IDs to apply
            search: Optional search clause for dimension filtering

        Returns:
            Full API response dict with rows, columns, summaryData.
        """
        global_filters = [
            {"type": "dateRange", "dateRange": date_range}
        ]
        if segment_ids:
            for sid in segment_ids:
                global_filters.append({"type": "segment", "segmentId": sid})

        metric_container = {
            "metrics": [
                {"id": m, "columnId": f"col_{i}"}
                for i, m in enumerate(metrics)
            ]
        }

        payload = {
            "rsid": self.rsid,
            "globalFilters": global_filters,
            "metricContainer": metric_container,
            "dimension": dimension,
            "settings": {
                "limit": limit,
                "page": 0,
                "nonesBehavior": "return-nones",
            },
        }

        if search:
            payload["search"] = {"clause": search}

        resp = requests.post(
            f"{self.base_url}/reports",
            headers=self._headers(),
            json=payload,
        )

        if resp.status_code not in (200, 206):
            print(f"Error: Report failed ({resp.status_code}): {resp.text}",
                  file=sys.stderr)
            print(f"Payload: {json.dumps(payload, indent=2)}", file=sys.stderr)
            sys.exit(1)

        data = resp.json()

        # Check for dimension authorization errors (206 partial content)
        if resp.status_code == 206:
            col_errors = data.get("columns", {}).get("columnErrors", [])
            if col_errors:
                error_desc = col_errors[0].get("errorDescription", "unknown")
                print(f"Warning: Report returned partial/empty data for "
                      f"dimension {dimension}: {error_desc}", file=sys.stderr)
                return {"rows": [], "summaryData": {"totals": []}}

        return data

    def run_breakdown(
        self,
        outer_dimension: str,
        outer_item_id: str,
        inner_dimension: str,
        metrics: List[str],
        date_range: str,
        limit: int = 10,
    ) -> dict:
        """Run a breakdown report (dimension within dimension item).

        AA 2.0 breakdowns work by adding a metricFilter of type "breakdown"
        to metricContainer, then referencing that filter from each metric.

        Args:
            outer_dimension: Parent dimension ID
            outer_item_id: Item ID to break down
            inner_dimension: Breakdown dimension ID
            metrics: List of metric IDs
            date_range: ISO date range
            limit: Max rows

        Returns:
            Full API response dict.
        """
        global_filters = [
            {"type": "dateRange", "dateRange": date_range}
        ]

        breakdown_filter_id = "breakdown_filter_0"
        metric_filters = [
            {
                "id": breakdown_filter_id,
                "type": "breakdown",
                "dimension": outer_dimension,
                "itemId": outer_item_id,
            }
        ]

        metric_container = {
            "metrics": [
                {"id": m, "columnId": f"col_{i}", "filters": [breakdown_filter_id]}
                for i, m in enumerate(metrics)
            ],
            "metricFilters": metric_filters,
        }

        payload = {
            "rsid": self.rsid,
            "globalFilters": global_filters,
            "metricContainer": metric_container,
            "dimension": inner_dimension,
            "settings": {
                "limit": limit,
                "page": 0,
                "nonesBehavior": "return-nones",
            },
        }

        resp = requests.post(
            f"{self.base_url}/reports",
            headers=self._headers(),
            json=payload,
        )

        if resp.status_code not in (200, 206):
            print(f"Error: Breakdown failed ({resp.status_code}): {resp.text}",
                  file=sys.stderr)
            return {"rows": [], "summaryData": {"totals": []}}

        data = resp.json()
        if resp.status_code == 206:
            col_errors = data.get("columns", {}).get("columnErrors", [])
            if col_errors:
                print(f"Warning: Breakdown returned partial data: "
                      f"{col_errors[0].get('errorDescription', 'unknown')}",
                      file=sys.stderr)
                return {"rows": [], "summaryData": {"totals": []}}

        return data


# ============================================================================
# Date Range Helpers
# ============================================================================

def build_date_ranges(days: int, no_compare: bool) -> dict:
    """Build primary and comparison date ranges.

    Returns:
        {
            "primary": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "iso": "...T.../...T..."},
            "comparison": {"start": ..., "end": ..., "iso": ...} or None,
            "days": int
        }
    """
    end = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start = end - timedelta(days=days)

    primary = {
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
        "iso": f"{start.strftime('%Y-%m-%dT00:00:00.000')}/{end.strftime('%Y-%m-%dT00:00:00.000')}",
    }

    comparison = None
    if not no_compare:
        comp_end = start
        comp_start = comp_end - timedelta(days=days)
        comparison = {
            "start": comp_start.strftime("%Y-%m-%d"),
            "end": comp_end.strftime("%Y-%m-%d"),
            "iso": f"{comp_start.strftime('%Y-%m-%dT00:00:00.000')}/{comp_end.strftime('%Y-%m-%dT00:00:00.000')}",
        }

    return {"primary": primary, "comparison": comparison, "days": days}


# ============================================================================
# Report Parsing Helpers
# ============================================================================

def _normalize_value(name: str, value: float) -> float:
    """Normalize AA metric values. Bouncerate comes as 0-1, convert to 0-100%."""
    if name == "bouncerate" and 0 <= value <= 1:
        return round(value * 100, 2)
    return value


def parse_report_rows(response: dict, metric_names: List[str]) -> List[dict]:
    """Parse AA report response into list of row dicts.

    Each row has "value" (dimension value) and one key per metric name.
    Bouncerate is normalized from 0-1 to 0-100%.
    """
    rows = response.get("rows", [])
    result = []
    for row in rows:
        entry = {"value": row.get("value", ""), "item_id": row.get("itemId", "")}
        data = row.get("data", [])
        for i, name in enumerate(metric_names):
            raw = data[i] if i < len(data) else 0
            entry[name] = _normalize_value(name, raw)
        result.append(entry)
    return result


def extract_summary(response: dict, metric_names: List[str]) -> dict:
    """Extract summaryData totals from report response."""
    summary = response.get("summaryData", {})
    totals = summary.get("totals", [])
    result = {}
    for i, name in enumerate(metric_names):
        raw = totals[i] if i < len(totals) else 0
        result[name] = _normalize_value(name, raw)
    return result


# ============================================================================
# Fetch Functions (9 Reports)
# ============================================================================

def _resolve_page_dim(config: dict) -> str:
    """Get page dimension from config or fall back to standard."""
    return config.get("dimensions", {}).get("page", STANDARD_DIMENSIONS["page_fallback"])


def _get_all_metrics(config: dict, include_conversion: bool = False,
                     include_engagement: bool = False,
                     extra: Optional[List[str]] = None) -> List[str]:
    """Build metric list from standard + config metrics."""
    metrics = list(STANDARD_METRICS)
    if include_conversion:
        for evt in config.get("conversion_events", []):
            metrics.append(evt["id"])
    if include_engagement:
        for evt in config.get("engagement_events", []):
            metrics.append(evt["id"])
    if extra:
        for m in extra:
            if m not in metrics:
                metrics.append(m)
    return metrics


def _metric_names(metrics: List[str], config: dict) -> List[str]:
    """Build human-readable metric name list matching metric ID order."""
    event_map = {}
    for evt in config.get("conversion_events", []):
        event_map[evt["id"]] = evt["name"]
    for evt in config.get("engagement_events", []):
        event_map[evt["id"]] = evt["name"]

    names = []
    for m in metrics:
        if m in event_map:
            names.append(event_map[m])
        else:
            # Strip "metrics/" prefix
            names.append(m.replace("metrics/", ""))
    return names


def _primary_conversion(config: dict) -> Optional[str]:
    """Get primary conversion event ID (first in list)."""
    events = config.get("conversion_events", [])
    return events[0]["id"] if events else None


def fetch_page_performance(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 1: Page performance - top pages with all metrics."""
    page_dim = _resolve_page_dim(config)
    extra = ["metrics/averagetimespentonsite", "metrics/pageviews", "metrics/singlepagevisits"]
    metrics = _get_all_metrics(config, include_conversion=True, extra=extra)
    names = _metric_names(metrics, config)

    resp = client.run_report(page_dim, metrics, date_range, limit=50)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary, "dimension": page_dim}


def fetch_channels(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 2: Channel performance."""
    metrics = _get_all_metrics(config, include_conversion=True)
    names = _metric_names(metrics, config)

    resp = client.run_report(STANDARD_DIMENSIONS["channel"], metrics, date_range, limit=20)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary}


def fetch_channel_detail(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 3: Channel detail (source/medium equivalent)."""
    primary = _primary_conversion(config)
    extra = [primary] if primary else []
    metrics = _get_all_metrics(config, extra=extra)
    names = _metric_names(metrics, config)

    resp = client.run_report(STANDARD_DIMENSIONS["channel_detail"], metrics, date_range, limit=30)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary}


def fetch_devices(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 4: Device breakdown."""
    primary = _primary_conversion(config)
    extra = ["metrics/averagetimespentonsite"]
    if primary:
        extra.append(primary)
    metrics = _get_all_metrics(config, extra=extra)
    names = _metric_names(metrics, config)

    resp = client.run_report(STANDARD_DIMENSIONS["device"], metrics, date_range, limit=10)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary}


def fetch_landing_pages(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 5: Landing page (entry page) performance."""
    primary = _primary_conversion(config)
    extra = [primary] if primary else []
    metrics = _get_all_metrics(config, extra=extra)
    names = _metric_names(metrics, config)

    resp = client.run_report(STANDARD_DIMENSIONS["entry_page"], metrics, date_range, limit=50)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary}


def fetch_new_vs_returning(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 6: New vs returning visitors."""
    primary = _primary_conversion(config)
    extra = ["metrics/averagetimespentonsite"]
    if primary:
        extra.append(primary)
    metrics = _get_all_metrics(config, extra=extra)
    names = _metric_names(metrics, config)

    resp = client.run_report(STANDARD_DIMENSIONS["new_returning"], metrics, date_range, limit=10)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary}


def fetch_element_clicks(client: AAClient, config: dict, date_range: str) -> Optional[dict]:
    """Report 7: Element clicks by link text."""
    link_dim = config.get("dimensions", {}).get("link_text")
    if not link_dim:
        return None

    metrics = _get_all_metrics(config, include_engagement=True)
    names = _metric_names(metrics, config)

    resp = client.run_report(link_dim, metrics, date_range, limit=50)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary, "dimension": link_dim}


def fetch_clickmap_regions(client: AAClient, config: dict, date_range: str) -> Optional[dict]:
    """Report 8: Clickmap regions."""
    region_dim = config.get("dimensions", {}).get("region")
    if not region_dim:
        return None

    metrics = _get_all_metrics(config, include_engagement=True)
    names = _metric_names(metrics, config)

    resp = client.run_report(region_dim, metrics, date_range, limit=30)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary, "dimension": region_dim}


def fetch_page_conversions(client: AAClient, config: dict, date_range: str) -> dict:
    """Report 9: Page x conversion events (wider net, 100 rows)."""
    page_dim = _resolve_page_dim(config)
    metrics = list(STANDARD_METRICS)
    for evt in config.get("conversion_events", []):
        metrics.append(evt["id"])
    names = _metric_names(metrics, config)

    resp = client.run_report(page_dim, metrics, date_range, limit=100)
    rows = parse_report_rows(resp, names)
    summary = extract_summary(resp, names)
    return {"rows": rows, "summary": summary, "dimension": page_dim}


# ============================================================================
# Landing Page x Channel Breakdowns
# ============================================================================

def fetch_landing_page_channels(
    client: AAClient, config: dict, date_range: str,
    landing_page_data: dict,
) -> dict:
    """Break down top 5 landing pages by channel.

    Uses the entry page dimension with a breakdown by last touch channel.
    """
    top_pages = landing_page_data.get("rows", [])[:5]
    if not top_pages:
        return {}

    primary = _primary_conversion(config)
    extra = [primary] if primary else []
    metrics = _get_all_metrics(config, extra=extra)
    names = _metric_names(metrics, config)

    result = {}
    for page in top_pages:
        item_id = page.get("item_id", "")
        if not item_id:
            continue

        resp = client.run_breakdown(
            outer_dimension=STANDARD_DIMENSIONS["entry_page"],
            outer_item_id=item_id,
            inner_dimension=STANDARD_DIMENSIONS["channel"],
            metrics=metrics,
            date_range=date_range,
            limit=10,
        )
        rows = parse_report_rows(resp, names)
        result[page["value"]] = rows

    return result


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Adobe Analytics performance audit - outputs JSON to stdout")
    parser.add_argument("--config", type=str,
                        help="Path to client config JSON file")
    parser.add_argument("--days", type=int, default=90,
                        help="Number of days to look back (default: 90)")
    parser.add_argument("--no-compare", action="store_true",
                        help="Skip period-over-period comparison")
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)
    client = AAClient(config)

    # Auth check
    print("Authenticating with Adobe IMS...", file=sys.stderr)
    client.get_token()
    print("Authentication successful.", file=sys.stderr)

    # Build date ranges
    dates = build_date_ranges(args.days, args.no_compare)
    primary_range = dates["primary"]["iso"]
    print(f"Date range: {dates['primary']['start']} to {dates['primary']['end']} "
          f"({args.days} days)", file=sys.stderr)

    # Run primary period reports
    print("Fetching page performance...", file=sys.stderr)
    pages = fetch_page_performance(client, config, primary_range)

    print("Fetching channels...", file=sys.stderr)
    channels = fetch_channels(client, config, primary_range)

    print("Fetching channel detail...", file=sys.stderr)
    channel_detail = fetch_channel_detail(client, config, primary_range)

    print("Fetching devices...", file=sys.stderr)
    devices = fetch_devices(client, config, primary_range)

    print("Fetching landing pages...", file=sys.stderr)
    landing_pages = fetch_landing_pages(client, config, primary_range)

    print("Fetching new vs returning...", file=sys.stderr)
    new_returning = fetch_new_vs_returning(client, config, primary_range)

    print("Fetching element clicks...", file=sys.stderr)
    element_clicks = fetch_element_clicks(client, config, primary_range)

    print("Fetching clickmap regions...", file=sys.stderr)
    clickmap_regions = fetch_clickmap_regions(client, config, primary_range)

    print("Fetching page conversions...", file=sys.stderr)
    page_conversions = fetch_page_conversions(client, config, primary_range)

    print("Fetching landing page x channel breakdowns...", file=sys.stderr)
    lp_channels = fetch_landing_page_channels(client, config, primary_range, landing_pages)

    # Build output
    output = {
        "meta": {
            "report_suite": config["report_suite"],
            "company_id": config["company_id"],
            "date_range": {
                "start": dates["primary"]["start"],
                "end": dates["primary"]["end"],
            },
            "days": args.days,
            "config_dimensions": config.get("dimensions", {}),
            "conversion_events": config.get("conversion_events", []),
            "engagement_events": config.get("engagement_events", []),
        },
        "site_totals": pages.get("summary", {}),
        "pages": pages.get("rows", []),
        "channels": channels.get("rows", []),
        "channel_detail": channel_detail.get("rows", []),
        "devices": devices.get("rows", []),
        "landing_pages": landing_pages.get("rows", []),
        "new_vs_returning": new_returning.get("rows", []),
        "element_clicks": element_clicks.get("rows", []) if element_clicks else [],
        "clickmap_regions": clickmap_regions.get("rows", []) if clickmap_regions else [],
        "page_conversions": page_conversions.get("rows", []),
        "landing_page_channels": lp_channels,
    }

    # Comparison period
    if dates["comparison"]:
        comp_range = dates["comparison"]["iso"]
        print("\nFetching comparison period...", file=sys.stderr)

        print("  Page performance...", file=sys.stderr)
        comp_pages = fetch_page_performance(client, config, comp_range)

        print("  Channels...", file=sys.stderr)
        comp_channels = fetch_channels(client, config, comp_range)

        print("  Devices...", file=sys.stderr)
        comp_devices = fetch_devices(client, config, comp_range)

        print("  Landing pages...", file=sys.stderr)
        comp_landing = fetch_landing_pages(client, config, comp_range)

        print("  New vs returning...", file=sys.stderr)
        comp_nr = fetch_new_vs_returning(client, config, comp_range)

        print("  Page conversions...", file=sys.stderr)
        comp_page_conv = fetch_page_conversions(client, config, comp_range)

        output["comparison"] = {
            "date_range": {
                "start": dates["comparison"]["start"],
                "end": dates["comparison"]["end"],
            },
            "site_totals": comp_pages.get("summary", {}),
            "pages": comp_pages.get("rows", []),
            "channels": comp_channels.get("rows", []),
            "devices": comp_devices.get("rows", []),
            "landing_pages": comp_landing.get("rows", []),
            "new_vs_returning": comp_nr.get("rows", []),
            "page_conversions": comp_page_conv.get("rows", []),
        }
    else:
        output["comparison"] = None

    # Output JSON to stdout
    print(json.dumps(output, indent=2))
    print(f"\nDone. {len(output['pages'])} pages, {len(output['channels'])} channels, "
          f"{len(output['landing_pages'])} landing pages.", file=sys.stderr)


if __name__ == "__main__":
    main()
