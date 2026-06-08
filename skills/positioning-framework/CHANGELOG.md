# Changelog

## [Unreleased]

### Fixed
- Module resolution hardening: agent-header.md (shared by all agents) and SKILL.md now state that modules/<name>.md references are repository-root-relative (a sibling of skills/) with symlink-aware resolution for isolated or installed invocations, and require agents to STOP and report rather than proceed on a remembered extraction or assessment protocol when a required module cannot be read. The orchestrator falls back to the 5 intake questions when modules/business-brief.md is unreadable.

## [1.1.0] - 2026-06-03

### Added
- Dual-mode output (KB mode): writes typed bronze/silver artifacts into a client knowledge base when a KB binding is detected; --scope and --no-kb flags; KB prior-work detection by frontmatter; post-write validation gate; legacy .claude/context/ behavior unchanged (chg_2026-06-03_positioning-framework-kb-native-writes)

## [1.0.0] - 2026-05-15

### Added
- Initial consolidated release: positioning, competitive research, and messaging framework with depth levels (quick/standard/deep), 4-agent orchestration, prior work detection, and GA4-guided page selection
