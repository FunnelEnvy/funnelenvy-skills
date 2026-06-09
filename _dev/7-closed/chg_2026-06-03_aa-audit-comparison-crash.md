---
fe-managed: true
name: aa-audit-comparison-crash
description: >
  Fix aa_audit.py crash during the comparison-period fetch: _normalize_value raises TypeError
  ("'<=' not supported between instances of 'int' and 'str'") when the Reports API returns a
  string cell value. Add a type guard and a regression test; --no-compare is the current
  workaround.
governed_by: change-management/change-document
status: Closed
resource_name: aa-audit
resource_version: "TBD"
impact: 2
confidence: 5
ease: 5
version: "0.4.0"
created: 2026-06-03
updated: 2026-06-03
---
# AA Audit Comparison-Period Crash

## Background

Hit live on 2026-06-03 during an aa-audit run: the main-period fetch completed, then the comparison-period `fetch_page_performance` call crashed in `_normalize_value` (`aa_audit.py:343`) because a report row cell arrived as a string and the bounds check `0 <= value <= 1` raised TypeError. The whole run's stdout was lost (JSON never emitted). Re-running with `--no-compare` succeeded.

## Current State

- `_normalize_value(name, value)` assumes numeric cells; the Reports API can return strings (e.g., "NaN" or locale-formatted values) in comparison windows.
- `parse_report_rows` passes raw cell values straight through.
- No tests exist for the parse path.

## Approach

Coerce cell values to float with a safe fallback (non-numeric → 0.0 with a stderr warning) in `_normalize_value` — the shared per-cell choke point used by both `parse_report_rows` and `extract_summary` — so all downstream math is type-safe regardless of which fetch path produced the cell; keep `--no-compare` semantics unchanged. Add unit coverage for string/NaN cells.

## Requirements

1. Add `_coerce_cell(name, value)` to `aa_audit.py`: attempts `float(value)`; on `TypeError`/`ValueError` or NaN result, returns `0.0` and emits a one-per-metric-name warning to stderr (stdout is reserved for the JSON payload).
2. `_normalize_value` calls `_coerce_cell` before the bouncerate bounds check, covering both `parse_report_rows` and `extract_summary` call paths.
3. No behavior change for numeric cells; bouncerate 0-1 → 0-100 normalization unchanged.
4. New `_tests/unit/test_aa_audit.py` loading `aa_audit.py` via importlib (hyphenated skill dir is not importable), covering: string-numeric cells, "NaN" strings, NaN floats, non-numeric garbage, and the bouncerate normalization path through both `parse_report_rows` and `extract_summary`.
5. `_tests/` scaffold (`__init__.py` files) created at repo root per the fe-sys-hq `_tests/{layer}/` architecture — first test in this repo.

## Validation

1. `python -m unittest _tests.unit.test_aa_audit -v` — all tests pass.
2. Live end-to-end: full `--days 90` run with comparison enabled against the known-crashing case (a client report suite via that client's AA config) completes and emits valid JSON including the `comparison` block. Pre-fix this run reproduces the TypeError at `aa_audit.py:343`.

## Changelog

| Version | Changes |
|---------|---------|
| 0.4.0 | QA → Closed: user approved QA 2026-06-03; unreleased changelog entry added to new skills/aa-audit/CHANGELOG.md (first CHANGELOG for this skill). |
| 0.3.0 | Build → QA: fix implemented (_coerce_cell + _normalize_value), 13 unit tests passing, live end-to-end validation against a client report suite with comparison enabled completed (exit 0, comparison block emitted, coercion warning observed on the previously-crashing bouncerate cell). |
| 0.2.0 | Backlog → Build (expedited per user direction): Requirements and Validation filled; coercion point refined to `_normalize_value` choke point covering both parse paths. |
| 0.1.0 | Initial backlog change document — TypeError crash observed live 2026-06-03; --no-compare workaround documented. |
