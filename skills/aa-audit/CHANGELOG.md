# Changelog

## [Unreleased]

### Fixed
- Comparison-period fetch crash: `_normalize_value` raised TypeError when the Reports API returned string cells (e.g., "NaN") in comparison windows; cells now coerce safely to float with 0.0 fallback and a stderr warning, with unit coverage in `_tests/unit/test_aa_audit.py` (chg_2026-06-03_aa-audit-comparison-crash)
