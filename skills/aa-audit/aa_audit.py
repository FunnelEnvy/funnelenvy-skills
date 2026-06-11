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


def resolve_scope(config: dict):
    """Resolve the optional sub-property scope to (segment_ids, search_prefix).

    Resolution precedence (one change point scopes all 9 reports):
    - scope.segment_id set     -> (["<id>"], None)   (preferred when a segment exists)
    - else scope.prefixes set  -> (None, "<broad single-token search clause>")
    - neither                  -> (None, None)        (whole-suite, pre-change behavior)

    The prefix fallback builds a SINGLE BROAD-TOKEN search clause on
    scope.prefix_dimension. AA's reporting search silently returns empty for
    narrow multi-token / colon `contains:` clauses, so the clause is kept to a
    single broad token. The first prefix token is used as the broad anchor.

    Returns:
        (segment_ids: Optional[List[str]], search_prefix: Optional[str])
    """
    scope = config.get("scope") or {}
    segment_id = scope.get("segment_id")
    if segment_id:
        return ([segment_id], None)

    prefixes = scope.get("prefixes") or []
    # Drop empty strings; the example config ships empty placeholders.
    prefixes = [p for p in prefixes if p]
    if prefixes:
        prefix_dim = scope.get("prefix_dimension") or STANDARD_DIMENSIONS["entry_page"]
        # Broad single-token clause only (never multi-token/colon contains).
        token = str(prefixes[0]).strip().split()[0]
        clause = f"( CONTAINS '{token}' )"
        # Encode the target dimension into the clause-bearing return; the
        # caller threads this onto run_report's `search` param, which scopes
        # the active report's own dimension. For prefix scoping we rely on the
        # entry/page dimension reports; a broad token keeps the search reliable.
        return (None, clause)

    return (None, None)


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

        # Default scope applied to every report unless a call overrides it.
        # Unset scope leaves both at falsy defaults so run_report reproduces
        # the exact pre-change payload (no segment filter, no search key).
        self.default_segment_ids: Optional[List[str]] = None
        self.default_search: Optional[str] = None

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
        # Merge client-level default scope when the call does not override it.
        # One change point (the resolved scope on AAClient) scopes all reports.
        if segment_ids is None:
            segment_ids = self.default_segment_ids
        if search is None:
            search = self.default_search

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

_coerce_warned: set = set()


