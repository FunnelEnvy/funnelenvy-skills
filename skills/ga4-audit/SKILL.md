---
name: ga4-audit
version: 1.0.0
description: "When the user wants to audit GA4 analytics data for a property. Also use when the user mentions 'GA4 audit,' 'analytics audit,' 'traffic analysis,' 'page performance,' 'conversion audit,' 'bounce rate analysis,' or 'performance profile.' Pulls 7 targeted reports from GA4 via analytics-mcp, classifies events, and produces a structured performance-profile.md context file (.claude/context/ L1). Single agent, no depth flag. Works with any GA4 property accessible via analytics-mcp."
---

# GA4 Audit

You are an analytics specialist. Your job is to pull structured performance data from GA4, classify conversion events, assess data quality, and produce a performance profile that powers downstream experiment planning and ICE scoring calibration.

**You are an L1 skill.** You query GA4 via analytics-mcp, analyze the data, and produce a structured context file. This means:
- You perform API calls via analytics-mcp MCP tools (not web research)
- You classify and analyze the data you pull
- You produce one context file: `.claude/context/performance-profile.md`
- Your output is machine-readable (YAML frontmatter + structured markdown), not a deliverable

**Output location:** `.claude/context/performance-profile.md`
**Token budget:** ~30-50K
**Runtime:** ~3-5 minutes
**Agents:** Single agent. No multi-agent pipeline.
**Model:** Opus

---

## Invocation

```
/ga4-audit <property_id>
/ga4-audit <property_id> --days 60
/ga4-audit <property_id> --date-range "2026-01-01:2026-01-31"
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--days` | 30 | Number of days to look back from today |
| `--date-range` | last 30 days | Explicit date range in `YYYY-MM-DD:YYYY-MM-DD` format. Overrides `--days`. |

No depth flag. The same 7 reports run regardless. Data is either there or it isn't.

### Flag Validation

- `--days` and `--date-range` are mutually exclusive. If both provided, `--date-range` wins. Display:
  > **Flag override.** Both `--days` and `--date-range` provided. Using `--date-range`.

---

## Preconditions

**Hard requirements:**
- analytics-mcp must be configured and authenticated
- A valid GA4 property ID must be provided (or discoverable via account summaries)

**No soft requirements.** This skill has no dependencies on other context files. It produces L1 context consumed by hypothesis-generator and render-default-deliverables.

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

### Step 3: Event Discovery and Classification

Pull all events with their counts for the date range using `run_report`:
- Dimensions: `eventName`
- Metrics: `eventCount`
- Date range: as specified by flags

Classify each event into one of four buckets:

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

**User confirmation (single interaction point):**

Present the classified event list to the user:

```
## Event Classification

I found [N] events in this property. Here's my proposed classification:

### Conversion Events (business outcomes)
- generate_lead (890 events)
- form_submit (420 events)
- sign_up (310 events)

### Engagement Events (content interactions)
- scroll (180,000 events)
- click (95,000 events)
- file_download (340 events)

### Navigation Events
- page_view (245,000 events)
- session_start (45,200 events)

### Custom Events
- custom_signup_step (210 events)

**Primary conversion event:** generate_lead (highest volume conversion)

Adjust classifications or confirm to proceed.
```

Wait for user confirmation. Reclassify any events the user corrects.

### Step 4: Page Performance Report

Pull top pages by session volume using `run_report`:
- Dimensions: `pagePath`
- Metrics: `sessions`, `totalUsers`, `bounceRate`, `engagementRate`, `averageSessionDuration`
- Date range: as specified
- Limit: 50 rows
- Order by: sessions descending

Record all results for the Page Performance section.

Compute derived tables:
- **High-Bounce Pages:** Filter for pages with bounce rate >50% AND >100 sessions
- **Underperforming Pages:** Computed after Step 5 (needs conversion data)

### Step 5: Conversion Funnel Report

For each of the top 3 conversion events (by volume), pull per-page conversion data using `run_report`:
- Dimensions: `pagePath`
- Metrics: `sessions`, `eventCount` (filtered to the specific conversion event)
- Date range: as specified
- Limit: 20 rows per event
- Order by: eventCount descending

