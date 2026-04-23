---
name: ga4-audit
version: 2.3.0
description: "When the user wants to audit GA4 analytics data for a property. Also use when the user mentions 'GA4 audit,' 'analytics audit,' 'traffic analysis,' 'page performance,' 'conversion audit,' 'bounce rate analysis,' or 'performance profile.' Pulls 11-15 targeted reports from GA4 via direct API or analytics-mcp fallback (including element-level interaction discovery and AI-referrer traffic segmentation), classifies events, and produces a structured performance-profile.md context file (.claude/context/ L1). Single agent, no depth flag. Works with any GA4 property."
---

# GA4 Audit

You are an analytics specialist. Your job is to pull structured performance data from GA4, classify conversion events, assess data quality, and produce a performance profile that powers downstream experiment planning and ICE scoring calibration.

**You are an L1 skill.** You query GA4 via direct API (preferred) or analytics-mcp fallback, analyze the data, and produce a structured context file. This means:
- You perform API calls via `ga4_client.py` (direct GA4 API) or analytics-mcp MCP tools as fallback (not web research)
- You classify and analyze the data you pull
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
/ga4-audit
/ga4-audit <property_id>
/ga4-audit <property_id> --days 30
/ga4-audit <property_id> --days 90 --no-compare
/ga4-audit <property_id> --date-range "2025-11-01:2026-01-31"
```

When no `<property_id>` is provided, the skill checks `company-identity.md` for a saved `ga4_property` value (see Step 2).

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--days` | 90 | Number of days to look back from today |
| `--date-range` | last 90 days | Explicit date range in `YYYY-MM-DD:YYYY-MM-DD` format. Overrides `--days`. |
| `--no-compare` | false | Skip period-over-period comparison |

No depth flag. The same reports run regardless of the lookback window. Data is either there or it isn't.

AI-referrer detection (Step 6b) is always-on. If runtime overhead exceeds ~15 seconds on a median run or per-client configurability becomes necessary, introduce `--skip-ai`. Not before.

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

### Comparison Rule (applies to ALL run_report calls)

When comparison is enabled (default), include a second date range for the comparison period. GA4 returns metrics for both periods in one response. When --no-compare is set, use only the primary date range. Do not repeat this logic per step.

---

## Preconditions

**Hard requirements:**
- GA4 API access via ONE of these (checked in order during Step 1):
  1. **Direct API (preferred):** `ga4_client.py` + credentials configured (see `.env.example`)
  2. **MCP fallback:** analytics-mcp configured and authenticated
- A valid GA4 property ID must be provided (or discoverable via account summaries)

**Soft requirements:**
- `company-identity.md` in `.claude/context/`: If present with confidence >= 2,
  Step 11 enriches the output with product-line groupings, funnel stage mapping,
  and tracking gap flags. If missing, Steps 1-10 produce complete output without it.

**Error states:**
- Neither API nor MCP available: Exit with "No GA4 access available. Configure credentials (see .env.example) or set up analytics-mcp."
- Property ID not found: List available properties and ask user to select.
- Property has zero data in date range: Exit with "No data found for property [ID] in the specified date range. Check the property ID and date range."

---

## Prior Work Detection

**None.** Unlike positioning context files, analytics data is a time-bounded snapshot. Each run overwrites `.claude/context/performance-profile.md` entirely. No incremental extension, no confidence-only-rises rule.

---

## Execution Pipeline

### Step 1: Authentication Check and Data Source Selection

Determine the data source for this session. Try direct API first, fall back to MCP.

**Step 1a: Try direct API**

Run `ga4_client.py` from the skill directory:
```
python ga4_client.py account-summaries 2>/dev/null || python3 ga4_client.py account-summaries
```

- **Exit code 0:** Set `data_source = "api"`. Display: `"Using GA4 Data API (direct)"`. Parse the JSON output for account summaries.
- **Exit code 2 (no credentials):** Proceed to Step 1b (MCP fallback).
- **Exit code 3 (auth failed):** Display the stderr message. Exit immediately. Do not fall back to MCP (credentials exist but are broken -- user needs to fix them).
- **Exit code 1 or other:** Proceed to Step 1b (MCP fallback).

