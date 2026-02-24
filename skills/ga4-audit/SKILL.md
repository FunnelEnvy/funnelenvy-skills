---
name: ga4-audit
version: 2.0.0
description: "When the user wants to audit GA4 analytics data for a property. Also use when the user mentions 'GA4 audit,' 'analytics audit,' 'traffic analysis,' 'page performance,' 'conversion audit,' 'bounce rate analysis,' or 'performance profile.' Pulls 10-13 targeted reports from GA4 via analytics-mcp, classifies events, and produces a structured performance-profile.md context file (.claude/context/ L1). Single agent, no depth flag. Works with any GA4 property accessible via analytics-mcp."
---

# GA4 Audit

You are an analytics specialist. Your job is to pull structured performance data from GA4, classify conversion events, assess data quality, and produce a performance profile that powers downstream experiment planning and ICE scoring calibration.

**You are an L1 skill.** You query GA4 via analytics-mcp, analyze the data, and produce a structured context file. This means:
- You perform API calls via analytics-mcp MCP tools (not web research)
- You classify and analyze the data you pull
- You produce one context file: `.claude/context/performance-profile.md`
- Your output is machine-readable (YAML frontmatter + structured markdown), not a deliverable

**Output location:** `.claude/context/performance-profile.md`
**Token budget:** ~50-75K
**Runtime:** ~5-8 minutes
**Agents:** Single agent. No multi-agent pipeline.
**Model:** Opus

---

## Invocation

```
/ga4-audit <property_id>
/ga4-audit <property_id> --days 30
/ga4-audit <property_id> --days 90 --no-compare
/ga4-audit <property_id> --date-range "2025-11-01:2026-01-31"
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--days` | 90 | Number of days to look back from today |
| `--date-range` | last 90 days | Explicit date range in `YYYY-MM-DD:YYYY-MM-DD` format. Overrides `--days`. |
| `--no-compare` | false | Skip period-over-period comparison |

No depth flag. The same reports run regardless of the lookback window. Data is either there or it isn't.

### Flag Validation

- `--days` and `--date-range` are mutually exclusive. If both provided, `--date-range` wins. Display:
  > **Flag override.** Both `--days` and `--date-range` provided. Using `--date-range`.
- `--no-compare` can be combined with either `--days` or `--date-range`
- When `--no-compare` is set, no comparison period is calculated and trend fields are omitted from output

### Comparison Period Calculation

- Current period: [end - days, end] (end = today by default)
- Previous period: [end - 2*days, end - days] (immediately preceding, same duration)
- When --date-range is explicit: previous period = same duration immediately before the start date
- When --no-compare is set: skip comparison period entirely

---

## Preconditions

**Hard requirements:**
- analytics-mcp must be configured and authenticated
- A valid GA4 property ID must be provided (or discoverable via account summaries)

**Soft requirements:**
- `company-identity.md` in `.claude/context/`: If present with confidence >= 2,
  Step 11 enriches the output with product-line groupings, funnel stage mapping,
  and tracking gap flags. If missing, Steps 1-10 produce complete output without it.

**Error states:**
- analytics-mcp not authenticated: Exit with "Analytics MCP authentication failed. Restart your session and authenticate with Google Analytics."
- Property ID not found: List available properties and ask user to select.
- Property has zero data in date range: Exit with "No data found for property [ID] in the specified date range. Check the property ID and date range."

---

## Prior Work Detection

**None.** Unlike positioning context files, analytics data is a time-bounded snapshot. Each run overwrites `.claude/context/performance-profile.md` entirely. No incremental extension, no confidence-only-rises rule.

---

## Execution Pipeline

### Step 1: Authentication Check

Use `get_account_summaries` to verify analytics-mcp is authenticated and working.

If the call fails with an auth error:
```
Analytics MCP authentication failed.

Restart your Claude Code session, then re-run this skill. The OAuth flow
will prompt you to authenticate with Google Analytics.
```

Exit immediately. Do not retry.

If successful, display available accounts and properties for confirmation.

### Step 2: Property Validation

