---
name: ga4-audit
version: 2.5.0
description: "When the user wants to audit GA4 analytics data for a property. Also use when the user mentions 'GA4 audit,' 'analytics audit,' 'traffic analysis,' 'page performance,' 'conversion audit,' 'bounce rate analysis,' or 'performance profile.' Pulls 11-15 targeted reports from GA4 via direct API or analytics-mcp fallback (including element-level interaction discovery and AI-referrer traffic segmentation), classifies events, and produces a structured performance-profile.md context file (.claude/context/ L1). Dual-mode output: when the working repo declares a CRO knowledge base binding, writes a typed silver-performance-analysis artifact into that KB instead (--scope required; --no-kb forces legacy). Single agent, no depth flag. Works with any GA4 property."
updated: 2026-07-22
---

# GA4 Audit

You are an analytics specialist. Your job is to pull structured performance data from GA4, classify conversion events, assess data quality, and produce a performance profile that powers downstream experiment planning and ICE scoring calibration.

**You are an L1 skill.** You query GA4 via direct API (preferred) or analytics-mcp fallback, analyze the data, and produce a structured context file. This means:
- You perform API calls via `ga4_client.py` (direct GA4 API) or analytics-mcp MCP tools as fallback (not web research)
- You classify and analyze the data you pull
- You produce one context file: `.claude/context/performance-profile.md` (KB mode: a typed `silver-performance-analysis` artifact instead, see `KB Mode (Dual-Mode Output)`)
- Your output is machine-readable (YAML frontmatter + structured markdown), not a deliverable

**Output location:** `.claude/context/performance-profile.md` (KB mode: `{kb_root}/reference/cro-{scope}/performance-analysis.md`, see `KB Mode (Dual-Mode Output)`)
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
| `--scope-page-contains` | (none) | Restrict every report to pages whose `pagePath` contains this substring (sub-property scope). Unset = whole property. |
| `--scope-host` | (none) | Restrict every report to a single `hostName` (sub-property scope). Combinable with `--scope-page-contains`. Unset = whole property. |
| `--scope` | (none) | KB mode only. Names which KB scope the run writes into (the bound type skill defines valid scopes). Required in KB mode; warn-and-ignore in legacy mode. Distinct from `--scope-page-contains`/`--scope-host`, which are analytics sub-property filters, not KB scopes. See `KB Mode (Dual-Mode Output)`. |
| `--no-kb` | off | Force legacy `.claude/context/` output even when a KB binding is detected. See `KB Mode (Dual-Mode Output)`. |

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

### Scope Rule (applies to ALL run_report calls)

When `--scope-page-contains <substr>` and/or `--scope-host <host>` is set, add a `dimensionFilter` to EVERY `run_report` request to restrict the unit of analysis to one sub-property inside a larger property. Follow the same "applies to ALL run_report calls" discipline as the Comparison Rule -- do not repeat the filter logic per step.

- `--scope-page-contains` -> `dimensionFilter` on `pagePath` with `matchType: CONTAINS` (substring).
- `--scope-host` -> `dimensionFilter` on `hostName` with exact match.
- Both set -> combine under an `andGroup` filter expression.
- When the step already needs a `dimensionFilter` (e.g., Step 5 event filter), wrap the existing filter and the scope filter in an `andGroup` so both apply.
- Unset (default) = whole property, exactly as before.

Record the resolved scope in frontmatter: `scope_applied` (bool), `scope_method` (`"page_contains"` | `"host"` | `"both"` | `"none"`), `scope_note` (human-readable description; when scope is approximate, note the page-attribution caveat and cap confidence at 3 on scope grounds).

---

## KB Mode (Dual-Mode Output)

This skill runs in one of two output modes, resolved ONCE at Step 0 (before Step 1) and held in-session. Only the write target and the addition of KB frontmatter change. Every report query, classification, failure-mode threshold, opportunity-sizing formula, and quality check is identical in both modes: this is a write-side adaptation, not an analysis change.

