---
fe-managed: true
name: positioning-framework-kb-native-writes
description: >
  Adapt positioning-framework to write KB-native artifacts (bronze + silver, with full KB
  frontmatter) directly into a client's medallion docs KB when a KB binding is detected,
  while preserving the legacy .claude/context/ behavior for non-KB clients. First Path B
  skill adaptation; the pilot client engagement is the first consumer.
governed_by: change-management/change-document
status: Discovery
resource_name: positioning-framework
resource_version: "TBD"
impact: 4
confidence: 4
ease: 2
initiative: cro-kb-path-b
version: "0.3.0"
created: 2026-06-03
updated: 2026-06-03
---

# positioning-framework KB-Native Writes (Path B)

## Background

FunnelEnvy CRO skills predate the fe-knowledge-base medallion KB model. `positioning-framework`
writes L0/L1 context to hardcoded `.claude/context/` paths and treats research byproducts
(`_research-extractions.md`, `_fetch-registry.md`) as overwritable scratch. The Path B initiative
retargets that I/O into a client's medallion KB so CRO output lands governed and typed.

Phase 0 closed in the pilot client engagement repo (private): a repo-local KB type skill defines
11 CRO artifact types with `field_definitions`, content layouts, and per-type `Transformation`
sections carrying output paths. The client docs KB is bound to that type, and empty CRO scope
directories exist (`captures/{research-extractions,fetch-registries,company-facts}/`,
`reference/cro-{scope}/`, `deliverables/`, `battle-cards/`). The engagement defines two scopes;
one runs first.

The canonical adaptation spec is an internal Path B skill-adaptation reference (private repo). It
rates this repo's adaptation low-effort with zero rename risk (paths are scope-agnostic) and
defines per-skill required changes. This change covers **positioning-framework only** — the first
of four skills, establishing the pattern the others will follow.

## Current State

- `positioning-framework` v1.0.0: orchestration hub (`skills/positioning-framework/SKILL.md`,
  ~840 lines) + `agent-header.md` + 5 phase files (`research`, `company`, `competitive`,
  `messaging`, `scoring`). Up to 4 sequential Opus agents by depth.
- 51 hardcoded `.claude/context/` / `.claude/deliverables/` references across the skill files.
- Outputs today: `company-identity.md` (L0), `competitive-landscape.md`, `audience-messaging.md`,
  `positioning-scorecard.md` (L1), plus operational `_research-extractions.md` and
  `_fetch-registry.md` (ephemeral, overwritten each run).
- Prior-work detection globs `.claude/context/` and reads frontmatter; extending skills raise
  confidence, mark extended sections.