def _coerce_cell(name: str, value) -> float:
    """Coerce a report cell to float. The Reports API can return strings
    (e.g., "NaN") in comparison windows; non-numeric cells become 0.0."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        result = float("nan")
    if result != result:  # NaN from API or failed parse
        if name not in _coerce_warned:
            _coerce_warned.add(name)
            print(f"  Warning: non-numeric cell value for '{name}' coerced to 0.0",
                  file=sys.stderr)
        return 0.0
    return result


def _normalize_value(name: str, value: float) -> float:
    """Normalize AA metric values. Bouncerate comes as 0-1, convert to 0-100%."""
    value = _coerce_cell(name, value)
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


# Default platform-native click dimensions for element interaction enumeration.
DEFAULT_INTERACTION_DIMENSIONS = [
    "variables/customlink",
    "variables/clickmaplink",
    "variables/clickmappage",
]


def resolve_interaction_dimensions(config: dict) -> Optional[List[str]]:
    """Resolve the element-interaction dimensions to enumerate.

    Precedence:
    1. config.interaction_dimensions (the new array knob) when present/non-empty.
    2. Back-compat: legacy config.dimensions.link_text -> [that single eVar].
    3. None when neither is configured (caller emits an explicit absence finding).
    """
    dims = config.get("interaction_dimensions")
    if dims:
        return list(dims)

    legacy = config.get("dimensions", {}).get("link_text")
    if legacy:
        return [legacy]

    return None


# Friction-interaction token set. A friction interaction is an element label
# denoting a validation error, dead-end, or failed action (rather than a
# navigation or success). The script pre-flags candidates deterministically via
# is_friction_token; the aa-audit SKILL's friction pass does richer
# interpretation on top. This constant + helper are the single source of truth
# the SKILL and the unit tests share, so the token set cannot silently drift.
FRICTION_TOKENS = ("error", "invalid", "required", "fail", "denied")


def is_friction_token(value: str) -> bool:
    """True when an interaction label matches a friction token (case-insensitive
    substring match). Safe on None/empty."""
    v = (value or "").lower()
    return any(tok in v for tok in FRICTION_TOKENS)


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


def fetch_element_interactions(
    client: AAClient, config: dict, date_range: str
) -> Optional[dict]:
    """Report 7 (generalized): Element interactions across click dimensions.

    Supersedes the prior single-dimension `fetch_element_clicks`. Iterates the
    resolved `interaction_dimensions` (default customlink/clickmaplink/clickmappage,
    legacy `dimensions.link_text` eVar honored via resolve_interaction_dimensions),
    running one scoped report per dimension.

    Search-reliability caveat: element events on a sub-property rank below
    site-wide noise, so each dimension is enumerated by a BROAD single-token
    prefix `search` at an UNtruncated limit (>= 400 rows). Narrow multi-token or
    colon `contains:` clauses silently return empty against AA's reporting
    search and must NOT be used here -- treat any such empty result as
    inconclusive, not as "no interactions." The broad-token scope clause is
    supplied by resolve_scope via the client default `search`.

    Returns:
        {"by_dimension": {dim: {"rows": [...], "summary": {...}}}, "dimensions": [...]}
        or None when no interaction dimensions are configured.
    """
    dims = resolve_interaction_dimensions(config)
    if not dims:
        return None

    metrics = _get_all_metrics(config, include_engagement=True)
    names = _metric_names(metrics, config)

    by_dimension = {}
    for dim in dims:
        # limit >= 400: untruncated enumeration so scoped sub-property elements
        # are not lost below the default top-50 waterline.
        resp = client.run_report(dim, metrics, date_range, limit=400)
        rows = parse_report_rows(resp, names)
        # Deterministically pre-flag friction candidates so the SKILL's friction
        # pass and downstream consumers share one token set (is_friction_token).
        for r in rows:
            r["friction"] = is_friction_token(str(r.get("value", "")))
        summary = extract_summary(resp, names)
        by_dimension[dim] = {"rows": rows, "summary": summary}

    return {"by_dimension": by_dimension, "dimensions": dims}


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


def fetch_event_liveness(client: AAClient, config: dict, date_range: str) -> List[dict]:
    """Event-liveness audit: count EVERY configured conversion + engagement
    event over the window and flag dead bindings.

    A configured event that returns zero over the full window is a dead binding
    (status="dead") -- the event is wired into config but the implementation is
    not firing it. Surfaced into the Measurement Integrity section.

    Returns a list of {event, name, count, status} (status="dead" when count == 0,
    else "live"). dark/spiked transitions are computed later by diffing against
    the comparison window via classify_regression.
    """
    events = list(config.get("conversion_events", [])) + list(config.get("engagement_events", []))
    if not events:
        return []

    metric_ids = [e["id"] for e in events]
    names = _metric_names(metric_ids, config)

    # A single dimensionless-style pull: use the page dimension report and read
    # summaryData totals for each event metric over the window.
    page_dim = _resolve_page_dim(config)
    resp = client.run_report(page_dim, metric_ids, date_range, limit=1)
    summary = extract_summary(resp, names)

    result = []
    for evt, name in zip(events, names):
        count = summary.get(name, 0) or 0
        result.append({
            "event": evt["id"],
            "name": evt["name"],
            "count": count,
            "status": "dead" if count == 0 else "live",
        })
    return result


def classify_regression(primary_count: float, comparison_count: float,
                        spike_factor: float = 3.0) -> str:
    """Classify an event/element regression by diffing primary vs comparison.

    Pure helper (unit-testable, no API). Given a metric's count in the primary
    (current) window and the comparison (prior) window:

    - present-then-0  (comparison > 0, primary == 0) -> "dark"   (went dark)
    - 0-then-present  (comparison == 0, primary > 0)  -> "spiked" (newly firing)
    - large jump      (primary >= spike_factor * comparison, comparison > 0) -> "spiked"
    - dead in both    (both == 0)                     -> "dead"
    - otherwise                                       -> "live"
    """
    p = primary_count or 0
    c = comparison_count or 0
    if p == 0 and c == 0:
        return "dead"
    if p == 0 and c > 0:
        return "dark"
    if c == 0 and p > 0:
        return "spiked"
    if c > 0 and p >= spike_factor * c:
        return "spiked"
    return "live"


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

    # Resolve optional sub-property scope and store on the client so every
    # report is scoped from one change point. Unset scope leaves the defaults
    # falsy, preserving the exact pre-change payload.
    scope_segment_ids, scope_search = resolve_scope(config)
    client.default_segment_ids = scope_segment_ids
    client.default_search = scope_search
    if scope_segment_ids:
        scope_method = "segment"
    elif scope_search:
        scope_method = "prefix"
    else:
        scope_method = "none"

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

    print("Fetching element interactions...", file=sys.stderr)
    element_interactions = fetch_element_interactions(client, config, primary_range)

    print("Fetching clickmap regions...", file=sys.stderr)
    clickmap_regions = fetch_clickmap_regions(client, config, primary_range)

    print("Fetching event liveness...", file=sys.stderr)
    event_liveness = fetch_event_liveness(client, config, primary_range)

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
            "interaction_dimensions": resolve_interaction_dimensions(config),
            "conversion_events": config.get("conversion_events", []),
            "engagement_events": config.get("engagement_events", []),
            "scope_applied": scope_method != "none",
            "scope_method": scope_method,
        },
        "site_totals": pages.get("summary", {}),
        "pages": pages.get("rows", []),
        "channels": channels.get("rows", []),
        "channel_detail": channel_detail.get("rows", []),
        "devices": devices.get("rows", []),
        "landing_pages": landing_pages.get("rows", []),
        "new_vs_returning": new_returning.get("rows", []),
        # Generalized element-interaction capture (supersedes element_clicks).
        # by_dimension keyed by interaction dimension; null when none configured.
        "element_interactions": element_interactions,
        "clickmap_regions": clickmap_regions.get("rows", []) if clickmap_regions else [],
        "event_liveness": event_liveness,
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

        print("  Element interactions...", file=sys.stderr)
        comp_element = fetch_element_interactions(client, config, comp_range)

        print("  Event liveness...", file=sys.stderr)
        comp_liveness = fetch_event_liveness(client, config, comp_range)

        # Liveness regression: diff each configured event's primary vs comparison
        # count to detect present-then-0 (dark) and 0-then-present/large-jump (spiked).
        comp_count_by_event = {e["event"]: e["count"] for e in comp_liveness}
        event_liveness_regressions = []
        for e in event_liveness:
            comp_count = comp_count_by_event.get(e["event"], 0)
            reg = classify_regression(e["count"], comp_count)
            # Promote the primary status with the regression classification so a
            # high-to-zero (dark) or zero-to-present (spiked) transition surfaces.
            if reg in ("dark", "spiked"):
                e["status"] = reg
            event_liveness_regressions.append({
                "event": e["event"],
                "name": e["name"],
                "primary_count": e["count"],
                "comparison_count": comp_count,
                "status": reg,
            })

        # Element-interaction regression: per dimension, diff each element value's
        # primary vs comparison count to flag dark/spiked elements.
        element_interaction_regressions = {}
        if element_interactions and comp_element:
            primary_by_dim = element_interactions.get("by_dimension", {})
            comp_by_dim = comp_element.get("by_dimension", {})
            for dim, primary_block in primary_by_dim.items():
                comp_block = comp_by_dim.get(dim, {})
                comp_rows = {r.get("value"): r for r in comp_block.get("rows", [])}
                dim_regs = []
                for r in primary_block.get("rows", []):
                    val = r.get("value")
                    p_count = r.get("visits", 0) or 0
                    comp_r = comp_rows.get(val, {})
                    c_count = comp_r.get("visits", 0) or 0
                    reg = classify_regression(p_count, c_count)
                    if reg in ("dark", "spiked"):
                        dim_regs.append({
                            "element": val,
                            "primary_count": p_count,
                            "comparison_count": c_count,
                            "status": reg,
                        })
                if dim_regs:
                    element_interaction_regressions[dim] = dim_regs

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
            "element_interactions": comp_element,
            "event_liveness": comp_liveness,
            "event_liveness_regressions": event_liveness_regressions,
            "element_interaction_regressions": element_interaction_regressions,
        }
    else:
        output["comparison"] = None

    # Output JSON to stdout
    print(json.dumps(output, indent=2))
    print(f"\nDone. {len(output['pages'])} pages, {len(output['channels'])} channels, "
          f"{len(output['landing_pages'])} landing pages.", file=sys.stderr)


if __name__ == "__main__":
    main()