- **Legacy mode** (default): write `.claude/context/performance-profile.md` exactly as documented in Step 10.
- **KB mode:** write the same profile content as a typed `silver-performance-analysis` artifact into a knowledge base declared by the working repo.

This is a single-agent skill: there is no agent parameter-block threading. Mode resolution produces in-session KB state (`kb_root`, `kb_type`, `scope`, type-def path) consulted only by Step 10 (the write).

### Mode Resolution Procedure (Step 0)

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy mode, and note in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy I/O."
3. Parse the KB root path (e.g., `docs/`) and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/` and its `artifacts/` directory defines `silver-performance-analysis` (the output type). If any check fails: legacy mode, and report which check failed. Never write typed artifacts into a half-configured KB.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope.

There is deliberately no `--kb` force flag. A failed detection of the output KB falls back to legacy loudly so a broken KB binding gets fixed instead of worked around.

### Schema Authority

This SKILL.md (Step 10) remains the authority for the performance-profile field set and body sections. In KB mode, the bound type def (`.claude/skills/{kb-type}/artifacts/silver-performance-analysis.md`) is additionally the authority for the KB output path, the KB frontmatter contract, and any required section layout the type imposes: read it during Step 10 before writing. `governed_by` is composed at runtime as `{kb-type}/silver-performance-analysis`. This skill never hardcodes a KB type skill name or client-specific path.

### Output Mapping and Frontmatter Contract

| Legacy context file | KB artifact type | Path under KB root | Required |
|---|---|---|---|
| `performance-profile.md` | `silver-performance-analysis` | `reference/cro-{scope}/performance-analysis.md` | output |

Resolve the write target by artifact TYPE, not by an assumed basename: the funnelenvy default basename is `performance-analysis.md`, but a KB type may name its artifact file differently. The directory is always `reference/cro-{scope}/`.

KB mode prepends KB frontmatter to the same profile body:

`fe-managed: true`, `name: {scope}-performance-analysis`, `description` (one line, generated), `kb_layer: silver`, `governed_by: {kb-type}/silver-performance-analysis`, `scope`, `data_provenance: client` (analytics is first-party client data), `generated_by: ga4-audit`, `confidence` (the same 1-5 value legacy mode computes), `depends_on`, `tags` (3-7 semantic), `version`, `created`, `updated`. The full performance-profile field set from Step 10 (including `schema_version: "2.3"`) rides along as additional frontmatter fields, so a downstream consumer that version-gates still sees the stamp. The type def's `field_definitions` are validated for required presence; additional fields and sections are permitted.

**`depends_on` policy for query-time data.** A performance analysis is a first-party projection of live analytics; it is not derived from any other KB artifact. So `depends_on` is an **empty list by default**: its provenance is the property and date range recorded in the body (`property_id`, `property_name`, `date_range`, `days`), not an in-KB source edge. The one optional edge: if the bound KB declares an analytics-configuration or reference artifact for the scope that this run actually consumed to resolve the property or scope, record a single same-layer edge to it. Never invent a bronze data-export edge the skill does not produce. If the bound `silver-performance-analysis` type def requires a non-empty `depends_on` and no such reference artifact exists, emit the empty list, note it in the completion message, and let the validation gate surface the type-def mismatch rather than fabricating an edge.

### Prior Work Detection (KB Mode)

Analytics data is a time-bounded snapshot, so the legacy "no incremental extension" rule holds in KB mode too. Glob `{kb_root}/reference/cro-{scope}/` for an existing `silver-performance-analysis` artifact. If present, overwrite it in place: preserve `created`, bump `version` (analytics snapshots are always a full re-pull, so a patch bump), set `updated` to today, replace the body wholesale. No diffing, no merging, no confidence-only-rises rule.

### Post-Write Validation Gate

After writing the KB artifact:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY <kb-start-scripts>/kb_type_validate.py validate {kb_root}/reference/cro-{scope}/performance-analysis.md
```

