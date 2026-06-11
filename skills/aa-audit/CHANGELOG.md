# Changelog

## [1.1.0] - 2026-06-11

### Fixed
- Comparison-period fetch crash: `_normalize_value` raised TypeError when the Reports API returned string cells (e.g., "NaN") in comparison windows; cells now coerce safely to float with 0.0 fallback and a stderr warning, with unit coverage in `_tests/unit/test_aa_audit.py` (chg_2026-06-03_aa-audit-comparison-crash)

### Added
- Element-interaction and measurement-integrity capture by default: optional `scope` config (segment or entry/page prefix) applied to every report; `interaction_dimensions` array (default customlink/clickmaplink/clickmappage, eVar override retained); scoped element enumeration via a broad single-token prefix search; `event_liveness` audit (dead bindings plus dark/spiked regressions across the comparison period); script-owned friction tagging (`is_friction_token`); element-instrumentation and a new Measurement Integrity section promoted to REQUIRED; performance-profile schema_version 2.3. Backward-compatible (unset scope reproduces prior behavior). [audit-skills-interaction-measurement-capture]
