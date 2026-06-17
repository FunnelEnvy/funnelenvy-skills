---
fe-managed: true
name: aa-audit-kb-dual-mode
description: >
  Give aa-audit dual-mode I/O so it can participate in the KB-native CRO pipeline. Today aa-audit
  is legacy-only: it writes its performance profile to `.claude/context/performance-profile.md` and
  has no KB-mode awareness (no `--scope`, no `kb_root`, no silver artifact write). The sibling CRO
  skills (positioning-framework, hypothesis-generator, live-capture, experiment-mockup) are dual-mode,
  so an AA-instrumented client cannot feed the bound knowledge base the way a GA4 client can.
governed_by: change-management/change-document
status: Backlog
resource_name: aa-audit
resource_version: "TBD"
impact: 4
confidence: 4
ease: 3
version: "0.1.0"
created: 2026-06-17
updated: 2026-06-17
related:
  - aa-audit-performance-profile-schema-conformance
---
# aa-audit KB Dual-Mode I/O

## Open Issues

**Source:** Approach OQ
**Generated:** 2026-06-17 PT

### Findings Detail

| # | Source | Finding | Description | Recommendation |
|---|--------|---------|-------------|----------------|
| 1 | Approach OQ | Which sibling to mirror: ga4-audit (same artifact) vs the experiment-mockup retrofit pattern | aa-audit produces an L1 performance profile, the same artifact ga4-audit produces, not an L2 deliverable like experiment-mockup. The KB-mode mapping for a performance profile is a silver artifact (`silver-performance-analysis`), which differs from the deliverable co-location pattern experiment-mockup uses. Mirror the producer that already writes that silver artifact. | Discovery: verify whether ga4-audit is already dual-mode; if so, mirror its performance-profile KB write contract (silver artifact type, frontmatter, supersede semantics) exactly. If neither GA4 nor AA audit is KB-aware yet, design the silver-performance-analysis write contract once and apply it to both (consider a combined or sequenced change). |
| 2 | Approach OQ | aa_audit.py output-path handling (script-affecting) | The skill executes `aa_audit.py`, which writes/feeds the profile. KB-mode output may require the script to accept an output path or the orchestrator to relocate the artifact post-run. This determines whether the change is script-affecting (test authoring) or purely SKILL.md-level. | Discovery: determine whether KB-mode output is handled in the orchestrator (SKILL.md only) or requires an `aa_audit.py` flag. Set the Change Profile `script-affecting` flag accordingly. |
| 3 | Approach OQ | Relationship to the open schema-conformance change | A peer backlog item (`aa-audit-performance-profile-schema-conformance`) already targets aa-audit's profile output contract. Dual-mode KB writes interact with that schema work (the silver artifact carries the schema). | Discovery: decide sequencing or merge with the schema-conformance change so the KB write side and the schema land coherently. |

## Background

The roadmap-presentation change (closed 2026-06-17) folded a KB dual-mode retrofit into experiment-mockup so that KB-mode mockups have a producer rather than always degrading to placeholders. That work surfaced the broader pattern: the CRO skill set is converging on dual-mode I/O (legacy `.claude/` plus a bound knowledge base), and aa-audit is the remaining producer that has no KB awareness. An AA-instrumented client therefore cannot populate the KB the way a GA4 client can, so the KB-native hypothesis-generator pipeline (which reads `silver-performance-analysis`) is unavailable for AA clients.

## Current State

- aa-audit is single-agent, legacy-only: it runs `aa_audit.py` against the AA 2.0 Reporting API and writes one L1 context file, `.claude/context/performance-profile.md`. No `--scope`, no `--no-kb`, no `kb_root`, no silver artifact write (grounded against `skills/aa-audit/SKILL.md`, 2026-06-17).
- ga4-audit produces the same `performance-profile.md` artifact. Whether ga4-audit is already dual-mode is unverified and is the primary Discovery question (it determines the template aa-audit should mirror).
- The other CRO skills (positioning-framework, hypothesis-generator, live-capture, experiment-mockup) are dual-mode, so the detection mechanism and `--scope`/`--no-kb` semantics are well-established and should be mirrored verbatim.

## Approach

Stub. Resolved during Discovery. Direction: mirror the established dual-mode detection mechanism and `--scope`/`--no-kb` semantics from the sibling skills, and write the KB-mode performance profile as the appropriate silver artifact (`silver-performance-analysis`) rather than `.claude/context/performance-profile.md`, with legacy behavior unchanged. The exact silver write contract is settled in Discovery against the artifact that ga4-audit produces (see `## Open Issues`).

## Requirements

Stub. Filled during Design.

## Verification Design

### Validation

Stub. Filled during Design. Must include: a legacy-mode run still writes `.claude/context/performance-profile.md` unchanged; a KB-mode run (`--scope`) writes the silver artifact to the bound KB with correct frontmatter; missing/invalid `--scope` in KB mode hard-stops; detection and flag semantics match the sibling CRO skills; no client content committed to this public repo.

## Verification Results

### Validation Outcomes

Pending. Populated during QA.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document: give aa-audit dual-mode I/O (KB silver-performance-analysis write plus legacy `.claude/context/` behavior) so AA clients can feed the KB-native CRO pipeline. Premise grounded against `skills/aa-audit/SKILL.md` (legacy-only today). Three approach open questions seeded: which sibling to mirror (ga4-audit, the same-artifact producer), `aa_audit.py` output-path handling (script-affecting determination), and the relationship to the open `aa-audit-performance-profile-schema-conformance` change. |