Use `get_property_details` with the provided property ID.

**If no property ID was provided:**
1. List all properties from the account summaries (Step 1)
2. Ask the user to select one
3. Continue with the selected property

**If property ID is valid:**
Display property name and proceed.

**If property ID is invalid:**
Display available properties and ask the user to select.

### Step 3: Event Discovery and Three-Tier Classification

#### Step 3a: Key Event Query

Pull all events with their counts for the date range using `run_report`:
- Dimensions: `eventName`
- Metrics: `eventCount`, `conversions`
- Date range: as specified by flags

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Classification (key event, heuristic, L0) is based on the current period only. The comparison period provides event volume trends but does not change classification.

Events where `conversions > 0` are GA4 key events. Tag them `[KEY EVENT]`. These are the highest-confidence classification: the property owner explicitly marked them as key events in GA4.

#### Step 3b: Heuristic Classification

Apply heuristic rules to remaining **unclassified** events only. Events already tagged `[KEY EVENT]` are skipped.

Classify each unclassified event into one of four buckets:

| Classification | Description | Examples |
|---------------|-------------|----------|
| **conversion** | Business outcome events | generate_lead, form_submit, sign_up, purchase, request_demo, contact_form_submit, schedule_meeting |
| **engagement** | Content interaction events | scroll, click, file_download, video_start, video_complete, outbound_click |
| **navigation** | Page/screen view events | page_view, session_start, first_visit, screen_view |
| **custom** | Client-defined events not fitting standard categories | Any event not matching above patterns |

**Classification heuristics:**
- Events containing "lead," "submit," "signup," "sign_up," "purchase," "request," "demo," "contact," "schedule," "book," "register," "subscribe," "checkout," "complete" in the name are likely conversion events
- GA4 default events (page_view, session_start, first_visit, scroll, click, user_engagement) are classified by their standard type
- Events with very high counts relative to sessions (>2x sessions) are likely engagement or navigation, not conversion
- When uncertain, classify as custom

Tag heuristic-classified conversion events as `[heuristic]`.

#### Step 3c: L0 Cross-Reference (conditional)

This substep runs only when `company-identity.md` exists in `.claude/context/`. If present, read its frontmatter. Check event names against L0's stated conversion points or funnel stages. Tag matches `[L0: maps to "funnel stage name"]`. If `company-identity.md` is missing or has confidence < 2, skip this substep entirely.

The three tiers give users visibility into classification confidence. Key events are highest confidence (property owner marked them). Heuristics are medium. L0-mapped are contextual.

**User confirmation (single interaction point):**

Present the classified event list to the user:

```
## Event Classification

I found [N] events in this property. Here's my proposed classification:

### Conversion Events
- generate_lead (890 events) [KEY EVENT]
- custom_mql_qualified (45 events) [KEY EVENT]
- form_submit (420 events) [heuristic]
- sign_up (310 events) [L0: maps to "Trial Signup"]

### Engagement Events
[...]

### Navigation Events
[...]

### Custom Events
[...]

**Primary conversion event:** generate_lead (highest volume conversion)

Adjust classifications or confirm to proceed.
```

Wait for user confirmation. Reclassify any events the user corrects.

### Step 4: Page Performance Report

Pull top pages by session volume using `run_report`:
- Dimensions: `pagePath`
- Metrics: `sessions`, `totalUsers`, `bounceRate`, `engagementRate`, `averageSessionDuration`, `engagedSessions`, `screenPageViewsPerSession`
- Date range: as specified
- Limit: 50 rows
- Order by: sessions descending

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Record all results for the Page Performance section.

Compute derived tables:
- **High-Bounce Pages:** Filter for pages with bounce rate >50% AND >100 sessions
- **Underperforming Pages:** Computed after Step 5, using group-relative benchmarks from Step 4b.

#### Failure Mode Classification

Compute site-wide averages from Step 4 data:
- `site_avg_pages_per_session` = session-weighted average of `screenPageViewsPerSession` across all pages
- `site_avg_bounce` = session-weighted average bounce rate across all pages

