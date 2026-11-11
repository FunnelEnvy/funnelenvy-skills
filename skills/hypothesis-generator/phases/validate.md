# Phase 4: Per-Row Checks

This phase checks every consolidated row against the evidence already loaded. It maps what it finds to blockers, which set the row's readiness tier in `rank`, and to annotations. It never removes a row. It performs no web research and writes nothing to disk except the row fields below.

## Output Per Row

Add to each row in the `consolidate` output:

- **`blockers`:** append any blocker below that applies, without duplicating one the lens set.
- **`blocker_reasons`:** an object mapping each blocker on the row to a one-line reason in plain words. It renders as the write-up's `**Readiness:**` line or the backlog row's `Readiness` cell. Lens-set blockers need a reason too; take it from the row's annotations or evidence.
- **`annotations`:** append any annotation below.
- **`validation_gates`:** one verdict per gate, `pass`, `fail` or `not-assessed`, each with a one-line note.

`not-assessed` means the backing artifact is absent. It is neutral: it adds no blocker.

## Blockers

| Evidence | Blocker |
|---|---|
| The primary metric is genuinely dark (`metric_instrumented` fails on the primary) | `metric-not-tracked` |
| No baseline for the primary metric on an instrumented surface, a refused or undatable window, or a documented data gap (`baseline_exists` fails) | `no-baseline` |
| The captured control is stale or contested, or the current state cannot be confirmed (`control_stable` fails); a confirm-first lever | `verify-current-state` |
| The read cannot work as designed but a redesign could (`powerable` or `segmentation_satisfied` fails); a broken mobile render; a strategic design that needs a disqualified baseline | `design-change` |
| Another artifact contradicts the premise (`premise_contradicted` fails); a blocking engagement constraint; a change so obvious it should ship rather than be tested | `client-decision` |

Traffic alone never sets a blocker. A row too slow for an A/B read already carries a directional or pre/post read model from the script.

**Annotations only, never a blocker:** a running experiment on the surface, contrarian counter-evidence, a partial pattern match, a guardrail metric that is dark while the primary is tracked, and an unregistered proof number.

## Tactical Gates

### `premise_contradicted`

The premise is the row's causal claim about why the page underperforms. Check it against every loaded artifact that bears on it. On conflict, authority runs measured performance, then observed structure, then inferred positioning.

- Highest-authority artifact corroborates: `pass`.
- It contradicts (the row says clutter suppresses conversion; the profile classifies the page as a deep-engagement demand problem): `fail`. Note which artifact contradicts.
- Only one artifact bears on it: `not-assessed`.

A refused profile window counts as absent here.

### `metric_instrumented`

Build the measurement inventory once per run:

- **Instrumented:** metrics the performance profile reports data for, plus metrics any other loaded artifact documents as live, in production or already reporting. Tag the second kind `live-elsewhere`.
- **Dark:** metrics the profile lists as data gaps, or that context names but nothing documents as live. A metric the profile is silent on and no artifact documents live is dark.

Then, per row:

- No performance profile: `not-assessed`.
- Primary and guardrail instrumented: `pass`. For a `live-elsewhere` metric, add the prerequisite "confirm the live [capability] fires on this surface before launch". That is a check, never a build.
- Primary dark: `fail`, blocker `metric-not-tracked`, and a build prerequisite naming the instrumentation.
- Guardrail dark, primary tracked: `pass` with an annotation and a build prerequisite.

### `baseline_exists`

- Baseline present, and its window counts under `Measurement-Regime Boundary` in `SKILL.md`: `pass`.
- A governing boundary refuses the window, or it is undatable: `fail`. Note the boundary date and its change text.
- Profile present but no baseline for the target surface: `fail`.
- No profile: `not-assessed`.

### `control_stable`

Read the structural capture's date and compare artifacts that describe the same element.

- Recent, uncontested capture: `pass`. An old but uncontested capture adds the prerequisite "verify the current page before launch".
- Two artifacts describe the element differently (a redesign may be in progress), or the capture is stale enough that the control likely changed: `fail`.
- No structural capture: `not-assessed`.

A broken mobile render is not a staleness signal. It sets `design-change` through the contrarian annotation, not this gate.

### `powerable`

This gate covers designs the row's read model cannot rescue:

- A pre-registered segment too small to read, a guardrail that cannot be read in the window, or a bundled thesis element seen by few visitors or not the dominant change: `fail`.
- Otherwise `pass`. Raw traffic is the read model's job, not this gate's.
- Non-A/B testing method, or no profile: `not-assessed`.

### `segmentation_satisfied`

- A pre-registered segment the platform can target and read: `pass`.
- A segment that cannot be isolated or read: `fail`, plus an instrumentation prerequisite.
- No segment pre-registered: `pass`.
- Non-A/B testing method, or no profile: `not-assessed`.

## Strategic Gates

`powerable` and `segmentation_satisfied` read `not-assessed` unless the strategic row's design is `ab`.

- **baseline_reliable:** for a pre/post read or a matched holdout that depends on history. `fail` when the loaded context documents the comparison window as unreliable (a tracking break, a conversion event that stopped firing, an unreconciled contradiction) or the boundary refuses it; the reason names a forward-only or randomized read as the fix. `pass` when the context does not disqualify it. `not-assessed` for randomized designs or no performance context.
- **metric_instrumented:** as the tactical gate, on the business metric. A metric readable only after this run's own Measurement Foundation entry fails, with the blocker `metric-not-tracked` naming that entry. When a readable-today metric can carry the read, prefer it.
- **premise_contradicted:** as the tactical gate. An unreconciled quantitative contradiction the lever's scoping depends on is a `fail`.

## Live Program

Read the history source for experiments running or queued, and for fold decisions on record. Match each row by surface and by lever class (headline and messaging, proof and trust, form, CTA, navigation, layout, pricing, personalization).

| Program state | Annotation |
|---|---|
| A running or queued experiment on the same surface and lever class, or a recorded fold covering them | "runs inside or after [the experiment, in plain words]: re-sync with it and read it cleanly", with a pointer to any copy this row developed |
| A running experiment on the same surface, different lever class | "runs after [the experiment] concludes on this page" |
| Ambiguous or on-hold status on the surface | "confirm [the experiment] has concluded before launch" |
| A concluded experiment | No annotation. A concluded test frees the surface |
| No history source bound | No annotation. In KB mode, add the prerequisite "live experiment program not reconciled: connect the completed-experiment knowledge base" |

Tactical rows only; the script already pairs strategic and tactical rows that share a mechanism. The annotation must name the experiment, because the render places it in `**Notes:**` or the backlog `Readiness` cell.

## Prerequisites

Collect, for the `Prerequisites and Data Gaps` method section, each item naming the affected rows by key:

- **Missing baseline data:** what is missing, which rows, how to collect it. When the boundary refuses the profile's primary window, add one line naming the window, the boundary date and its change text, and asking for a baseline that starts on or after that date.
- **Verification needed:** claimed-only proof, unregistered numbers, `[NEEDS CLIENT INPUT]` or `[NEEDS CONFIRMATION]` sections, verify-first contrarian checks, old captures, `live-elsewhere` confirmations.
- **Infrastructure:** dark metrics to instrument, targeting or personalization tooling, non-isolable segments.
- **Inputs not loaded:** for example "Run /ga4-audit for data-calibrated sizing and traffic-driven hypotheses" or "Run /live-capture for structure-driven candidates".
