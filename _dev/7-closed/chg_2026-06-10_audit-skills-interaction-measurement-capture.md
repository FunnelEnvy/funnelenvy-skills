---
fe-managed: true
name: audit-skills-interaction-measurement-capture
description: >
  Make aa-audit and ga4-audit capture, by default on every run, six gap classes the audits
  currently miss: element-interaction instrumentation state (presence AND absence), missing-instrumentation
  asserted as a top finding, measurement-integrity regressions (dead bindings, zero-crossings),
  friction interactions, sub-property scoping, and scoped new-vs-returning/engagement depth. Promotes
  element-instrumentation to a REQUIRED output section and adds a Measurement Integrity section.
governed_by: change-management/change-document
status: Closed
resource_name: [aa-audit, ga4-audit]
resource_version: "TBD"
impact: 5
confidence: 4
ease: 2
initiative: cro-kb-path-b
blocks: [audit-skills-kb-native-writes, aa-audit-performance-profile-schema-conformance]
status_note: "Closed, QA approved; unreleased pending release + marketplace force-update"
version: "0.8.0"
created: 2026-06-10
updated: 2026-06-11
---
# Audit Skills Interaction & Measurement-Integrity Capture

## Background

A manual Adobe Analytics pull surfaced six measurement gaps in a client performance profile that `/aa-audit` had produced but had not captured: a configured conversion event whose binding returned zero for the entire window (a dead binding), three element-click events that regressed dark partway through the window, a configurator required-choice validation error firing at several multiples of configuration starts, and no element instrumentation on any structural CTA. Five of the six are structural in the skills, not specific to one client. The objective is to fix both audit skills so a default run captures these classes of gap on any client, without a human writing a single ad-hoc query.

The bar: a default run on a blended enterprise report suite should have produced the element-instrumentation and measurement-integrity content that had to be hand-written into the reference analysis, including the click-tracking regression and the configurator-error datapoint.

This concern is mode-independent (it improves the captured data in both legacy `.claude/context/` and KB-native modes), but it is filed under `cro-kb-path-b` because it shares files and the `performance-profile` schema with that initiative's in-flight items and must be sequenced against them.

## Current State

Verified against the working-repo source on 2026-06-10 (not the older marketplace copy; the only divergence there is the Jun 4 `_coerce_cell` NaN fix, which does not touch these gaps):

- **Suite-wide blindness (master cause).** `aa_audit.py:run_report` accepts `segment_ids` and `search`, but `main()` passes neither, and there is no `scope` config knob. All 9 reports run against the whole report suite. When the unit of analysis is one storefront inside a blended suite, that storefront sits below the waterline of every top-N list. `ga4-audit` shares the assumption (whole property, no sub-property/segment scoping).
- **Element clicks config-gated on the wrong default dimension.** `fetch_element_clicks` (`aa_audit.py:528`) returns `None` unless `config.dimensions.link_text` is set; `aa-config.example.json` defaults it to `variables/evar200`. Client configs frequently leave `dimensions` empty, so the step returns `None` and the SKILL writes "No element-level interaction data available." On a `customlink`-based implementation the real clicks live in `variables/customlink` and Activity Map (`clickmaplink`/`clickmappage`).
- **No prefix/search scoping on the element query.** `fetch_element_clicks` pulls top 50 suite-wide with no `search` clause; sub-property events rank below site-wide noise.
- **Element interactions excluded from the comparison period.** The comparison block in `main()` (lines 701-736) re-pulls pages, channels, devices, landing pages, new-vs-returning, and page conversions, but not `element_clicks` or `clickmap_regions`, so a high-to-zero regression is structurally uncapturable. GA4 Step 5b is current-period only.
- **No friction-interaction class.** Both skills model events as positive funnel/engagement events from config; no step surfaces high-volume error/validation interactions.
- **No event-liveness / dead-binding audit.** Neither skill enumerates which configured events returned zero over the window.
- **Element-Level Interactions is OPTIONAL.** `aa-audit/SKILL.md` Step 7 + body section 9 are optional; absence is a silent skip (`element_interactions_available: false` on the GA4 side).

