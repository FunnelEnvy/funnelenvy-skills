# Changelog

## [1.1.0] - 2026-11-23

### Added
- KB mode (dual-mode I/O). When the working repo declares a CRO knowledge base binding, the skill amends the scope's `bronze-company-facts`, `silver-strategy-context` and optional L1 silver artifacts instead of `.claude/context/` files. It finds them by type, routes L0 items between the two L0 artifacts by positioning-framework's section table, and keeps the change plan, surgical edits, provenance comments and proof-point ID rules. Mode resolution follows `modules/kb-mode.md`: binding detects the mode, no `--kb` force flag, HARD STOP on a missing or invalid `--scope`, and `--no-kb` forces legacy. The input must be a bronze capture inside the KB, cited in `depends_on` where the type declares it. With kb-start loaded, its `Artifact Write Routing` governs each write; without it, a `kb_type_validate.py` gate runs once per amended artifact. Step 6 lists stale silver dependents and the scope's experiment roadmap. [positioning-update-kb-mode]
- `--provenance client|research` flag, default `client`. Research input gets `origin: research` comments, no `has_client_input` and the standard confidence rules, so the skill can refresh positioning from a research extraction. In KB mode, `client` input sets `data_provenance: client` where the type declares the field, and `research` input never downgrades it. [positioning-update-kb-mode]

### Fixed
- Step 7 now passes the run's mode to render-default-deliverables. Legacy mode invokes it with `--no-kb`, which fixes the re-render stopping on a missing `--scope` in a repo with a KB binding. KB mode finds the scope's gold deliverables by type and invokes it with `--scope`. The `--context-dir` note no longer claims the render reads a fixed directory. [positioning-update-kb-mode]

## [1.0.1] - 2026-07-05

### Fixed
- Repo-audit doc corrections, no behavior change: the two Confidence Rules references to a bare `agent-header.md` now point explicitly to `skills/positioning-framework/agent-header.md` (this skill has no agent-header of its own; the bare reference was dangling). Added `updated` frontmatter field and this changelog.

## [1.0.0] - 2026-03-17

### Added
- Initial release: single-agent client feedback amendment skill. Parses freeform feedback, classifies into six change types (CORRECT, ADD, REMOVE, AMEND, CONSTRAINT, GAP), presents a structured change plan for approval, executes surgical edits to L0+L1 context files, and triggers deliverable re-render. Client > tier-0 > research authority; corrections are upgrades; proof point IDs immutable.