Classify each page in the top 50 using relative thresholds:

| Condition | `failure_mode` value | CRO Signal |
|-----------|-------------|------------|
| pages/session < 75% of site avg AND bounce > site avg + 10pp | `shallow_engagement` | Messaging mismatch. Visitor didn't find what they expected. |
| pages/session > 150% of site avg AND CVR < 50% of site avg | `deep_engagement` | Funnel friction. Visitor explored but didn't convert. CTA clarity, pricing, or trust issue. |
| Neither condition met | `null` | No clear failure mode. |

**Rules:**
- Thresholds are relative to site-wide averages, not absolute. This adapts to any site type.
- If a site has uniform engagement across all pages (no page deviates beyond the thresholds), no failure modes are assigned. This is correct.
- `deep_engagement` requires conversion data from Step 5. Compute `failure_mode` for that condition after Step 5 completes.
- Store `failure_mode` for each page in the top 50. Results go into the frontmatter `top_pages` entries and the body Page Performance section.

### Step 4b: Page Grouping by URL Pattern

Group pages by URL prefix to enable group-relative benchmarks (used in Step 5 for underperforming detection and Step 9b for opportunity sizing).

**Data-driven prefix detection:**

1. Take the top 50 pages from Step 4.
2. Strip known non-semantic prefixes before segmenting:
   - Locale codes: /en/, /fr/, /de/, /es/, /pt/, /ja/, /zh/, /ko/, /it/, /nl/, /ru/
     (2-letter ISO 639-1 codes as first segment)
   - Date patterns: /YYYY/, /YYYY/MM/, /YYYY/MM/DD/
   Example: /en/blog/post-1 -> /blog/post-1, /2025/02/my-post -> /my-post
3. Extract first path segment from the cleaned URL (e.g., /blog/post-1 -> /blog).
4. Count occurrences of each first segment.
5. Segments appearing 3+ times become groups.
6. Pages not matching any group stay as individual entries.
7. Pages with <50 sessions that don't match a group -> "Long Tail" bucket.

Sites with mostly top-level paths (`/feature-a`, `/about`, `/pricing`) won't produce meaningful groups via prefix detection. These fall through to the fallback heuristics, which is correct.

**Fallback heuristics** (when prefix detection produces <3 groups):

```
/blog/* -> Blog
/product/* or /products/* -> Product Pages
/case-stud* -> Case Studies
/resource* -> Resources
/docs/* or /documentation/* -> Documentation
/pricing* -> Pricing
```

When L0 exists (Step 11), its explicit product lines or service categories with distinct URL patterns override data-driven groups.

**Output:**

Compute session-weighted averages for each group.

```markdown
### Page Group Performance

| Group | URL Pattern | Pages | Sessions | Weighted Bounce | Weighted Engagement | Conversions | Group CVR |
|-------|------------|-------|----------|----------------|--------------------|----|-----------|
| Blog | /blog/* | 18 | 12,400 | 61.2% | 38.8% | 24 | 0.19% |
| Product | /solutions/* | 6 | 8,900 | 41.3% | 58.7% | 178 | 2.0% |
```

Weighted bounce/engagement = session-weighted averages across pages in the group.

When comparison data is present, compute group metrics for both periods. This enables group-level trend detection.

### Step 5: Conversion Funnel Report

For each of the top 3 conversion events (by volume), pull per-page conversion data using `run_report`:
- Dimensions: `pagePath`
- Metrics: `sessions`, `eventCount` (filtered to the specific conversion event)
- Date range: as specified
- Limit: 20 rows per event
- Order by: eventCount descending

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Compute per-page conversion rate: `eventCount / sessions * 100`

Compute site-wide conversion rate for the primary event: `total primary event count / total sessions * 100`

Compute **Underperforming Pages** using group-relative benchmarks:
1. For each page group (from Step 4b), compute the group average CVR.
2. A page underperforms when:
   - CVR < 50% of its GROUP average (not site-wide), AND
   - >200 sessions