Resolve `<kb-start-scripts>` from the fe-knowledge-base plugin's kb-start skill `scripts/` directory (marketplace plugin cache or source repo). If validation reports errors, fix the artifact frontmatter/sections and re-validate. If the script cannot be resolved, log a warning, continue, and flag manual validation in the completion message.

### KB Mode Completion Message

Replace the first line of the Step 10 completion summary with the KB artifact lines and append validation status:

```
Performance analysis written to {kb_root}/reference/cro-{scope}/performance-analysis.md
  Type: silver-performance-analysis | Scope: {scope} | Version: {v}
  depends_on: [reference artifact if consumed, else "none (query-time first-party data)"]

  [standard Property / Date range / Sessions / etc. lines unchanged]

  Validation: kb_type_validate.py passed | failed (fixed and re-validated) | unresolved (manual validation needed)
```

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

**None.** Unlike positioning context files, analytics data is a time-bounded snapshot. Each run overwrites `.claude/context/performance-profile.md` entirely. No incremental extension, no confidence-only-rises rule. (KB mode applies the same overwrite-in-place rule to the `silver-performance-analysis` artifact, see `KB Mode (Dual-Mode Output)` > `Prior Work Detection (KB Mode)`.)

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

**Event liveness / dead-binding audit (feeds Measurement Integrity):** Step 3a already pulls every event with counts. From that same data:
- Flag any configured or key event returning zero over the window as a **dead binding** (`status="dead"`) -- the event is defined/expected but not firing.
- When comparison is enabled, diff each event's primary vs comparison count to flag **zero-crossings**: present-then-0 -> `dark`; 0-then-present or a large jump -> `spiked`.
- Emit these into the `event_liveness[]` frontmatter list (each `event`, `count`, `status`) and roll dead bindings + zero-crossings into `measurement_integrity_flags[]` for the REQUIRED Measurement Integrity body section (Step 10).
- "Expected" events for dead-binding purposes are the conversion/key events from classification plus any L0-stated conversion points (Step 3c).

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

### Step 5b: Element-Level Interaction Discovery (REQUIRED output)

This step discovers element-level interactions and produces the REQUIRED Element-Level Interactions body section. It ALWAYS emits `element_instrumentation_state` (`present` | `partial` | `absent`) -- absence is asserted as a finding, never a silent skip.

**No silent skip.** Even when no custom event-scoped parameters exist, GA4 enhanced measurement (autotrack) `linkText`/`linkUrl` are enumerated. If those also yield nothing, set `element_instrumentation_state: "absent"`, populate `missing_element_classes`, set a non-null `instrumentation_ask`, and the body section LEADS with the gap statement. The legacy "No element-level interaction data available" terminal skip is removed.

**Scoped page set:** enumerate interactions across the scoped sub-property page set (per the Scope Rule), not only the Step-4 top pages. When scope is unset, this is the property's top pages as before.

#### Step 5b-1: Parameter Discovery

Query custom dimensions and metrics for the property (see Data Source Routing table). Collect:
- Custom event-scoped dimensions (e.g., `customEvent:form_id`, `customEvent:cta_label`, `customEvent:button_text`)
- Note which are event-scoped vs user-scoped (only event-scoped are useful here)

Also check for standard enhanced measurement dimensions that carry element context:
- `linkText` (from enhanced measurement click events)
- `linkUrl` (from enhanced measurement click events)
- `fileExtension`, `fileName` (from file_download events)
- `videoTitle` (from video events)

**Always enumerate autotrack.** `linkText`/`linkUrl` are available on any property with enhanced measurement enabled, independent of custom event-scoped parameters. Enumerate them even when no custom event params exist. Only when BOTH custom params AND `linkText`/`linkUrl` return no data do you record `element_instrumentation_state: "absent"` -- and even then you emit the section with the absence finding (see Step 5b-4). Do not skip the step.

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

Run one query per discovered parameter dimension (up to 5 total). When no custom event-scoped parameters exist, still run the `linkText` (and, budget permitting, `linkUrl`) autotrack queries. If multiple parameters exist, prioritize:
1. Custom parameters with "cta," "button," "label," or "form" in the name
2. `linkText` (most informative standard dimension)
3. `linkUrl`
4. Other custom event-scoped dimensions
5. `videoTitle`, `fileExtension`

