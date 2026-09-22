---
fe-managed: true
name: tests
description: >
  Automated test suite for this repo's Python scripts. stdlib-only unittest
  infrastructure with fixture-based testing, three-layer architecture
  (unit/functional/integration), and a script coverage floor.
governed_by: document-management
version: "1.0.0"
created: 2026-09-22
updated: 2026-09-22
title: Tests
---
# Tests

Automated test suite for this repo's Python scripts. Uses stdlib `unittest` with no external dependencies, so any machine with Python can run the tests.

Tests here are sized by what callers depend on, not by what the code contains. A case earns its place by naming something an outside consumer would see break, and it is asserted once, at the cheapest layer that can observe it. The rules are in [CLAUDE.md](CLAUDE.md) under `Test Necessity`.

## Contents

- [Usage](#usage)
- [Architecture](#architecture)
- [Test Authoring Conventions](#test-authoring-conventions)
- [Fixture Conventions](#fixture-conventions)

## Usage

```bash
# All tests
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python); $PY -m unittest discover _tests/ -v

# Single layer
python -m unittest discover _tests/unit -v
python -m unittest discover _tests/functional -v
python -m unittest discover _tests/integration -v

# Single file
python -m unittest _tests.{layer}.test_{script_name} -v
```

## Architecture

Three-layer test architecture with increasing scope:

| Layer | Purpose | Side Effects | Speed |
|---|---|---|---|
| Unit | Pure function-in, value-out tests | None | Fast |
| Functional | Public function contracts, CLI output | `tempfile` only | Medium |
| Integration | Composition chain, import resolution | `tempfile` only | Slower |

### Directory Layout

```
_tests/
├── README.md       # This file
├── CLAUDE.md       # Agent-facing rules: Test Necessity, Test-Verdict Integrity
├── CHANGELOG.md    # Test infrastructure changelog
├── __init__.py
├── helpers.py      # Shared fixture helpers, where the repo has them
├── fixtures/       # Static fixtures
├── unit/           # test_{script_name}.py per script
├── functional/     # test_{script_name}.py per script
├── integration/    # test_{script_name}.py per composition
└── _dev/           # Change documents for test infrastructure changes
```

A repo carries only the layers and directories it needs.

## Test Authoring Conventions

- **Naming**: Test files follow `test_{script_name}.py` in the appropriate layer directory
- **Framework**: `unittest` (stdlib) only — no pytest, no pip
- **Assertions**: Use specific assertions (`assertEqual`, `assertIn`, `assertRaises`) over generic `assertTrue`
- **Test methods**: Name as `test_{behavior_being_tested}` — descriptive enough to diagnose failures without reading the test body
- **One concept per test**: Each test method verifies one behavior or edge case
- **No test interdependence**: Tests must not rely on execution order or shared mutable state across methods

## Fixture Conventions

### Static Fixtures

Checked into `_tests/fixtures/`. Small, purpose-built `.md` files, not copies of real repo documents. Each fixture tests one specific pattern or edge case. Read-only in tests.

### Programmatic Fixtures

Created via `tempfile`, using the repo's shared fixture helpers where it has them. Used by tests that need a directory tree or a git repo. A test gets its own fresh fixture, or a fresh copy of one built once, and cleans it up. When a fixture may be shared instead is in [CLAUDE.md](CLAUDE.md) under `Test Necessity` H4.
