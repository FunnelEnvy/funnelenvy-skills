# Phase 1: Page Selection

## Goal

Decide which pages to capture. Capture is expensive (one navigation + multi-viewport DOM read per page), so select the pages where structural facts have the most downstream leverage, always include the homepage and a positive-control page, and degrade gracefully when no performance data exists.

This is the capture skill's OWN selection mechanism. It is NOT `detect.md` Step 1c. Step 1c (Performance-Driven Triggers) governs whether performance hypotheses FIRE, not which pages to capture. Do not cite Step 1c as the selector.

## Inputs

- The site root URL and any `--urls` override.
- Per-page performance metrics, if available:
  - Legacy mode: `.claude/context/performance-profile.md` (frontmatter `top_pages` + the page-performance body table).
  - KB mode: the scope's `silver-performance-analysis` artifact. It may lack `schema_version`; match the per-page traffic/bounce/CVR table by content, not by rigid field names.

## Procedure

### Step 0: Explicit list override

If `--urls` was provided, use exactly that list. Skip the rest of this phase. Still always-capture the homepage if it is not already in the list (it is positioning's top surface).

### Step 1: No-profile fallback

If no performance profile is available (neither legacy file nor KB silver performance artifact):

1. Fetch the homepage and read its top-nav links and primary CTAs.
2. Nav-crawl depth 1-2 from those links to assemble a candidate list (cap ~10 pages).
3. Always include the homepage.
4. Set a coverage caveat and CAP the artifact confidence at 3 (recorded in Phase 3). The skill must work for clients with no analytics audit.

Skip to Step 4.

### Step 2: Extract per-page metrics

From the performance profile, extract for each page: `path`, `sessions`, `cvr` (conversion/submit rate), `bounce` (bounce rate %), and `mobile_bounce` / `desktop_bounce` if a device split exists. Also note a `benchmark_cvr` (the site-average or peer-group CVR the profile reports). Build a JSON array:

```json
{
  "benchmark_cvr": 2.0,
  "pages": [
    {"path": "/pricing", "sessions": 5600, "cvr": 0.4, "bounce": 51.0, "mobile_bounce": 58.0, "desktop_bounce": 44.0, "lane": "conversion"},
    {"path": "/blog/guide-x", "sessions": 3200, "cvr": null, "bounce": 62.0, "lane": "content"}
  ]
}
```

Classify each page's `lane`: `conversion` (product, pricing, solution, demo, contact, signup) or `content` (blog, resources, guides, docs). When unsure, default to `conversion`.

**Device-gap inputs are currently always absent.** The per-page `mobile_bounce` / `desktop_bounce` fields are not emitted by the current producers: ga4-audit and aa-audit report device data at site level only, with no per-page device cross-report. So the 0.15 device term in Step 3 contributes 0 today. Do not derive per-page values from the site-level device split; leave the fields out and let the term zero out. The term is forward-compatible: it activates automatically if a producer adds a per-page device cross-report.

### Step 3: Rank deterministically

Run the selection script (the arithmetic is reliability-critical, so it is scripted, not done by hand):

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY skills/live-capture/scripts/page_select.py --metrics <metrics.json> [--conversion-slots 8] [--content-slots 2]
```

The script implements the authoritative formula:

```
traffic_norm        = page_sessions / max(page_sessions)
conversion_gap_norm = clamp((benchmark_cvr - page_cvr) / benchmark_cvr, 0, 1)   # distance BELOW benchmark, never raw CVR
bounce_norm         = page_bounce / 100
device_gap_norm     = abs(mobile_bounce - desktop_bounce) / 100
leverage = 0.35*traffic_norm + 0.30*conversion_gap_norm + 0.20*bounce_norm + 0.15*device_gap_norm
```

- `conversion_gap` is distance below benchmark, so a high-converting page does not score as leverage. Pages with no CVR contribute 0 to that term.
- **Two lanes:** Lane 1 (conversion) ranked by `leverage`, default 8 slots. Lane 2 (content/resource) ranked by raw organic sessions, default 1-2 slots (so the content-page consumer CR-04 has input).
- **Always-capture (injected by the script):** the homepage (positioning's top surface, often absent from a per-page profile) and the healthiest page (lowest bounce / highest CVR among captured candidates, a propagatable positive control).

The script returns the ordered, deduplicated page list with each page's lane and a flag for always-capture injection.

### Step 4: Emit the selection

Carry forward: the ordered page list, each page's lane, and a coverage note. If the no-profile fallback ran, carry the confidence cap (3) and the caveat text. If the page count exceeds the frontmatter digest cap (~10), note that the digest will cover the selected pages only and the body carries the rest.

## Output

The ordered page list (with lanes), plus the coverage note and any confidence cap, passed to Phase 2.