**Step 1b: Try MCP fallback**

Only reached when Step 1a exits with code 2 (no credentials) or code 1 (general error).

Use `get_account_summaries` via analytics-mcp.

- If successful: Set `data_source = "mcp"`. Display: `"Using analytics-mcp (fallback). For better performance, configure direct API credentials (see .env.example in ga4-audit skill)."`.
- If MCP fails with auth error:
  ```
  No GA4 access available.

  Option 1 (recommended): Configure direct API credentials.
  See .env.example in the ga4-audit skill directory.

  Option 2: Set up analytics-mcp and restart your session.
  ```
  Exit immediately. Do not retry.

**Step 1c: Confirm**

Display available accounts and properties for confirmation. The remaining steps use `data_source` to route all queries.

### Step 2: Property Validation

Query property details with the provided property ID (see Data Source Routing table).

**If no property ID was provided:**
1. Check `.claude/context/company-identity.md` for `ga4_property` in the YAML frontmatter.
   - If found: use it as the property ID. Display: "Using GA4 property from company context: [property_id]". Proceed to `get_property_details` validation.
   - If not found: fall through to step 2.
2. List all properties from the account summaries (Step 1)
3. Ask the user to select one
4. Continue with the selected property

**If property ID is valid:**
Display property name and proceed.

**If property ID is invalid:**
Display available properties and ask the user to select.

### Step 3: Event Discovery and Three-Tier Classification

#### Step 3a: Key Event Query

Pull all events with their counts for the date range using a report query:
- Dimensions: `eventName`
- Metrics: `eventCount`, `conversions`
- Date range: as specified by flags


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

Pull top pages by session volume using a report query:
- Dimensions: `pagePath`
- Metrics: `sessions`, `totalUsers`, `bounceRate`, `engagementRate`, `averageSessionDuration`, `engagedSessions`, `screenPageViewsPerSession`
- Date range: as specified
- Limit: 50 rows
- Order by: sessions descending


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

Columns: Group | URL Pattern | Pages | Sessions | Weighted Bounce | Weighted Engagement | Conversions | Group CVR

Weighted bounce/engagement = session-weighted averages across pages in the group.

When comparison data is present, compute group metrics for both periods. This enables group-level trend detection.

### Step 5: Conversion Funnel Report

For each of the top 3 conversion events (by volume), pull per-page conversion data using a report query:
- Dimensions: `pagePath`
- Metrics: `sessions`, `eventCount` (filtered to the specific conversion event)
- Date range: as specified
- Limit: 20 rows per event
- Order by: eventCount descending


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

### Step 5b: Element-Level Interaction Discovery

