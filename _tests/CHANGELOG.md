---
fe-managed: true
name: tests-changelog
description: Changelog for the automated test suite.
governed_by: change-management/changelog
managed_by: change-management
version: "1.0.0"
created: 2026-09-22
updated: 2026-09-22
title: Changelog
---
# Changelog

## [Unreleased]

### Changed
- `CLAUDE.md` body synced with fe-sys-hq `_tests` v1.7.1 (fe-sys-hq v3.24.0): `Assertion causality` requires running the fail-first proof against the pre-change code and recording a partition line, a cited pre-existing test is proven by mutation, and `Change-management integration` splits the proof across Design, Build and QA

## [1.0.0] - 2026-09-22

### Added

- `_tests` becomes a managed resource. `CLAUDE.md` and `README.md` arrive from fe-sys-hq's `test-suite-rightsizing` change, carrying the `Test Necessity` and `Test-Verdict Integrity` rules and the suite's layout and conventions. Both bodies are identical across the six `_tests` repos; frontmatter stays per repo.
