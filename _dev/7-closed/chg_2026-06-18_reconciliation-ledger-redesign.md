---
fe-managed: true
name: reconciliation-ledger-redesign
description: >
  Redesign the chrome that roadmap-presentation's scaffold_site.py emits into a "reconciliation
  ledger" visual language: IBM Plex Mono as a dedicated data layer, a disciplined disposition
  palette, a hero run-order spine and provenance line replacing the gradient hero and stat tiles,
  plus a roadmap-first hub section order. SKILL.md Phase 5 and the design-system class list are
  synced to the rebuilt CSS. Emitted-chrome only; no client content, no script logic change.
  Stacked on stable-mockup-resolution-key (shares scripts/scaffold_site.py); both unreleased.
governed_by: change-management/change-document
status: Closed
resource_name: [roadmap-presentation]
resource_version: "0.3.0"
impact: 3
confidence: 4
ease: 4
version: "0.1.0"
created: 2026-06-18
updated: 2026-06-18
status_note: Closed - authored retroactively over completed, verified work
---
# Reconciliation-Ledger Redesign

## Background

`roadmap-presentation` renders an experiment roadmap into a client-facing hub-and-spoke site. All chrome (CSS, JS, page shells, pager chain) is emitted by `scripts/scaffold_site.py` so renders cannot drift; the agent only does judgment work (curation, section-mapping, humanizer pass). The original chrome (v0.1.0/v0.2.0) used a gradient hero, a `.stat-row`/`.stat-item` tile strip, and a generic FunnelEnvy palette. For a pitch deliverable that is fundamentally a record of recorded evidence (experiment codes, ICE scores, dispositions, dates), that styling read as a brochure rather than a ledger.

This redesign reworks the emitted visual language into a "reconciliation ledger": IBM Plex Sans for prose plus IBM Plex Mono for the data layer, a restrained disposition palette, a hero run-order spine, and a roadmap-first hub order so the experiment portfolio and run order lead.

The work was authored in an external session and applied to the repo as a complete, verified unit; this change document was authored retroactively at Closed (user decision) to give the already-present `SKILL.md` 0.3.0 changelog entry its referenced backing doc.

### Relationship to stable-mockup-resolution-key

This change is stacked on `chg_2026-06-18_stable-mockup-resolution-key` (in QA at authoring time). Both are unreleased and both touch `roadmap-presentation` (this one shares `scripts/scaffold_site.py`). The two are cleanly separable: stable-mockup owns the Phase 3 Key-resolution behavior plus the `scaffold_site.py` docstring sync; this change owns the emitted CSS rebuild plus the Phase 5 / design-system / Quality-Rules prose. Notably, stable-mockup's QA explicitly reverted an out-of-scope CSS redesign a Build agent had injected into `scaffold_site.py`; this change is the correct, separately-scoped home for that CSS work.

## Current State

Verified against the applied working tree (`skills/roadmap-presentation/`):

- `SKILL.md` is at `version: 0.3.0` with three inline changelog rows (0.1.0, 0.2.0 stable-mockup, 0.3.0 this change). Phase 3 Key-resolution from stable-mockup is intact (5 `**Key:**` references; Phase 3 key-based resolution present).
- `scripts/scaffold_site.py` `STYLES_CSS` is rebuilt; both page shells load IBM Plex Mono. The number-keyed in-site asset logic (zero-padded `experiment-NN/`) is unchanged.
- The full test suite passes 74/74, including `_tests/unit/test_scaffold_site.py` invariants: byte-identical determinism across runs, no em dashes in emitted output, no client strings in emitted chrome, and number-keyed asset paths.

## Approach

### Change Profile

