---
fe-managed: true
name: hypothesis-generator-kb-native
description: >
  Extend the dual-mode KB-native pattern to hypothesis-generator: read silver positioning/
  performance artifacts from a bound CRO knowledge base instead of .claude/context/ files, and
  write the experiment roadmap as a typed gold-experiment-roadmap artifact. First skill in the
  Path B chain to exercise the KB read side and a gold-layer write.
governed_by: change-management/change-document
status: Backlog
resource_name: hypothesis-generator
resource_version: "TBD"
impact: 4
confidence: 4
ease: 3
initiative: cro-kb-path-b
version: "0.1.0"
created: 2026-06-03
updated: 2026-06-03
---
# Hypothesis Generator KB-Native I/O

## Background

positioning-framework v1.1.0 writes the silver layer KB-natively (chg_2026-06-03_positioning-framework-kb-native-writes, pilot-validated 2026-06-03). hypothesis-generator is the next consumer in the CRO chain: it reads L0/L1 context and produces the prioritized experiment roadmap. In KB terms it reads the scope's silver artifacts and composes the first gold artifact (`gold-experiment-roadmap`) — the medallion upward-propagation step the pilot deliberately deferred ("no gold consumer exists yet" was a tracked finding of the pilot's post-write reviews).

## Current State

- hypothesis-generator reads `.claude/context/*.md` (L0 + L1 + performance-profile) and writes to `.claude/deliverables/`.
- The KB silver layer for a piloted scope now exists in a client repo (strategy-context, competitive-analysis, audience-analysis, positioning-scorecard, performance-analysis) with declared `depends_on` edges.
- The bound KB type defines `gold-experiment-roadmap` with output path `deliverables/{scope}-…` and `field_definitions`.

## Approach

Add KB mode mirroring positioning-framework's: mode resolution, `--scope`, prior-work detection via frontmatter glob over the scope's silver artifacts, gold artifact output per the type def with `depends_on` to the silver sources it composes from. Read-side mapping replaces the `.claude/context/` glob.

## Requirements

Stub — filled during Design.

## Validation

Stub — filled during Design. Must include a KB-native run producing a gold-experiment-roadmap that passes kb_type_validate.py with correct silver→gold depends_on edges and zero legacy-path writes.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document — KB-native read side + first gold-layer write for the Path B chain. |
