---
fe-managed: true
name: positioning-modules-path-resolution
description: >
  positioning-framework phase files reference modules/ documents (web-extract, competitive-
  assessment, voc-extraction, reddit-research, business-brief) by repo-root-relative path. Agents
  launched with skill-dir or external working directories cannot resolve them and silently
  improvise from inline phase content. Make module references resolvable in every launch context.
governed_by: change-management/change-document
status: Backlog
resource_name: positioning-framework
resource_version: "TBD"
impact: 3
confidence: 4
ease: 4
version: "0.1.0"
created: 2026-06-03
updated: 2026-06-03
---
# Positioning Framework Modules Path Resolution

## Background

During the 2026-06-03 KB-native pilot, both research agents reported the `modules/` documents referenced by `phases/competitive.md` and SKILL.md (`modules/web-extract.md`, `modules/competitive-assessment.md`, `modules/voc-extraction.md`, `modules/reddit-research.md`, `modules/business-brief.md`) as missing and improvised from inline phase content. The modules exist — at the repo root, not under `skills/positioning-framework/` — so relative references only resolve when the reader's working directory happens to be the repo root. Subagents launched with absolute skill-dir paths, or running in a different working repo (the KB-native deployment model), cannot resolve them. The quality loss is silent: agents proceed without the claim-assessment framework, extraction-pipeline detail, and VOC protocol.

## Current State

- `modules/` lives at the repo root and ships with the plugin (`source: "./"`), so cache copies do contain it — the defect is reference resolution, not packaging.
- Phase files reference `modules/...` with no anchor; agent launch prompts (SKILL.md examples) list only agent-header.md and phase files.
- Several modules are shared by other skills (hypothesis-generator, landing-page-generator), so moving them under one skill is not obviously correct.

## Approach

Candidates for Design: (a) include the resolved absolute module paths in the orchestrator's agent launch prompts (mirrors how phase files are already passed); (b) move positioning-specific modules under the skill and leave shared ones with explicit cross-skill paths; (c) inline critical module content into phase files. Leaning (a) — smallest change, fixes every launch context, no content moves.

## Requirements

Stub — filled during Design.

## Validation

Stub — filled during Design. Must include an agent run from a non-repo working directory that reads at least one module file successfully.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document — silent module-resolution failure observed in both research agents during the 2026-06-03 pilot. |