Architecture note: `aa_audit.py` orchestrates all reporting itself (fixes land in the script + config + SKILL.md interpretation). `ga4_client.py` is a thin proxy (`run-report`, `custom-dimensions`, etc.); the agent constructs each request in SKILL.md, so GA4 fixes land mostly as SKILL.md steps and query patterns, with at most minor client additions.

Coupled in-flight work in the same initiative: [audit-skills-kb-native-writes](../1-backlog/chg_2026-06-03_audit-skills-kb-native-writes.md) (cross-skill schema-version contract) and [aa-audit-performance-profile-schema-conformance](../1-backlog/chg_2026-06-03_aa-audit-performance-profile-schema-conformance.md) (AA frontmatter conformance), both of which depend on the final schema shape this change alters.

## Research

### Root cause to fix mapping (the six gap classes)

| # | Root cause | Shared fix | AA specifics | GA4 specifics |
|---|------------|-----------|--------------|---------------|
| 1 | Suite-wide blindness (master) | `scope` config block applied to every report | Pass `segment_ids` (or a `search` prefix) on every `run_report` | `dimensionFilter` (`pagePath`/`hostName` contains) or audience |
| 2 | Element clicks gated on one mis-defaulted eVar | `interaction_dimensions` array; default to platform-native click dims; enumerate by scope prefix | Default `[customlink, clickmaplink, clickmappage]`; eVar override retained | `linkText`/`linkUrl` + discovered custom params; enumerate even with no custom event params (autotrack) |
| 3 | No prefix/search scoping on element query | Broad single-token prefix `search`, untruncated limit | Thread scope + `search` into `fetch_element_clicks` and Activity Map fetch | Include scoped sub-property page set, not just Step-4 top pages |
| 4 | Element interactions excluded from comparison | Include element clicks + liveness set in comparison; flag dark/spike | Add `element_clicks` + new `event_liveness` to the comparison block | Add element events to the trend computation |
| 5 | No friction-interaction class | Friction pass (token-match + top non-navigation) | Surface from Custom Link values | Surface from event names / `linkText` |
| 6 | No event-liveness / dead-binding audit | Count every configured event over window; flag zeros and zero-crossings; emit `Measurement Integrity` subsection | New `event_liveness` fetch | Fold liveness into Step 3 |

Plus the cross-cutting meta-fix: promote element-instrumentation from a silent skip to a REQUIRED finding (presence with volumes, AND absence asserted as the lead data gap with a recommended instrumentation ask).

### Target output shape (from a worked reference analysis)

A hand-written reference performance analysis is the model for what a correct default run should produce. Its element-instrumentation section carries: a Custom Link inventory table (`link_name | instances over window | status`), an Activity Map deployment-status statement, a regression subsection (events firing then going to zero, with the date window), a friction subsection (error firing rate vs. a baseline such as configuration starts), and a dimension-scoping-constraint statement. Dead bindings (a configured event returning zero across the full window) live in a measurement-integrity callout. The reliable enumeration method is a broad single-token prefix `search` at an untruncated limit; narrow multi-token/colon `contains:` clauses silently return empty and must be treated as inconclusive. These structural elements define the new REQUIRED sections and the config defaults.

## Approach

The six Discovery design questions are resolved and integrated below. The change has three layers, all backward-compatible: a config without `scope`/`interaction_dimensions` runs exactly as today.

### Change Profile

- **Script-affecting: yes.** Adds new fetch functions to `aa_audit.py` (scoped element enumeration, event liveness), threads `scope`/`search` through `run_report`, and extends the comparison block. New and modified scripts pull in `_tests/` authoring.
- **Performance-affecting: yes.** Changes audit capture behavior and output coverage (new REQUIRED sections, new capture passes, new schema fields). Per skill-management eval policy this warrants eval-task definition before Build.
- **Test-eval-only: no.** Touches production scripts, both SKILL.md files, the AA config schema/example, and the shared `performance-profile` schema.

### Scope of the change

One combined change spanning both skills (decision 1), with per-skill `Requirements` sub-sections authored in Design so the divergent implementation surfaces stay separable. This mirrors the `audit-skills-kb-native-writes` precedent.

### Layer 1: Config + schema