**Element-event trend (comparison):** when comparison is enabled, include the comparison date range on these queries (per the Comparison Rule) so element-event volumes carry a primary-vs-comparison trend. An element that fired then went to zero is a `dark` zero-crossing; surface it in Measurement Integrity alongside event liveness.

#### Step 5b-3: Compute Interaction Metrics

For each page x event x parameter combination:
- **Interaction rate:** `eventCount / page_sessions * 100` (using page sessions from Step 4)
- **Relative share:** What percentage of that event type on that page does this element represent

Flag notable findings:
- Primary CTA click rate <3% on pages with >500 sessions (low CTA engagement)
- One element gets >5x interactions of the next element for the same event type (CTA hierarchy dominance)
- Later items in sequential elements (carousel slides, tab panels) get <20% of first item interactions (content below first view invisible)

#### Step 5b-4: Record Results and Determine Instrumentation State

Always determine and emit `element_instrumentation_state`:
- `present`: meaningful interaction volume returned across the scoped page set.
- `partial`: some interactions return data but expected structural element classes (e.g., primary CTA, nav, form fields) are missing.
- `absent`: neither custom params nor autotrack `linkText`/`linkUrl` returned data for the scoped unit.

Populate `tracked_elements[]` (each `name`, `count`, `status` -- `dark` when the comparison trend flagged a present-then-0 element, else `live`). For `partial`/`absent`, populate `missing_element_classes[]` and a non-null `instrumentation_ask` (e.g., "Enable enhanced measurement outbound click tracking" or "Instrument primary CTA via a custom event parameter").

The Element-Level Interactions body section is ALWAYS written (Step 10 section 9). When state is `absent`/`partial` it LEADS with the gap statement and the `instrumentation_ask`. `element_interactions_available` is retained for back-compat but is no longer a skip signal -- `element_instrumentation_state` is authoritative.

#### Step 5b-5: Friction Pass

Rank event names and `linkText` values matching friction tokens (`error`, `invalid`, `required`, `fail`, `denied`) and surface the top non-navigation interactions by volume. When a baseline event is determinable (e.g., a form-start or a flow-start event), compute `ratio_to_baseline` (friction count / baseline count); else null. Populate `friction_interactions[]` (each `interaction`, `count`, `ratio_to_baseline`, `type`). These surface in the Measurement Integrity body section.

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

Construct the performance profile with the structure below. Do NOT read `schemas/performance-profile.md` -- this section is the authoritative reference at runtime. **Mode branch:** in legacy mode, write `.claude/context/performance-profile.md`. In KB mode (resolved at Step 0), write the same content as a `silver-performance-analysis` artifact per `KB Mode (Dual-Mode Output)` > `Output Mapping and Frontmatter Contract` (KB frontmatter prepended, `schema_version: "2.3"` and the full field set ride along), then run the post-write validation gate. The field set and body sections below are identical in both modes.

#### Frontmatter Fields

All fields required unless noted.

