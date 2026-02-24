> **Authoritative schema.** ga4-audit is a single-agent skill with no phase files.
> This schema file is the authoritative definition. `skills/ga4-audit/SKILL.md` references it directly.

---

# Performance Profile Schema (Layer 1)

**Version:** 1.0.0
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
schema_version: "1.0"
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
  - path: "/pricing"
    sessions: 5600
    bounce_rate: 38.5
  - path: "/solutions/enterprise"
    sessions: 3200
    bounce_rate: 51.3
  - path: "/blog/guide-to-x"
    sessions: 2800
    bounce_rate: 62.0
  - path: "/demo"
    sessions: 2100
    bounce_rate: 28.4

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

# Data quality
traffic_adequacy: "high"             # high | adequate | low
sampling_applied: false
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

**Downstream consumption pattern:** Read frontmatter first. If `top_pages`, `primary_conversion_rate`, `traffic_adequacy`, and `device_mobile_pct` are sufficient for your needs, stop there. Only read the body when you need per-page conversion funnels, channel breakdowns, or the full high-bounce analysis.

---

### Markdown Body Sections

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

| Page | Sessions | Users | Bounce Rate | Engagement Rate | Avg Duration |
|------|----------|-------|-------------|-----------------|--------------|
| / | 12,400 | 9,800 | 42.1% | 57.9% | 1:42 |
| /pricing | 5,600 | 4,200 | 38.5% | 61.5% | 2:15 |
| ... | ... | ... | ... | ... | ... |

### High-Bounce Pages (>50% bounce, >100 sessions)

| Page | Sessions | Bounce Rate | Engagement Rate | Notes |
|------|----------|-------------|-----------------|-------|
| /blog/guide-to-x | 2,800 | 62.0% | 38.0% | Top blog entry point |

### Underperforming Pages (conversion rate <50% of site average)

| Page | Sessions | Page Conversion Rate | Site Average | Gap |
|------|----------|---------------------|--------------|-----|
| /solutions/enterprise | 3,200 | 0.5% | 1.97% | -75% |
```

"High-Bounce" threshold: >50% bounce rate AND >100 sessions (filters out low-traffic noise). "Underperforming" threshold: page conversion rate below 50% of site-wide primary conversion rate AND >200 sessions.

**Used by:** hypothesis-generator (performance-driven triggers: landing page mismatch, conversion friction, first-impression failure), website-audit (page prioritization).

---

#### 3. Conversion Events (REQUIRED)

Full event inventory with classification, plus per-page conversion funnels for top conversion events.

```markdown
## Conversion Events

### Event Inventory

| Event | Count | Classification | Notes |
|-------|-------|---------------|-------|
| generate_lead | 890 | conversion | Primary conversion event |
| form_submit | 420 | conversion | |
| page_view | 245,000 | navigation | Default GA4 |
| scroll | 180,000 | engagement | Default GA4 |
| click | 95,000 | engagement | |
| file_download | 340 | engagement | |
| custom_signup_step | 210 | custom | Funnel event |

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

#### 5. Device Performance (REQUIRED)

Desktop/mobile/tablet split with gap analysis.

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
```

Gap significance: "High" = >10pp bounce gap or >50% conversion rate gap. "Medium" = 5-10pp bounce or 25-50% conversion gap. "Low" = <5pp bounce and <25% conversion gap.

**Used by:** hypothesis-generator (mobile UX/messaging friction triggers), website-audit (mobile optimization priority).

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
```

Landing page data uses `landingPage` dimension in GA4. Different from Page Performance (which includes all pageviews, not just entries).

**Used by:** hypothesis-generator (first-impression failure triggers, landing page messaging mismatch), website-audit (entry experience audit).

---

#### 7. Key Metrics Summary (REQUIRED)

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

This section is explicitly opinionated. It's the analyst's interpretation of the raw data, designed to feed hypothesis generation. Each point must cite a specific metric from sections 1-6.

**Used by:** hypothesis-generator (additional signal source for context-derived hypotheses), render-default-deliverables (executive summary data points).

---

## Completeness Checklist

> A checklist item passes with either (a) populated content or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

A performance-profile.md file is considered **complete** when:

- [ ] YAML frontmatter has all required fields (schema, schema_version, generated_by, last_updated, last_updated_by, confidence, company, property_id, property_name, date_range, days, total_sessions, total_users, device_mobile_pct, top_pages, conversion_events, primary_conversion_event, primary_conversion_rate, top_channels, traffic_adequacy, sampling_applied)
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