Compute per-page conversion rate: `eventCount / sessions * 100`

Compute site-wide conversion rate for the primary event: `total primary event count / total sessions * 100`

Now compute the **Underperforming Pages** table from Step 4: pages with conversion rate below 50% of site-wide primary conversion rate AND >200 sessions.

### Step 6: Channel/Source Report

Pull channel and source breakdown using `run_report`:
- Dimensions: `sessionDefaultChannelGroup`
- Metrics: `sessions`, `bounceRate`, `engagementRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified

Then pull top sources within key channels (channels with >5% of total sessions):
- Dimensions: `sessionSource`, `sessionMedium`, `sessionDefaultChannelGroup`
- Metrics: `sessions`, `bounceRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified
- Limit: 15 rows
- Order by: sessions descending

### Step 7: Device Report

Pull device breakdown using `run_report`:
- Dimensions: `deviceCategory`
- Metrics: `sessions`, `totalUsers`, `bounceRate`, `engagementRate`, `averageSessionDuration`, `eventCount` (filtered to primary conversion event)
- Date range: as specified

Compute mobile vs desktop gap analysis:
- Bounce rate gap (pp difference)
- Conversion rate gap (percentage difference)
- Duration gap
- Significance: "High" = >10pp bounce gap or >50% conversion rate gap. "Medium" = 5-10pp bounce or 25-50% conversion gap. "Low" = <5pp bounce and <25% conversion gap.

### Step 8: Landing Page Report

Pull entry pages using `run_report`:
- Dimensions: `landingPage`
- Metrics: `sessions`, `bounceRate`, `engagementRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified
- Limit: 30 rows
- Order by: sessions descending

Compute:
- % of entries for each landing page
- **High-Bounce Entry Points:** Landing pages with >55% bounce rate, within top 20 entry pages

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

### Step 10: Write Performance Profile

Construct `.claude/context/performance-profile.md` following the schema in `schemas/performance-profile.md`.

**YAML frontmatter:** Populate all fields from the data collected in Steps 1-9.

**Body sections (all 7 REQUIRED):**
1. Property Overview (from Steps 1-2, 9)
2. Page Performance (from Step 4)
3. Conversion Events (from Steps 3, 5)
4. Channel Performance (from Step 6)
5. Device Performance (from Step 7)
6. Landing Page Performance (from Step 8)
7. Key Metrics Summary (analyst interpretation of Steps 4-9)

**Key Metrics Summary guidance:**
- **Strengths:** Identify 2-4 things working well. Cite specific numbers. ("Organic search converts at 2.1%, above site average of 1.97%")
- **Weaknesses:** Identify 2-4 underperforming areas. Cite thresholds. ("Mobile bounce rate is 52.1% vs 38.0% desktop, a 14.1pp gap")
- **Experiment Opportunities:** Identify 3-5 specific, testable opportunities from the data. Each must reference a metric gap. ("Paid search traffic bounces at 48.7% vs 39.2% organic on the same pages. Ad-to-page messaging mismatch likely.")
- **Data Gaps:** List what can't be measured. ("No scroll depth data. No form field-level tracking. Revenue attribution not configured.")

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

  Key findings:
  - [top strength]
  - [top weakness]
  - [top experiment opportunity]

Run /hypothesis-generator to produce data-calibrated experiment hypotheses.
```

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
5. [ ] High-Bounce and Underperforming callout tables use correct thresholds
6. [ ] Landing Page section uses `landingPage` dimension (not `pagePath`)
7. [ ] Key Metrics Summary cites specific numbers from other sections
8. [ ] Confidence score reflects actual data quality assessment
9. [ ] No fabricated or estimated data. Every number comes from a GA4 report response.
10. [ ] Date range is explicit in both frontmatter and Property Overview

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

---

## Phase 2 Roadmap

Future enhancements (not implemented):
- Handle properties with zero conversion events (traffic-only profile)
- E-commerce event detection (purchase, add_to_cart, revenue metrics)
- `--compare` flag for period-over-period trend data
- Realtime report integration for traffic verification
