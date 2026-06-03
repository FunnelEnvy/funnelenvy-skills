---
fe-managed: true
name: hypothesis-generator-kb-native
description: >
  Extend the dual-mode KB-native pattern to hypothesis-generator: read silver positioning/
  performance artifacts from a bound CRO knowledge base instead of .claude/context/ files, and
  write the experiment roadmap as a typed gold-experiment-roadmap artifact. First skill in the
  Path B chain to exercise the KB read side and a gold-layer write.
governed_by: change-management/change-document
status: QA
resource_name: hypothesis-generator
resource_version: "TBD"
impact: 4
confidence: 4
ease: 3
initiative: cro-kb-path-b
version: "0.5.0"
created: 2026-06-03
updated: 2026-06-03
---
# Hypothesis Generator KB-Native I/O

## Background

positioning-framework v1.1.0 writes the silver layer KB-natively ([chg_2026-06-03_positioning-framework-kb-native-writes](../7-closed/chg_2026-06-03_positioning-framework-kb-native-writes.md), pilot-validated 2026-06-03). hypothesis-generator is the next consumer in the CRO chain: it reads L0/L1 context and produces the prioritized experiment roadmap. In KB terms it reads the scope's silver artifacts and composes the first gold artifact (`gold-experiment-roadmap`) — the medallion upward-propagation step the pilot deliberately deferred ("no gold consumer exists yet" was a tracked finding of the pilot's post-write reviews).

## Current State

- hypothesis-generator (v1.5.0) reads `.claude/context/*.md` (L0 + L1 + performance-profile) and writes to `.claude/deliverables/experiment-roadmap.md`. No KB awareness.
- The KB silver layer for a piloted scope now exists in a client repo (strategy-context, competitive-analysis, audience-analysis, positioning-scorecard, performance-analysis) with declared `depends_on` edges.
- The bound KB type defines `gold-experiment-roadmap` with output path `deliverables/{scope}-experiment-roadmap.md` and `field_definitions`.
- The piloted scope's performance artifact is aa-audit-generated: no `schema_version` frontmatter, and its body structure differs from the ga4-audit v2.x performance-profile schema that gates 12 of [detect.md](../../skills/hypothesis-generator/phases/detect.md)'s Step 1c performance-driven triggers.

## Approach

