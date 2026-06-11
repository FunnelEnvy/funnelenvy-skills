---
name: aa-audit
version: 1.1.0
description: "When the user wants to audit Adobe Analytics data for a property. Also use when the user mentions 'AA audit,' 'Adobe Analytics audit,' 'AA performance profile,' or 'AA traffic analysis.' Runs a Python script against the AA 2.0 Reporting API, interprets the JSON output, and produces a structured performance-profile.md context file (.claude/context/ L1). Single agent, no depth flag. Works with any AA implementation given a client config file."
updated: 2026-06-11
---

# AA Audit

You are an analytics specialist. Your job is to run the AA audit script, interpret the structured JSON output, classify performance patterns, and produce a performance profile that powers downstream experiment planning and ICE scoring calibration.

**You are an L1 skill.** You run a Python script that queries Adobe Analytics, analyze the returned data, and produce a structured context file. This means:
- You execute `aa_audit.py` which handles all API calls and outputs JSON
- You interpret and analyze the JSON data
- You produce one context file: `.claude/context/performance-profile.md`
- Your output is machine-readable (YAML frontmatter + structured markdown), not a deliverable

**Output location:** `.claude/context/performance-profile.md`
**Token budget:** ~50-80K
**Runtime:** ~5-8 minutes
**Agents:** Single agent. No multi-agent pipeline.
**Model:** Opus

---

## Invocation

```
/aa-audit
/aa-audit --config /path/to/config.json
/aa-audit --config /path/to/config.json --days 30
/aa-audit --config /path/to/config.json --days 90 --no-compare
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--config` | (required or from env) | Path to client AA config JSON |
| `--days` | 90 | Number of days to look back from today |
| `--no-compare` | false | Skip period-over-period comparison |

### Config Resolution

The Python script resolves config in this order:
1. `--config /path/to/config.json` CLI flag
2. `ADOBE_AA_CONFIG` env var pointing to file path
3. Fail with clear error

### Credential Requirements

These env vars must be set (never stored in repo):
- `ADOBE_AA_CLIENT_ID`
- `ADOBE_AA_CLIENT_SECRET`
- `ADOBE_AA_ORG_ID`

---

## Preconditions

**Hard requirements:**
- Python 3 with `requests` package installed
- Adobe Analytics credentials set as env vars
- A valid config JSON file accessible at the specified path
- The `aa_audit.py` script must be locatable (same directory as this SKILL.md)

**Soft requirements:**
- `company-identity.md` in `.claude/context/`: If present with confidence >= 2,
  Step 8 enriches the output with product-line groupings, funnel stage mapping,
  and tracking gap flags. If missing, Steps 1-7 produce complete output without it.

**Error states:**
- Credentials not set: Script exits with "ADOBE_AA_CLIENT_ID and ADOBE_AA_CLIENT_SECRET env vars required."
- Config not found: Script exits with "Config file not found: [path]"
- Auth fails: Script exits with token error. Tell user to check credentials.
- No data: If JSON output has empty pages/channels arrays, exit with "No data returned. Check report suite ID and date range."

---

## Prior Work Detection

**None.** Analytics data is a time-bounded snapshot. Each run overwrites `.claude/context/performance-profile.md` entirely. No incremental extension, no confidence-only-rises rule.

---

## Execution Pipeline

### Step 1: Locate Script and Run

Find `aa_audit.py` in the same directory as this SKILL.md. Run it with the user's flags:

```bash
python3 /path/to/aa_audit.py --config /path/to/config.json --days N [--no-compare]
```

Capture stdout (JSON) and stderr (progress messages). Display progress to the user as the script runs.

If the script exits with an error, display the error and stop. Do not retry.

**Config notes (optional blocks):**
- `scope`: isolates one sub-property inside a blended report suite. `scope.segment_id` (preferred when a segment exists) applies that segment to every report; otherwise `scope.prefixes` builds a broad single-token `search` clause on `scope.prefix_dimension` (default `variables/entrypage`). When `scope` is unset, every report runs whole-suite (pre-change behavior). The script reports the resolved method in `meta.scope_method` (`segment` | `prefix` | `none`). When scope is prefix-only (approximate), note the post-consent page-attribution caveat in the profile and cap confidence.
- `interaction_dimensions`: array of element-click dimensions to enumerate (default `customlink`/`clickmaplink`/`clickmappage`). Legacy `dimensions.link_text` is honored as a single-eVar fallback when `interaction_dimensions` is absent.