This step discovers custom event parameters and queries element-level interactions on top pages. It adds specificity to downstream hypotheses by capturing which elements visitors interact with (or don't).

**Skip conditions:** If no custom dimensions/parameters exist AND enhanced measurement dimensions yield no data, skip entirely. Output: "No element-level interaction data available."

#### Step 5b-1: Parameter Discovery

Query custom dimensions and metrics for the property (see Data Source Routing table). Collect:
- Custom event-scoped dimensions (e.g., `customEvent:form_id`, `customEvent:cta_label`, `customEvent:button_text`)
- Note which are event-scoped vs user-scoped (only event-scoped are useful here)

Also check for standard enhanced measurement dimensions that carry element context:
- `linkText` (from enhanced measurement click events)
- `linkUrl` (from enhanced measurement click events)
- `fileExtension`, `fileName` (from file_download events)
- `videoTitle` (from video events)

If no custom event-scoped dimensions exist AND no enhanced measurement element dimensions are available, skip this step entirely.

#### Step 5b-2: Element Interaction Queries (max 5 additional `run_report` calls)

For the top 3-5 non-navigation events by volume (from Step 3), query with page path + discovered parameter dimensions:

```
run_report:
  dimensions: [pagePath, eventName, <discovered_parameter>]
  metrics: [eventCount]
  dimensionFilter: eventName IN [top non-navigation events]
  date_range: as specified
  limit: 100 rows
  order_by: eventCount descending
```

Run one query per discovered parameter dimension (up to 5 total). If multiple parameters exist, prioritize:
1. Custom parameters with "cta," "button," "label," or "form" in the name
2. `linkText` (most informative standard dimension)
3. `linkUrl`
4. Other custom event-scoped dimensions
5. `videoTitle`, `fileExtension`

#### Step 5b-3: Compute Interaction Metrics

For each page x event x parameter combination:
- **Interaction rate:** `eventCount / page_sessions * 100` (using page sessions from Step 4)
- **Relative share:** What percentage of that event type on that page does this element represent

Flag notable findings:
- Primary CTA click rate <3% on pages with >500 sessions (low CTA engagement)
- One element gets >5x interactions of the next element for the same event type (CTA hierarchy dominance)
- Later items in sequential elements (carousel slides, tab panels) get <20% of first item interactions (content below first view invisible)

#### Step 5b-4: Record Results

Store element interaction data for the frontmatter and body section. If no meaningful interactions were discovered, set `element_interactions_available: false` in frontmatter and skip the body section.

### Step 6: Channel/Source Report

Pull channel and source breakdown using a report query:
- Dimensions: `sessionDefaultChannelGroup`
- Metrics: `sessions`, `bounceRate`, `engagementRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified


Then pull top sources within key channels (channels with >5% of total sessions):
- Dimensions: `sessionSource`, `sessionMedium`, `sessionDefaultChannelGroup`
- Metrics: `sessions`, `bounceRate`, `eventCount` (filtered to primary conversion event)
- Date range: as specified
- Limit: 15 rows
- Order by: sessions descending


### Step 6b: AI-Traffic Source Detection

Segment referral sessions from LLM/AI chat tools. These sit inside "Referral" in default channel groups, so they're invisible without explicit segmentation.

GA4 does not normalize LLM source values, so this step pulls raw segments and collapses them at the reporting layer.

#### Queries

**Query 1 - By source (full audit window):**
- Dimensions: `sessionSource`
- Metrics: `sessions`, `totalUsers`, `newUsers`, `engagedSessions`, `averageSessionDuration`, `conversions`
- dimensionFilter: `sessionSource` PARTIAL_REGEXP match against AI_REGEX below
- Limit: 50
- Order by: sessions descending

**Query 2 - Monthly trajectory (full audit window):**
- Dimensions: `yearMonth`
- Metrics: `sessions`, `totalUsers`, `newUsers`
- dimensionFilter: same AI filter
- Order by: yearMonth ascending

**Query 3 - Top AI-driven landing pages (full audit window):**
- Dimensions: `landingPage`, `sessionSource`
- Metrics: `sessions`, `totalUsers`, `conversions`
- dimensionFilter: same AI filter
- Limit: 25
- Order by: sessions descending

Recent 90-day source-by-month mix shifts are derived in-memory from Query 2 combined with a source-level slice of Query 1. No separate API call.

#### AI_REGEX

Case-insensitive, PARTIAL_REGEXP:

```
chatgpt|openai|claude\.ai|anthropic|gemini\.google|bard\.google|perplexity|copilot\.microsoft|copilot\.cloud|phind|poe\.com|deepseek|chat\.mistral|mistral\.ai|character\.ai|groq|you\.com|meta\.ai|huggingface
```

**CRITICAL - regex mode:** GA4's `FULL_REGEXP` requires whole-string match (not substring). `chatgpt` as FULL_REGEXP does NOT match `chatgpt.com`. You MUST use `PARTIAL_REGEXP`. Verify by eyeballing that `chatgpt.com` appears in results when a site has meaningful referral volume. If zero rows return on a site with known AI traffic, check the filter mode first.

Mistral is matched via `chat\.mistral` or `mistral\.ai` specifically rather than bare `mistral` to avoid false positives on unrelated source strings containing those seven characters.

#### Source Normalization

Present both the raw source rows AND a collapsed view. Known variant pairs to merge:

| Canonical | Variants seen |
|---|---|
| chatgpt | chatgpt.com, openai, chatgpt.com), prod-usch-auditchatgpt.us.kworld.kpmg.com |
| perplexity | perplexity.ai, perplexity |
| copilot | copilot.microsoft.com, copilot.cloud.microsoft |
| gemini | gemini.google.com, bard.google.com |
| claude | claude.ai |
| mistral | chat.mistral.ai, mistral.ai |

The collapsed view feeds the summary table. The raw view appears in an appendix so readers can see what GA4 actually returned. New variants encountered in the wild should be added to the canonical map as a maintenance task, not papered over with inference.

#### Computed Fields

- `ai_sessions_count` - sum across all AI sources, collapsed
- `ai_sessions_pct` - `ai_sessions_count / total_sessions_audit_window * 100`, 2 decimals
- `ai_conversions_count` - sum of conversions across AI sources
- `ai_conversion_rate` - `ai_conversions_count / ai_sessions_count * 100`, 2 decimals. Set to `null` when `ai_sessions_count == 0`.
- `top_ai_sources` - list of `{source, sessions, pct_of_ai}` for collapsed top 5
- `ai_traffic_trend` - compare last 3 months vs prior 3 months (or prior 6mo average for 12mo audits):
  - `growing` if delta > +25%
  - `declining` if delta < -25%
  - `flat` otherwise
  - `insufficient_data` if any month < 5 sessions OR window < 6 months
- `ai_not_set_landing_pct` - share of AI sessions with `(not set)` landing page. Data quality flag; >15% suggests a landing page capture gap.

#### Quality Checks

- If AI regex returns zero rows, log a diagnostic noting possible causes (regex mode error, zero traffic in window, window too narrow). Do NOT fail the audit. Proceed with `ai_sessions_count: 0`.
- If `ai_not_set_landing_pct > 15%`, include a "Tracking Gap" flag in the Data Quality section (implementation issue on landing page capture).
- If raw sources contain dedup pairs (e.g., both `perplexity` and `perplexity.ai` with traffic), call out in caveats so the client understands the collapse.

#### Skip Condition

If `ai_sessions_count < 20` across the audit window, collapse the body subsection (see Section 4 below) to a one-liner:

> AI-referrer traffic: {count} sessions across {n} sources over the audit window. Below reporting threshold - detailed breakdown omitted.

Frontmatter fields are still populated (with small values) so downstream consumers can read the signal.

### Step 7: Device & User Segment Report

Pull device breakdown using a report query:
- Dimensions: `deviceCategory`
- Metrics: `sessions`, `totalUsers`, `bounceRate`, `engagementRate`, `averageSessionDuration`, `engagedSessions`, `screenPageViewsPerSession`, `eventCount` (filtered to primary conversion event)
- Date range: as specified


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


**Conversion enrichment call** (conditional, same pattern as Step 8b):
Runs ONLY when Step 3 classified heuristic conversion events that are NOT already GA4 key events.
```
run_report:
  dimensions: [newVsReturning, eventName]
  metrics: [eventCount]
  dimensionFilter: eventName IN [heuristic-classified conversion event names from Step 3b]
  date_range: as specified
```


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

Pull entry pages using a report query:
- Dimensions: `landingPage`
- Metrics: `sessions`, `bounceRate`, `engagementRate`, `engagedSessions`, `screenPageViewsPerSession`, `eventCount` (filtered to primary conversion event)
- Date range: as specified
- Limit: 30 rows
- Order by: sessions descending


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


Post-processing: aggregate `eventCount` per page x channel across matching event names. Merge with key event `conversions` from the primary call into a unified conversion count.

**Mismatch detection thresholds:**
- Bounce mismatch: >15pp gap between channels on the same page
- Conversion mismatch: one channel's conversion rate <50% of another on the same page

**Output:** New subsection under Landing Page Performance:

Columns: Landing Page | Better Channel | Worse Channel | Metric | Better Value | Worse Value | Gap

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

**AI-referrer tracking gap:** If Step 6b returned `ai_not_set_landing_pct > 15%`, flag under Data Quality as a landing page capture implementation issue for AI-referral traffic.

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

Columns: Page | Issue | Formula | Impact Bucket | Action Category | Note

Each row includes a sizing_note. Action categories: `messaging`, `ux`, `form`, `structural`.

### Step 10: Write Performance Profile

Construct `.claude/context/performance-profile.md` with the structure below. Do NOT read `schemas/performance-profile.md` -- this section is the authoritative reference at runtime.

#### Frontmatter Fields

All fields required unless noted.

- Metadata: `schema` ("performance-profile"), `schema_version` ("2.2"), `generated_by` ("ga4-audit"), `last_updated`, `last_updated_by` ("ga4-audit"), `confidence` (1-5), `company`, `property_id`, `property_name`, `date_range`, `days`
- Traffic: `total_sessions`, `total_users`, `device_mobile_pct` (integer %)
- Top pages (top 5 only): `top_pages[]` each with `path`, `sessions`, `bounce_rate`, `pages_per_session`, `avg_engagement_sec`, `failure_mode` (null | "shallow_engagement" | "deep_engagement")
- Conversions (conversion-classified only): `conversion_events[]` each with `name`, `count`, `classification`. Plus `primary_conversion_event`, `primary_conversion_rate` (%)
- Channels (top 3): `top_channels[]` each with `channel`, `sessions`, `bounce_rate`
- Mismatches: `source_page_mismatches[]` each with `page`, `better_channel`, `worse_channel`, `gap_type` ("bounce" | "conversion"), `better_value`, `worse_value`. Empty array if none.
- New/returning: `new_vs_returning` with `new_sessions_pct`, `new_conversion_rate`, `returning_conversion_rate`, `returning_to_new_ratio`, `signal` (familiarity_dependent | normal_b2b | strong_first_visit | acquisition_heavy)
- Page groups: `page_groups[]` each with `group`, `url_pattern`, `monthly_sessions`, `conversion_rate`, `bounce_rate`, `page_count`
- Opportunities: `top_opportunities[]` each with `page`, `issue`, `formula_type`, `current_metric`, `target_metric`, `monthly_sessions`, `estimated_monthly_impact` ("small" | "medium" | "large"), `action_category`, `sizing_note`
- Data quality: `traffic_adequacy` ("high" | "adequate" | "low"), `sampling_applied` (bool)
- Element interactions (from Step 5b, omit entirely when no element data): `element_interactions_available` (bool), `element_interaction_events` (int, number of events with element data), `discovered_parameters` (list of parameter names found), `top_interactions[]` each with `page`, `event`, `element` (parameter value, e.g. "Request Demo"), `parameter` (dimension name, e.g. "linkText"), `count`, `interaction_rate` (%). Top 10 by count.
- AI-referrer traffic (from Step 6b): `ai_sessions_count` (int), `ai_sessions_pct` (float, 2 decimals), `ai_conversions_count` (int), `ai_conversion_rate` (float, 2 decimals, null when `ai_sessions_count == 0`), `ai_traffic_trend` (string: `growing` | `flat` | `declining` | `insufficient_data`), `ai_not_set_landing_pct` (float, 2 decimals), `top_ai_sources[]` up to 5, each with `source` (canonical name), `sessions` (int), `pct_of_ai` (float).
- Comparison (omit entirely when --no-compare): `comparison_period` with `start`, `end`. `trends` with `sessions_change_pct`, `primary_cvr_change_pp`, `bounce_rate_change_pp`, `mobile_bounce_change_pp`
- L0: `l0_available` (bool), `l0_confidence` (int | null)

#### Body Sections (8 REQUIRED, 2 OPTIONAL)

All sections include trend tags when comparison is enabled.

1. **Property Overview** -- Property metadata, date range, data quality notes (prose, no table).
2. **Page Performance** -- 4 subsections:
   - Top Pages: Page | Sessions | Users | Bounce Rate | Engagement Rate | Avg Duration | Pages/Session | Avg Engagement (sec) | Failure Mode
   - High-Bounce Pages (>50% bounce, >100 sessions): Page | Sessions | Bounce Rate | Engagement Rate | Notes
   - Page Group Performance: Group | URL Pattern | Pages | Sessions | Weighted Bounce | Weighted Engagement | Conversions | Group CVR
   - Underperforming Pages (<50% group avg CVR, >200 sessions): Page | Group | Sessions | Page CVR | Group Avg CVR | Gap
3. **Conversion Events** -- Event Inventory: Event | Count | Classification | Notes. Per-page funnels (top 3 events): Page | Sessions | Conversions | Conversion Rate. Missing Tracking Gaps (list).
4. **Channel Performance** -- By Channel Group: Channel | Sessions | % of Total | Bounce Rate | Engagement Rate | Conversions | Conv Rate. Top Sources: Source/Medium | Channel | Sessions | Bounce Rate | Conv Rate. Followed by **AI-Referrer Traffic** subsection (see below).
5. **Device & User Segment Performance** -- Device Breakdown: Device | Sessions | % of Total | Bounce Rate | Engagement Rate | Avg Duration | Conv Rate. Mobile vs Desktop Gap: Metric | Desktop | Mobile | Gap | Significance. New vs Returning: Segment | Sessions | % of Total | Bounce Rate | Engagement Rate | Avg Duration | Conv Rate. Include returning:new ratio and signal.
6. **Landing Page Performance** -- Top Entry Pages (use `landingPage` dimension, not `pagePath`): Landing Page | Sessions | % of Entries | Bounce Rate | Engagement Rate | Conv Rate. High-Bounce Entry Points (>55% bounce, top 20): Landing Page | Sessions | Bounce Rate | Top Source | Notes. Source x Landing Page Mismatches: Landing Page | Better Channel | Worse Channel | Metric | Better Value | Worse Value | Gap.
7. **Opportunity Sizing** -- Page | Issue | Formula | Impact Bucket | Action Category | Note. Each row includes sizing_note.
8. **Key Metrics Summary** -- Strengths (2-4, cite numbers), Weaknesses (2-4, cite thresholds), Experiment Opportunities (3-5, cite metric gaps), Data Gaps. Each point cites specific numbers from sections 1-8.
9. **Element-Level Interactions** (OPTIONAL, from Step 5b) -- Only present when element interaction data was discovered. 3 subsections:
   - Discovered Parameters: Parameter | Scope | Source | Events With Data
   - Per-Page Interaction Breakdown (top 10 pages by session volume that have element data): Page | Event | Element (parameter value) | Parameter | Count | Interaction Rate | Notes
   - Interaction Gaps: pages with >500 sessions and primary CTA click rate <3%, CTA hierarchy dominance (one element >5x clicks of next), sequential content drop-off (<20% of first item). If none, "No notable interaction gaps detected."
10. **L0 Enrichment Notes** (OPTIONAL) -- Product-Line Grouping Overrides, Funnel Stage Mapping, Tracking Gaps. Only when L0 consumed.

##### Channel Performance: AI-Referrer Traffic subsection (always present, collapses below threshold)

Appears inside Section 4 after the Top Sources table.

Full format when `ai_sessions_count >= 20`:

```markdown
### AI-Referrer Traffic

**Summary:** {ai_sessions_count} sessions ({ai_sessions_pct}% of total), {ai_conversions_count} conversions ({ai_conversion_rate}% CVR). Trend: {ai_traffic_trend}.

**By source (collapsed):**

| Source | Sessions | Users | Conv | CVR |
|--------|---------:|------:|-----:|----:|
| [top_ai_sources rows] |

**Monthly trajectory:**

[yearMonth | sessions table, full audit window]

**Top AI-driven landing pages:**

[landingPage | source | sessions | conv, top 10]

**Data quality / caveats:**
- Source normalization: [list any dedup pairs found, or "No variant collapsing required."]
- `(not set)` landing page share: {ai_not_set_landing_pct}% [flag if >15%]
- Raw source rows in appendix below.

<details>
<summary>Raw (un-collapsed) AI source rows</summary>

[raw sessionSource rows before normalization]

</details>
```

Collapsed format when `ai_sessions_count < 20`:

```markdown
### AI-Referrer Traffic

{ai_sessions_count} sessions across {n} sources over the audit window. Below reporting threshold - detailed breakdown omitted.
```

#### Trend Tags

When comparison data is available (--no-compare not set), apply to Key Metrics Summary and relevant body sections:
- `[WORSENING]`: degraded >10% or >5pp
- `[IMPROVING]`: improved >10% or >5pp
- `[STABLE]`: within +/-10% or +/-5pp

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
  Element interactions: [N events with element data | no element data available]
  AI-referrer traffic: [N sessions ([pct]%), [trend] | below reporting threshold | none detected]

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

## Quality Checks

Before writing the final file, verify:

1. [ ] All 8 REQUIRED body sections are present (populated or gap-marked). OPTIONAL sections (Element-Level Interactions, L0 Enrichment Notes) present when applicable.
2. [ ] YAML frontmatter has all required fields. `schema_version` is `"2.2"`.
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
20. [ ] If element interaction data discovered: `element_interactions_available: true` in frontmatter, Element-Level Interactions body section present with all 3 subsections
21. [ ] If no element interaction data: `element_interactions_available: false` in frontmatter (or field omitted entirely), no Element-Level Interactions body section
22. [ ] AI-referrer frontmatter fields populated (all 7 fields). When `ai_sessions_count == 0`, `ai_conversion_rate` is `null` and `top_ai_sources` is an empty list.
23. [ ] AI-Referrer Traffic body subsection present inside Section 4 (Channel Performance). Collapsed one-liner when `ai_sessions_count < 20`, full breakdown otherwise.
24. [ ] Queries in Step 6b use `PARTIAL_REGEXP` (not `FULL_REGEXP`). If `FULL_REGEXP` was used by mistake, `chatgpt.com` will not match the `chatgpt` token and results will be empty or wrong.
25. [ ] Source normalization applied (chatgpt/perplexity/copilot/gemini/claude/mistral variants collapsed into canonical map). Raw rows preserved in appendix.
26. [ ] `ai_not_set_landing_pct > 15%` surfaces as a Tracking Gap entry in the Data Quality section.

---

## Data Source Routing

Step 1 sets `data_source` to either `"api"` or `"mcp"`. Use this table for ALL queries in Steps 2-8:

| Operation | API (`data_source = "api"`) | MCP (`data_source = "mcp"`) | Used In |
|-----------|----------------------------|----------------------------|---------|
| Account summaries | `ga4_client.py account-summaries` | `get_account_summaries` | Step 1 |
| Property details | `ga4_client.py property-details --property-id {id}` | `get_property_details` | Step 2 |
| Custom dimensions | `ga4_client.py custom-dimensions --property-id {id}` | `get_custom_dimensions_and_metrics` | Step 5b |
| Run report | `ga4_client.py run-report --property-id {id} --request '{json}'` | `run_report` | Steps 3-8 |

**API mode:** Run `ga4_client.py` from the ga4-audit skill directory. All output is JSON on stdout. Parse the JSON response to extract data.

**MCP mode:** Use analytics-mcp MCP tools directly. Response format matches standard MCP tool output.

Both modes return equivalent data structures. The GA4 API JSON response format is the same regardless of access method.

### Report Request Format

When using `ga4_client.py run-report`, pass the request body as a JSON string via `--request` or save to a file and use `--request-file`. The request body follows the [GA4 Data API RunReportRequest](https://developers.google.com/analytics/devguides/reporting/data/v1/rest/v1beta/properties/runReport) format:

- `dateRanges`: Array of `{ "startDate", "endDate" }`. Use "NdaysAgo" format or "YYYY-MM-DD".
- `dimensions`: Array of `{ "name" }` objects
- `metrics`: Array of `{ "name" }` objects
- `dimensionFilter`: Optional filter expression
- `metricFilter`: Optional filter expression
- `orderBys`: Array of ordering specs
- `limit`: Row limit (default 10000)

**Common GA4 dimensions:**
- `pagePath`, `landingPage`, `deviceCategory`
- `sessionDefaultChannelGroup`, `sessionSource`, `sessionMedium`
- `eventName`, `yearMonth`

**Common GA4 metrics:**
- `sessions`, `totalUsers`, `newUsers`, `bounceRate`, `engagementRate`
- `averageSessionDuration`, `engagedSessions`, `eventCount`, `conversions`

**Filtering for specific events:** Use `dimensionFilter` on `eventName` dimension to isolate specific conversion events when pulling per-page conversion data.

**PARTIAL_REGEXP filtering:** For AI-referrer segmentation in Step 6b, set the dimensionFilter `matchType` to `PARTIAL_REGEXP` (substring match) rather than `FULL_REGEXP` (whole-string match). The AI_REGEX lists fragments, not full source strings.