- **AA `scope` block (decision 2).** New optional `scope` config supporting both a `segment_id` (preferred when one exists) and an entry-page/page `prefixes` list (fallback). Applied to every report via the existing `run_report` `segment_ids`/`search` parameters. When `scope` is unset, every report runs whole-suite as today. The agent documents the post-consent page-attribution caveat in the profile and caps confidence when scoping is approximate (no segment, prefix-only). GA4 analog: a `dimensionFilter` on `pagePath`/`hostName`, or an audience.
- **`interaction_dimensions` array (decision 3).** Replace the single `link_text` knob with an `interaction_dimensions` array. AA default `[variables/customlink, variables/clickmaplink, variables/clickmappage]`; the custom-eVar mapping is retained as an override for clients who route clicks through an eVar. `aa-config.example.json` repointed accordingly. GA4 default: `linkText`/`linkUrl` plus discovered custom params.
- **Schema-version bump (decision 6).** A single new shared `performance-profile` `schema_version` (target `"2.3"`, confirmed in Design against the cross-skill contract owner) carries the new fields. This change is sequenced ahead of the KB-native contract work, recorded by the `blocks` edges on both sibling docs.

### Layer 2: Capture

- **AA:** new scoped element-enumeration fetch (broad single-token prefix `search` at an untruncated limit, iterating `interaction_dimensions`) and a new `event_liveness` fetch (counts every configured event over the window). `scope`/`search` plumbed through `run_report`. `element_clicks` and the liveness set added to the comparison block so dark/spike regressions are detectable. A friction pass ranks interaction values matching error/invalid/required/fail tokens and surfaces top non-navigation interactions. The broad-prefix search-reliability caveat (narrow multi-token/colon `contains:` clauses silently return empty and are inconclusive) is documented in the SKILL and applied by the enumeration.
- **GA4:** parallel SKILL.md steps. Scoped element discovery including autotrack (`linkText`/`linkUrl` enumerated even with no custom event params), element events added to the trend computation, event-liveness folded into Step 3, a friction pass over event names/`linkText`, and scoped new-vs-returning/engagement depth (decisions 4 and 5).

### Layer 3: Output

Promote element-instrumentation to a REQUIRED body section in both SKILL.md files, and add a REQUIRED `Measurement Integrity` section (decision 4). When the scoped sub-property has no element instrumentation, the profile asserts it as the lead data gap with a recommended instrumentation ask rather than a silent skip. Liveness zeros and zero-crossings surface in `Measurement Integrity`. Friction interactions surface in the element section. Quality Checks in both skills are extended to enforce the new REQUIRED sections.

### Alternatives Considered

- **Two separate per-skill change docs.** Rejected: the skills share the `performance-profile` schema and the conceptual gap model, so a single change keeps the schema-version bump and the gap taxonomy coherent. Architectural divergence is handled by per-skill `Requirements` sub-sections, not by splitting the lifecycle.
- **Scope via a single mechanism (segment-only or prefix-only).** Rejected: segment-only fails clients with no pre-built segment for the sub-property (the motivating case); prefix-only is partial post-consent in a blended suite. Supporting both, segment preferred with prefix fallback, covers both implementations with a documented accuracy caveat.

## Requirements

Organized as shared schema requirements followed by per-skill implementation requirements. All config additions are optional with backward-compatible defaults: an unset `scope` and unset `interaction_dimensions` reproduce pre-change query behavior.

### R0: Shared performance-profile schema (both skills)

Bump `schema_version` from the current producer values (`aa-audit` `"2.0"`, `ga4-audit` `"2.2"`) to a single shared `"2.3"`. New/changed frontmatter fields (proposed canonical set; `audit-skills-kb-native-writes` adopts these into its cross-skill contract per the `blocks` edge):