3. Exception: if an ENTIRE group's CVR < 25% of the top-performing group,
   flag the GROUP as a strategic opportunity (not individual pages).
   Example: "Blog group converts at 0.19% vs Product group at 2.0%.
   Blog-to-conversion path is a structural opportunity, not individual
   post underperformance."

Output:

```markdown
### Underperforming Pages (conversion rate <50% of group average)

| Page | Group | Sessions | Page CVR | Group Avg CVR | Gap |
|------|-------|----------|----------|---------------|-----|
```

### Step 6: Channel/Source Report

Pull channel and source breakdown using `run_report`:
- Dimensions: `sessionDefaultChannelGroup`
- Metrics: `sessions`, `bounceRate`, `engagementRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Then pull top sources within key channels (channels with >5% of total sessions):
- Dimensions: `sessionSource`, `sessionMedium`, `sessionDefaultChannelGroup`
- Metrics: `sessions`, `bounceRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified
- Limit: 15 rows
- Order by: sessions descending

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

### Step 7: Device & User Segment Report

Pull device breakdown using `run_report`:
- Dimensions: `deviceCategory`
- Metrics: `sessions`, `totalUsers`, `bounceRate`, `engagementRate`, `averageSessionDuration`, `engagedSessions`, `screenPageViewsPerSession`, `eventCount` (filtered to primary conversion event)
- Date range: as specified

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Compute mobile vs desktop gap analysis:
- Bounce rate gap (pp difference)
- Conversion rate gap (percentage difference)
- Duration gap
- Significance: "High" = >10pp bounce gap or >50% conversion rate gap. "Medium" = 5-10pp bounce or 25-50% conversion gap. "Low" = <5pp bounce and <25% conversion gap.

### Step 7b: New vs Returning Report

**Primary call:**
```
run_report:
  dimensions: [newVsReturning]
  metrics: [sessions, totalUsers, bounceRate, engagementRate, averageSessionDuration, conversions]
  date_range: as specified
```

Note: `conversions` counts GA4 key events. Only 2-3 rows expected (new, returning, possibly null).

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

**Conversion enrichment call** (conditional, same pattern as Step 8b):
Runs ONLY when Step 3 classified heuristic conversion events that are NOT already GA4 key events.
```
run_report:
  dimensions: [newVsReturning, eventName]
  metrics: [eventCount]
  dimensionFilter: eventName IN [heuristic-classified conversion event names from Step 3b]
  date_range: as specified
```

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Post-processing: aggregate into unified conversion counts per segment.

**Signal classification** (apply internally, include signal in output):

| Returning:New Ratio | Signal | CRO Implication |
|---------------------|--------|-----------------|
| >5x | `familiarity_dependent` | First-visit likely failing. Nurture opportunity. |
| 2-5x | `normal_b2b` | Multiple touches expected. Standard B2B pattern. |
| 1-2x | `strong_first_visit` | First-visit conversion working. Optimize for it. |
| <1x | `acquisition_heavy` | New-visitor dominated. Check returning visitor bounce rate to distinguish strong acquisition from weak retention. |

**Output:** New subsection under Device & User Segment Performance, after the mobile vs desktop gap analysis.

### Step 8: Landing Page Report

Pull entry pages using `run_report`:
- Dimensions: `landingPage`
- Metrics: `sessions`, `bounceRate`, `engagementRate`, `engagedSessions`, `screenPageViewsPerSession`, `eventCount` (filtered to primary conversion event)
- Date range: as specified
- Limit: 30 rows
- Order by: sessions descending

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Compute:
- % of entries for each landing page
- **High-Bounce Entry Points:** Landing pages with >55% bounce rate, within top 20 entry pages

### Step 8b: Landing Page x Source Cross-Tab

**Primary call** (always runs):
```
run_report:
  dimensions: [landingPage, sessionDefaultChannelGroup]
  metrics: [sessions, bounceRate, engagementRate, conversions]
  date_range: as specified
  limit: 100 rows
  order_by: sessions descending
```

Note: `conversions` counts GA4 key events identified in Step 3a. No filtering needed.

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

