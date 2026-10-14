# Changelog

## [2.1.0] - 2026-10-13

### Added
- `phases/qa.md` Step 4e, Independent Review Gates. Every copy pass gets four gates, rerun after every copy change, in two fresh subagents and never in the QA context: (1) a cold reader that sees only the visitor-visible page text in scroll order, reports what it thinks is sold from the H1 alone, and flags every person's name, product term or acronym used before the page says what it is; (2) a Julian audit (ATF-1 to ATF-6, Section 5 hard-rule order, feature blocks, and a recorded desire, labor and confusion read); (3) a truth check (every claim traces to a source, and surfaces describing the same event agree); (4) a line-level delete test ("what would the visitor lose if this line were cut?"). A gate reviewer subagent runs gates 2 to 4 and judges gate 1 without seeing QA's own results. A gate that cannot run in a fresh subagent is BLOCKED, never substituted. Report schema 2.1 adds `review_gates`, `cold_reader_header_read` and `delete_test_cuts`; any gate FAIL or BLOCKED fails QA. Copy fixes after QA go through Phase 2, then Phase 3 and Phase 4 rerun.
- `agent-header.md` Content Integrity rule 6, No self-grading: a phase's self-check confirms format only; quality verdicts come from the Phase 4 gates.
- Header-only litmus test (Julian Shapiro: "If the visitor reads only this text on your page, will they know exactly what you sell?") as Rule 1 test 1 in `modules/conversion-playbook.md`, run before the competitor-swap test, and wired into the copy phase's headline variants, its D2 construct row, and QA ATF-1. A question, slogan or pain statement on its own fails; it can open the hero as the hook line.
- `modules/conversion-playbook.md` 2.1: the Purchase Rate = Desire - (Labor + Confusion) frame, Rule 7 (subheader: one or two sentences, both jobs by default), Line-Level Rules (every line earns its place, introduce names and terms before use, examples only where needed, one story, objection answers as conversion copy), Feature Blocks, two new copy anti-patterns (process copy, undefined names and terms), and matching QA checklist items. The copy phase applies the Line-Level Rules and Feature Blocks while writing.

### Fixed
- The subheader rule contradicted itself: `modules/lp-audit-taxonomy.md` D2 and the copy phase's D2 row said "exactly one of ... Not both", while QA ATF-6 asked for both jobs. Julian Shapiro's guide, which D2 cites, uses the subheader for both, and his examples do both. D2 and the copy phase now match ATF-6: both jobs by default, one job is a warning, a restatement fails. The copy phase's "1 sentence explaining HOW" subheadline line is corrected to one or two sentences. `lp-audit-taxonomy.md` 1.1.0 also names the model correctly (Purchase Rate = Desire - (Labor + Confusion), not "desire-minus-labor") and adds the header-only test plus D8 delete-test and introduce-before-use checks.
- The `pain-lead` hero variant ("Headline names the pain") produced headers that never say what is sold. `modules/section-taxonomy.md`, `templates/section-catalog.html`, the playbook's Unaware and Problem Aware headline rows, and the taxonomy's D2 pain-led row now require the headline to name the pain and what is sold.
- `phases/qa.md` pointed at conversion-playbook "Section 9" for the QA checklist; the checklist is Section 11. The copy phase's module scope ("Sections 1-4, 6 only") left out Sections 9 and 10, which its own steps cite. The SKILL.md body version line read 2.0.1 against frontmatter 2.0.3.
- `schemas/campaign-brief.md` qa-report reference copy re-synced with the authoritative phase-file schema, per the Schema Authority rule (it still showed schema 1.1 without the 2.0 fields).

## [2.0.3] - 2026-07-14

### Changed
- `agent-header.md`: the `## Em Dashes` section is replaced by a `## Prose Style` reference to the shared `modules/prose-craft.md` humanizer / anti-AI-writing module (em dashes, hedging, and the full sign set). The context-driven Voice Rules and the "Banned terms are absolute" Content Integrity rule are unchanged. Faithful refactor: the em-dash ban is preserved via the module, and applying the full sign set is an intended quality improvement. [prose-craft-module-consolidation]

## [2.0.2] - 2026-07-07

### Fixed
- Phantom context reads in `phases/copy.md`: the phase read four frontmatter fields no producer writes. `tone_dimensions`/`vocabulary_stats` corrected to brand-voice's real fields (`primary_tone`, `person`, `jargon_tolerance`, `sentence_length_avg`); `device_split` corrected to `device_mobile_pct`; the L0 "proof point counts by tier" read repointed at the body Proof Point Registry (proof points are body-only, `target_market` stays frontmatter). Also corrected the `device_split.mobile_pct` signal references in `modules/section-taxonomy.md` and `templates/section-catalog.html` to `device_mobile_pct`.

## [2.0.1] - 2026-07-05

### Fixed
- Repo-audit contract completion, no pipeline behavior change: added the skill-level Quality Checks section (the dev rules require one; Phase 4 QA is a pipeline stage, not the skill checklist), the per-agent Model Selection table (the skill spawns three subagents; the bare Model line did not satisfy the convention), the `updated` frontmatter field, and this changelog.

## [2.0.0] - 2026-03-31

### Changed
- Composable section taxonomy: replaced the fixed wireframe with signal-driven section assembly. The copy agent selects and sequences sections from `modules/section-taxonomy.md` based on campaign brief signals and L0/L1 context; the design agent renders from `templates/section-catalog.html` (or a client `brand-components.html`, which replaces it when present). Brand component constraint layer across the pipeline; semantic component matching (Step 3.5). Legacy wireframe retained as `templates/wireframe-demo-legacy.jsx` (reference only).
- 2026-04-02 follow-up fix: duplicate social proof sections no longer emitted.

(History below reconstructed from git log during the 2026-07-05 audit; this file did not exist before 2.0.1.)

## [1.1.0] - 2026-03-17

### Added
- LP audit taxonomy integration: construct-mode dimensions routed per phase (Copy: D1,D2,D3,D5,D7,D8,D10; Design: D4,D6,D9; QA: 10-dimension scoring).

## [1.0.0] - 2026-03-08

### Added
- Initial release: four-phase pipeline (Brief Builder, Copy Agent, Design Agent, QA Validator) with human review gates. Consumes L0+L1 context, produces `.claude/deliverables/campaigns/<slug>/` (brief.md, copy.md, page.html, qa-report.md).
