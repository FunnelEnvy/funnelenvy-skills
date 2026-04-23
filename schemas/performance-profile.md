> **Reference copy.** The authoritative schema is inlined in `skills/ga4-audit/SKILL.md` (Step 10).
> This file is a human-readable reference for contributor orientation. If the two diverge, SKILL.md wins.

---

# Performance Profile Schema (Layer 1)

**Version:** 2.2.0
**Output path:** `.claude/context/performance-profile.md`
**Produced by:** `ga4-audit`
**Consumed by:** hypothesis-generator (ICE scoring calibration + performance-driven hypotheses), website-audit (traffic prioritization), render-default-deliverables (executive summary enrichment)

---

## Purpose

Time-bounded analytics snapshot from GA4. Contains page-level traffic, engagement, conversion, channel, device, and AI-referrer data. Unlike other L1 context files, this is a full overwrite on each run (analytics data is a snapshot, not incremental knowledge).

**Boundary rule:** This file contains observed behavioral data from analytics. It does not contain positioning analysis (that's `audience-messaging.md`), competitive context (that's `competitive-landscape.md`), or recommendations (that's L2 deliverables). The "Key Metrics Summary" section is the one exception: it contains opinionated analysis of what the data means for experiments.

---

## Schema Definition

### YAML Frontmatter

```yaml
---
schema: performance-profile
schema_version: "2.2"
generated_by: ga4-audit
last_updated: 2026-04-23
last_updated_by: ga4-audit
confidence: 3                        # 1-5, lowest section confidence within this file
company: "Company Name"
property_id: "342047065"
property_name: "Acme Corp - GA4"
date_range: "2025-04-23 to 2026-04-23"
days: 365

# Traffic summary
total_sessions: 246679
total_users: 172100
device_mobile_pct: 38                # integer percentage

# Page performance summary (top 5)
top_pages:
  - path: "/"
    sessions: 12400
    bounce_rate: 42.1
    pages_per_session: 2.1
    avg_engagement_sec: 102
    failure_mode: null
  # ... (see SKILL.md Step 10 for full spec)

# Conversion summary
conversion_events:
  - name: "generate_lead"
    count: 890
    classification: conversion
primary_conversion_event: "generate_lead"
primary_conversion_rate: 1.97

# Channel summary (top 3)
top_channels:
  - channel: "Organic Search"
    sessions: 18900
    bounce_rate: 39.2
  # ...

# Source x page mismatches (Step 8b)
source_page_mismatches: []

# New vs returning (Step 7b)
new_vs_returning:
  new_sessions_pct: 42
  new_conversion_rate: 0.8
  returning_conversion_rate: 3.2
  returning_to_new_ratio: 1.38
  signal: "normal_b2b"

# Page groups (Step 4b)
page_groups:
  - group: "Blog"
    url_pattern: "/blog/*"
    monthly_sessions: 12400
    conversion_rate: 0.19
    bounce_rate: 61.2
    page_count: 18

# Opportunity sizing (Step 9b)
top_opportunities:
  - page: "/pricing"
    issue: "Paid search bounce 15pp above organic"
    formula_type: "bounce_reduction"
    current_metric: 54.0
    target_metric: 39.0
    monthly_sessions: 3400
    estimated_monthly_impact: "medium"
    action_category: "messaging"
    sizing_note: "Estimated using standard CRO conservatism factors (0.4x), not property-specific data"

# Data quality
traffic_adequacy: "high"             # high | adequate | low
sampling_applied: false

# Element-level interactions (Step 5b; omitted when no element data)
element_interactions_available: true
element_interaction_events: 3
discovered_parameters:
  - "linkText"
  - "customEvent:cta_label"
top_interactions:
  - page: "/pricing"
    event: "click"
    element: "Request Demo"
    parameter: "linkText"
    count: 245
    interaction_rate: 4.4

# AI-referrer traffic (Step 6b; always present, fields populated even when 0)
ai_sessions_count: 1490
ai_sessions_pct: 0.60
ai_conversions_count: 15
ai_conversion_rate: 1.01             # null when ai_sessions_count == 0
ai_traffic_trend: "flat"             # growing | flat | declining | insufficient_data
ai_not_set_landing_pct: 3.2
top_ai_sources:
  - source: "chatgpt"
    sessions: 998
    pct_of_ai: 67.0
  - source: "perplexity"
    sessions: 212
    pct_of_ai: 14.2
  - source: "copilot"
    sessions: 158
    pct_of_ai: 10.6
  - source: "gemini"
    sessions: 74
    pct_of_ai: 5.0
  - source: "claude"
    sessions: 48
    pct_of_ai: 3.2

# Period-over-period comparison (omitted when --no-compare)
comparison_period:
  start: "2024-04-23"
  end: "2025-04-23"
trends:
  sessions_change_pct: -12.3
  primary_cvr_change_pp: 0.3
  bounce_rate_change_pp: 2.1
  mobile_bounce_change_pp: 4.5

# L0 enrichment (Step 11)
l0_available: false
l0_confidence: null
---
```

**AI-referrer field notes:**
- `ai_sessions_count`: Sum of sessions across all AI referrers after canonical-source collapsing. Always populated (including `0`).
- `ai_sessions_pct`: Share of total audit-window sessions from AI referrers, 2 decimals. Always populated.
- `ai_conversions_count`: Sum of conversions (GA4 key events) across all AI referrers.
- `ai_conversion_rate`: `ai_conversions_count / ai_sessions_count * 100`, 2 decimals. Set to `null` when `ai_sessions_count == 0` to avoid divide-by-zero.
- `ai_traffic_trend`: Classification of trajectory. `growing` when delta > +25%, `declining` when < -25%, `flat` otherwise. `insufficient_data` when any month has < 5 sessions or the audit window < 6 months.
- `ai_not_set_landing_pct`: Data quality flag. Landing page is `(not set)` when GA4 couldn't capture the entry page for the session. Values > 15% indicate an implementation gap.
- `top_ai_sources`: Top 5 canonical sources with collapsed counts. Empty list `[]` when `ai_sessions_count == 0`. `source` uses the canonical name from the normalization map, not the raw GA4 value.

**Downstream consumption pattern:** Read frontmatter first. Element interaction and AI-referrer data are both present in frontmatter for fast checks. Read the full body only when detailed breakdowns are needed.

---

## Source Normalization - AI Traffic

GA4 returns inconsistent source values for LLM referrers. When querying `sessionSource`, apply `PARTIAL_REGEXP` (not `FULL_REGEXP` - see gotcha below) and dedupe known variant pairs before reporting.

### Canonical Map

| Canonical | Variants seen in the wild |
|---|---|
| chatgpt | `chatgpt.com`, `openai`, `chatgpt.com)`, `prod-usch-auditchatgpt.us.kworld.kpmg.com` |
| perplexity | `perplexity.ai`, `perplexity` |
| copilot | `copilot.microsoft.com`, `copilot.cloud.microsoft` |
| gemini | `gemini.google.com`, `bard.google.com` |
| claude | `claude.ai` |
| mistral | `chat.mistral.ai`, `mistral.ai` |

New variants encountered in production runs should be added to the canonical map as a maintenance task. Do not collapse unknown variants by inference.

### Regex Gotcha

GA4's `FULL_REGEXP` matches against the entire dimension value, not a substring. `chatgpt` as `FULL_REGEXP` will NOT match `chatgpt.com`. All AI-source queries MUST use `PARTIAL_REGEXP`.

The AI detection regex (case-insensitive, PARTIAL_REGEXP):

```
chatgpt|openai|claude\.ai|anthropic|gemini\.google|bard\.google|perplexity|copilot\.microsoft|copilot\.cloud|phind|poe\.com|deepseek|chat\.mistral|mistral\.ai|character\.ai|groq|you\.com|meta\.ai|huggingface
```

Mistral is matched via `chat\.mistral` or `mistral\.ai` rather than bare `mistral` to avoid false positives on unrelated source strings.

### Default Classification

Google's default channel grouping buckets all LLM referrers under "Referral." Any AI-channel view requires explicit segmentation. It is not provided natively.

---

## Markdown Body Sections

8 REQUIRED + 2 OPTIONAL (Element-Level Interactions, L0 Enrichment Notes).

For the full body section spec, see `skills/ga4-audit/SKILL.md` Step 10.

AI-referrer reporting lives inside Section 4 (Channel Performance) as a named subsection that appears after the Top Sources table. The subsection has two formats:

- **Full format** when `ai_sessions_count >= 20`: summary line, collapsed source table, monthly trajectory, top AI-driven landing pages, caveats (including any dedup pairs detected and `(not set)` flag), collapsible raw-source appendix.
- **Collapsed format** when `ai_sessions_count < 20`: one-line summary noting the count, number of sources, and that detailed breakdown is omitted due to low volume.

The frontmatter fields populate in both cases so downstream consumers can read the signal without needing to parse the body.

---

## Completeness Checklist

> A checklist item passes with either (a) populated content or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

A performance-profile.md file is considered **complete** when:

- [ ] YAML frontmatter has all required fields. `schema_version: "2.2"`.
- [ ] Property Overview includes data quality notes (sampling status, coverage gaps)
- [ ] Page Performance has top 50 pages (or all pages if fewer) with traffic and engagement metrics
- [ ] High-Bounce Pages table populated (or marked "None above threshold")
- [ ] Underperforming Pages table populated (or marked "None above threshold" or "No conversion data")
- [ ] Conversion Events has full event inventory with classification
- [ ] Per-page conversion funnels for up to 3 conversion events
- [ ] Missing Tracking Gaps documented (or marked "No gaps detected")
- [ ] Channel Performance breakdown by channel group with conversion data
- [ ] AI-Referrer Traffic subsection present inside Channel Performance. Collapsed one-liner when `ai_sessions_count < 20`, full breakdown otherwise.
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
- [ ] If element interaction data discovered: `element_interactions_available: true`, Element-Level Interactions body section present with all 3 subsections
- [ ] If no element interaction data: `element_interactions_available: false` or field omitted, no Element-Level Interactions body section
- [ ] Every event classified into exactly one tier: `[KEY EVENT]`, `[heuristic]`, or `[L0: ...]`
- [ ] Opportunity sizing uses impact buckets, not point estimates
- [ ] AI-referrer frontmatter fields populated (all 7 fields). `ai_conversion_rate` is `null` when `ai_sessions_count == 0`. `top_ai_sources` is `[]` when no AI traffic.
- [ ] AI-referrer queries used `PARTIAL_REGEXP` (not `FULL_REGEXP`). Verify by confirming `chatgpt.com` appears in results on properties with known AI referral traffic.
- [ ] AI source normalization applied (canonical collapsing done). Raw rows retained in the appendix inside the body subsection.
- [ ] `ai_not_set_landing_pct > 15%` is surfaced as a Tracking Gap entry in Data Quality.

---

## Versioning Rules

Unlike other L1 context files, performance-profile.md is **overwritten entirely on each run**. Analytics data is a time-bounded snapshot. There is no incremental extension.

- Each run sets `generated_by` and `last_updated_by` to `ga4-audit`
- No prior work detection. No confidence-only-rises rule.
- Date range is always explicit in frontmatter

### Schema Version History

| Version | Change |
|---------|--------|
| 2.2 | Added AI-referrer traffic frontmatter fields and body subsection (Step 6b). |
| 2.1 | Added element-level interaction frontmatter and body section (Step 5b). |
| 2.0 | Added page groups, source mismatches, period-over-period trends, failure modes, opportunity sizing. |
| 1.0 | Initial schema. |

Downstream skills should gate capability checks on `schema_version`. For example, a consumer that wants AI-referrer data should check `schema_version >= "2.2"`.

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
| 2026-04-23 | Added AI-referrer traffic fields (schema 2.2) | ga4-audit |
| 2026-02-23 | Initial creation | ga4-audit |
```