| Field | Type | Notes |
|-------|------|-------|
| `scope_applied` | bool | True when a sub-property scope was applied to all reports |
| `scope_method` | string (open) | How the unit of analysis was isolated. Open string covering both producers' values: AA emits `segment` \| `prefix` \| `none` (R1); GA4 emits `page_contains` \| `host` \| `both` \| `none` (R2). The shared schema field accepts the union; each producer documents its own enum. |
| `scope_note` | string | Human-readable scope description + accuracy caveat when approximate |
| `element_instrumentation_state` | `"present"` \| `"partial"` \| `"absent"` | Replaces the silent-skip semantics; always emitted |
| `tracked_elements[]` | list | Each: `name`, `count`, `status` (`live` \| `dark`) |
| `missing_element_classes[]` | list of strings | Element classes expected but not instrumented (drives the ask) |
| `instrumentation_ask` | string \| null | Recommended instrumentation ask when state is `absent`/`partial` |
| `event_liveness[]` | list | Each configured/key event: `event`, `count`, `status` (`live` \| `dead` \| `dark` \| `spiked`) |
| `measurement_integrity_flags[]` | list | Dead bindings + zero-crossings surfaced for the body section |
| `friction_interactions[]` | list | Each: `interaction`, `count`, `ratio_to_baseline` (nullable), `type` |

`element_interactions_available` is retained for back-compat but is no longer a skip signal; `element_instrumentation_state` is authoritative.

Body sections (both SKILL.md): promote element interactions from OPTIONAL to **REQUIRED**, and add a new **REQUIRED** `Measurement Integrity` section. When `element_instrumentation_state` is `absent`, the element section leads with the gap statement + `instrumentation_ask` rather than being skipped. Quality Checks in both SKILL.md extended to enforce both REQUIRED sections, liveness coverage, and the scope note.

### R1: aa-audit (config + `aa_audit.py` + SKILL.md)

**Config (`aa-config.example.json` + `load_config`):**
- Add optional `scope` block: `{ "segment_id": "<id>", "prefixes": ["<substr>"], "prefix_dimension": "variables/entrypage" }`. `prefix_dimension` defaults to `variables/entrypage`; `variables/page` permitted. Either `segment_id` or `prefixes` may be set; `segment_id` takes precedence.
- Replace `dimensions.link_text` with an `interaction_dimensions` array; default `["variables/customlink", "variables/clickmaplink", "variables/clickmappage"]`. Back-compat: when `interaction_dimensions` is absent but legacy `dimensions.link_text` is present, use `[dimensions.link_text]` (preserves the eVar override path).

**`aa_audit.py`:**
- Add `resolve_scope(config) -> (segment_ids, search_prefix)`: `segment_id` to `segment_ids=[id]`; else `prefixes` to a single broad-token `search` clause on `prefix_dimension` (broad single-token only; never multi-token/colon contains). Store resolved values on the `AAClient` (`default_segment_ids`, `default_search`) so `run_report` merges them into every report by default. One change point scopes all 9 reports.
- Add `fetch_element_interactions(client, config, date_range)`: iterate `interaction_dimensions`; per dimension run a scoped report using the broad single-token prefix `search` at an untruncated limit (>= 400 rows); return per-dimension rows. Replaces `fetch_element_clicks` (keeps eVar override via the back-compat array).
- Add `fetch_event_liveness(client, config, date_range)`: count every configured `conversion_events` + `engagement_events` over the window; return `[{event, name, count, status}]` with `status="dead"` when count == 0.
- Comparison block (`main()`): add `element_interactions` and `event_liveness` to the comparison-period fetches; diff against primary to set `status="dark"` (present then 0) and `status="spiked"` (0 then present, or large jump).
- Emit the new structures in the output JSON. Document the broad-prefix search-reliability caveat as a code comment on the enumeration.

**SKILL.md:**
- Note `scope`/`interaction_dimensions` config in Step 1.
- Rework Step 7 into a REQUIRED interpretation of element instrumentation: presence with volumes AND explicit absence assertion (`missing_element_classes`, `instrumentation_ask`).
- Add a Measurement Integrity step interpreting `event_liveness` (dead bindings, dark/spiked) and friction interactions (token match: error/invalid/required/fail/denied + top non-navigation interactions, with ratio to a baseline event when determinable).
- Step 9: bump to `schema_version "2.3"`, add R0 fields, make element-instrumentation + Measurement Integrity REQUIRED body sections, document the search caveat, scope caveat, and confidence cap when scope is approximate.
- Extend Quality Checks per R0.

### R2: ga4-audit (SKILL.md; `ga4_client.py` unchanged)

`ga4_client.py` is a thin proxy; all GA4 query construction is agent-driven in SKILL.md, so no script change is required.

