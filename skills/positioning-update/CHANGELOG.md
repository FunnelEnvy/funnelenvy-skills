# Changelog

## [1.0.1] - 2026-07-05

### Fixed
- Repo-audit doc corrections, no behavior change: the two Confidence Rules references to a bare `agent-header.md` now point explicitly to `skills/positioning-framework/agent-header.md` (this skill has no agent-header of its own; the bare reference was dangling). Added `updated` frontmatter field and this changelog.

## [1.0.0] - 2026-03-17

### Added
- Initial release: single-agent client feedback amendment skill. Parses freeform feedback, classifies into six change types (CORRECT, ADD, REMOVE, AMEND, CONSTRAINT, GAP), presents a structured change plan for approval, executes surgical edits to L0+L1 context files, and triggers deliverable re-render. Client > tier-0 > research authority; corrections are upgrades; proof point IDs immutable.
