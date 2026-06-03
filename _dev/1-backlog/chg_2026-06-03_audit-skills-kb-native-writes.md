---
fe-managed: true
name: audit-skills-kb-native-writes
description: >
  Extend the dual-mode KB-native output pattern from positioning-framework v1.1.0 to the two
  audit skills (ga4-audit, aa-audit): when the working repo declares a CRO knowledge base
  binding, write the performance profile as a typed silver-performance-analysis artifact at its
  type-defined path instead of .claude/context/performance-profile.md.
governed_by: change-management/change-document
status: Backlog
resource_name: [ga4-audit, aa-audit]
resource_version: "TBD"
impact: 4
confidence: 4
ease: 3
initiative: cro-kb-path-b
version: "0.1.0"
created: 2026-06-03
updated: 2026-06-03
---
# Audit Skills KB-Native Writes

## Background

positioning-framework v1.1.0 shipped dual-mode output (chg_2026-06-03_positioning-framework-kb-native-writes), validated by a first KB-native pilot run on 2026-06-03. During that pilot, an aa-audit run was needed mid-flow and its output was manually written as a `silver-performance-analysis` KB artifact instead of the legacy `.claude/context/performance-profile.md` — proving the adaptation pattern for the audit skills with zero schema friction. The KB type's artifact definition (5 H2 sections) absorbed the aa-audit 8-section interpretation content cleanly.

## Current State

- ga4-audit and aa-audit both write `.claude/context/performance-profile.md` (shared schema).
- The positioning-framework KB-mode machinery (mode resolution from the working repo CLAUDE.md, `--scope`/`--no-kb` flags, KB frontmatter contract, post-write validation via kb_type_validate.py) is authored per-skill, not shared.
- Pilot learning: the audit skills are single-agent, so the adaptation is smaller than positioning-framework's — one output mapping row (`performance-profile.md` → `silver-performance-analysis` at `reference/cro-{scope}/performance-analysis.md`), no multi-agent parameter threading.
- Pilot learning: `depends_on` is required by the silver type but audit data is query-time (no bronze source artifact exists); the pilot used a same-layer edge to the analytics reference doc. The adaptation needs a documented `depends_on` policy for this case (same-layer reference vs bronze data-export capture).

## Approach

Mirror the positioning-framework KB Mode section in both audit skills: pre-flight mode resolution, `--scope` requirement, type-def-driven output path/frontmatter/layout, post-write validation gate. Extract or restate the shared mode-resolution procedure consistently. Resolve the `depends_on` policy for query-time data as part of Design.

## Requirements

Stub — filled during Design.

## Validation

Stub — filled during Design. Must include a KB-native audit run whose artifact passes kb_type_validate.py and lands zero files in .claude/context/.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document — extend KB-native writes to the audit skills; pattern proven manually during the 2026-06-03 pilot. |
