---
fe-managed: true
name: experiment-mockup-changelog
title: Changelog
description: Changelog for the experiment-mockup skill.
governed_by: change-management/changelog
version: "1.6.0"
created: 2026-09-21
updated: 2026-09-21
---
# Changelog

## [Unreleased]

## [1.6.0]

### Changed
- Capture-fidelity bundle (P1-P4). **P1 overlay hygiene:** a new `capture.md` Step 0 precondition (and a cross-reference in inject.md Step 2b) dismisses/hides floating overlays (consent banners, chat widgets, sticky promos) before every screenshot, identically across the pair, hiding only floating overlays and never in-flow content or the treatment's layout context; capture-time only, recorded in placement metadata, not shared into live-capture. **P2 salience-scaled framing:** `capture.md` Step 1 now scales the frame to the treatment keyed on the resolved `change_type` (element/copy-scale = tight crop; section-scale = viewport framing; primary type governs a bundled type) plus a one-directional size backstop that only tightens (never loosens a tight crop); the 390px mobile pair follows the same rule; output filenames unchanged (the tight crop replaces the full-viewport primary pair, no context pair). **P3 spot-the-diff:** inject.md Step 2b adds a side-by-side check that the change is identifiable at a glance by someone who has not read the hypothesis, forcing a tighter-crop re-frame within the existing 2-cycle self-fix budget; annotation overlays remain forbidden (fix framing, not labeling). **P4 target-fidelity gate:** a new inject.md pre-build gate resolves the hypothesis's named region to the page's visual reality and stops-and-asks on a named-region-vs-visual-structure disagreement (naming both candidates) instead of silently picking the copy-match; static-build.md folds the same check into its existing Step 2 clarification ask (DOM-structure reasoning) with a Risk Flag when running non-interactively. placement.md `schema_version` 1.1 -> 1.2 with a new `Section 7: Capture Fidelity Notes`; four new Quality Checks; `generated_by` literal swept to v1.6.0 across the phase templates. [experiment-mockup-capture-communicates-change]

## [1.5.0]

### Changed
- Treatment-quality bundle (P1-P5). **P1 treatment-type taxonomy:** consumes hypothesis-generator's new `**Change type:**` field (extracted in Step 2; classified locally on legacy roadmaps that predate it, no hard failure, mirroring the `**Key:**` fallback). `inject.md`'s single insert-only "CRO Placement Principles" doctrine is restructured into "Treatment Principles by Change Type": cross-type invariants plus five per-type branches (insert = the prior rules verbatim; replace-copy edits text in place at original tag/styles; modify changes only named properties with an explicit primary-CTA-prominence exception; remove verifies reflow; reorder checks seams). Step 1 generalized to "Build the Treatment" and branches on type; `static-build.md` Step 5 gets the same branch logic. `annotate.md` becomes type-aware (Section 1/2 framing) and its frontmatter gains `change_type` / `change_type_source` with schema_version -> "1.1". Fixes the previously-broken archetypes (a headline or CTA-label test was forbidden by the old "never h1/h2" / "never the primary CTA color" rules). **P2 copy-craft + distillation contract:** `modules/copy-craft.md` loaded in all three modes; a Distillation Contract in inject.md/static-build.md makes quantified claims from the hypothesis copy immutable (they passed proof-integrity upstream and this skill has no registry access) and forbids introducing new claims. **P3 candidate pass + self-review:** inject Step 1a sketches/scores 2-3 candidates internally and builds only the winner (Section 4 now documents a real comparison), with a skip rule when the treatment is fully pinned; inject Step 2b screenshots the injected state and self-reviews before first presentation (2-cycle fix budget); static mode runs the checklist as a reasoning pass. **P4 mobile:** the self-review and `capture.md` add a 390px pair (`control-screenshot-mobile.png` / `mockup-screenshot-mobile.png`); annotate Section 5 responsive note becomes observed (live/playwright) vs speculative (static). **P5 type-conditional dimensions + variation awareness:** Step 6 loads lp-audit-taxonomy conditionally (base D1/D3/D5/D8; +D6 for CTA/form; +D7 for persuasion mechanisms; +D4 for reorder/remove; base+D6 when the type is absent); when the hypothesis carries a Variation block, the Recommended variation is mocked and named, others listed. Also fixed the pre-existing `generated_by: experiment-mockup v1.0.0` literal (now v1.5.0) in the capture/static-build/annotate templates. [experiment-mockup-treatment-quality]

