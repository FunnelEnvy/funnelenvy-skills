---
fe-managed: true
name: tests-claude
title: Automated Test Suite
description: >
  Agent-optimized context for this repo's automated test suite. Test-running commands,
  authoring conventions, test-necessity and test-verdict-integrity rules, and
  change-management integration for the Design/Build/QA test lifecycle.
governed_by: document-management
managed_by: change-management
version: "1.0.0"
created: 2026-09-22
updated: 2026-09-22
---
# Automated Test Suite

Automated test suite for this repo's Python scripts. stdlib `unittest` infrastructure with a three-layer architecture, fixture-based testing, and a script coverage floor. Load `change-management` before working with test lifecycle operations. Load `document-management` before reviewing or editing managed files in this directory.

## Architecture

| Directory | Purpose |
|---|---|
| `unit/` | Pure function-in, value-out tests — no side effects |
| `functional/` | Public function contracts and CLI output — `tempfile` only |
| `integration/` | Composition chains and cross-module import resolution — `tempfile` only |
| `fixtures/` | Static purpose-built `.md` files for read-only fixture tests |
| `_dev/` | Change documents for test infrastructure changes |

## Operations

- **Running tests in-session**: Use `python -m unittest discover _tests/ -v` for the full suite, `python -m unittest discover _tests/{layer} -v` for a single layer, and `python -m unittest _tests.{layer}.test_{script_name} -v` for a single file. A full-layer or full-suite run can take minutes. Let it finish rather than killing it, and run it in the background if you need the session free. A long run is not a hang, but it is not automatically a normal cost either: one file carrying most of a layer's time is a `Test Necessity` H4 target.
- **Authoring tests**: Test files follow `test_{script_name}.py` in the correct layer directory (`unit/`, `functional/`, or `integration/`). Use `unittest` (stdlib) only — no pytest, no pip. Every script the repo owns must have at least one test case. That is a floor, not a target; `Test Necessity` H6 governs everything above it. Every test MUST satisfy `Test Necessity` and `Test-Verdict Integrity` below.
- **Authoring fixtures**: Static fixtures are small purpose-built `.md` files checked into `fixtures/` for read-only patterns. Programmatic fixtures are created via `tempfile`, using the repo's shared fixture helpers where they exist. `Test Necessity` H4 governs whether a test builds its own, copies one, or shares one. Tests must clean up after themselves.
- **Change-management integration**: Design's `Test design analysis` captures coverage planning in the change document's `Verification Design > Tests` subsection. The Build step runs `python -m unittest _tests.{layer}.test_{script_name} -v` for each new or modified script and authors new test files and fixtures per the design. The QA step runs the full suite as pre-QA verification.

## Test Necessity

A test case MUST earn its place, and no two cases may earn it the same way. A case buys detection (it fails when someone breaks the behavior it names), a contract record (it states what a script promises its callers), or refactor cover (internals can change while behavior holds). It costs wall-clock, authoring friction on every edit to the script, and failure noise when redundant cases fail together. `Test Necessity` asks whether a case should exist; `Test-Verdict Integrity` asks whether its verdict means anything. They are one property checked at two moments.

These rules bind a case as you author or modify it. Removing existing cases under them is its own change.

**H1. A case names what breaks at the boundary.** A case earns its place by saying, in one line, what an outside consumer would observe differently if the behavior changed: a message, an exit code, an output key, a file on disk, a dispatched argv. Reaching the behavior through internals is fine. The boundary consequence is what has to be nameable. The failing shape is a case whose only account of itself is that a function exists, returns a value, or has a particular signature.

- **Citations must resolve.** Where a case leans on a requirement number, a prior defect, or a sibling test, that reference must be findable. An unresolvable citation is a finding, not decoration.
- **A test of the test file's own helpers is not a test of the script.** It is permitted, and it counts neither toward nor against the script's budget.

**H2. One case per distinct observable, plus one per reachable path that differs.** The budget unit is what the surface produces that a caller acts on: each happy path, each distinct operator-facing message or verdict, and each flag combination that changes output.

- **Not exit codes.** One code often carries several messages with different remedies, and a caller branches on the message. Counting by code understates the budget and drives a reviewer to cut message contracts.
- **Count it this way.** Enumerate the script's own message or refusal set, then multiply by the reachable paths that genuinely differ. Add the output-changing flag combinations and the subcommands' happy paths. The result is a floor to reason from, not a quota.
- **Collapse rule.** Cases differing only in fixture shape collapse to one. Cases differing in the message a caller acts on do not.
- **A parametrized mirror states its discriminator.** Re-running a case set under a second configuration needs a one-line statement of what the second run can catch that the first cannot. Without it, the mirror is a duplicate.

