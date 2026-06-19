---
fe-managed: true
name: hypothesis-generator-kb-silver-input-basenames
description: >
  Fix three KB-mode Read-side Mapping rows in hypothesis-generator that derive the on-disk filename
  from the artifact-type stem (`competitive-analysis.md`, `audience-analysis.md`, `performance-analysis.md`)
  instead of the canonical producer basename. The wrong basenames are written by no producer and read
  by no other skill, so on a KB-mode regen the competitive, audience, and performance silver inputs are
  silently not found and not read -- degrading the roadmap and capping all Confidence scores at 4.
governed_by: change-management/change-document
status: Closed
status_note: "Completed via the change-management Patch Process; runtime cross-confirmed by the sibling producer-binding doc's bound-KB run (Confidence not capped at 4)."
resource_name: hypothesis-generator
resource_version: "TBD"
initiative: cro-kb-path-b
impact: 4
confidence: 5
ease: 5
version: "0.1.0"
created: 2026-06-19
updated: 2026-06-19
related:
  - hypothesis-generator-experiment-history-producer-binding
---
# hypothesis-generator: KB-Mode Silver Input Basenames

## Background

A KB-mode regen in a consumer repo silently read only three of its six scope silver inputs. The competitive, audience, and performance analyses -- all present on disk -- were not found, so the roadmap was generated without competitive/audience context and **capped all Confidence scores at 4** (the no-`performance-profile.md` rule in [score.md](../../skills/hypothesis-generator/phases/score.md) line 21), with only a generic "run /ga4-audit" note. No error surfaced; the degraded output looked normal.

The root cause is a path-derivation bug in the KB-mode `Read-side Mapping` table. Three rows derive the on-disk filename from the **artifact-type stem** (`silver-competitive-analysis` → `competitive-analysis.md`) instead of reusing the **canonical producer basename**. KB mode is supposed to change only the directory (`.claude/context/` → `reference/cro-{scope}/`), never the basename. The "Legacy context file" column in the same rows already carries the correct basename, which is what makes this unambiguous.

## Current State

[SKILL.md](../../skills/hypothesis-generator/SKILL.md) `KB Mode (Dual-Mode Output)` > `Read-side Mapping`, the table at lines 86-95. Three rows have the wrong basename in the "Path under KB root" column:

```
| competitive-landscape.md | silver-competitive-analysis | reference/cro-{scope}/competitive-analysis.md | optional |   <- wrong basename (line 90)
| audience-messaging.md     | silver-audience-analysis    | reference/cro-{scope}/audience-analysis.md     | optional |   <- wrong basename (line 91)
| performance-profile.md    | silver-performance-analysis | reference/cro-{scope}/performance-analysis.md  | optional |   <- wrong basename (line 92)
```

The canonical basenames are set by the **producer skills**, and they are NOT the `-analysis` stems:

- [positioning-framework/SKILL.md](../../skills/positioning-framework/SKILL.md) writes `competitive-landscape.md` and `audience-messaging.md`.
- ga4-audit writes `performance-profile.md`.
- hypothesis-generator's own [score.md](../../skills/hypothesis-generator/phases/score.md) references `performance-profile.md` (lines 21, 65-67, 76), contradicting its own SKILL.md table.
- `live-capture` and `landing-page-generator` also consume `competitive-landscape.md` / `audience-messaging.md` / `performance-profile.md`.

So the `-analysis` filenames at lines 90-92 are written by no producer and read by no other skill -- a path-derivation bug confirmed by the legacy column in the same rows being correct.

The other three silver rows are already correct: `strategy-context.md` (line 88), `positioning-scorecard.md` (line 89), `live-structure.md` (line 93).

## Approach

Change the "Path under KB root" basenames at lines 90-92 to match the legacy column, leaving only the directory different:

```
reference/cro-{scope}/competitive-landscape.md
reference/cro-{scope}/audience-messaging.md
reference/cro-{scope}/performance-profile.md
```

Add a one-line rule to the table preamble (after line 84, before the table): **KB mode changes the directory (`.claude/context/` → `reference/cro-{scope}/`), never the basename.** That makes the artifact-type column a type label, not a filename source, and prevents the same bug from recurring on the next row added.

This is a three-cell table correction plus one preamble sentence. No phase-file edits, no scoring-logic edits, no schema change.

### Open Questions

- The `silver-*-analysis` artifact-type names in the second column are correct as *type labels* and should be left unchanged -- only the path basenames are wrong. Confirm the bound strategy KB type skill actually defines those silver types under those names (verified in the consumer repo where this surfaced), so the type-label column needs no edit. (Carried to Design for a quick grounding check.)
- Whether this should run as a Patch (the change-management Patch Process fits a three-cell correction) rather than a full lifecycle change document. The handoff requested a `chg_` doc; recorded here for the user to confirm at the Backlog → next-step transition.

## Requirements

Ran via the change-management Patch Process (three-cell correction; no Design phase). As built:

1. `skills/hypothesis-generator/SKILL.md` Read-side Mapping rows at lines 90-92: basenames corrected to `competitive-landscape.md` / `audience-messaging.md` / `performance-profile.md` (directory unchanged, `reference/cro-{scope}/`).
2. `skills/hypothesis-generator/SKILL.md` table preamble: added the rule "KB mode changes the directory, never the basename" so the artifact-type column reads as a type label, not a filename source.
3. `skills/hypothesis-generator/CHANGELOG.md`: `[Unreleased] > Fixed` entry. No version bump (resolved at release).

## Validation

- `bash scripts/validate-hypothesis-generator.sh` = 31/0/0; no em-dashes; no stale `-analysis.md` basename remains anywhere in the skill.
- Runtime cross-confirmed by the sibling `experiment-history-producer-binding` bound-KB run: with the corrected basenames, the competitive/audience/performance silver inputs were read and Confidence was not globally capped at 4.
