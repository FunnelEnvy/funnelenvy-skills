# Changelog

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