- **Scope:** add a scope input (flag, e.g. `--scope-page-contains <substr>` and/or `--scope-host <host>`) applied as a `dimensionFilter` (on `pagePath`/`hostName`) to every `run_report` request, per the existing "Comparison Rule (applies to ALL run_report calls)" pattern. Unset = whole property as today. Record `scope_applied`/`scope_method`/`scope_note`.
- **Step 3 (liveness):** Step 3a already pulls all events with counts. Add: flag configured/key events returning zero over the window as dead bindings, and with comparison on, flag zero-crossings (dark/spiked). Emit to `event_liveness` / Measurement Integrity.
- **Step 5b (element discovery rework):** include the scoped sub-property page set rather than only Step-4 top pages; enumerate `linkText`/`linkUrl` even when no custom event-scoped params exist (autotrack); add element events to the trend computation (comparison). Remove the Step 5b-4 silent skip: always emit `element_instrumentation_state`, asserting `absent`/`partial` as a finding with `instrumentation_ask`.
- **Friction pass:** rank event names / `linkText` values matching error/invalid/required/fail tokens and surface top non-navigation interactions.
- **Step 10:** bump `schema_version` `"2.2"` to `"2.3"`, add R0 fields, promote section 9 (Element-Level Interactions) from OPTIONAL to REQUIRED, add the REQUIRED Measurement Integrity section.
- Extend the `## Quality Checks` section (line ~822) per R0.

## Verification Design

### Validation

Post-implementation acceptance criteria (derived from Requirements):

1. **AA scope plumbing.** A config with `scope.segment_id` produces every report payload carrying that segment in `globalFilters`; a config with `scope.prefixes` produces every report carrying a single broad-token `search` clause on `prefix_dimension`; a config with no `scope` produces report payloads byte-identical to the pre-change script (golden-payload diff with mocked transport).
2. **AA interaction dimensions.** Default config enumerates `customlink`/`clickmaplink`/`clickmappage`; a config with legacy `dimensions.link_text` and no `interaction_dimensions` still enumerates that single eVar.
3. **AA enumeration method.** Element enumeration issues one scoped query per `interaction_dimensions` entry using a broad single-token prefix `search` at limit >= 400; the search-reliability caveat is present in both the code comment and the SKILL.
4. **Event liveness + regressions.** `event_liveness` is present in output; a configured event with count 0 over the window is `status="dead"`; with comparison on, a present-then-0 event is `status="dark"` and a 0-then-present event is `status="spiked"`.
5. **Required output sections (both skills).** The profile contains a REQUIRED element-instrumentation section and a REQUIRED Measurement Integrity section. When instrumentation is absent, the element section leads with the gap statement and a non-null `instrumentation_ask` (no silent skip).
6. **Schema version + consumer smoke.** Both skills emit `schema_version "2.3"` with the R0 fields; a hypothesis-generator `detect.md` run over a `2.3` profile consumes it without error.
7. **GA4 scope + discovery.** A GA4 scope input applies a `dimensionFilter` to every `run_report`; element discovery includes the scoped page set and enumerates `linkText`/`linkUrl` with no custom params present (autotrack); element events appear in the trend computation.
8. **Backward compatibility.** An unset-scope, default-config run on both skills reproduces pre-change query behavior; the only output delta is the now-always-present element-instrumentation and Measurement Integrity sections, which degrade to explicit "absent" findings.
9. **Quality Checks.** Both SKILL.md Quality Checks enforce the two new REQUIRED sections; the full test suite (`python -m unittest discover _tests/ -v`) is green.

### Evals

Not applicable in this repo. This change is performance-affecting, but a scan confirms the repo has no `_evals/` harness (no `_evals/` directory anywhere). No eval tasks can be matched, and standing up an eval framework is out of scope for this change.

- **Matched tasks:** none (no harness).
- **Coverage analysis / new checks/tasks/fixtures / expected metric direction / graduation plan:** N/A.
- **Deviation + follow-up:** per skill-management eval policy, performance-affecting changes define eval tasks before Build; that presupposes a harness this public repo lacks. Verification for this change rests on `Validation` + `Tests`. Standing up an `_evals/` harness for the skills repo is a candidate backlog item (related to the parked change-capture proposals) for the user to confirm or defer.