## [1.4.2]

### Changed
- Browser-mode contract parity back-port: Step 5 gains the WAF/enterprise-bot-management guidance (fingerprinting signals, preferred real-Chrome configurations, "static fallback is NOT a WAF remedy") and a new Step 5.6 headless pre-flight probe (`navigator.webdriver` / `HeadlessChrome` check, surfaced before launching the phase agent) that live-capture already carried; the two skills' duplicated detection contract had drifted. The contract now has a canonical editing source at `modules/browser-mode.md` (drift canary enforced by `scripts/registry_check.py`); the inline copy stays runtime-self-contained.

## [1.4.1]

### Changed
- Repo-audit contract completion, no behavior change: added the Quality Checks section (the dev rules require one; the file previously had none). Also gains the `modules/kb-mode.md` canonical-contract pointer in its KB-mode section (drift canary enforced by `scripts/registry_check.py`).

## [1.4.0]

### Changed
- Control ("before") screenshot capture. `capture.md` Step 1 now captures a Before/After pair from the same scroll position and viewport: it restores the original state (removes the injected element, restores any modified originals), screenshots the unmodified viewport as `control-screenshot.png`, then re-injects and screenshots the after as `mockup-screenshot.png`. `inject.md` Step 5 now hands off the injected element's class/id and any modified-original markup so capture can restore the control. New live/playwright-only output `control-screenshot.png` added to agent-header Section 2, SKILL.md Output Files, and the Step 7 completion summary. Static mode writes no control (documented in `static-build.md`). Pairs with render-program-site's optional `control_screenshot` to render a Before/After comparison; absence is backward compatible (after-only).

## [1.3.2]

### Changed
- Reference rename: roadmap-presentation -> render-program-site across the KB-mode and mockup-output prose (the consumer skill was replaced). No behavioral change.

## [1.3.0]

### Changed
- Key-based output-directory resolution: `Step 4` now resolves the output directory from the matched hypothesis's persisted `**Key:**` field instead of `slugify(experiment name)`, with a shared fallback contract (prefer `**Key:**`; when absent, fall back to `slugify(title)` and print a one-line warning, no hard failure on keyless roadmaps). `Step 2` now also extracts the `**Key:**` field. Decouples mockup resolution from mutable roadmap heading titles (chg_2026-06-18_stable-mockup-resolution-key).

## [1.3.0]

### Changed
- Dual-mode I/O retrofit (KB / legacy). New `KB Mode (Dual-Mode Output)` section: mode resolution mirrors hypothesis-generator and roadmap-presentation exactly (`--no-kb` forces legacy; a detected `Knowledge Bases` binding plus a valid `--scope` selects KB mode; missing/invalid `--scope` in KB mode is a HARD STOP listing valid scopes; failed detection falls back to legacy loudly). Read side: KB mode reads the gold roadmap at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`; legacy unchanged. Write side: KB mode writes mockups to `{kb_root}/deliverables/experiments/<slug>/` (co-located so roadmap-presentation resolves them; not a KB artifact, no `kb_layer`); legacy unchanged. New `--scope` and `--no-kb` flags; mode-aware roadmap-exists precondition, output-directory resolution (Step 1b, Step 2, Step 4), completion message, and Architecture Notes layer line. Phase path references generalized to the orchestrator-provided output directory (legacy path shown as the canonical example).

## [1.2.0]

### Changed
- Playwright browser mode added (screenshot-based iteration) as the secondary detection tier between Chrome DevTools and static.
