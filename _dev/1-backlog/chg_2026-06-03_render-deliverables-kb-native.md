---
fe-managed: true
name: render-deliverables-kb-native
description: >
  Extend the dual-mode KB-native pattern to render-default-deliverables: read the scope's silver
  positioning artifacts from a bound CRO knowledge base and write gold-strategy-deliverable and
  gold-battle-card artifacts at their type-defined paths. Re-enables the positioning-framework
  auto-invoke that KB mode currently skips.
governed_by: change-management/change-document
status: Backlog
resource_name: render-default-deliverables
resource_version: "TBD"
impact: 3
confidence: 4
ease: 3
initiative: cro-kb-path-b
version: "0.1.0"
created: 2026-06-03
updated: 2026-06-03
---
# Render Default Deliverables KB-Native I/O

## Background

positioning-framework v1.1.0's KB mode skips the render-default-deliverables auto-invoke because this skill still reads/writes legacy paths — the KB Mode Completion Message tells users gold-layer rendering arrives with this adaptation (chg_2026-06-03_positioning-framework-kb-native-writes). The 2026-06-03 pilot produced a complete silver layer whose post-write reviews repeatedly flagged "no gold consumer exists" as the open upward-propagation step.

## Current State

- render-default-deliverables reads `.claude/context/*.md` and writes `.claude/deliverables/`.
- The bound KB type defines `gold-strategy-deliverable` (`deliverables/{scope}-…`, tagged with `deliverable_type`) and `gold-battle-card` (`battle-cards/{scope}-{competitor}`).
- Pilot learning: competitive-analysis artifacts carry inline per-competitor battle-card data and proof IDs — composition-ready for per-competitor gold battle cards.

## Approach

Add KB mode: mode resolution, `--scope`, read the scope's silver artifacts via frontmatter glob, render each deliverable as its gold artifact type with `depends_on` to the silver sources composed. Restore the positioning-framework auto-invoke in KB mode once shipped (small follow-up edit to positioning-framework's KB Mode section).

## Requirements

Stub — filled during Design.

## Validation

Stub — filled during Design. Must include a KB-native render pass producing at least one gold-strategy-deliverable and one gold-battle-card that pass kb_type_validate.py with silver→gold depends_on edges.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document — gold-layer rendering for the Path B chain; unblocks the KB-mode auto-invoke skip. |
