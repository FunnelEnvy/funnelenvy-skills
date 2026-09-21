---
fe-managed: true
name: render-program-site-changelog
title: Changelog
description: Changelog for the render-program-site skill.
governed_by: change-management/changelog
version: "0.8.0"
created: 2026-09-21
updated: 2026-09-21
---
# Changelog

## [Unreleased]

## [0.8.0]

### Changed
- Humanizer pass consolidated to the shared `modules/prose-craft.md` module. Phase 4 and the References table now point at [`modules/prose-craft.md`](../../modules/prose-craft.md) instead of the deleted skill-local humanizer reference under `references/` (the empty directory drops out). The module preserves the former 10-sign list verbatim in intent and adds 9 non-duplicative StrategyU signs (lazy descriptors, copula avoidance, synonym cycling, nominalization, fake-precision hedging, awkward verb-noun pairings, anthropomorphized data, staccato noun-phrase lists, structural tells), so the Phase 4 pass now applies the fuller sign set. No generator change; templates, gate, map, and slots are untouched.

## [0.7.0]

### Changed
- Editorial data-story design language. The output is restyled from a dashboard to an editorial data-story: mono uppercase eyebrows over full-sentence claim headlines, flat white with hairline framing instead of card shadows, a larger type scale (17px body; hub `h2` 30px/800; spoke `h1` 38px), and IBM Plex Mono leaned on as a data face (tags, numbers, labels, `tnum`). Three generator changes: (1) the five hub section headings become PROSE slots on page id `program` -- `strategy-headline`, `backlog-headline`, `sequence-headline`, `decisions-headline`, `foundation-headline` -- each pre-filled with its former label so an uncurated regen still renders, and the mono eyebrow stays as the section label; (2) a new code-emitted `.program-stats` band (deterministic, no slot; claim-captioned `.statbox` numbers derived from parsed data, placed between the hero and the map); (3) the backlog card wall becomes audit-style `.brow` rows (number + title + page + ICE + ladder + mono `.tag` tier chip) under the existing tier headers. Bet cards and account `.test off` cards stay cards but restyle flat via CSS; the retired `.badge` pill is replaced by `.tag`. Templates: `hub.html` gains the headline tokens + `{{PROGRAM_STATS}}`; `base.html` and the three spoke templates are unchanged (nav-mono, hero-scale, `.sec` grammar are CSS-only). Map geometry, edge/gate logic, and every existing slot id are untouched; four new `program` headline slots (plus `foundation-headline`) are added. The hub `sequence` slot now defaults empty (like `decisions`) instead of pre-filling the raw `## Sequencing` section, so an uncurated render degrades to the standard slot placeholder rather than a wall of text; the Phase 3 curation contract gains a concrete `.tl-row` timeline shape and a distill-not-dump directive. 1 new unit-test class (6 cases).

## [0.6.0]

### Changed
- Red-team tombstone skip. `render_site.py` now skips a red-team **tombstone** slot (a `### N.` gold section with no `**Key:**` line, kept in place by `cro-roadmap-red-team` so audit-trail "Experiment N" cross-references stay valid) in the bet/test altitudes instead of crashing on the missing `**Key:**`/`**Scores:**`, and assigns surviving bet/test ids **contiguously in document order** (`sb-01, sb-02, ...`; `p-01, p-02, ...`) so a red-teamed roadmap renders with a hole-free id sequence. This unblocks re-rendering any roadmap that has been through a red-team pass. Compatibility: a roadmap with no tombstones and no ordinal gaps renders **byte-identically** to 0.5.x (contiguous ids equal the raw ordinals); the only output shift is when a tombstone precedes a surviving item, where the survivor ids close the gap. A present-but-empty `**Key:**` is an authoring bug, not a tombstone, and still raises. Account plays are exempt and keep raw-ordinal `ap-NN` ids (unchanged). Documented in `edge-contract.md` (`Red-team tombstones` subsection + the contiguous-over-survivors `id` derivation bullet). 4 new unit-test classes.

## [0.5.2]