### Step 2: Parse JSON and Validate

Parse the JSON output. Verify:
- `site_totals` has non-zero `visits`
- `pages` array is non-empty
- `channels` array is non-empty

If validation fails, report which sections are empty and suggest checking the report suite ID.

Display a summary:
```
AA data pulled successfully.

  Report suite: [rsid]
  Date range: [start] to [end] ([N] days)
  Site totals: [visits] visits, [visitors] visitors
  Pages: [N] rows
  Channels: [N] rows
  Comparison: [enabled | disabled]
```

### Step 3: Interpret Page Performance

From the `pages` array and `site_totals`:

1. **Compute site-wide averages:**
   - Total visits, visitors, pageviews, bounces
   - Bounce rate = bounces / visits (or from bouncerate metric directly)
   - Pages per session = pageviews / visits (from site totals)
   - Avg time on site (from averagetimespentonsite if available)

2. **For each page row, compute:**
   - Bounce rate (from bouncerate column or bounces/visits)
   - Engagement rate = 100 - bounce_rate
   - Pages per session approximation (pageviews / visits for that page)
   - Conversion rates for each conversion event (event count / visits)

3. **Failure mode classification** (same thresholds as ga4-audit):
   - `shallow_engagement`: pages/session < 75% of site avg AND bounce > site avg + 10pp
   - `deep_engagement`: pages/session > 150% of site avg AND CVR < 50% of site avg
   - `null`: neither condition met

4. **High-bounce pages:** Filter for bounce rate >50% AND >100 visits

5. **Page grouping by URL pattern:**
   - Extract first path segment, group pages appearing 3+ times
   - Compute session-weighted averages per group
   - Pages with <50 visits not matching a group go to "Long Tail"

### Step 4: Interpret Conversion Events

From the config's `conversion_events` and `engagement_events`:

1. **Event inventory:** List all configured events with their total counts from site_totals
2. **Primary conversion event:** First conversion event in config list
3. **Site-wide CVR:** Primary event total / total visits
4. **Per-page conversion funnels:** From `page_conversions` data, top pages by each conversion event
5. **Underperforming pages:** Pages with CVR < 50% of their group average AND >200 visits

**User confirmation:** Present the event list from config and ask user to confirm the primary conversion event. If they want to change it, adjust downstream analysis.

### Step 5: Interpret Channel, Device, and Segment Data

**Channels** (from `channels` array):
- Compute % of total visits per channel
- Compute conversion rate per channel for primary event
- Note channel concentration (flag if any channel >70%)

**Channel detail** (from `channel_detail` array):
- Top sources within key channels

**Devices** (from `devices` array):
- Compute mobile vs desktop gaps (bounce rate, conversion rate, duration)
- Significance: High (>10pp bounce gap or >50% CVR gap), Medium (5-10pp / 25-50%), Low (<5pp / <25%)