- Metadata: `schema` ("performance-profile"), `schema_version` ("2.3"), `generated_by` ("ga4-audit"), `last_updated`, `last_updated_by` ("ga4-audit"), `confidence` (1-5), `company`, `property_id`, `property_name`, `date_range`, `days`
- Scope (schema 2.3): `scope_applied` (bool), `scope_method` ("page_contains" | "host" | "both" | "none"), `scope_note` (string | null; description + page-attribution caveat when approximate)
- Traffic: `total_sessions`, `total_users`, `device_mobile_pct` (integer %)
- Top pages (top 5 only): `top_pages[]` each with `path`, `sessions`, `bounce_rate`, `pages_per_session`, `avg_engagement_sec`, `failure_mode` (null | "shallow_engagement" | "deep_engagement")
- Conversions (conversion-classified only): `conversion_events[]` each with `name`, `count`, `classification`. Plus `primary_conversion_event`, `primary_conversion_rate` (%)
- Channels (top 3): `top_channels[]` each with `channel`, `sessions`, `bounce_rate`
- Mismatches: `source_page_mismatches[]` each with `page`, `better_channel`, `worse_channel`, `gap_type` ("bounce" | "conversion"), `better_value`, `worse_value`. Empty array if none.
- New/returning: `new_vs_returning` with `new_sessions_pct`, `new_conversion_rate`, `returning_conversion_rate`, `returning_to_new_ratio`, `signal` (familiarity_dependent | normal_b2b | strong_first_visit | acquisition_heavy)
- Page groups: `page_groups[]` each with `group`, `url_pattern`, `monthly_sessions`, `conversion_rate`, `bounce_rate`, `page_count`
- Opportunities: `top_opportunities[]` each with `page`, `issue`, `formula_type`, `current_metric`, `target_metric`, `monthly_sessions`, `estimated_monthly_impact` ("small" | "medium" | "large"), `action_category`, `sizing_note`
- Data quality: `traffic_adequacy` ("high" | "adequate" | "low"), `sampling_applied` (bool)
- Element instrumentation (schema 2.3, from Step 5b, ALWAYS emitted): `element_instrumentation_state` ("present" | "partial" | "absent"), `tracked_elements[]` each `name`/`count`/`status` ("live" | "dark"), `missing_element_classes[]`, `instrumentation_ask` (string | null). `element_interactions_available` (bool) retained for back-compat but no longer a skip signal. Detail fields (present when state is `present`/`partial`): `element_interaction_events` (int), `discovered_parameters` (list of parameter names found), `top_interactions[]` each with `page`, `event`, `element` (parameter value, e.g. "Request Demo"), `parameter` (dimension name, e.g. "linkText"), `count`, `interaction_rate` (%). Top 10 by count.
- Measurement integrity (schema 2.3, from Steps 3 + 5b-5): `event_liveness[]` each `event`/`count`/`status` ("live" | "dead" | "dark" | "spiked"), `measurement_integrity_flags[]` (dead bindings + zero-crossings), `friction_interactions[]` each `interaction`/`count`/`ratio_to_baseline` (nullable)/`type`
- AI-referrer traffic (from Step 6b): `ai_sessions_count` (int), `ai_sessions_pct` (float, 2 decimals), `ai_conversions_count` (int), `ai_conversion_rate` (float, 2 decimals, null when `ai_sessions_count == 0`), `ai_traffic_trend` (string: `growing` | `flat` | `declining` | `insufficient_data`), `ai_not_set_landing_pct` (float, 2 decimals), `top_ai_sources[]` up to 5, each with `source` (canonical name), `sessions` (int), `pct_of_ai` (float).
- Comparison (omit entirely when --no-compare): `comparison_period` with `start`, `end`. `trends` with `sessions_change_pct`, `primary_cvr_change_pp`, `bounce_rate_change_pp`, `mobile_bounce_change_pp`
- L0: `l0_available` (bool), `l0_confidence` (int | null)

#### Body Sections (10 REQUIRED, 1 OPTIONAL)

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
9. **Element-Level Interactions** (REQUIRED, from Step 5b) -- ALWAYS present; `element_instrumentation_state` is emitted in every run.
   - When `present`/`partial`, 3 subsections:
     - Discovered Parameters: Parameter | Scope | Source | Events With Data
     - Per-Page Interaction Breakdown (top 10 pages by session volume that have element data, across the scoped page set): Page | Event | Element (parameter value) | Parameter | Count | Interaction Rate | Notes
     - Interaction Gaps: pages with >500 sessions and primary CTA click rate <3%, CTA hierarchy dominance (one element >5x clicks of next), sequential content drop-off (<20% of first item). If none, "No notable interaction gaps detected."
   - When `absent` (or `partial` with missing structural classes): the section LEADS with the gap statement -- which structural element classes are not instrumented (`missing_element_classes`) and the recommended `instrumentation_ask`. This is a finding, not a skip.