**Conversion enrichment call** (conditional):
Runs ONLY when Step 3 classified heuristic conversion events that are NOT already GA4 key events. If all conversion events are key events, skip this call.
```
run_report:
  dimensions: [landingPage, sessionDefaultChannelGroup, eventName]
  metrics: [eventCount]
  dimensionFilter: eventName IN [heuristic-classified conversion event names from Step 3b]
  date_range: as specified
  limit: 200 rows
  order_by: eventCount descending
```

When comparison is enabled (default): include a second date range for the comparison period. The GA4 Data API returns metrics for both periods in the same response. When --no-compare is set: use only the primary date range.

Post-processing: aggregate `eventCount` per page x channel across matching event names. Merge with key event `conversions` from the primary call into a unified conversion count.

**Mismatch detection thresholds:**
- Bounce mismatch: >15pp gap between channels on the same page
- Conversion mismatch: one channel's conversion rate <50% of another on the same page

**Output:** New subsection under Landing Page Performance:

```markdown
### Source x Landing Page Mismatches

| Landing Page | Better Channel | Worse Channel | Metric | Better Value | Worse Value | Gap |
|-------------|---------------|--------------|--------|-------------|------------|-----|
| /pricing | Organic (39%) | Paid Search (54%) | Bounce Rate | 39% | 54% | 15pp |
```

If no mismatches exceed thresholds, output: "No source x landing page mismatches exceeded thresholds (>15pp bounce gap or >50% conversion rate gap)."

### Step 9: Data Quality Assessment

Assess data quality across all reports:

**Traffic adequacy:**
- `high`: >10,000 sessions in the date range
- `adequate`: 1,000-10,000 sessions
- `low`: <1,000 sessions

**Sampling status:** Check if any report responses indicate sampling was applied.

**Event coverage:** Check for gaps:
- Pages with forms but no form-related conversion events
- High-traffic pages with no conversion events at all
- Missing enhanced measurement events (scroll, outbound_click, file_download)

**Device distribution:** Flag if mobile traffic is >60% or <15% (unusual for B2B).

**Channel concentration:** Flag if any single channel represents >70% of traffic.

Set confidence score:
- 5: No sampling, complete tracking, high traffic
- 4: Minor gaps (missing some enhanced measurement events, or adequate traffic)
- 3: Sampling applied OR significant tracking gaps
- 2: Major coverage issues (very few events, low traffic, most pages un-tracked)
- 1: Unreliable data (sampling + low traffic + major gaps)

### Step 9b: Opportunity Sizing

Compute quantified opportunity estimates for underperforming pages and groups identified in Steps 4b, 5, and 8b.

**Three formula types:**

| Type | Formula | When |
|------|---------|------|
| CVR Improvement | `impact = (target_rate - current_rate) * monthly_sessions * conservatism` | Page converts below group average |
| Bounce Reduction | `impact = bouncing_sessions * recovery_rate * site_cvr * conservatism` | High-bounce page |
| Traffic Reallocation | `impact = sessions * capture_rate * conservatism` | Informational pages with no conversion path |

**Target metric sources:**

| Type | target_metric source |
|------|---------------------|
| CVR Improvement | Group average CVR from Step 4b page groups |
| Bounce Reduction | Best-channel bounce rate for that page from Step 8b cross-tab; falls back to group average bounce from Step 4b if no cross-tab mismatch exists |
| Traffic Reallocation | N/A (uses capture_rate constants) |

**Conservatism factors:**
- Conservatism factor: 0.4 across all formulas
- Recovery rates: 0.15 (messaging changes), 0.10 (UX changes)
- Capture rates: 0.01 (informational), 0.03 (product pages)

These are working estimates, not calibrated against property-specific or FunnelEnvy historical data. Treat as provisional defaults.

**Output impact buckets, NOT point estimates.** The raw formula output is computed internally for bucketing but NOT exposed in frontmatter or body. The bucket is what downstream consumers use.

- `small`: <5 estimated additional conversions/month
- `medium`: 5-20 estimated additional conversions/month
- `large`: >20 estimated additional conversions/month

