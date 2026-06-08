# Changelog

## [Unreleased]

### Fixed
- Module resolution hardening: the `modules/slugify.md` reference now states that `modules/` is repository-root-relative (a sibling of `skills/`, not inside the skill folder) with symlink-aware resolution for isolated or installed invocations (e.g., `~/.claude/skills/render-default-deliverables/`), and documents an explicit fallback slug rule (lowercase, non-alphanumerics to single hyphens, collapse, trim) to apply with a run-output note if `slugify.md` cannot be read, rather than guessing slug formats.

## [1.0.0] - 2026-02-20

### Added
- Initial release: L2 rendering skill that consumes L0 + L1 context and produces human-readable deliverables (executive summary, messaging guide, competitive comparison matrix, battle cards). No research, no analysis, no web fetches.