Add a `KB Mode (Dual-Mode Output)` section to hypothesis-generator mirroring [positioning-framework's](../../skills/positioning-framework/SKILL.md), adapted for a single-agent, read-side skill producing the first gold write. Only read/write targets, the addition of gold frontmatter, and performance-profile schema tolerance change; all analysis behavior (Phases 2–4 reasoning, ICE scoring, pattern library, spec intake, `--max`, contrarian triggers) is identical in both modes. Bounded "In KB mode:" blocks only — legacy instructions are never rewritten.

### Mode resolution

Resolved once in Phase 1 step 0 (before context loading), mirroring positioning-framework's procedure:

1. `--no-kb` set → legacy mode.
2. Working repo `CLAUDE.md` must have a `Knowledge Bases` section; absent → legacy mode with a notice.
3. The declared KB type skill must exist and its `artifacts/` must define `gold-experiment-roadmap`, `silver-strategy-context`, and `bronze-company-facts` (the output type plus the two types backing the hard L0 precondition). Any missing → legacy mode, reporting which check failed. Optional silver types/instances are graceful degradation, never a mode-resolution failure — a missing optional silver artifact is treated identically to a missing optional legacy context file.
4. `--scope <slug>` must match a valid scope defined by the type skill; missing or invalid → HARD STOP listing valid scopes. No scope guessing.

No `--kb` force flag; failed detection falls back to legacy loudly. Because the skill is single-agent, resolved KB state (kb_root, kb_type, scope, type-def paths) is held in-session — positioning's per-agent KB Parameter Block threading is not needed.

### Read-side mapping

In KB mode, Phase 1 replaces the `.claude/context/*.md` glob with reads of the scope's artifacts:

| Legacy context file | KB artifact type | Path under KB root | Required |
|---|---|---|---|
| `company-identity.md` | `bronze-company-facts` + `silver-strategy-context` | `captures/company-facts/{scope}-company-facts.md` + `reference/cro-{scope}/strategy-context.md` | REQUIRED |
| `positioning-scorecard.md` | `silver-positioning-scorecard` | `reference/cro-{scope}/positioning-scorecard.md` | optional |
| `competitive-landscape.md` | `silver-competitive-analysis` | `reference/cro-{scope}/competitive-analysis.md` | optional |
| `audience-messaging.md` | `silver-audience-analysis` | `reference/cro-{scope}/audience-analysis.md` | optional |
| `performance-profile.md` | `silver-performance-analysis` | `reference/cro-{scope}/performance-analysis.md` | optional |
| `_fetch-registry.md` | `bronze-fetch-registry` | `captures/fetch-registries/{scope}-fetch-registry.md` | optional (page-block check only) |

- L0 precondition: the lower of `bronze-company-facts.confidence` and `silver-strategy-context.confidence` must be ≥ 3 (positioning's two-artifact rule). Existing error states reworded for KB artifacts ("No silver CRO artifacts found for scope {scope}. Run /positioning-framework --scope {scope} first.").
- Scope isolation is absolute: artifacts from another scope are never read.
- Prior work detection: glob `deliverables/{scope}-experiment-roadmap.md`; if present, the run supersedes it in place (below).

### Performance-profile schema equivalence

detect.md Step 1c trigger conditions are written against ga4-audit v2.0/v2.1 field names. Profiles produced by other audit skills (e.g., aa-audit) may carry equivalent data under different structure and no `schema_version`. New rule in Step 1c:

- When the profile carries `schema_version`, the existing version gate applies unchanged.
- When `schema_version` is absent, bypass the version gate and evaluate each trigger by **content equivalence**: if the profile body carries semantically equivalent data (e.g., a pre-sized opportunity table with impact buckets ↔ `top_opportunities.estimated_monthly_impact`; period-delta trend tables ↔ `trends.*`; a page-level traffic/bounce table ↔ page sessions/bounce conditions), the trigger fires against that content. Triggers whose data has no equivalent in the profile self-gate off, exactly as absent fields do today.

This keeps trigger logic unchanged while making Step 1c schema-tolerant. No client-specific references; the equivalence table names profile content shapes, not clients.

### Output

Single gold artifact at `deliverables/{scope}-experiment-roadmap.md`, replacing `.claude/deliverables/experiment-roadmap.md`:

- **Frontmatter** (the sole exception to the deliverable's no-frontmatter rule): `fe-managed: true`, `name: {scope}-experiment-roadmap`, `description`, `kb_layer: gold`, `governed_by: {kb-type}/gold-experiment-roadmap` (composed at runtime — this skill never hardcodes a KB type skill name or client path), `scope`, `data_provenance` (`client` if any consumed silver is client-provenance, else `public`), `generated_by: hypothesis-generator`, `depends_on`, `tags` (3–7 semantic), `version`, `created`, `updated`.
- **`depends_on`**: gold→silver only — KB-root-relative paths of the silver artifacts actually consumed, omitting missing optional ones. Bronze inputs are excluded: company facts flow transitively through strategy-context's existing bronze edge, and the fetch registry is an operational read (page-block status), not a content-composition source.
- **Body**: the full legacy 9-section render, unchanged. The Deliverable Purity Constraint still applies to the body in both modes (no pattern IDs, no system terms). The bound type def's Content Layout is the authority for required sections; the client-side type def is being updated to describe this render (tracked in the client repo's change management).
- **Re-run semantics**: supersede in place — preserve `created`, bump `version` (minor when inputs changed materially, patch for a re-render of the same inputs), set `updated`, overwrite the body. No merge: a roadmap is a complete projection of current context, matching legacy re-render behavior.
- **Post-write validation gate**: run kb-start's `kb_type_validate.py validate` on the written artifact (probe-then-run python resolution); fix and re-validate on errors; if the script cannot be resolved, warn, continue, and flag manual validation in the completion message.
- **Completion message**: KB-mode variant reporting artifact path, type, scope, version, `depends_on`, standard tier/pattern counts, and validation status.

## Alternatives Considered

- **Conservative `schema_version` floor (absent → "1.0", v2.x triggers skipped).** Rejected by the user in favor of content-equivalence evaluation: the piloted scope's aa-audit profile carries real opportunity-sizing, trend, and page-performance data that would be silently ignored, materially reducing performance-driven coverage in the first gold pilot.
- **Restructuring the KB-mode render under the type def's 3 H2s (Roadmap Summary / Hypotheses / Pattern Coverage).** Rejected: collapsing the Quick Wins / Strategic Bets / Explorations tiers degrades the stakeholder-facing deliverable and loses the tier ordering signal. The type def is the editable surface; it gets updated client-side to describe the proven 9-section render.

## Requirements

All edits are additive bounded "In KB mode:" blocks or new sections; legacy instruction text is never rewritten. No version bumps during Build (release-time per change-management).

### R1 — `skills/hypothesis-generator/SKILL.md`

1. **Frontmatter `description`**: add the dual-mode note (reads a bound CRO KB's silver artifacts and writes a typed gold-experiment-roadmap when a KB binding is detected; legacy `.claude/context/` behavior otherwise).
2. **Flags table** (`Invocation`): add `--scope <slug>` (KB mode only; required in KB mode; warn-and-ignore in legacy mode) and `--no-kb` (force legacy output) rows.
3. **New `## KB Mode (Dual-Mode Output)` section** between `Invocation` and `Preconditions`, containing: mode statement (only read/write targets, gold frontmatter, and performance-profile schema tolerance change; Phases 2–4 analysis identical); `Mode Resolution Procedure` (the four steps from the Approach, run as Phase 1 step 0); `KB State` (single-agent: resolved once, held in-session); `Schema Authority` (the bound type def's `gold-experiment-roadmap` definition is the authority for output path, frontmatter contract, and required section layout; `governed_by` composed at runtime; this skill never hardcodes a KB type skill name or client path); `Read-side Mapping` table (per the Approach); `Output Mapping` and `KB Frontmatter Contract` (per the Approach, including the gold→silver `depends_on` rule); `Prior Work Detection (KB Mode)` (scope-isolated artifact reads; existing gold artifact triggers supersede-in-place); `Post-Write Validation Gate` (`kb_type_validate.py`, probe-then-run interpreter resolution, warn-and-continue if unresolvable); `KB Mode Completion Message`.
4. **`Preconditions`**: bounded KB-mode subsection — hard requirement restated as the two-artifact lowest-confidence ≥ 3 rule; soft requirements mapped to optional silver artifacts (identical degradation semantics); the `schema_version` block gains a pointer to the detect.md content-equivalence rule for profiles lacking `schema_version`; error states reworded for KB artifacts.
5. **`Phase 1: Context Discovery and Loading`**: step 0 mode resolution insertion; KB-mode branch of the step 1 glob (replaced by KB-mode prior work detection); handoff check branches — page-block status from the scoped `bronze-fetch-registry` path, external-deliverables check against `{kb_root}/deliverables/{scope}-experiment-roadmap.md`; pre-flight summary lists KB artifact paths in KB mode.
6. **`Phase 5: Render` → `Step 5b`**: KB-mode write target `{kb_root}/deliverables/{scope}-experiment-roadmap.md`; gold frontmatter prepend; supersede-in-place re-run rule; post-write validation gate invocation; KB-mode completion message variant.
7. **`Output Format`**: note that in KB mode the same body renders to the KB path with the frontmatter block prepended.
8. **`Deliverable Purity Constraint`**: one sentence — the required gold frontmatter block is the sole KB-mode exception; the body remains free of all prohibited terms in both modes.
9. **`Re-render Behavior`**: KB-mode paragraph documenting supersede-in-place (preserve `created`, bump `version` minor/patch by input materiality, set `updated`, overwrite body, no merge).

### R2 — `skills/hypothesis-generator/phases/detect.md`

1. **`Step 1c: Performance-Driven Triggers`**: new `Profile Schema Equivalence` subsection — version gate unchanged when `schema_version` present; when absent, evaluate triggers by content equivalence (pre-sized opportunity tables with impact buckets ↔ `top_opportunities.estimated_monthly_impact`; period-delta trend tables ↔ `trends.*`; page-level traffic/bounce tables ↔ page sessions/bounce conditions); triggers without equivalent content self-gate off.
2. **`Required Inputs` / `Graceful Degradation`**: one-line note that in KB mode the orchestrator supplies the same context bodies sourced from the scope's silver artifacts; trigger logic unchanged.

### R3 — repo `README.md` and `CLAUDE.md`

hypothesis-generator descriptions gain the dual-mode KB-native note. No version table changes (release-time).

### R4 — `skills/hypothesis-generator/CHANGELOG.md` (new)

Create with an `[Unreleased]` entry describing dual-mode KB-native I/O, mirroring positioning-framework's CHANGELOG pattern.

### R5 — change document

Kept in sync with actual Build deltas.

## Validation

Static (this change, pre-merge):

1. **Legacy regression**: diff inspection confirms every change is an additive bounded block or new section; no legacy instruction path is altered. A repo without a `Knowledge Bases` CLAUDE.md section resolves to legacy mode.
2. **Public-repo sweep**: `git diff main..HEAD` greps clean (case-insensitive) for client identifiers; all examples use `{kb-type}`, `{scope}`, generic `docs/`.
3. **document-management review** findings-clean on all changed/created markdown; `link_audit.py` clean.

Pilot (post-merge acceptance gate, deferred to a bound-KB client repo session):

4. A KB-native run (`/hypothesis-generator --scope <slug>`) produces a gold-experiment-roadmap at the type-defined path that passes `kb_type_validate.py`, with `depends_on` listing exactly the silver artifacts consumed (gold→silver only), zero writes to `.claude/context/` or `.claude/deliverables/`, body free of prohibited terms, and absolute scope isolation.
5. Performance-driven triggers fire via content equivalence against a `schema_version`-less profile (the piloted scope's artifact), with the completion summary reporting performance-driven opportunity counts > 0 given the profile carries sized opportunities and trends.

## Changelog

| Version | Changes |
|---------|---------|
| 0.5.0 | QA — public-repo sweep clean, additive-diff legacy regression verified (all modified lines preserve original text verbatim), link audits and frontmatter validation clean after fixing one stale lifecycle-move link in the aa-audit conformance backlog doc. |
| 0.4.0 | Build — R1-R4 implemented as designed: SKILL.md KB Mode section + bounded branches at every legacy I/O touchpoint, detect.md Profile Schema Equivalence subsection + KB sourcing note, README/CLAUDE.md dual-mode descriptions, skill CHANGELOG.md created with [Unreleased] entry. No deviations from Requirements. |
| 0.3.0 | Design — Requirements filled (R1 SKILL.md KB Mode section + bounded branches, R2 detect.md Profile Schema Equivalence, R3 repo doc descriptions, R4 skill CHANGELOG creation, R5 doc sync); Validation filled (3 static checks pre-merge, 2 pilot acceptance checks post-merge). |
| 0.2.0 | Discovery — Approach filled: dual-mode KB I/O mirroring positioning-framework adapted for single-agent read-side + first gold write; mode resolution gate (output type + L0-backing types); read-side mapping table; performance-profile content-equivalence rule for Step 1c; gold output contract (frontmatter, gold→silver depends_on, 9-section render, supersede-in-place re-runs, post-write validation). Alternatives recorded. |
| 0.1.0 | Initial backlog change document — KB-native read side + first gold-layer write for the Path B chain. |