**Output:**

```markdown
## Opportunity Sizing

| Page | Issue | Formula | Impact Bucket | Action Category |
|------|-------|---------|--------------|-----------------|
| /pricing | Paid search bounce 15pp above organic | bounce_reduction | medium | messaging |
| /blog | Blog group CVR 90% below Product group | traffic_reallocation | small | structural |
```

Each row includes a sizing_note: "Estimated using standard CRO conservatism factors (0.4x), not property-specific data"

Action categories: `messaging`, `ux`, `form`, `structural`.

### Step 10: Write Performance Profile

Construct `.claude/context/performance-profile.md` following the schema in `schemas/performance-profile.md`.

**YAML frontmatter:** Populate all fields from the data collected in Steps 1-9.

**Body sections (all 8 REQUIRED):**
1. Property Overview (from Steps 1-2, 9)
2. Page Performance (from Step 4, 4b) (includes trend tags when comparison enabled)
3. Conversion Events (from Steps 3, 5) (includes trend tags when comparison enabled)
4. Channel Performance (from Step 6) (includes trend tags when comparison enabled)
5. Device & User Segment Performance (from Steps 7, 7b) (includes trend tags when comparison enabled)
6. Landing Page Performance (from Step 8, 8b) (includes trend tags when comparison enabled)
7. Opportunity Sizing (from Step 9b)
8. Key Metrics Summary (analyst interpretation of Steps 4-9b) (includes trend tags when comparison enabled)

**Key Metrics Summary guidance:**
- **Strengths:** Identify 2-4 things working well. Cite specific numbers. ("Organic search converts at 2.1%, above site average of 1.97%")
- **Weaknesses:** Identify 2-4 underperforming areas. Cite thresholds. ("Mobile bounce rate is 52.1% vs 38.0% desktop, a 14.1pp gap")
- **Experiment Opportunities:** Identify 3-5 specific, testable opportunities from the data. Each must reference a metric gap. ("Paid search traffic bounces at 48.7% vs 39.2% organic on the same pages. Ad-to-page messaging mismatch likely.")
- **Data Gaps:** List what can't be measured. ("No scroll depth data. No form field-level tracking. Revenue attribution not configured.")

**Trend tags** (when comparison data is available, i.e. --no-compare not set):

Apply trend tags to findings in Key Metrics Summary and relevant body sections:
- [WORSENING]: metric degraded >10% or >5pp (for rates)
- [IMPROVING]: metric improved >10% or >5pp
- [STABLE]: change within +/-10% or +/-5pp

Example: "Mobile bounce rate is 52.1% vs 38.0% desktop, a 14.1pp gap [WORSENING: +4.5pp vs prior period]"

When --no-compare is set: omit all trend tags. Do not reference comparison data.

Write the file to `.claude/context/performance-profile.md`.

**Completion summary:**

```
Performance profile written to .claude/context/performance-profile.md

  Property: [Name] ([ID])
  Date range: [start] to [end] ([N] days)
  Sessions: [N] | Users: [N] | Mobile: [N]%
  Conversion events: [N] classified ([primary] as primary, [rate]% site-wide)
  Traffic adequacy: [high/adequate/low]
  Confidence: [N]
  Comparison: [enabled, vs [start] to [end] | disabled (--no-compare)]

  Key findings:
  - [top strength]
  - [top weakness]
  - [top experiment opportunity]

Run /hypothesis-generator to produce data-calibrated experiment hypotheses.
```

### Step 11: L0 Enrichment (Optional Post-Processing)

This step is NOT part of the core pipeline. Steps 1-10 run independently.
Step 11 adds value when company-identity.md exists, without breaking anything.

1. Glob .claude/context/company-identity.md
2. If missing or confidence < 2: skip entirely.
   Set frontmatter l0_available: false, l0_confidence: null.
   Write these fields to the already-saved performance-profile.md and stop.
