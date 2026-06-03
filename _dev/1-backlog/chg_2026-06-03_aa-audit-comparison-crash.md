---
fe-managed: true
name: aa-audit-comparison-crash
description: >
  Fix aa_audit.py crash during the comparison-period fetch: _normalize_value raises TypeError
  ("'<=' not supported between instances of 'int' and 'str'") when the Reports API returns a
  string cell value. Add a type guard and a regression test; --no-compare is the current
  workaround.
governed_by: change-management/change-document
status: Backlog
resource_name: aa-audit
resource_version: "TBD"
impact: 2
confidence: 5
ease: 5
version: "0.1.0"
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

Coerce cell values to float with a safe fallback (non-numeric → 0.0 or None with a logged warning) at the `parse_report_rows` boundary so all downstream math is type-safe; keep `--no-compare` semantics unchanged. Add unit coverage for string/NaN cells.

## Requirements

Stub — filled during Design.

## Validation

Stub — filled during Design. Must include a unit test feeding string cells through parse_report_rows and a full --days run with comparison enabled completing end-to-end.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial backlog change document — TypeError crash observed live 2026-06-03; --no-compare workaround documented. |
