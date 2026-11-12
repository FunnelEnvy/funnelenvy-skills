---
fe-managed: true
name: tests-changelog
description: Changelog for the automated test suite.
governed_by: change-management/changelog
managed_by: change-management
version: "1.1.0"
created: 2026-09-22
updated: 2026-11-12
title: Changelog
---
# Changelog

## [1.1.0] - 2026-11-12

### Added
- Opt-in `live/` layer synced from fe-sys-hq `_tests` v2.0.0 (fe-sys-hq v3.42.0): `CLAUDE.md` `Live Tests` section (v1.2.0), `README.md` layer row and run command, `helpers.py` `live_opt_in_skip_reason` and `LiveWriteGuard` with their unit and functional tests, and an empty `live/` package

### Changed
- `CLAUDE.md` body synced with fe-sys-hq `_tests` v1.7.1 (fe-sys-hq v3.24.0): `Assertion causality` requires running the fail-first proof against the pre-change code and recording a partition line, a cited pre-existing test is proven by mutation, and `Change-management integration` splits the proof across Design, Build and QA
- `CLAUDE.md` opening paragraph points to document-management's `docstring-standards` reference before any docstring write in this directory.

## [1.0.0] - 2026-09-22

### Added

- `_tests` becomes a managed resource. `CLAUDE.md` and `README.md` arrive from fe-sys-hq's `test-suite-rightsizing` change, carrying the `Test Necessity` and `Test-Verdict Integrity` rules and the suite's layout and conventions. Both bodies are identical across the six `_tests` repos; frontmatter stays per repo.