### Tests

Script-affecting via `aa_audit.py` only (`ga4_client.py` unchanged; GA4 logic is agent-driven and covered by `Validation`, not unit tests).

- **Affected scripts:** `skills/aa-audit/aa_audit.py` (new `resolve_scope`, `fetch_element_interactions`, `fetch_event_liveness`; scope threading on `AAClient`/`run_report`; comparison-block additions).
- **Coverage analysis:** existing `_tests/unit/test_aa_audit.py` (unittest, importlib module-load) covers only `_coerce_cell`, `_normalize_value`, `parse_report_rows`, `extract_summary`. No coverage for scope resolution, payload scoping, interaction-dimension resolution, element enumeration, or liveness flagging.
- **New test cases/fixtures** (extend `_tests/unit/test_aa_audit.py`, stdlib `unittest`, mock `requests.post`; no network):
  - `resolve_scope`: segment_id to `segment_ids`; prefixes to a single broad-token search clause; empty scope to `(None, None)`.
  - `run_report` payload scoping: with scope, `globalFilters` carries the segment and/or `search` is set; without scope, payload equals the pre-change shape (golden dict).
  - `interaction_dimensions` resolution: default three-dimension list; legacy `dimensions.link_text` fallback to a one-element list.
  - `fetch_element_interactions`: one query per dimension, broad-prefix `search`, limit >= 400; rows parsed.
  - `fetch_event_liveness`: zero-count configured event to `status="dead"`.
  - Regression classification helper: present-then-0 to `"dark"`; 0-then-present to `"spiked"`.
  - Friction token match: values matching error/invalid/required/fail flagged.
- **Expected outcomes:** new cases pass; existing cases unaffected; `python -m unittest discover _tests/ -v` green. New behaviors to catch as regressions: scope leaking into a no-scope run, and the element-enumeration search clause regressing to a narrow multi-token form.

## Verification Results

### Validation Outcomes

All 9 validation criteria confirmed against the implemented change. No unmet or deferred criteria.

- Criterion 1 (AA scope plumbing): `resolve_scope` + `AAClient.default_segment_ids`/`default_search` merge in `run_report`; golden-payload test confirms byte-identical no-scope payload (`test_no_scope_payload_is_golden`). Verified.
- Criterion 2 (AA interaction dimensions): `resolve_interaction_dimensions` default three-dimension list + legacy `link_text` fallback; both tested. Verified.
- Criterion 3 (AA enumeration method): `fetch_element_interactions` runs one query per dimension at `limit=400`, threads broad-token scope search; caveat present in code comment (`aa_audit.py:616-622`) and SKILL Step 7. Verified.
- Criterion 4 (event liveness + regressions): `fetch_event_liveness` flags count==0 as `dead`; `classify_regression` returns `dark`/`spiked`; comparison block wires both. Tested. Verified.
- Criterion 5 (required output sections, both skills): both SKILL.md promote Element-Level Interactions + add Measurement Integrity as REQUIRED, with explicit absence-as-finding. Verified.
- Criterion 6 (schema version + consumer smoke): both skills emit `schema_version "2.3"`; hypothesis-generator `detect.md` consumes a 2.3 profile via `>=` version gates and retained `element_interactions_available`. Static check (no live MCP run); confirmed by reading SKILL Preconditions gates + detect.md equivalence handling. Verified.
- Criterion 7 (GA4 scope + discovery): Scope Rule applies `dimensionFilter` to every `run_report`; Step 5b enumerates scoped page set + autotrack `linkText`/`linkUrl`; element-event trend added to comparison. Verified (SKILL-level, agent-driven, no script).
- Criterion 8 (backward compatibility): unset-scope default config reproduces pre-change query behavior (golden-payload test); only output delta is the now-always-present sections degrading to explicit absence. Verified.
- Criterion 9 (Quality Checks): both SKILL.md Quality Checks enforce the two REQUIRED sections; full suite green (56 passed). Verified.

### Tests Results

| Metric | Value |
|--------|-------|
| Total  | 56    |
| Passed | 56    |
| Failed | 0     |