3. If present: read frontmatter + relevant body sections.
4. Enrich the already-written performance-profile.md:
   a. Product-line page groupings: override data-driven groups from Step 4b
      where L0 provides explicit product/service categories with URL patterns.
   b. Funnel stage mapping: map conversion events to L0's stated funnel stages.
   c. Tracking gap flags: compare L0's stated services/funnels against detected
      events. Flag missing tracking.
   d. Contextualized Key Metrics Summary: add company-specific observations.
      Example: "L0 states enterprise as primary segment but /enterprise
      converts at 0.5%"
5. Update frontmatter: l0_available: true, l0_confidence: [value from L0]
6. Re-write performance-profile.md with enrichments.

When L0 confidence is 1-2, use it but tag enrichments with
[BASED ON LOW-CONFIDENCE L0].

Step 11 adds a new section to the performance profile body: "L0 Enrichment Notes". This section documents what L0 added (product-line overrides, funnel mappings, tracking gaps) or notes that L0 wasn't available.

---

## Inline Schema Reference

The authoritative schema is defined in `schemas/performance-profile.md`. Refer to it for:
- Complete YAML frontmatter field definitions
- Body section templates and content requirements
- Completeness checklist
- Confidence scoring criteria

---

## Quality Checks

Before writing the final file, verify:

1. [ ] All 7 body sections are present (populated or gap-marked)
2. [ ] YAML frontmatter has all required fields
3. [ ] Sampling status is reported accurately
4. [ ] Conversion events are classified and confirmed by user
5. [ ] High-Bounce callout table uses >50% bounce / >100 sessions thresholds. Underperforming table uses <50% of group average CVR / >200 sessions.
6. [ ] Landing Page section uses `landingPage` dimension (not `pagePath`)
7. [ ] Key Metrics Summary cites specific numbers from other sections
8. [ ] Confidence score reflects actual data quality assessment
9. [ ] No fabricated or estimated data. Every number comes from a GA4 report response.
10. [ ] Date range is explicit in both frontmatter and Property Overview
11. [ ] Page grouping covers >90% of sessions (no more than 10% in "Long Tail")
12. [ ] Opportunity sizing uses impact buckets (small/medium/large), not point estimates
13. [ ] Every opportunity has a sizing_note disclaiming conservatism factors
14. [ ] Every event is classified into exactly one category (Conversion: KEY EVENT | heuristic | L0-mapped, OR Engagement, OR Noise/Ignored). No unclassified events.
15. [ ] If --no-compare not set: trends section present with all four trend metrics
16. [ ] If L0 consumed: l0_available is true and enrichment notes section exists
17. [ ] Underperforming pages use group-relative benchmarks (not site-wide)
18. [ ] New vs Returning section present with signal classification
19. [ ] Source x Landing Page Mismatches uses >15pp bounce / <50% CVR thresholds

---

## Analytics MCP Tool Reference

This skill uses the following analytics-mcp tools:

| Tool | Used In | Purpose |
|------|---------|---------|
| `get_account_summaries` | Step 1 | Auth check + property discovery |
| `get_property_details` | Step 2 | Property validation |
| `run_report` | Steps 3-8 | All data queries |

**`run_report` parameters:**
- `property_id`: GA4 property ID (numeric string)
- `date_ranges`: Array of `{ startDate, endDate }`. Use "NdaysAgo" format or "YYYY-MM-DD".
- `dimensions`: Array of `{ name }` objects
- `metrics`: Array of `{ name }` objects
- `dimension_filter`: Optional filter expression
- `metric_filter`: Optional filter expression
- `order_bys`: Array of ordering specs
- `limit`: Row limit (default 10000)

**Common GA4 dimensions:**
- `pagePath`, `landingPage`, `deviceCategory`
- `sessionDefaultChannelGroup`, `sessionSource`, `sessionMedium`
- `eventName`

**Common GA4 metrics:**
- `sessions`, `totalUsers`, `bounceRate`, `engagementRate`
- `averageSessionDuration`, `eventCount`, `conversions`

**Filtering for specific events:** Use `dimension_filter` on `eventName` dimension to isolate specific conversion events when pulling per-page conversion data.