### Changed
- Legacy-lane fix: `render_site.py` now loads frontmatter-less roadmaps as body-only files (hypothesis-generator's legacy deliverables carry no YAML frontmatter by design; the documented legacy default inputs previously crashed the parser), and gate check 7 skips the sidecar version lock per-file when a roadmap carries no `version`, reporting the skip as an explicit `note:` line on stdout (never silent). KB gold roadmaps always carry `version`, so that lane locks exactly as before; mixed pairs still fail closed on real skew in the versioned file. Semantics documented in `edge-contract.md` check 7 and Preconditions. Also: fixed the dead `#kb-mode-dual-mode-io` anchor left by the 0.5.1 section rename; "override mode resolution" wording aligned to "override the mode-resolved inputs"; Phase 2 command block now uses the probe-then-run `$PY` pattern with the full `skills/render-program-site/scripts/` path; Phase 3 curation instruction rewritten to match the generator's actual pre-filled slot labels (the previously cited label-to-region map never existed in `edge-contract.md`). 8 new unit tests.

## [0.5.1]

### Changed
- Repo-audit doc corrections, no generator change. Mode resolution rewritten to match hypothesis-generator/experiment-mockup exactly: KB binding detection alone selects KB mode (previously step 2 said binding AND a valid `--scope` select it while step 3 said a missing `--scope` in KB mode is a HARD STOP -- contradictory); `--scope` names the scope (required in KB mode, warn-and-ignore in legacy) and never selects the mode. Section renamed `KB Mode (Dual-Mode Output)` to match the header the other dual-mode skills use and cross-reference. Added the Model declaration (Opus for the curation/humanizer passes). Also gains the `modules/kb-mode.md` canonical-contract pointer in its KB-mode section (drift canary enforced by `scripts/registry_check.py`).

## [0.5.0]

### Changed
- Measurement Foundation rendering. `render_site.py` now parses the strategic gold roadmap's optional `## Measurement Foundation` section (hypothesis-generator SKILL.md > Strategic Roadmap Output Format) into a new item class: foundation entries (bold-labeled items; unscored, keyless, no ICE, no tier, no map presence, no cross-altitude edges, no spokes). The hub gains a conditional `#measurement-foundation` section between the strategy cards and the backlog (one `.mf` card per entry: label as title, prose through `foundation-lead`/`foundation-<n>` curation slots, no score chips) plus a nav link; new `#measurement-foundation`/`.mf-grid`/`.mf` CSS. Foundation entries are excluded from every sidecar-related gate check (binding completeness, dangling targets, executor-status derivation, version-lock scope) and require no sidecar entries; a sidecar edge whose target names a foundation entry fails as a dangling target (check 2). Composes with the optional account altitude (both, either, or neither). Output is byte-identical to 0.4.0 for any strategic roadmap without the section (empty `{{MEASUREMENT_FOUNDATION}}` reproduces the hub seam; no nav link). Also adds the `informs` edge-direction semantics note to `edge-contract.md` (edges point bet -> test; behavior unchanged).

## [0.4.0]

### Changed
- Optional account-program altitude. New `--account-program <path>` renders an off-store account layer: `load_account` parses the deliverable standalone (plays sliced from `## The Account-Level Plays`, cohorts from the `## The Account-Cohort Taxonomy` table; no `**Key:**`/`**Scores:**` required), a separate account-binding gate leg validates the plays (>=1 play, unique ordinals, required `Cohort`/`The play`/`How it is measured` labels), the hub gains a conditional `#account-program` section + nav link, and one `ap-NN.html` spoke is emitted per play. Account plays never enter the 7-check edge gate or the Impact-by-Ease map. `extract_sections` id-prefix generalized to `{bet:sb, test:p, play:ap}`. New `templates/spoke-account.html` + `#account-program`/`.cohort`/`.x-tag.off` CSS. Output is byte-identical to 0.3.x for any program supplying no account program (empty `{{ACCOUNT_PROGRAM}}` reproduces the hub seam; no `ap-*.html`; no nav link). Also corrects the stale `0.2.1` version pin in README.md / in-repo CLAUDE.md.

## [0.3.0]

### Changed
- Optional Before/After mockup render. The `mockup` block accepts an optional `control_screenshot` (experiment-mockup's `control-screenshot.png`): when present and resolvable, the tactical spoke's "Proposed change" section renders a labeled two-frame Before/After comparison (responsive grid, stacks under 760px) instead of a single after screenshot. `copy_mockup_assets` now copies `control.png` alongside `screenshot.png` and returns a dict of resolved paths; the gate rejects a non-string `control_screenshot`; a missing control file degrades to after-only. Output is byte-identical to 0.2.x for any `mockup` block without a resolvable `control_screenshot`. New `.mockup-compare` / `.mockup-label` CSS.

## [0.2.0]

### Changed
- Inputs reconciled with hypothesis-generator's actual output: the generator now reads the two prose gold roadmaps (`gold-experiment-roadmap`, `gold-strategic-roadmap`) in place and derives per-item data (id from `### N.` ordinal, key from `**Key:**`, title, tier from the enclosing tier H2, ICE from `**Scores:**`, page) from the gold bodies. The cross-altitude edge binding plus the gate-classification fields (`delivery_surface`, `executor_status`, per-test `mechanism_class`, optional `status`/`run_tag`/`keystone`/`mockup`) move to a new render-owned sidecar `{scope}-program-edges.md` keyed by gold Key. KB-mode strategic input renamed `{scope}-strategic-experiment-layer.md` -> `{scope}-strategic-roadmap.md`; tactical collision resolved by reading the gold artifact directly. Gate check 7 redefined as a sidecar-vs-gold version lock; new binding checks (every gold bet bound, every sidecar Key resolves, every live test has a `mechanism_class`). `render_site.py` gains `--edges`. Replaces the bespoke hand-authored `bets:`/`tests:`/`edges:` frontmatter that no deliverable carried.

## [0.1.0]

### Added
- Initial skill: deterministic two-altitude program-site generator (`render_site.py`) with a 7-check edge-contract gate, Impact-by-Ease map, dual-mode I/O, and a scoped LLM curation + humanizer pass over spoke prose slots. Replaces roadmap-presentation.
