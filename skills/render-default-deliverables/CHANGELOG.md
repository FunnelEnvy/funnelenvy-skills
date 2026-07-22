# Changelog

## [1.1.0] - 2026-07-22

### Added
- KB-native I/O (dual-mode). When the working repo declares a CRO knowledge base binding, the skill reads the scope's silver artifacts (`silver-strategy-context` + `bronze-company-facts` as the L0 equivalent, plus optional `silver-positioning-scorecard` / `silver-audience-analysis` / `silver-competitive-analysis`) and writes the deliverables as typed gold artifacts: `gold-strategy-deliverable` (executive-summary, messaging-guide, competitive-comparison-matrix, distinguished by `deliverable_type`) at `deliverables/{scope}-*.md` and `gold-battle-card` (one per competitor) at `battle-cards/{scope}-{competitor}.md`, each carrying gold-to-silver `depends_on`. New `--scope` and `--no-kb` flags. Mode resolution mirrors the canonical `modules/kb-mode.md` contract (binding-detects-mode, no `--kb` force flag, HARD STOP on missing/invalid scope). Deliverable bodies are byte-identical to legacy; only gold frontmatter is prepended, and the `Deliverable Purity Constraint` still governs the body. `manifest.md` is not written in KB mode (the KB artifact graph is the index). This closes the gap that made positioning-framework skip its render auto-invoke in KB mode. [render-deliverables-kb-native]

## [1.0.2] - 2026-07-05

### Fixed
- Repo-audit contract completion, no behavior change: added the Model declaration (Opus; previously the only skill besides render-program-site with no model line anywhere). Preconditions now state the KB-mode position explicitly: no KB read path yet, positioning-framework skips the auto-run in KB mode, and the legacy workaround is `--no-kb` (this was documented on the positioning-framework side only).

## [1.0.1] - 2026-06-11

### Fixed
- Module resolution hardening: the `modules/slugify.md` reference now states that `modules/` is repository-root-relative (a sibling of `skills/`, not inside the skill folder) with symlink-aware resolution for isolated or installed invocations (e.g., `~/.claude/skills/render-default-deliverables/`), and documents an explicit fallback slug rule (lowercase, non-alphanumerics to single hyphens, collapse, trim) to apply with a run-output note if `slugify.md` cannot be read, rather than guessing slug formats.

## [1.0.0] - 2026-02-20

### Added
- Initial release: L2 rendering skill that consumes L0 + L1 context and produces human-readable deliverables (executive summary, messaging guide, competitive comparison matrix, battle cards). No research, no analysis, no web fetches.