- Target artifact types (authoritative defs live in the client repo's KB type skill under
  `.claude/skills/{kb-type}/artifacts/`): `bronze-company-facts`, `bronze-research-extraction`,
  `bronze-fetch-registry`, `silver-strategy-context`, `silver-competitive-analysis`,
  `silver-audience-analysis`, `silver-positioning-scorecard` (4 remaining types belong to the
  other three skills' later adaptations).

## Approach

### Mode Resolution (Pre-Flight)

A new orchestrator pre-flight step, slotted with the existing flag parsing (SKILL.md:433), runs
once before any agent launches:

1. Parse the working repo's CLAUDE.md `Knowledge Bases` section for KB root and type skill name.
2. Verify the type skill resolves repo-local (`.claude/skills/{kb-type}/`) and defines the 7 CRO
   artifact types in `artifacts/`.
3. If both hold and `--no-kb` is absent: **KB mode**. Require `--scope <slug>`; hard-stop with the
   type skill's valid scope list if missing. Otherwise: **legacy mode**, byte-identical behavior
   to v1.0.0. There is deliberately no `--kb` force flag: when detection fails, the skill falls
   back to legacy and tells the user which check failed, keeping a broken KB binding loud instead
   of writing typed artifacts into a half-configured KB.
4. Thread the mode as a parameter block in every agent launch prompt (after the existing `depth:`
   line): `kb_mode`, `kb_root`, `kb_type`, `scope`, plus the artifact type def paths the agent
   needs. This reuses the existing parameter-threading mechanism (depth line, GA4 payload,
   business brief).

Nothing about agent count, ordering, depth gating, research instructions, or analysis quality
rules changes. Only read/write targets and output document shape branch on mode.

### Schema Authority in KB Mode

Phase files keep their inline schemas as the authority for analytical content. In KB mode, the
client's artifact type defs (`.claude/skills/{kb-type}/artifacts/{type}.md`) are the authority for
output path, frontmatter contract, and body section layout. Agents read the relevant type def at
execution time, the same pattern as phase-file inline schemas. `governed_by` is composed at
runtime as `{kb-type}/{artifact-type}` — the skill never hardcodes a client type-skill name.

### Output Mapping (KB Mode)

| Legacy output | KB artifact (type) | Path | depends_on |
|---|---|---|---|
| `company-identity.md` (facts ~60%) | `bronze-company-facts` | `captures/company-facts/{scope}-company-facts.md` | — |
| `company-identity.md` (analysis ~40%) | `silver-strategy-context` | `reference/cro-{scope}/strategy-context.md` | bronze-company-facts |
| `_research-extractions.md` | `bronze-research-extraction` | `captures/research-extractions/{scope}-research-extractions.md` | — |
| `_fetch-registry.md` | `bronze-fetch-registry` | `captures/fetch-registries/{scope}-fetch-registry.md` | — |
| `competitive-landscape.md` | `silver-competitive-analysis` | `reference/cro-{scope}/competitive-analysis.md` | bronze-company-facts, bronze-research-extraction |
| `audience-messaging.md` | `silver-audience-analysis` | `reference/cro-{scope}/audience-analysis.md` | silver-strategy-context |
| `positioning-scorecard.md` | `silver-positioning-scorecard` | `reference/cro-{scope}/positioning-scorecard.md` | silver-competitive-analysis, silver-audience-analysis |

Research byproducts become first-class bronze: written once by Agent 1, appended by Agent 2
(fetch registry), never treated as ephemeral scratch in KB mode.

**L0 split section mapping** (company-identity body → two artifacts):

| company-identity section | Destination | Notes |
|---|---|---|
| Company Overview | bronze: `Company Overview` | |
| Services & Capabilities | bronze: `Product Catalog` | Service Exclusions folded in as subsection |
| Company Stats | bronze: `Key Statistics` | |
| Glossary | bronze: `Glossary` | |
| Constraints | bronze: `Constraints` | |
| Homepage Messaging | bronze: `Homepage Messaging` | verbatim |
| Proof Point Registry | bronze: additional section | factual proof; IDs stay immutable |
| Pricing Model | bronze: additional section | facts |
| Target Segments | silver: `Target Segments` | Anti-Personas folded in as subsection |
| Stated Differentiators | silver: `Differentiators` | proof references point at bronze registry |
| Buying Triggers | silver: `Buying Triggers` | |
| Category Gap | silver: `Category Gap` | |
| Retired Positioning | silver: additional section | analysis |

Sections beyond a type def's REQUIRED list are valid — `kb_type_validate.py` checks required
section presence and frontmatter `field_definitions`, not unknown extras. Frontmatter blocks
split the same way: `company` block (incl. `ga4_property`) stays on bronze; `category` and
`target_market` summaries move to silver.

In KB mode, downstream agents (2-4) that today read `company-identity.md` read BOTH
`bronze-company-facts` and `silver-strategy-context`.

### KB Frontmatter Contract

Every artifact carries: `fe-managed: true`, `name`, `description`, `kb_layer` (value-locked per
type), `governed_by: {kb-type}/{artifact-type}`, `scope`, `generated_by: positioning-framework`,
`tags` (3-7 semantic), `version`, `created`, `updated`. Silver additionally: `data_provenance`
(`public` when all source material is public web research; `client` when client-provided input
such as a business brief, intake answers, or client docs materially shaped the artifact, mirroring
`provenance.has_client_input`; assessed per artifact, not per run), `depends_on` (per Output
Mapping), `confidence` (1-5, same mechanics as legacy). Extension
metadata the legacy schema carries (depth, provenance block, extension markers) rides along as
additional fields — permitted by the validator.

### Prior-Work Detection (KB Mode)

Glob `{kb_root}/reference/cro-{scope}/*.md` + the three scoped captures paths, filter by
frontmatter `governed_by` + `scope`, then apply the existing confidence/depth extend-vs-skip rules
unchanged. Legacy `.claude/context/` globbing is untouched in legacy mode. KB artifacts from a
different scope are never read or extended — scope isolation is absolute. One semantic shift: in
KB mode the research byproducts ARE prior work (first-class bronze) — a re-run at higher depth
extends the fetch registry rather than overwriting it. In legacy mode they remain ephemeral.

### Post-Write Validation Gate

After each agent writes its artifacts in KB mode, the orchestrator runs
`kb_type_validate.py validate` (fe-knowledge-base plugin script, runs standalone via python3) on
the new files and fixes validation errors before launching the next agent. This makes the
acceptance criterion a built-in quality gate rather than a post-hoc check.

### Scope Boundaries

- **render-default-deliverables auto-invoke is skipped in KB mode** (it is not yet Path B
  adapted); the orchestrator tells the user gold rendering arrives with that skill's adaptation.
- Downstream repo skills (`ga4-audit`, `hypothesis-generator`) still read `.claude/context/`;
  their KB adaptations are separate change docs per the Path B spec.
- L0 bootstrap protocol (consuming-skill stub creation) is untouched — it serves legacy mode.

### Evals

No `_evals/` infrastructure exists in this repo; no matched eval tasks. Behavioral validation is
the live first-client run defined in `Validation`.

## Requirements

Stub — filled during Design after Approach approval.

## Validation

Stub — to include at minimum the acceptance criteria for the first run, executed from the pilot
client repo (results documented privately there):

- `/positioning-framework` in KB mode writes bronze + silver artifacts into the client KB at the
  type-defined paths for the requested scope
- `kb_type_validate.py validate` passes on every new artifact
- `kb_graph.py health` shows correct `depends_on` edges (per the Output Mapping graph, no
  layer-inverted edges)
- Zero files land in `.claude/context/`
- Legacy mode regression: a non-KB invocation still writes `.claude/context/` exactly as v1.0.0

## Changelog

| Version | Changes |
|---|---|
| 0.3.0 | Discovery: all 6 Open Issues resolved with user (decisions integrated into Approach); client references sanitized for public repo |
| 0.2.0 | Discovery: research-informed Approach (mode resolution, schema authority, output + L0 split mapping tables, validation gate, scope boundaries); Open Issues recommendations sharpened, OQ 5 (render skip) and OQ 6 (data_provenance) added |
| 0.1.0 | Initial backlog creation from Path B handoff |
