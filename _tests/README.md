---
fe-managed: true
name: tests
description: >
  Automated test suite for this repo's Python scripts. stdlib-only unittest
  infrastructure with fixture-based testing, three default layers
  (unit/functional/integration) plus an opt-in live layer, and a script
  coverage floor.
governed_by: document-management
managed_by: change-management
version: "1.1.0"
created: 2026-09-22
updated: 2026-11-12
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

# Live layer: only after the owner approves the run (see CLAUDE.md, Live Tests)
FE_LIVE_TESTS=1 python -m unittest discover -s _tests/live -t . -v

# Single file
python -m unittest _tests.{layer}.test_{script_name} -v
```

## Architecture

Three default layers with increasing scope, plus an opt-in `live/` layer:

| Layer | Purpose | Side Effects | Speed |
|---|---|---|---|
| Unit | Pure function-in, value-out tests | None | Fast |
| Functional | Public function contracts, CLI output | `tempfile` only | Medium |
| Integration | Composition chain, import resolution | `tempfile` only | Slower |
| Live | Checks against a live external service | Guarded writes to the real service, deleted in cleanup | Network-bound |

The `live/` layer runs only when `FE_LIVE_TESTS=1` is set in the run's own environment, never from `.env`. Default runs, the change-management §5 Build and §6 QA runs included, report it as skipped, and it counts nothing toward the coverage floor. [CLAUDE.md](CLAUDE.md) `Live Tests` holds its rules.

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
├── live/           # Opt-in tests against a live service
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
