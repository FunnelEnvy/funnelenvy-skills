# Changelog

## [1.0.1] - 2026-07-05

### Fixed
- Repo-audit contract completion, no behavior change: added the per-agent Model Selection table (the skill spawns two subagents; the bare Model line did not satisfy the convention), the `updated` frontmatter field, and this changelog.

## [1.0.0] - 2026-03-25

### Added
- Initial release: two sequential agents (Extract + Analyze) producing a standalone `brand-voice.md` L1 context file (tone spectrum, vocabulary fingerprint, example library, consistency map, voice rules) plus the operational `_voice-extractions.md`. Observe and compare modes; brand-doc auto-detection; does not require positioning-framework first.
