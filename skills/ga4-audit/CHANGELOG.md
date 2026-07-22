# Changelog

## [2.5.0] - 2026-07-22

### Added
- KB-native output (dual-mode). When the working repo declares a CRO knowledge base binding, the skill writes the performance profile as a typed `silver-performance-analysis` artifact at `reference/cro-{scope}/performance-analysis.md` instead of `.claude/context/performance-profile.md`. New `--scope` (KB scope, distinct from the analytics `--scope-page-contains`/`--scope-host` sub-property filters) and `--no-kb` flags. Mode resolution mirrors the canonical `modules/kb-mode.md` contract (binding-detects-mode, no `--kb` force flag, HARD STOP on missing/invalid scope). `depends_on` is empty by default for query-time first-party analytics (provenance is the property id + date range); one optional same-layer edge if the KB declares an analytics-reference artifact the run consumed. `schema_version: "2.3"` and the full field set ride along in the KB artifact frontmatter. Legacy behavior is byte-unchanged when no binding is detected. Cross-skill schema-version contract now explicit in `schemas/performance-profile.md`. [audit-skills-kb-native-writes]

## [2.4.1] - 2026-07-05

### Fixed
- Repo-audit convention fix, no content change: the top-level Quality Checks section moved after Data Source Routing so the file ends with the quality checklist (the dev rules require quality checks at the end). Pure section reorder; every line is unchanged.

## [2.4.0] - 2026-06-11

### Added
- Element-interaction and measurement-integrity capture by default: --scope-page-contains/--scope-host flags applied as a dimensionFilter to every report; event-liveness in Step 3 (dead bindings plus zero-crossings); Step 5b reworked to drop the silent skip, always enumerate autotrack linkText/linkUrl and the scoped page set, and add element events to trends; friction pass over event names and linkText; element-instrumentation and a new Measurement Integrity section promoted to REQUIRED; performance-profile schema_version 2.3. [audit-skills-interaction-measurement-capture]