10. **Measurement Integrity** (REQUIRED, from Steps 3 + 5b-5) -- ALWAYS present.
    - Dead Bindings: configured/key events returning zero over the window (`event_liveness` rows with `status="dead"`). Each: Event | Count | Status.
    - Zero-Crossings (comparison only): events/elements that went `dark` (present-then-0) or `spiked` (0-then-present or large jump).
    - Friction Interactions: token-matched (error/invalid/required/fail/denied) and top non-navigation interactions: Interaction | Count | Ratio to Baseline | Type.
    - If none of the three classes detected, state "No dead bindings, zero-crossings, or friction interactions detected" -- the section is still present.
11. **L0 Enrichment Notes** (OPTIONAL) -- Product-Line Grouping Overrides, Funnel Stage Mapping, Tracking Gaps. Only when L0 consumed.

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

Write the file to `.claude/context/performance-profile.md` (legacy mode). In KB mode, write to the `silver-performance-analysis` path and run the validation gate per `KB Mode (Dual-Mode Output)`, and use the KB Mode Completion Message instead of the summary below.

**Completion summary (legacy mode):**

```
Performance profile written to .claude/context/performance-profile.md

  Property: [Name] ([ID])
  Date range: [start] to [end] ([N] days)
  Sessions: [N] | Users: [N] | Mobile: [N]%
  Conversion events: [N] classified ([primary] as primary, [rate]% site-wide)
  Traffic adequacy: [high/adequate/low]
  Confidence: [N]
  Comparison: [enabled, vs [start] to [end] | disabled (--no-compare)]
  Scope: [page_contains | host | both | whole-property]
  Element instrumentation: [present | partial | absent]
  Measurement integrity: [N dead bindings, N dark/spiked, N friction]
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

## Quality Checks

Before writing the final file, verify:

1. [ ] All 10 REQUIRED body sections are present (populated or gap-marked), including Element-Level Interactions and Measurement Integrity. OPTIONAL section (L0 Enrichment Notes) present when applicable.
2. [ ] YAML frontmatter has all required fields. `schema_version` is `"2.3"`.
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
20. [ ] Element-Level Interactions section present (REQUIRED): `element_instrumentation_state` (`present` | `partial` | `absent`) emitted in frontmatter; when `present`/`partial` the 3 subsections are populated; when `absent`/`partial` the section LEADS with the gap statement, `missing_element_classes` is populated, and `instrumentation_ask` is non-null (no silent skip)
21. [ ] Autotrack enumerated: `linkText`/`linkUrl` queried even when no custom event-scoped parameters exist
22. [ ] Measurement Integrity section present (REQUIRED): `event_liveness` covers configured/key events; dead bindings flagged; with comparison, dark/spiked zero-crossings surfaced; `friction_interactions` populated (or "None detected")
23. [ ] Scope frontmatter present (`scope_applied`, `scope_method`, `scope_note`); when a scope flag is set, the `dimensionFilter` was applied to every `run_report` call and confidence capped when scope is approximate
24. [ ] AI-referrer frontmatter fields populated (all 7 fields). When `ai_sessions_count == 0`, `ai_conversion_rate` is `null` and `top_ai_sources` is an empty list.
25. [ ] AI-Referrer Traffic body subsection present inside Section 4 (Channel Performance). Collapsed one-liner when `ai_sessions_count < 20`, full breakdown otherwise.
26. [ ] Queries in Step 6b use `PARTIAL_REGEXP` (not `FULL_REGEXP`). If `FULL_REGEXP` was used by mistake, `chatgpt.com` will not match the `chatgpt` token and results will be empty or wrong.
27. [ ] Source normalization applied (chatgpt/perplexity/copilot/gemini/claude/mistral variants collapsed into canonical map). Raw rows preserved in appendix.
28. [ ] `ai_not_set_landing_pct > 15%` surfaces as a Tracking Gap entry in the Data Quality section.

---
