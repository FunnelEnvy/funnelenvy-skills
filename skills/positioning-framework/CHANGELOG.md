# Changelog

## [1.1.2] - 2026-07-05

### Fixed
- Repo-audit schema alignment, no behavior change: `phases/company.md` now lists Homepage Messaging as numbered body section #15 (REQUIRED) in the inline schema enumeration and adds it to the completeness checklist (the construction instructions existed but the numbered list stopped at #14, so the authoritative schema never declared the section it required agents to build); the reference copy `schemas/company-identity.md` drops its "Top Landing Pages" sub-table, which nothing in the repo produces or consumes (reference-copy drift; the phase file is authoritative). Also: `schemas/competitive-landscape.md` gains the missing #13 Post-Research Questionnaire section its own completeness checklist already required (matching `phases/competitive.md`), and real company names in `phases/competitive.md` example questions were replaced with fictional placeholders per the public-repo rule. Also gains the `modules/kb-mode.md` canonical-contract pointer in its KB-mode section (drift canary enforced by `scripts/registry_check.py`). Structural: the quick-depth readout template, tips, quality rules, and context-file spec (~148 lines) moved verbatim to new `phases/quick-readout.md`, read by the orchestrator only on quick-depth runs (STOP if unreadable); Orchestrator Quality Checks moved to the end of SKILL.md per the quality-checks-last convention. SKILL.md shrinks from 1056 to ~915 lines with no wording changes.

## [1.1.1] - 2026-06-11

### Fixed
- Module resolution hardening: agent-header.md (shared by all agents) and SKILL.md now state that modules/<name>.md references are repository-root-relative (a sibling of skills/) with symlink-aware resolution for isolated or installed invocations, and require agents to STOP and report rather than proceed on a remembered extraction or assessment protocol when a required module cannot be read. The orchestrator falls back to the 5 intake questions when modules/business-brief.md is unreadable.

## [1.1.0] - 2026-06-03

### Added
- Dual-mode output (KB mode): writes typed bronze/silver artifacts into a client knowledge base when a KB binding is detected; --scope and --no-kb flags; KB prior-work detection by frontmatter; post-write validation gate; legacy .claude/context/ behavior unchanged (chg_2026-06-03_positioning-framework-kb-native-writes)

## [1.0.0] - 2026-05-15

### Added
- Initial consolidated release: positioning, competitive research, and messaging framework with depth levels (quick/standard/deep), 4-agent orchestration, prior work detection, and GA4-guided page selection