**H3. Test at the cheapest layer that can observe the promise, and assert it once.** Unit is cheapest, then functional, then integration. The `Architecture` table defines what each layer can observe: a promise that needs a real repo or a file on disk is not unit-observable, so functional is its cheapest layer. Once a promise is asserted at its cheapest layer, do not assert it again higher up unless the wiring itself is the promise.

**H4. Copy an expensive fixture; share it only when you cannot copy it.** Ask whether the fixture can be copied before asking whether it can be shared. A copy preserves per-test isolation exactly, so it needs no mutation analysis. Build once per module and hand each case a fresh copy. Reach for class-scoped sharing only where copying is impossible (a live process, a socket, an external resource) or where copying is itself too slow.

- **Know the fixture's cost.** A fixture that spawns subprocesses or builds a directory tree gets its construction time measured once and recorded beside it. A tenth of a second reads as free, and at a hundred calls it is not. Measure the copy too: on a slow filesystem it can cost as much as the build.

**H5. Protect the cases that cannot be rebuilt.** A case asserting an absence (a retired exit code, a deleted predicate, a withdrawn sentence, an instruction that must not reappear in generated output) is not removable on the grounds that nothing exercises it. The code it guards is already gone, so nothing is left to attach a replacement to. It reads as an obvious cut and is the opposite.

- **Positive controls need a bound.** A case labelled as passing both ways by design is exempt from the fail-first check in `Assertion causality`, which makes it the cheapest kind to over-add. A change adding more than a couple states why in its change document.
- **One mechanical removal shortcut stands:** a case asserting something the framework or the standard library already guarantees can go.

**H6. Script coverage is a floor, not a target.** The coverage requirement in `Operations` means at least one case per script. It does not mean a case for every function and branch. Read that way, it ratchets the suite upward on every change, and this rule leaves that reading nothing to cite.

## Test-Verdict Integrity

A test's verdict MUST be caused by the behavior it names, and by nothing else. The two rule families below are that one property read at two scopes: the host must not decide the verdict, and the assertion must be caused by the behavior under test. Both are instances of the general property, so a cause not listed here is still governed by it.

**Scope.** These rules bind a test as you author or modify it. They are not a claim that the existing suite already complies. Bring a site into compliance when you touch it. Sweeping an unswept surface is its own change, not a widening of whatever change brought you here.

### Host independence

A test MUST NOT let the host decide its verdict. Each rule names its operative mechanism.

- **Absolutize an expected absolute path the way the code under test does** — `os.path.abspath`, never `os.path.normpath` over a hardcoded POSIX literal. `normpath('/a/b')` yields a drive-letter-free path on Windows and will not equal the drive-lettered result the code returns.
- **Isolate the home directory by setting both `HOME` and `USERPROFILE`**, never `HOME` alone. `ntpath.expanduser` reads `USERPROFILE` and never consults `HOME`, so a `HOME`-only isolation silently runs the test against the real user profile.
- **Compare paths in one separator form** when the other side is rendered by git or by a JSON serializer, which always emit forward slashes. Convert the **expected** side to forward slashes only. Re-normalizing the observed side would let a real separator defect through.
- **Remove a fixture tree in a way that tolerates read-only files**, never with a bare `shutil.rmtree`. git writes committed object files read-only, and Windows refuses to unlink them, so the removal has to clear the read-only bit and retry. A teardown that passes `ignore_errors` never raises and sits outside this rule; its defect is the silent swallow, not an unlink failure.
- **Name the codec on any `subprocess.run` whose output is decoded** — `encoding='utf-8'`, never `text=True` alone. `text=True` decodes with the host locale codec, so a child's UTF-8 arrives mojibaked under cp1252.
- **Gate on a capability probe where the test needs an OS capability the host may withhold**, such as creating a symlink, via `@unittest.skipUnless`. Skip rather than fail, and gate the whole test rather than only its positive assertions. Never weaken an assertion to something the incapable host can satisfy; that trades a false failure for a false pass.

### Assertion causality

A green assertion MUST be caused by the behavior under test.

- **Isolate the key under test in a multi-key sort.** Build the fixture so the primary key opposes every lower-priority tie-break. A case whose name order agrees with its score order passes with the score key ignored entirely.
- **Cover every reachable branch you claim.** A suite claiming exhaustive coverage of a decision table or mode branch MUST carry one case per reachable branch the design enumerates.
- **Show a new or modified test to FAIL against the pre-change code** before its coverage claim is accepted. Where a case is a deliberate positive control, asserting something the change must *not* alter, label it as one, so "passes both ways" reads as recorded intent rather than an unexamined result.