**New vs returning** (from `new_vs_returning` array):
- The data uses `variables/visitnumber` (AA's Visit Number dimension). Rows have values "1", "2", "3", etc.
- Bucket: visit number "1" = new visitors, visit number "2"+ = returning visitors. Aggregate all 2+ rows into a single "returning" segment.
- Compute returning:new ratio using the aggregated visit counts.
- Signal classification:
  - >5x: `familiarity_dependent`
  - 2-5x: `normal_b2b`
  - 1-2x: `strong_first_visit`
  - <1x: `acquisition_heavy`

### Step 6: Interpret Landing Pages and Mismatches

**Landing pages** (from `landing_pages` array):
- % of entries for each
- High-bounce entry points (>55% bounce, top 20)

**Source x Landing Page mismatches** (from `landing_page_channels`):
- For each top landing page, compare channel performance
- Bounce mismatch: >15pp gap between channels
- Conversion mismatch: one channel's CVR <50% of another

### Step 7: Interpret Element Instrumentation (REQUIRED)

This produces the REQUIRED Element-Level Interactions body section. It always emits a finding -- presence with volumes when elements are tracked, AND an explicit absence assertion when they are not. Never silently skip.

**Element interactions** (from `element_interactions.by_dimension`, keyed by interaction dimension):
- For each dimension, list top interacted elements by visit volume and interaction rate = element count / total visits.
- Roll up into `tracked_elements[]` (each `name`, `count`, `status`). `status="dark"` when the comparison block flagged a present-then-0 regression for that element; else `live`.

**Clickmap regions** (from `clickmap_regions` array, if present):
- Top interacted regions (supplementary).

**Determine `element_instrumentation_state`:**
- `present`: interaction dimensions configured AND meaningful volume returned across the scoped unit.
- `partial`: some interaction dimensions return data but expected structural element classes (e.g., primary CTA) are missing.
- `absent`: no interaction dimensions configured, OR all configured dimensions return empty for the scoped unit.

**Absence assertion (when `partial`/`absent`):**
- Populate `missing_element_classes[]` (e.g., primary CTA, nav links, form fields not instrumented).
- Set a non-null `instrumentation_ask` recommending the specific tracking to add (e.g., "Instrument primary CTA clicks via Custom Link s.tl() or Activity Map").
- The body section LEADS with this gap statement. Do not write "No element-level interaction data available" as a terminal skip -- absence is a finding, not a non-result.

**Search-reliability caveat:** element enumeration uses a broad single-token prefix `search` at an untruncated limit. Empty results from a narrow/over-scoped query are inconclusive, NOT proof of absence. The script already enumerates broadly; if a dimension returns empty under an approximate (prefix-only) scope, treat as inconclusive and note it.

### Step 7b: Measurement Integrity (REQUIRED)

This produces the REQUIRED Measurement Integrity body section from `event_liveness` and a friction pass. Always emit it.

**Event liveness / dead bindings** (from `event_liveness[]`):
- Each configured conversion/engagement event carries `count` and `status`.
- `dead`: count == 0 over the full window -- a configured event whose binding never fired. Surface as a dead binding (the implementation is wired in config but not emitting).
- `dark`: present in the comparison window then 0 in primary (from `comparison.event_liveness_regressions`) -- a click/event that regressed dark partway through.
- `spiked`: 0 then present, or a large jump -- newly firing or a measurement spike worth flagging.
- Roll dead bindings + dark/spiked zero-crossings into `measurement_integrity_flags[]`.

**Friction interactions** (from `element_interactions` values + event names):
- The script pre-flags friction candidates: each `element_interactions` row carries a `friction` boolean set by `aa_audit.py`'s `is_friction_token` (the single source of truth for the token set, shared by script, SKILL, and tests). Use that flag rather than re-deriving tokens. For event names not run through the script, apply the same helper conceptually.
- Surface the top non-navigation interactions by volume.
- When a baseline event is determinable (e.g., a form-start or configuration-start event), compute `ratio_to_baseline` for each friction interaction (friction count / baseline count); else leave `ratio_to_baseline` null.
- Populate `friction_interactions[]` (each `interaction`, `count`, `ratio_to_baseline`, `type`).

If no events are dead/dark/spiked and no friction interactions are detected, state that explicitly ("No dead bindings, zero-crossings, or friction interactions detected") -- the section is still present.

### Step 8: Opportunity Sizing and Analysis

**Three formula types (same as ga4-audit):**

| Type | Formula | When |
|------|---------|------|
| CVR Improvement | `(target_rate - current_rate) * monthly_sessions * 0.4` | Page converts below group average |
| Bounce Reduction | `bouncing_sessions * recovery_rate * site_cvr * 0.4` | High-bounce page |
| Traffic Reallocation | `sessions * capture_rate * 0.4` | Pages with no conversion path |

**Recovery rates:** 0.15 (messaging), 0.10 (UX)
**Capture rates:** 0.01 (informational), 0.03 (product/service pages)

**Impact buckets (not point estimates):**
- `small`: <5 estimated additional conversions/month
- `medium`: 5-20
- `large`: >20

**Comparison period analysis** (when comparison data present):
- Compute trends: sessions_change_pct, primary_cvr_change_pp, bounce_rate_change_pp, mobile_bounce_change_pp
- Apply trend tags: `[WORSENING]` (>10% or >5pp), `[IMPROVING]` (>10% or >5pp), `[STABLE]` (within)

### Step 9: Write Performance Profile

Construct `.claude/context/performance-profile.md` using the same schema as ga4-audit output.

#### Frontmatter Fields

All fields required unless noted.

- Metadata: `schema` ("performance-profile"), `schema_version` ("2.3"), `generated_by` ("aa-audit"), `last_updated`, `last_updated_by` ("aa-audit"), `confidence` (1-5), `company` (from config company_id), `report_suite`, `date_range`, `days`
- Traffic: `total_sessions` (visits), `total_users` (visitors), `device_mobile_pct` (integer %)
- Top pages (top 5): `top_pages[]` each with `path`, `sessions`, `bounce_rate`, `pages_per_session`, `avg_engagement_sec`, `failure_mode`
- Conversions: `conversion_events[]` each with `name`, `count`, `classification`. Plus `primary_conversion_event`, `primary_conversion_rate` (%)
- Channels (top 3): `top_channels[]` each with `channel`, `sessions`, `bounce_rate`
- Mismatches: `source_page_mismatches[]` each with `page`, `better_channel`, `worse_channel`, `gap_type`, `better_value`, `worse_value`
- New/returning: `new_vs_returning` with `new_sessions_pct`, `new_conversion_rate`, `returning_conversion_rate`, `returning_to_new_ratio`, `signal`
- Page groups: `page_groups[]` each with `group`, `url_pattern`, `monthly_sessions`, `conversion_rate`, `bounce_rate`, `page_count`
- Opportunities: `top_opportunities[]` each with `page`, `issue`, `formula_type`, `current_metric`, `target_metric`, `monthly_sessions`, `estimated_monthly_impact`, `action_category`, `sizing_note`
- Data quality: `traffic_adequacy` ("high" | "adequate" | "low"), `sampling_applied` (false for AA 2.0 virtual report suites)
- Scope (schema 2.3): `scope_applied` (bool), `scope_method` ("segment" | "prefix" | "none", from `meta.scope_method`), `scope_note` (string | null; description + accuracy caveat when approximate/prefix-only)
- Element instrumentation (schema 2.3, ALWAYS emitted): `element_instrumentation_state` ("present" | "partial" | "absent"), `tracked_elements[]` each `name`/`count`/`status` ("live" | "dark"), `missing_element_classes[]`, `instrumentation_ask` (string | null). `element_interactions_available` retained for back-compat but is no longer a skip signal.
- Measurement integrity (schema 2.3): `event_liveness[]` each `event`/`count`/`status` ("live" | "dead" | "dark" | "spiked"), `measurement_integrity_flags[]`, `friction_interactions[]` each `interaction`/`count`/`ratio_to_baseline` (nullable)/`type`
- Comparison (omit when --no-compare): `comparison_period` with `start`, `end`. `trends` with `sessions_change_pct`, `primary_cvr_change_pp`, `bounce_rate_change_pp`, `mobile_bounce_change_pp`
- L0: `l0_available` (bool), `l0_confidence` (int | null)

#### AA-to-GA4 Metric Mapping

Use these mappings when writing the output to match the ga4-audit schema:

| Schema Field | AA Metric | Notes |
|---|---|---|
| sessions | metrics/visits | Direct |
| users | metrics/visitors | Direct |
| bounce_rate | metrics/bouncerate | Direct (%) |
| engagement_rate | 100 - bouncerate | Computed |
| avg_duration | metrics/averagetimespentonsite | Seconds |
| pages_per_session | pageviews / visits | Computed from site totals |
| conversions | from config conversion_events | Client-specific |

#### Body Sections (10 REQUIRED, 1 OPTIONAL)

1. **Property Overview** - Report suite metadata, date range, data quality notes. Include the scope statement: scoped sub-property (segment/prefix) or whole-suite, plus the accuracy caveat when prefix-only.
2. **Page Performance** - 4 subsections: Top Pages, High-Bounce Pages, Page Group Performance, Underperforming Pages.
3. **Conversion Events** - Event Inventory, Per-page funnels, Missing Tracking Gaps.
4. **Channel Performance** - By Channel, Top Sources (from channel_detail).
5. **Device & User Segment Performance** - Device Breakdown, Mobile vs Desktop Gap, New vs Returning.
6. **Landing Page Performance** - Top Entry Pages, High-Bounce Entry Points, Source x Landing Page Mismatches.
7. **Opportunity Sizing** - Quantified opportunities with impact buckets.
8. **Element-Level Interactions** (REQUIRED, from Step 7) - ALWAYS present. Element inventory with volumes (`tracked_elements`) and interaction rates when instrumented; when `element_instrumentation_state` is `partial`/`absent`, LEADS with the gap statement, `missing_element_classes`, and `instrumentation_ask`. Includes the broad-prefix search-reliability caveat. Friction interactions surface here.
9. **Measurement Integrity** (REQUIRED, from Step 7b) - ALWAYS present. Dead bindings (configured events with zero volume over the window), dark/spiked zero-crossings (from the comparison diff), and friction interactions (token match + top non-navigation, with ratio-to-baseline when determinable).
10. **Key Metrics Summary** - Strengths, Weaknesses, Experiment Opportunities, Data Gaps.
11. **L0 Enrichment Notes** (OPTIONAL) - Only when company-identity.md consumed.

**Scope + confidence caveat:** when `scope_method` is `prefix` (approximate, no segment), document the post-consent page-attribution caveat in Property Overview and cap `confidence` (do not exceed 3 on scope grounds alone).

#### Trend Tags (when comparison enabled)

- `[WORSENING]`: degraded >10% or >5pp
- `[IMPROVING]`: improved >10% or >5pp
- `[STABLE]`: within +/-10% or +/-5pp

### Step 10: L0 Enrichment (Optional)

1. Glob `.claude/context/company-identity.md`
2. If missing or confidence < 2: set `l0_available: false`, skip.
3. If present: enrich with product-line groupings, funnel stage mapping, tracking gap flags.
4. Update frontmatter and add "L0 Enrichment Notes" section.

---

## Quality Checks

Before writing the final file, verify:

1. [ ] All 10 REQUIRED body sections present (including Element-Level Interactions and Measurement Integrity)
2. [ ] YAML frontmatter has all required fields; `schema_version` is `"2.3"`
3. [ ] Conversion events confirmed by user
4. [ ] High-Bounce uses >50% bounce / >100 sessions thresholds
5. [ ] Underperforming uses <50% group avg CVR / >200 sessions
6. [ ] Landing Page section uses entry page data (not page path)
7. [ ] Key Metrics Summary cites specific numbers
8. [ ] Confidence score reflects data quality
9. [ ] No fabricated data - every number from AA JSON output
10. [ ] Date range explicit in frontmatter and Property Overview
11. [ ] Page grouping covers >90% of sessions
12. [ ] Opportunity sizing uses impact buckets, not point estimates
13. [ ] Every opportunity has sizing_note with conservatism factors
14. [ ] New vs Returning section present with signal classification
15. [ ] Source x Landing Page Mismatches uses >15pp bounce / <50% CVR thresholds
16. [ ] If comparison enabled: trends section present with all four metrics
17. [ ] If L0 consumed: l0_available true and enrichment section exists
18. [ ] Element-Level Interactions section present (REQUIRED): `element_instrumentation_state` emitted; when `partial`/`absent`, `missing_element_classes` populated and `instrumentation_ask` non-null, section leads with the gap statement (no silent skip)
19. [ ] Measurement Integrity section present (REQUIRED): `event_liveness` covers every configured event; dead bindings and dark/spiked zero-crossings surfaced; friction interactions populated (or "None detected")
20. [ ] Scope frontmatter present (`scope_applied`, `scope_method`, `scope_note`); when `scope_method` is `prefix`, scope note + accuracy caveat in Property Overview and confidence capped accordingly

---

## Completion Summary

After writing the file, display:

```
Performance profile written to .claude/context/performance-profile.md

  Report suite: [rsid] ([company_id])
  Date range: [start] to [end] ([N] days)
  Sessions: [N] | Users: [N] | Mobile: [N]%
  Conversion events: [N] configured ([primary] as primary, [rate]% site-wide)
  Traffic adequacy: [high/adequate/low]
  Confidence: [N]
  Comparison: [enabled, vs [start] to [end] | disabled (--no-compare)]
  Scope: [segment | prefix (approximate) | whole-suite]
  Element instrumentation: [present | partial | absent]
  Measurement integrity: [N dead bindings, N dark/spiked, N friction]

  Key findings:
  - [top strength]
  - [top weakness]
  - [top experiment opportunity]

Run /hypothesis-generator to produce data-calibrated experiment hypotheses.
```