`python -m unittest discover _tests/ -v`, all pass. 24 cases in `_tests/unit/test_aa_audit.py` cover scope resolution, payload scoping, interaction-dimension resolution, element enumeration, event liveness, regression classification, and script-owned friction token matching (`is_friction_token` + `fetch_element_interactions` row tagging).

## Changelog

| Version | Changes |
|---------|---------|
| 0.8.0 | Closed: QA approved, terminal-gate fresh review CLEAR (independent sensitive-data sweep clean, 56/56 tests, doc reflects code). Moved to `_dev/7-closed/`, status Closed. `[Unreleased]` entries added to `skills/aa-audit/CHANGELOG.md` and a newly-created `skills/ga4-audit/CHANGELOG.md` (closes the missing-changelog gap for that skill), both slug-tagged. `resource_version` stays TBD until release. |
| 0.7.0 | QA fix: resolved the one Needs Attention finding (friction token-match had no production coverage, option a, script-owned). Extracted `FRICTION_TOKENS` + `is_friction_token` into `aa_audit.py`, tagged each `element_interactions` row with a `friction` flag in `fetch_element_interactions`, repointed `TestFrictionTokenMatch` at the production helper, and added a `fetch_element_interactions` friction-tagging test. aa-audit SKILL Step 7b friction pass now consumes the row `friction` flag (single source of truth; removes the duplicated token literal). `## Open Issues` cleared. Full suite green (56/56). |
| 0.6.0 | QA: Build to QA move (status, version, status_note). Document-management full-document review of both SKILL.md files, schema reference copy, and change doc; code review of `aa_audit.py` + `test_aa_audit.py`; sampling validation of `aa-config.example.json`. Ready-to-Fix: R0 `scope_method` redefined as an open string documenting the AA/GA4 union (resolves the seeded R0-vs-schema/R2 drift). One Needs Attention finding persisted to `## Open Issues` (friction token-match has no production-code coverage). Full suite green (54/54). All 9 validation criteria confirmed. Client-free re-scan clean. |
| 0.5.0 | Build: Design to Build move (status, version, status_note). Implemented R0 (schema reference copy bumped to 2.3 with new scope/element-instrumentation/event-liveness/friction fields), R1 (aa-config.example.json `scope` block + `interaction_dimensions`; `aa_audit.py` `resolve_scope`, `AAClient` default scope merge in `run_report`, `fetch_element_interactions`, `fetch_event_liveness`, `classify_regression` helper, comparison-block + output additions; aa-audit SKILL.md Step 1 config note, reworked Step 7, new Measurement Integrity step, Step 9 schema 2.3 + REQUIRED sections, Quality Checks), and R2 (ga4-audit SKILL.md scope flags + dimensionFilter, Step 3 liveness, Step 5b rework removing silent skip, friction pass, Step 10 schema 2.3 + REQUIRED sections, Quality Checks). Authored 7 new test groups in `_tests/unit/test_aa_audit.py`; full suite green. |
| 0.4.0 | Design: Backlog to Design move (status, version, status_note); authored `Requirements` (R0 shared schema_version 2.3 + new frontmatter fields, R1 aa-audit config/script/SKILL, R2 ga4-audit SKILL with ga4_client unchanged) and `Verification Design` (9 Validation criteria; Evals recorded N/A with rationale, no `_evals/` harness in repo; Tests scoped to `aa_audit.py` with per-case plan). |
| 0.3.0 | Discovery approach finalized: all six Approach OQs resolved (option 2, apply all recommendations) and integrated into a three-layer `Approach` with locked decisions; `## Open Issues` removed; `Alternatives Considered` added (combined-vs-split, scope mechanism); `status_note` updated. Scores re-evaluated, no shift. |
| 0.2.0 | Backlog to Discovery transition: status set to Discovery, `Approach > Change Profile` authored (script-affecting, performance-affecting, test-eval-only flags), `status_note` set. All client-identifying and sensitive content genericized for the public repo; em dashes removed. |
| 0.1.0 | Initial backlog change document: capture element-interaction state, missing-instrumentation findings, measurement-integrity regressions, friction interactions, sub-property scoping, and scoped new-vs-returning/engagement depth by default in both audit skills. Root causes verified against working-repo source; six Approach OQs seeded. |
