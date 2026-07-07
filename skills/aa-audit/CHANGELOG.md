# Changelog

## [1.1.1] - 2026-07-07

### Fixed
- Honest schema stamp: the emitted `performance-profile.md` stamped `schema_version: "2.3"` while omitting the seven `ai_*` AI-referrer frontmatter fields the shared schema declares mandatory from 2.2 ("always present, populated even when 0") -- a violation of the schema's own version-gating rule for consumers. Now stamps `"2.1"`, the highest version whose full REQUIRED field set this skill emits; the 2.3-era field groups it does emit (scope, element instrumentation, measurement integrity) are documented as additive above the stamp. `schemas/performance-profile.md` gains a Producer Variance note (report_suite in place of property_id/property_name; no ai_* fields; element data limited to non-page-associated `tracked_elements[]`), and SKILL.md documents the page-association limitation (AA element data carries no page association, so hypothesis-generator's page-level element triggers self-gate off; page-associated interactions via AA breakdown reports noted as a future enhancement).

## [1.1.0] - 2026-06-11

### Fixed
- Comparison-period fetch crash: `_normalize_value` raised TypeError when the Reports API returned string cells (e.g., "NaN") in comparison windows; cells now coerce safely to float with 0.0 fallback and a stderr warning, with unit coverage in `_tests/unit/test_aa_audit.py` (chg_2026-06-03_aa-audit-comparison-crash)

### Added
- Element-interaction and measurement-integrity capture by default: optional `scope` config (segment or entry/page prefix) applied to every report; `interaction_dimensions` array (default customlink/clickmaplink/clickmappage, eVar override retained); scoped element enumeration via a broad single-token prefix search; `event_liveness` audit (dead bindings plus dark/spiked regressions across the comparison period); script-owned friction tagging (`is_friction_token`); element-instrumentation and a new Measurement Integrity section promoted to REQUIRED; performance-profile schema_version 2.3. Backward-compatible (unset scope reproduces prior behavior). [audit-skills-interaction-measurement-capture]
