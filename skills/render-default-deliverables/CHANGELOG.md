# Changelog

## [1.2.0] - 2026-11-23

### Fixed
- KB mode now follows the bound gold type definitions, as `Schema Authority` already said it should. A new `Type Definition Read` step records each definition's allowed `deliverable_type` values, output path pattern and required fields before the plan. Each deliverable maps by meaning to one listed value, and its path is resolved from the pattern; no match, or more than one, is a HARD STOP. The fixed `competitive-comparison-matrix` value and the fixed `deliverables/` and `battle-cards/` paths are gone. Restated defaults in the completion message, the `Output location` line and the repo `CLAUDE.md` now point at the type definition. [render-default-deliverables-kb-type-authority]
- Gold frontmatter now adds `title`, `managed_by` and every field the type definition marks required, including a battle card's `competitor`. A required field that neither the skill nor the prior render supplies takes its stated default; with no stated default it is a HARD STOP before any write. In place of the old keep-only-`created` rule, an overwrite classes each prior field the skill does not set by its type definition. A field tied to a specific version, or to a review or send event, takes its stated default; with no stated default it is a HARD STOP. Other fields keep their value. The plan lists each reset and each kept non-default value, and asks Reset or Keep for a field whose definition is unclear; with no answer the run stops. The completion message repeats all three. [render-default-deliverables-kb-type-authority] [render-default-deliverables-kb-type-authority]
- The post-write gate ran one `kb_type_validate.py` call over several globs, which the validator rejects as a usage error, so it checked nothing. It now runs once per written artifact at its resolved path with `--artifact-type-path`, and fails on any non-zero exit or on a finding that the type layer did not run. [render-default-deliverables-kb-type-authority]

### Added
- Prior-render search. With nothing at an artifact's resolved path, the run searches that directory for an artifact of the same type, scope and `deliverable_type` (or `competitor`) and names each match in the plan. The plan asks for each match, and a bare proceed is not an answer. The operator answers Relocate (move it with the KB's own tooling, then re-run) or Confirm (write a first render); with no answer the run stops. The skill moves no file. [render-default-deliverables-kb-type-authority]

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
