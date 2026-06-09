#!/usr/bin/env python3
"""
page_select - deterministic page-selection ranking for the live-capture skill.

Implements the Section 8 leverage algorithm. The arithmetic is reliability-
critical (it decides what gets captured), so it is scripted rather than done by
hand. Stdlib only. Invoked by the live-capture skill's select phase.

Input (JSON, via --metrics <file> or stdin):
    {
      "benchmark_cvr": 2.0,
      "pages": [
        {"path": "/pricing", "sessions": 5600, "cvr": 0.4, "bounce": 51.0,
         "mobile_bounce": 58.0, "desktop_bounce": 44.0, "lane": "conversion"},
        {"path": "/blog/guide", "sessions": 3200, "cvr": null, "bounce": 62.0,
         "lane": "content"}
      ]
    }

Output (JSON to stdout): ordered, deduplicated selection:
    {"selection": [
        {"path": "/", "lane": "conversion", "leverage": 0.0, "always_capture": "homepage"},
        {"path": "/pricing", "lane": "conversion", "leverage": 0.71, "always_capture": null},
        ...
    ]}

Leverage = 0.35*traffic_norm + 0.30*conversion_gap_norm
         + 0.20*bounce_norm  + 0.15*device_gap_norm
where conversion_gap_norm is clamped distance BELOW benchmark (never raw CVR),
so a high-converting page does not score as leverage.
"""
import argparse
import json
import sys

W_TRAFFIC = 0.35
W_CONV_GAP = 0.30
W_BOUNCE = 0.20
W_DEVICE_GAP = 0.15

DEFAULT_CONVERSION_SLOTS = 8
DEFAULT_CONTENT_SLOTS = 2

HOMEPAGE_PATHS = ("/", "", "/index", "/home")


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def compute_leverage(page, max_sessions, benchmark_cvr):
    """Leverage score for one page. Missing inputs contribute 0 to their term."""
    sessions = page.get("sessions") or 0
    traffic_norm = (sessions / max_sessions) if max_sessions else 0.0

    cvr = page.get("cvr")
    if cvr is None or not benchmark_cvr:
        conversion_gap_norm = 0.0
    else:
        conversion_gap_norm = _clamp((benchmark_cvr - cvr) / benchmark_cvr, 0.0, 1.0)

    bounce = page.get("bounce")
    bounce_norm = (bounce / 100.0) if bounce is not None else 0.0

    mob = page.get("mobile_bounce")
    desk = page.get("desktop_bounce")
    if mob is not None and desk is not None:
        device_gap_norm = abs(mob - desk) / 100.0
    else:
        device_gap_norm = 0.0

    return round(
        W_TRAFFIC * traffic_norm
        + W_CONV_GAP * conversion_gap_norm
        + W_BOUNCE * bounce_norm
        + W_DEVICE_GAP * device_gap_norm,
        4,
    )


def _is_homepage(path):
    return (path or "").rstrip("/").lower() in tuple(p.rstrip("/") for p in HOMEPAGE_PATHS)


def _healthiest(pages):
    """Positive control: lowest bounce, tie-broken by highest CVR. None if no signal."""
    scored = [p for p in pages if p.get("bounce") is not None or p.get("cvr") is not None]
    if not scored:
        return None
    return min(
        scored,
        key=lambda p: (
            p.get("bounce") if p.get("bounce") is not None else 100.0,
            -(p.get("cvr") if p.get("cvr") is not None else 0.0),
        ),
    )


def select(metrics, conversion_slots=DEFAULT_CONVERSION_SLOTS, content_slots=DEFAULT_CONTENT_SLOTS):
    """Return the ordered, deduplicated page selection with leverage + always_capture flags."""
    pages = metrics.get("pages", [])
    benchmark_cvr = metrics.get("benchmark_cvr")
    max_sessions = max((p.get("sessions") or 0) for p in pages) if pages else 0

    lev = {}
    for p in pages:
        lev[p["path"]] = compute_leverage(p, max_sessions, benchmark_cvr)

    conversion = sorted(
        [p for p in pages if p.get("lane", "conversion") == "conversion"],
        key=lambda p: lev[p["path"]],
        reverse=True,
    )[:conversion_slots]

    content = sorted(
        [p for p in pages if p.get("lane") == "content"],
        key=lambda p: (p.get("sessions") or 0),
        reverse=True,
    )[:content_slots]

    # Ordered assembly with always-capture injection, deduplicated by path.
    selection = []
    seen = set()

    def add(path, lane, always=None):
        if path in seen:
            # Upgrade the always_capture flag if a later reason applies.
            if always:
                for entry in selection:
                    if entry["path"] == path and not entry["always_capture"]:
                        entry["always_capture"] = always
            return
        seen.add(path)
        selection.append(
            {"path": path, "lane": lane, "leverage": lev.get(path, 0.0), "always_capture": always}
        )

    # Homepage always first (positioning's top surface, often absent from a per-page profile).
    home = next((p for p in pages if _is_homepage(p["path"])), None)
    if home is not None:
        add(home["path"], home.get("lane", "conversion"), always="homepage")
    else:
        add("/", "conversion", always="homepage")

    # Healthiest page (positive control), if identifiable.
    healthy = _healthiest(pages)
    if healthy is not None:
        add(healthy["path"], healthy.get("lane", "conversion"), always="positive_control")

    for p in conversion:
        add(p["path"], "conversion")
    for p in content:
        add(p["path"], "content")

    return selection


def main(argv=None):
    parser = argparse.ArgumentParser(description="Deterministic live-capture page selection.")
    parser.add_argument("--metrics", default="-", help="Path to metrics JSON, or '-' for stdin.")
    parser.add_argument("--conversion-slots", type=int, default=DEFAULT_CONVERSION_SLOTS)
    parser.add_argument("--content-slots", type=int, default=DEFAULT_CONTENT_SLOTS)
    args = parser.parse_args(argv)

    raw = sys.stdin.read() if args.metrics == "-" else open(args.metrics, encoding="utf-8").read()
    metrics = json.loads(raw)
    selection = select(metrics, args.conversion_slots, args.content_slots)
    print(json.dumps({"selection": selection}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
