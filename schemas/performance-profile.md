> **Authoritative schema.** ga4-audit is a single-agent skill with no phase files.
> This schema file is the authoritative definition. `skills/ga4-audit/SKILL.md` references it directly.

---

# Performance Profile Schema (Layer 1)

**Version:** 2.0.0
**Output path:** `.claude/context/performance-profile.md`
**Produced by:** `ga4-audit`
**Consumed by:** hypothesis-generator (ICE scoring calibration + performance-driven hypotheses), website-audit (traffic prioritization), render-default-deliverables (Tier 4 opportunity sizing)

---

## Purpose

Time-bounded analytics snapshot from GA4. Contains page-level traffic, engagement, conversion, channel, and device data. Unlike other L1 context files, this is a full overwrite on each run (analytics data is a snapshot, not incremental knowledge).

**Boundary rule:** This file contains observed behavioral data from analytics. It does not contain positioning analysis (that's `audience-messaging.md`), competitive context (that's `competitive-landscape.md`), or recommendations (that's L2 deliverables). The "Key Metrics Summary" section is the one exception: it contains opinionated analysis of what the data means for experiments.

---

## Schema Definition

### YAML Frontmatter

```yaml
---
schema: performance-profile
schema_version: "2.0"
generated_by: ga4-audit
last_updated: 2026-02-23
last_updated_by: ga4-audit
confidence: 3                        # 1-5, lowest section confidence within this file
company: "Company Name"
property_id: "342047065"
property_name: "Acme Corp - GA4"
date_range: "2026-01-24 to 2026-02-23"
days: 30

# Traffic summary
total_sessions: 45200
total_users: 32100
device_mobile_pct: 38                # integer percentage

# Page performance summary (top 5)
top_pages:
  - path: "/"
    sessions: 12400
    bounce_rate: 42.1
    pages_per_session: 2.1
    avg_engagement_sec: 102
    failure_mode: null
  - path: "/pricing"
    sessions: 5600
    bounce_rate: 38.5
    pages_per_session: 2.8
    avg_engagement_sec: 135
    failure_mode: null
  - path: "/solutions/enterprise"
    sessions: 3200
    bounce_rate: 51.3
    pages_per_session: 1.2
    avg_engagement_sec: 45
    failure_mode: "shallow_engagement"
  - path: "/blog/guide-to-x"
    sessions: 2800
    bounce_rate: 62.0
    pages_per_session: 1.1
    avg_engagement_sec: 38
    failure_mode: "shallow_engagement"
  - path: "/demo"
    sessions: 2100
    bounce_rate: 28.4
    pages_per_session: 3.4
    avg_engagement_sec: 180
    failure_mode: null

# Conversion summary
conversion_events:
  - name: "generate_lead"
    count: 890
    classification: conversion
  - name: "form_submit"
    count: 420
    classification: conversion
  - name: "sign_up"
    count: 310
    classification: conversion
primary_conversion_event: "generate_lead"
primary_conversion_rate: 1.97        # percentage

# Channel summary (top 3)
top_channels:
  - channel: "Organic Search"
    sessions: 18900
    bounce_rate: 39.2
  - channel: "Paid Search"
    sessions: 10200
    bounce_rate: 48.7
  - channel: "Direct"
    sessions: 8400
    bounce_rate: 35.1

# Source x page mismatches (from Step 8b)
source_page_mismatches:
  - page: "/pricing"
    better_channel: "Organic Search"
    worse_channel: "Paid Search"
    gap_type: "bounce"          # bounce | conversion
    better_value: 39.0          # lower bounce = better; higher CVR = better
    worse_value: 54.0

# New vs returning (from Step 7b)
new_vs_returning:
  new_sessions_pct: 42         # integer percentage
  new_conversion_rate: 0.8     # percentage
  returning_conversion_rate: 3.2
  returning_to_new_ratio: 1.38 # returning sessions / new sessions
  signal: "normal_b2b"         # familiarity_dependent | normal_b2b | strong_first_visit | acquisition_heavy

# Page groups (from Step 4b)
page_groups:
  - group: "Blog"
    url_pattern: "/blog/*"
    monthly_sessions: 12400
    conversion_rate: 0.19
    bounce_rate: 61.2
    page_count: 18
  - group: "Product"
    url_pattern: "/solutions/*"
    monthly_sessions: 8900
    conversion_rate: 2.0
    bounce_rate: 41.3
    page_count: 6

# Opportunity sizing (from Step 9b)
top_opportunities:
  - page: "/pricing"
    issue: "Paid search bounce 15pp above organic"
    formula_type: "bounce_reduction"
    current_metric: 54.0
    target_metric: 39.0
    monthly_sessions: 3400
    estimated_monthly_impact: "medium"   # small (<5) | medium (5-20) | large (>20)
    action_category: "messaging"          # messaging | ux | form | structural
    sizing_note: "Estimated using standard CRO conservatism factors (0.4x), not property-specific data"

# Data quality
traffic_adequacy: "high"             # high | adequate | low
sampling_applied: false

# Period-over-period comparison (from Fix 5; omitted when --no-compare)
comparison_period:
  start: "2025-10-27"
  end: "2026-01-24"
trends:
  sessions_change_pct: -12.3        # negative = declining
  primary_cvr_change_pp: 0.3        # percentage points
  bounce_rate_change_pp: 2.1
  mobile_bounce_change_pp: 4.5

# L0 enrichment (from Step 11)
l0_available: false          # bool: whether company-identity.md was consumed
l0_confidence: null          # int|null: L0 confidence at consumption time
---
```

**Field notes:**
- `traffic_adequacy`: "high" = >10K sessions/mo. "adequate" = 1K-10K. "low" = <1K. Drives downstream confidence caps.
- `sampling_applied`: Whether GA4 applied data sampling to any report. If true, all metrics are approximate.
- `device_mobile_pct`: Integer percentage of sessions from mobile devices. Quick downstream check for mobile optimization priority.
- `top_pages`: Only top 5 in frontmatter. Full top 50 in body. Sorted by sessions descending.
- `conversion_events`: Only events classified as "conversion" type. Full event inventory (including engagement/navigation/custom) in body.
- `primary_conversion_event`: The highest-volume conversion event. Used by downstream skills as the default metric.
- `primary_conversion_rate`: Site-wide conversion rate for the primary event.
- `pages_per_session`: Average pages viewed per session for this page's visitors. From `screenPageViewsPerSession` metric.
- `avg_engagement_sec`: Average engaged time in seconds. Derived from `engagedSessions` and `averageSessionDuration`.
- `failure_mode`: `null` (no clear failure pattern), `"shallow_engagement"` (messaging mismatch: low pages/session + high bounce), or `"deep_engagement"` (funnel friction: high pages/session + low conversion). Thresholds are relative to site-wide averages.
- `source_page_mismatches`: Pages where channel performance diverges significantly. `gap_type` is `"bounce"` (>15pp gap) or `"conversion"` (>50% CVR gap). Empty array if no mismatches exceed thresholds.
- `new_vs_returning`: Visitor mix analysis. `signal` classifies the returning:new ratio into a B2B behavioral pattern. `returning_to_new_ratio` is returning sessions divided by new sessions.
- `page_groups`: URL-prefix-based page groupings with aggregated metrics. Groups with 3+ pages via data-driven detection, with fallback heuristics.
- `top_opportunities`: Quantified experiment opportunities. `estimated_monthly_impact` is a bucket (small/medium/large), not a point estimate. `formula_type` is one of: `cvr_improvement`, `bounce_reduction`, `traffic_reallocation`. `action_category` is one of: `messaging`, `ux`, `form`, `structural`.
- `comparison_period`: The previous period used for trend comparison. Same duration as the primary period, immediately preceding it. Omitted entirely when `--no-compare` is used.
- `trends`: Period-over-period changes for key metrics. `_pct` fields are percentage changes. `_pp` fields are percentage point changes. Omitted when `--no-compare` is used.
- `l0_available`: Whether `company-identity.md` was found and consumed by Step 11. When `false`, no L0 enrichment was applied.
- `l0_confidence`: The confidence score of the L0 file at consumption time. `null` when L0 was not available.

**Downstream consumption pattern:** Read frontmatter first. If `top_pages`, `primary_conversion_rate`, `traffic_adequacy`, and `device_mobile_pct` are sufficient for your needs, stop there. Only read the body when you need per-page conversion funnels, channel breakdowns, or the full high-bounce analysis. If `trends` fields exist, the profile includes period-over-period comparison data. If omitted, the profile is a single-period snapshot. If `l0_available` is `true`, enrichment notes are available. If `false`, the profile was produced from GA4 data alone.

---

### Markdown Body Sections

8 REQUIRED sections + 1 OPTIONAL (L0 Enrichment Notes).

#### 1. Property Overview (REQUIRED)

Property metadata and data quality notes.

```markdown
## Property Overview

**Property:** [Name] ([ID])
**Date range:** [start] to [end] ([N] days)
**Total sessions:** [N] | **Total users:** [N]
**Data quality:** [sampling status, coverage gaps, event tracking completeness]
```

Note any data quality issues: sampling, missing events, suspicious patterns (e.g., 90% of sessions from one source). These feed into confidence scoring.

**Used by:** All downstream consumers (data quality context), ga4-audit (self-assessment).

---

#### 2. Page Performance (REQUIRED)

Top 50 pages by session volume with engagement metrics, plus callout tables for problem pages.

```markdown
## Page Performance

### Top Pages by Traffic

| Page | Sessions | Users | Bounce Rate | Engagement Rate | Avg Duration | Pages/Session | Avg Engagement (sec) | Failure Mode |
|------|----------|-------|-------------|-----------------|--------------|---------------|----------------------|--------------|
| / | 12,400 | 9,800 | 42.1% | 57.9% | 1:42 | 2.1 | 102 | - |
| /pricing | 5,600 | 4,200 | 38.5% | 61.5% | 2:15 | 2.8 | 135 | - |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### High-Bounce Pages (>50% bounce, >100 sessions)

| Page | Sessions | Bounce Rate | Engagement Rate | Notes |
|------|----------|-------------|-----------------|-------|
| /blog/guide-to-x | 2,800 | 62.0% | 38.0% | Top blog entry point |

### Page Group Performance

| Group | URL Pattern | Pages | Sessions | Weighted Bounce | Weighted Engagement | Conversions | Group CVR |
|-------|------------|-------|----------|----------------|--------------------|----|-----------|
| Blog | /blog/* | 18 | 12,400 | 61.2% | 38.8% | 24 | 0.19% |
| Product | /solutions/* | 6 | 8,900 | 41.3% | 58.7% | 178 | 2.0% |

### Underperforming Pages (conversion rate <50% of group average)

| Page | Group | Sessions | Page CVR | Group Avg CVR | Gap |
|------|-------|----------|----------|---------------|-----|
| /solutions/enterprise | Product | 3,200 | 0.5% | 2.0% | -75% |
```

The top pages table includes `Pages/Session`, `Avg Engagement (sec)`, and `Failure Mode` columns. These enable failure mode classification: `shallow_engagement` (messaging mismatch) vs `deep_engagement` (funnel friction) vs no failure mode. See SKILL.md Step 4 for classification thresholds.

"High-Bounce" threshold: >50% bounce rate AND >100 sessions (filters out low-traffic noise). "Underperforming" threshold: page conversion rate below 50% of group average CVR AND >200 sessions.

**Used by:** hypothesis-generator (performance-driven triggers: landing page mismatch, conversion friction, first-impression failure), website-audit (page prioritization).

---

#### 3. Conversion Events (REQUIRED)

Full event inventory with classification, plus per-page conversion funnels for top conversion events.

```markdown
## Conversion Events

### Event Inventory

| Event | Count | Classification | Notes |
|-------|-------|---------------|-------|
| generate_lead | 890 | conversion | Primary conversion event [KEY EVENT] |
| form_submit | 420 | conversion | [heuristic] |
| page_view | 245,000 | navigation | Default GA4 |
| scroll | 180,000 | engagement | Default GA4 |
| click | 95,000 | engagement | |
| file_download | 340 | engagement | |
| custom_signup_step | 210 | custom | Funnel event |

Events are tagged with their classification source: `[KEY EVENT]` (GA4 property-configured key event), `[heuristic]` (string-matching classification), or `[L0: maps to ...]` (matched to company-identity.md funnel stage).

### Event Classification Key
- **conversion**: Business outcome events (form completions, signups, purchases)
- **engagement**: Content interaction events (scroll, click, download, video)
- **navigation**: Page/screen view events
- **custom**: Client-defined events not fitting standard categories

### Per-Page Conversion Funnel: [primary_conversion_event]

| Page | Sessions | Conversions | Conversion Rate |
|------|----------|------------|-----------------|
| /demo | 2,100 | 250 | 11.9% |
| /pricing | 5,600 | 168 | 3.0% |
| /contact | 1,800 | 144 | 8.0% |
| / | 12,400 | 124 | 1.0% |
| ... | ... | ... | ... |

### Per-Page Conversion Funnel: [second_conversion_event]
[Same table format]

### Per-Page Conversion Funnel: [third_conversion_event]
[Same table format]

### Missing Tracking Gaps
- [Events that likely should exist but don't, e.g., no form_submit on a page with a form]
- [Missing enhanced measurement events]
```

Classification is confirmed with user during skill execution. Up to 3 conversion events get per-page funnel tables.

**Used by:** hypothesis-generator (form optimization triggers, untested high-value page triggers, conversion friction triggers), render-default-deliverables (opportunity sizing).

---

#### 4. Channel Performance (REQUIRED)

Channel group breakdown with engagement and conversion metrics.

```markdown
## Channel Performance

### By Channel Group

| Channel | Sessions | % of Total | Bounce Rate | Engagement Rate | Conversions | Conv Rate |
|---------|----------|-----------|-------------|-----------------|-------------|-----------|
| Organic Search | 18,900 | 41.8% | 39.2% | 60.8% | 372 | 1.97% |
| Paid Search | 10,200 | 22.6% | 48.7% | 51.3% | 153 | 1.50% |
| Direct | 8,400 | 18.6% | 35.1% | 64.9% | 210 | 2.50% |
| ... | ... | ... | ... | ... | ... | ... |

### Top Sources Within Key Channels

| Source / Medium | Channel | Sessions | Bounce Rate | Conv Rate |
|----------------|---------|----------|-------------|-----------|
| google / cpc | Paid Search | 8,900 | 49.1% | 1.45% |
| google / organic | Organic Search | 16,200 | 38.5% | 2.05% |
| ... | ... | ... | ... | ... |
```

"Key channels" = any channel with >5% of total sessions.

**Used by:** hypothesis-generator (channel-specific messaging mismatch triggers), ga4-campaign-analysis (baseline context).

---

#### 5. Device & User Segment Performance (REQUIRED)

Desktop/mobile/tablet split with gap analysis, plus new vs returning user analysis.

```markdown
## Device Performance

### Device Breakdown

| Device | Sessions | % of Total | Bounce Rate | Engagement Rate | Avg Duration | Conv Rate |
|--------|----------|-----------|-------------|-----------------|--------------|-----------|
| Desktop | 28,000 | 61.9% | 38.0% | 62.0% | 2:10 | 2.30% |
| Mobile | 15,200 | 33.6% | 52.1% | 47.9% | 1:05 | 1.20% |
| Tablet | 2,000 | 4.4% | 40.5% | 59.5% | 1:55 | 1.90% |

### Mobile vs Desktop Gap Analysis

| Metric | Desktop | Mobile | Gap | Significance |
|--------|---------|--------|-----|-------------|
| Bounce Rate | 38.0% | 52.1% | +14.1pp | High - mobile UX friction |
| Conversion Rate | 2.30% | 1.20% | -1.10pp | High - mobile conversion gap |
| Avg Duration | 2:10 | 1:05 | -1:05 | Medium - content consumption gap |

### New vs Returning

| Segment | Sessions | % of Total | Bounce Rate | Engagement Rate | Avg Duration | Conv Rate |
|---------|----------|-----------|-------------|-----------------|--------------|-----------|
| New | 19,000 | 42.0% | 48.2% | 51.8% | 1:20 | 0.8% |
| Returning | 26,200 | 58.0% | 36.1% | 63.9% | 2:05 | 3.2% |

**Returning:New ratio:** 1.38 | **Signal:** normal_b2b
```

Gap significance: "High" = >10pp bounce gap or >50% conversion rate gap. "Medium" = 5-10pp bounce or 25-50% conversion gap. "Low" = <5pp bounce and <25% conversion gap.

**Used by:** hypothesis-generator (mobile UX/messaging friction triggers, familiarity dependence triggers), website-audit (mobile optimization priority).

---

#### 6. Landing Page Performance (REQUIRED)

Entry pages (first page in session) with bounce and engagement metrics.

```markdown
## Landing Page Performance

### Top Entry Pages

| Landing Page | Sessions | % of Entries | Bounce Rate | Engagement Rate | Conv Rate |
|-------------|----------|-------------|-------------|-----------------|-----------|
| / | 10,800 | 23.9% | 42.1% | 57.9% | 1.2% |
| /blog/guide-to-x | 2,600 | 5.8% | 68.0% | 32.0% | 0.3% |
| ... | ... | ... | ... | ... | ... |

### High-Bounce Entry Points (>55% bounce, top 20 entry pages)

| Landing Page | Sessions | Bounce Rate | Top Source | Notes |
|-------------|----------|-------------|-----------|-------|
| /blog/guide-to-x | 2,600 | 68.0% | Organic Search | Content-to-CTA path broken |

### Source x Landing Page Mismatches

| Landing Page | Better Channel | Worse Channel | Metric | Better Value | Worse Value | Gap |
|-------------|---------------|--------------|--------|-------------|------------|-----|
| /pricing | Organic (39%) | Paid Search (54%) | Bounce Rate | 39% | 54% | 15pp |
```

Landing page data uses `landingPage` dimension in GA4. Different from Page Performance (which includes all pageviews, not just entries).

**Used by:** hypothesis-generator (first-impression failure triggers, landing page messaging mismatch, channel-specific mismatch triggers), website-audit (entry experience audit).

---

#### 7. Opportunity Sizing (REQUIRED)

Quantified experiment opportunities with impact buckets.

```markdown
## Opportunity Sizing

| Page | Issue | Formula | Impact Bucket | Action Category | Note |
|------|-------|---------|--------------|-----------------|------|
| /pricing | Paid search bounce 15pp above organic | bounce_reduction | medium | messaging | Standard CRO conservatism (0.4x) |

If no opportunities exceed the "small" threshold, state: "No opportunities met minimum impact threshold."
```

**Used by:** hypothesis-generator (pre-sized opportunity list for ICE calibration), render-default-deliverables (Tier 4 opportunity sizing).

---

#### 8. Key Metrics Summary (REQUIRED)

Opinionated analysis of what the data means. This is the one section that contains interpretation, not just data.

```markdown
## Key Metrics Summary

### Strengths
- [What's working well, backed by specific metrics]

### Weaknesses
- [What's underperforming, backed by specific metrics and thresholds]

### Experiment Opportunities
- [Specific pages/channels/devices where data suggests testable improvements]
- [Each opportunity should reference a specific metric gap]

### Data Gaps
- [What can't be measured with current tracking]
- [Missing events, insufficient traffic on key pages, etc.]
```

This section is explicitly opinionated. It's the analyst's interpretation of the raw data, designed to feed hypothesis generation. Each point must cite a specific metric from sections 1-7. When comparison data is available, findings include trend tags: `[WORSENING]`, `[IMPROVING]`, `[STABLE]`.

**Used by:** hypothesis-generator (additional signal source for context-derived hypotheses), render-default-deliverables (executive summary data points).

---

#### 9. L0 Enrichment Notes (OPTIONAL)

L0-derived context added by Step 11 post-processing. Only present when `company-identity.md` was available.

```markdown
## L0 Enrichment Notes

**L0 consumed:** [Yes (confidence: N) | No (not available)]

### Product-Line Grouping Overrides
[Which data-driven groups were overridden by L0 product categories, or "None"]

### Funnel Stage Mapping
[Which conversion events map to L0 funnel stages, or "No funnel stages defined in L0"]

### Tracking Gaps (L0 vs Observed)
[Services/funnels in L0 with no corresponding tracked events, or "No gaps detected"]
```

**Used by:** hypothesis-generator (funnel-aware triggers, tracking gap opportunities), render-default-deliverables (contextualized narrative).

---

## Completeness Checklist

> A checklist item passes with either (a) populated content or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

A performance-profile.md file is considered **complete** when:

- [ ] YAML frontmatter has all required fields (schema, schema_version, generated_by, last_updated, last_updated_by, confidence, company, property_id, property_name, date_range, days, total_sessions, total_users, device_mobile_pct, top_pages, conversion_events, primary_conversion_event, primary_conversion_rate, top_channels, source_page_mismatches, new_vs_returning, page_groups, top_opportunities, traffic_adequacy, sampling_applied, comparison_period (when applicable), trends (when applicable), l0_available, l0_confidence)
- [ ] Property Overview includes data quality notes (sampling status, coverage gaps)
- [ ] Page Performance has top 50 pages (or all pages if fewer) with traffic and engagement metrics
- [ ] High-Bounce Pages table populated (or marked "None above threshold")
- [ ] Underperforming Pages table populated (or marked "None above threshold" or "No conversion data")
- [ ] Conversion Events has full event inventory with classification
- [ ] Per-page conversion funnels for up to 3 conversion events
- [ ] Missing Tracking Gaps documented (or marked "No gaps detected")
- [ ] Channel Performance breakdown by channel group with conversion data
- [ ] Device Performance includes mobile vs desktop gap analysis
- [ ] Landing Page Performance uses `landingPage` dimension (not `pagePath`)
- [ ] High-Bounce Entry Points table populated (or marked "None above threshold")
- [ ] Key Metrics Summary has Strengths, Weaknesses, Experiment Opportunities, and Data Gaps
- [ ] Every metric claim in Key Metrics Summary cites a specific number from sections 1-6
- [ ] `confidence` value reflects data quality (5 = no sampling + complete tracking, 4 = minor gaps, 3 = sampling or significant gaps, 2 = major coverage issues, 1 = unreliable data)
- [ ] Page Group Performance subsection populated (or "No meaningful groups detected")
- [ ] Underperforming Pages uses group-relative benchmarks (not site-wide)
- [ ] Opportunity Sizing section populated (or "No opportunities met minimum threshold")
- [ ] Source x Landing Page Mismatches subsection populated (or "No mismatches exceeded thresholds")
- [ ] New vs Returning subsection populated with signal classification
- [ ] If comparison enabled: `comparison_period` and `trends` frontmatter fields present
- [ ] If comparison enabled: trend tags (`[WORSENING]`/`[IMPROVING]`/`[STABLE]`) applied to Key Metrics Summary
- [ ] `l0_available` and `l0_confidence` frontmatter fields present (even when false/null)
- [ ] If L0 consumed: L0 Enrichment Notes section present
- [ ] Every event classified into exactly one tier: `[KEY EVENT]`, `[heuristic]`, or `[L0: ...]`
- [ ] Opportunity sizing uses impact buckets, not point estimates

---

## Versioning Rules

Unlike other L1 context files, performance-profile.md is **overwritten entirely on each run**. Analytics data is a time-bounded snapshot. There is no incremental extension.

- Each run sets `generated_by` and `last_updated_by` to `ga4-audit`
- No prior work detection. No confidence-only-rises rule.
- Date range is always explicit in frontmatter
- If a downstream skill needs trend data, run the skill twice with different `--date-range` flags and compare manually (or wait for Phase 2 `--compare` flag)

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
| 2026-02-23 | Initial creation | ga4-audit |
```