- **Script-affecting: yes** - modifies `scripts/scaffold_site.py` (registered in the skill's `## Scripts` table). The change is to the `STYLES_CSS` data the script emits plus the page-shell font links and the docstring; no control-flow or asset-keying logic changes. Covered by the existing `_tests/unit/test_scaffold_site.py` (no new test file required - the existing suite already asserts the emitted-output invariants the redesign must preserve: determinism, no em dashes, no client strings, number-keyed assets).
- **Performance-affecting: no** - funnelenvy-skills has no `_evals/` framework and no eval task targets this skill.
- **Test-eval-only: no** - targets production `SKILL.md` and `scaffold_site.py`.

Rework the emitted chrome into the reconciliation-ledger language and sync the SKILL.md instruction prose to match:

1. Rebuild `STYLES_CSS` in `scaffold_site.py`: add IBM Plex Mono as a data-layer font (`.mono` for codes, scores, percentages, counts, dates, versions); introduce a disciplined disposition palette (blue = active/run/net-new and links, amber = the single caution hue for gated, green reserved for measured wins only, gray/slate for reframed/held/superseded); add a hero run-order spine (`.hero-seq`/`.hs-chip`/`.hs-stage`) and a `.provenance` meta line, replacing the gradient hero and the `.stat-row`/`.stat-item` tiles; add `.recon-bar`/`.recon-legend` (proportion summary with linked IDs); lighten borders and reduce shadows. Both page shells load IBM Plex Mono.
2. Rewrite `SKILL.md` Phase 5 for a roadmap-first hero and hub section order (experiment portfolio and run order lead; never lead with a standalone live-program reconciliation table since per-card disposition badges already carry the verdict).
3. Add judgment passes (roadmap-first ordering, mono data layer, link experiment references) and Quality Rules 11-13.
4. Sync the design-system class list in `SKILL.md` to the real emitted inventory (`.stat-row` removed; `.mono`/`.provenance`/`.hero-seq`/`.recon-bar`/`.recon-legend` added).

Constraint preserved throughout: emitted chrome stays generic and reusable, carrying no client content, and the script's behavioral contract (number-keyed in-site assets, determinism) is unchanged.

Out of scope (non-goals): any client content in emitted chrome; any change to mockup resolution (owned by stable-mockup-resolution-key); any change to the number-keyed in-site asset path; new tests (existing suite covers the invariants).

## Requirements

All edits are in `skills/roadmap-presentation/`.

### 1. scripts/scaffold_site.py

**1a. STYLES_CSS rebuild.** Replace the stylesheet with the reconciliation-ledger CSS: `--font-mono` IBM Plex Mono added alongside `--font-sans`; `.mono` data-layer class and `.ids`/`.ids a` linked-identifier styling; disposition-state CSS variables (`--st-active`, `--st-gated`, `--st-reframed`, `--st-closed`, `--win`) and the restrained palette; `.provenance`, `.hero-seq`/`.hs-stage`/`.hs-chip` (with `.lead`), `.recon-bar`/`.recon-legend`, `.recon-table`, `.prelim`/`.prelim-card`, `.live-pill`, `.live-status`; gradient hero and `.stat-row`/`.stat-item` removed; lighter `--line`/`--line-2` hairlines and reduced `--card-shadow`. A `prefers-reduced-motion` block is added.

**1b. Page-shell fonts.** Both the hub and spoke shells add the IBM Plex Mono `<link>` (plus `preconnect`) alongside IBM Plex Sans.

**1c. Docstring.** The module docstring and the design-system comment describe the reconciliation-ledger language. No change to the number-keyed-asset clause (still true).

**1d. No behavioral change.** Asset keying, write counts, pager chain, and determinism are unchanged. `_tests/unit/test_scaffold_site.py` must still pass without modification.

### 2. SKILL.md

**2a. Intro.** The `The split:` paragraph describes the reconciliation-ledger design language (IBM Plex Sans for prose, IBM Plex Mono for the data layer, disposition palette, hero run-order spine).

**2b. Phase 2 hub-level content.** Add the provenance line and run-order spine inputs to the hub-level content list.

**2c. Phase 5 rewrite.** Roadmap-first hero (provenance line, headline stating the first move/verdict, run-order spine linking to spokes, then the measurement-constraint callout); experiment portfolio is the first full section after the hero; mono data layer and linked experiment references mandated; demote any front-loaded live-program section into the run-order section.

**2d. Design-system class list.** Sync to the emitted inventory: add `.mono`, `.provenance`, `.hero-seq`/`.hs-stage`/`.hs-chip`, `.recon-bar`/`.recon-legend`; remove `.stat-row`/`.stat-item`. Add the palette-discipline paragraph.

**2e. Quality Rules.** Add rules 11-13 (roadmap-first ordering; mono the data layer; no dead identifiers + disciplined palette).

**2f. Changelog + version.** `version` frontmatter `0.2.0 -> 0.3.0`; inline `## Changelog` table gains the `0.3.0` row tagged `(chg_2026-06-18_reconciliation-ledger-redesign)`.

## Verification Design

### Validation

Each criterion is confirmable by inspecting the edited files and running the existing test suite. No live browser run required (the change is emitted-chrome CSS plus instruction prose).

1. **CSS rebuilt, fonts loaded.** `scaffold_site.py` `STYLES_CSS` carries the `.mono` data layer and disposition palette; both page shells load IBM Plex Mono. `.stat-row`/`.stat-item` and the gradient hero are gone.
2. **Determinism and no-client-content preserved.** The emitted chrome is byte-identical across runs, carries no em dashes and no client strings, per `test_scaffold_site.py`.
3. **No site-path / behavior regression.** In-site asset paths remain number-keyed; write count, pager chain, and asset-dir creation are unchanged. Script behavior is otherwise identical (CSS/docstring/font-link only).
4. **SKILL.md synced.** Phase 5 is roadmap-first; the design-system class list matches the emitted inventory (`.stat-row` removed; mono/provenance/hero-seq/recon-* added); Quality Rules 11-13 present; intro describes the design language.
5. **Stable-mockup preserved.** Phase 3 Key-resolution and the `scaffold_site.py` docstring's key clause from `chg_2026-06-18_stable-mockup-resolution-key` are intact (this change did not revert them).
6. **Version and changelog hygiene.** `SKILL.md` is `0.3.0` with the slug-tagged `0.3.0` inline changelog row; `resource_version` stays TBD until release; README/CLAUDE.md version sync deferred to release.

## Verification Results

### Validation Outcomes

All 6 validation criteria confirmed against the applied working tree.

- Criterion 2 and 3 confirmed by the full suite: 74/74 pass, including `test_scaffold_site.py` determinism, no-em-dash, no-client-string, and number-keyed-asset invariants.
- Criterion 4 confirmed by inspection: Phase 5 roadmap-first; class list synced (`.stat-row` absent, `.mono`/`.provenance`/`.hero-seq`/`.recon-bar`/`.recon-legend` present); Quality Rules 11-13 present.
- Criterion 5 confirmed: 5 `**Key:**` references remain in `SKILL.md`; Phase 3 key-based resolution language present; `scaffold_site.py` docstring retains the key-resolution clause.

### Tests Results

| Metric | Value |
|--------|-------|
| Total  | 74    |
| Passed | 74    |
| Failed | 0     |

`scaffold_site.py` STYLES_CSS rebuild and font-link edits confirmed behavior-unchanged; `test_scaffold_site.py` passes unmodified (determinism, no em dashes, no client strings, number-keyed assets).

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Change document authored retroactively at Closed (user decision) over completed, externally-authored, verified work. Documents the reconciliation-ledger redesign of roadmap-presentation's emitted chrome: `scaffold_site.py` STYLES_CSS rebuilt (IBM Plex Mono data layer, disposition palette, hero run-order spine + provenance line, recon-bar/legend; gradient hero and stat-row tiles removed), both page shells load IBM Plex Mono, docstring synced; `SKILL.md` Phase 5 roadmap-first rewrite, design-system class list synced, Quality Rules 11-13, version 0.2.0 -> 0.3.0. Stacked on stable-mockup-resolution-key (shares `scaffold_site.py`; Phase 3 Key-resolution preserved). Full suite 74/74. resource_version TBD until release. |
