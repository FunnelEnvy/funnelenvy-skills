# Phase: Premise & Measurement Validation

This phase runs after construct (Phase 3) and before score (Phase 4). It is the single place where each hypothesis's premise, metric instrumentation, baseline, control stability, statistical power, and segmentation are checked against the artifacts already loaded. Construct produces hypotheses; this phase decides which of their claims actually hold on the page before score commits a Confidence number to them.

It performs NO web research and writes NOTHING to disk. It emits an internal per-hypothesis `validation_gates` record consumed by `phases/score.md`, exactly as construct's hypothesis record is internal. The gate record never appears in the deliverable (see SKILL.md `Deliverable Purity Constraint`).

## Required Inputs

- The construct hypothesis records (Phase 3 output): each hypothesis with its causal mechanism (`construct.md` Step 4), primary and guardrail metrics (Step 5 / 5a), Test Feasibility output (Step 5b), pre-registered segment (Step 5 segmentation pre-registration), and self-critique (Step 10).
- detect's Step 1f annotations: the measurement inventory (`instrumented_metrics` / `dark_metrics`) and the staleness signals (capture-date tags + cross-artifact element-disagreement). Absent legs read as not-assessed (see Graceful Degradation).
- The loaded performance / audience / competitive / structural artifact bodies already in context (carried forward from Phase 1), used for premise triangulation. No file is re-fetched; this phase reads what is already in context.

## Depth Behavior

This phase does not vary by depth. Every hypothesis is validated regardless of how it was produced or how the context was researched.

## Graceful Degradation

Each gate is evaluated only against the artifacts that exist. A gate whose backing artifact is absent is `not-assessed`, never `fail`. Absence never lowers Confidence on its own (the rule is stated verbatim under `Tri-state gate semantics` below).

| Missing Context | Gate behavior |
|----------------|---------------|
| performance-profile.md | `metric_instrumented` and `powerable` read `not-assessed` (no measurement inventory, no power determination). Neutral. No Confidence penalty beyond the existing performance-profile cap in `score.md`. |
| Structural observation artifact | `control_stable` reads `not-assessed` (no capture-date or element-disagreement signal available). Neutral. |
| No baseline for the target page | `baseline_exists` reads `fail` only when a baseline was expected and is genuinely absent on an instrumented surface; when no performance profile exists at all, it reads `not-assessed` (the global no-performance Confidence cap already applies in `score.md`). |
| Fewer artifacts than KB mode (legacy mode) | Triangulate across whatever artifacts exist. `premise_contradicted` can still fire when two present artifacts disagree; it reads `not-assessed` when only one artifact bears on the premise. Absence never sets a gate to fail. |

**Boundary: per-gate neutrality vs the global no-performance ceiling (these are two different mechanisms, not a contradiction).** Two absence rules coexist and must not be conflated:

1. **Per-gate neutrality (this phase).** An individual gate whose backing artifact is absent is `not-assessed` and applies NO Confidence penalty. This is a per-hypothesis, per-gate rule. It never caps.
2. **The global no-performance ceiling (`score.md` / `ice-scoring.md`, pre-existing).** When NO performance profile exists for the run at all, Confidence is capped at 4 globally. This is a portfolio-wide ceiling on certainty, not a per-gate penalty, and it predates these gates.

Both can be true at once: in a run with no performance profile, `metric_instrumented`, `powerable`, and `baseline_exists` all read `not-assessed` (rule 1, no per-gate cap), AND the global ceiling holds Confidence at 4 (rule 2). The acceptance-criterion phrase "a hypothesis is NOT capped merely because an artifact is missing" governs rule 1 (the gates); it does not repeal rule 2 (the documented global ceiling, which reflects that zero baseline data legitimately lowers the certainty ceiling). A run with no performance profile therefore correctly produces no gate-driven cap and no Quick Win, the latter from the global ceiling, not from the gates.

---

## Tri-state gate semantics

**Each gate is pass / fail / not-assessed. Only an affirmative fail caps Confidence. Not-assessed (the artifact backing the gate is absent) is neutral and never penalizes Confidence on its own.**

- `pass`: the artifact was present and the check cleared (premise corroborated, metric instrumented, baseline present, control fresh and uncontested, powerable, segmentation satisfied).
- `fail`: the artifact was present and the check did NOT clear (an affirmative contradiction, an uninstrumented metric, a missing-but-expected baseline, a stale or contested control, an unpowerable thesis metric, a non-isolable required segment). Only this state caps Confidence in `score.md` Step 4.
- `not-assessed`: the artifact backing the gate is absent, so the check could not run. This is neutral. It never caps Confidence and never blocks Confidence 4-5 on its own.

A gate whose backing artifact is absent (for example `control_stable` with no structural observation artifact, or `metric_instrumented` / `powerable` with no performance profile) is `not-assessed`, NOT `fail`. A Build or run-time agent must never read "Confidence 4-5 requires all gates pass" as penalizing legacy or absent-artifact mode: a not-assessed gate satisfies that requirement, only an affirmative fail violates it.

## The validation_gates record

Emit one `validation_gates` record per hypothesis with six named gates. Each gate carries a tri-state value and a one-line note:

```
validation_gates:
  premise_contradicted: <pass | fail | not-assessed>   # an affirmative FAIL means the premise IS contradicted by another loaded artifact
  metric_instrumented:  <pass | fail | not-assessed>   # FAIL = a primary or guardrail metric is genuinely dark (not documented live anywhere in loaded context); a live-elsewhere metric PASSES with a per-surface confirmation note
  baseline_exists:      <pass | fail | not-assessed>   # FAIL = an expected baseline is genuinely absent on an instrumented surface
  control_stable:       <pass | fail | not-assessed>   # FAIL = capture is stale or two artifacts contest the same element
  powerable:            <pass | fail | not-assessed>   # FAIL = the thesis metric is unpowerable (from construct.md Step 5b)
  segmentation_satisfied: <pass | fail | not-assessed> # FAIL = a required segment cannot be isolated / instrumented
  notes:
    premise_contradicted: "[one line: which artifact contradicts, or 'corroborated by performance', or 'single-artifact, not assessed']"
    metric_instrumented: "[one line]"
    baseline_exists: "[one line]"
    control_stable: "[one line: capture date and any element-disagreement, or 'no structural artifact']"
    powerable: "[one line: per-variant MDE or 'unpowerable on thesis metric']"
    segmentation_satisfied: "[one line]"
```

`premise_contradicted` is the one gate whose name reads inverted: an affirmative `fail` means the premise IS contradicted (the bad state), `pass` means it was checked and corroborated. The other five read normally (`pass` is the good state). `score.md` Step 4 treats any affirmative `fail` on any gate as a Confidence cap, so the inversion does not change how the cap is applied; the note column makes the meaning explicit for the agent.

---

## Gate Process

Run the gates below for every hypothesis. Order does not matter; the gates are independent. Record each as pass / fail / not-assessed with a one-line note.

### Gate 1: premise_contradicted (FM1, premise triangulation)

Cross-check each hypothesis's causal premise (its Observation + Principle from `construct.md` Step 4 Causal Mechanism) against the loaded performance / audience / competitive / structural artifact bodies. The premise is a causal claim about why the current page underperforms ("clutter suppresses form-opens," "returning users can't find login," "the hero's generic claim loses paid visitors"). Test it against what the other artifacts actually say.

**Authority order on conflict: measured performance > observed structure > inferred positioning.** When two artifacts disagree about the premise, the higher-authority artifact wins. A premise inferred from positioning that the performance profile contradicts is contradicted; a structural observation that the performance profile contradicts is contradicted; a positioning inference that a structural observation contradicts is contradicted.

Procedure:
1. State the premise's testable claim in one line.
2. Find every loaded artifact that bears on it.
3. If the highest-authority bearing artifact corroborates the premise: `pass`, note the corroboration.
4. If the highest-authority bearing artifact contradicts it (for example the premise asserts "these pages are cluttered and that suppresses conversion" while the performance profile classifies them as `deep_engagement` / demand problems, not distraction): surface the contradiction in the note, then attempt to resolve. If the premise can be re-grounded on the higher-authority artifact, rewrite is a construct concern (flag it back); if it cannot, set `premise_contradicted: fail`.
5. If only one artifact bears on the premise (nothing to triangulate against): `not-assessed`.

A `fail` here means the hypothesis cannot reach Confidence 4-5 (`score.md` Step 4 caps it) and it cannot tier as a Quick Win (`score.md` Step 6).

### Gate 2: metric_instrumented (FM4, instrumentation enforcement)

Check the hypothesis's primary metric AND its guardrail metric (from `construct.md` Step 5 / 5a) against detect's Step 1f `instrumented_metrics` list.

- No performance profile (no inventory exists): `not-assessed`. Neutral. This precedence is unchanged and comes first: a run with no performance profile reads `not-assessed` regardless of any `live-elsewhere` entries the live-capability leg may have produced.
- Both primary and guardrail in `instrumented_metrics`: `pass`. When a metric is in `instrumented_metrics` via the `live-elsewhere` tag (detect Step 1f: documented live / in production / already reporting in a non-performance-profile artifact, not natively in the profile), the gate still `pass`es, and attaches a per-surface **confirmation** readiness note ("confirm the live [capability] fires on this surface / form before launch"), NOT an instrumentation-build prerequisite. The capability exists; the only residual is confirming it fires on this specific surface. This is verification, not a build, and it must never be routed to Prerequisites as tracking to stand up.
- A primary or guardrail metric in `dark_metrics`, or absent from `instrumented_metrics` entirely: before treating it as dark, check the loaded context for a statement that this metric or its measurement capability is live / in production / already reporting (the same status-reading the live-capability leg performs; this is the enforcement backstop in case the leg missed it). If found: treat it as `live-elsewhere` instrumented -> `pass` with the per-surface confirmation note above. Only when NO loaded artifact documents the capability as live (the genuine-dark case, which is what `dark_metrics` now means after detect Step 1f's live-capability leg): `fail`. Route the genuinely-dark metric to Prerequisites (the instrumentation it needs, stated as a build), and the hypothesis cannot reach Confidence 4-5. A hypothesis whose PRIMARY metric is genuinely dark is additionally routed by `score.md` Step 5b (Infeasible Routing) to "What's Not Here" until instrumentation lands.

This is the gate that catches the pilot failure where the roadmap named element-click, scroll-section, qualified-lead, and homepage analytics as read metrics while its own Prerequisites listed them as missing. The inverse failure is equally a defect and equally caught here: do not route a capability documented live in production (per any loaded artifact, not only the performance profile) to Prerequisites as something to stand up. The `live-elsewhere` path above prevents that overstatement.

### Gate 3: baseline_exists

Check whether the target surface has a baseline for the primary metric (the Baseline line from `construct.md` Step 5b / the performance profile).

- Baseline present for the primary metric on the target surface: `pass`.
- Performance profile present but the target surface has no baseline for the primary metric (homepage with no instrumented primary conversion, an uninstrumented page): `fail`. The hypothesis cannot reach Confidence 4-5 on a baseline it does not have.
- No performance profile at all: `not-assessed` (the global no-performance Confidence cap in `score.md` already applies; this gate adds nothing on top).

### Gate 4: control_stable (FM2, staleness / control stability)

Read detect's Step 1f staleness signals for the target surface.

- A capture-date tag plus no element-disagreement, and the capture is recent enough that the control is trustworthy: `pass`. Optionally attach a "verify current before launch" prerequisite when the capture is old but uncontested (does not fail the gate; it is a launch-time check).
- A cross-artifact element-disagreement on the target surface (two artifacts describe the same element differently, the redesign-in-progress signal), OR a capture stale enough that the control likely no longer matches the live page: `fail`, and attach the "verify current before launch" prerequisite. A `fail` here means the captured control is contested or out of date, so a test launched against it may be testing a control that no longer exists.
- No structural observation artifact: `not-assessed`. Neutral.

**CTR-14 boundary (Boundary 2, binding).** The `control_stable` gate DEFERS to CTR-14 when `mobile_render_clean: false` is the only signal on the surface. A broken mobile render is CTR-14's rendering-defect reframe (`modules/contrarian-triggers.md` CTR-14, the Device/OS Defect Misattribution trigger): it is a fix, not a test, and CTR-14 already routes it to fix-and-monitor in `construct.md` Step 7. It is NOT a staleness signal, so `control_stable` does not fire on it. `control_stable` is reserved for capture-date and cross-artifact element-disagreement signals. The two never co-fire on the same observation: a broken render is owned by CTR-14, a stale or contested capture is owned by `control_stable`. (Per detect's Step 1f, the staleness leg never emits a `mobile_render_clean` signal in the first place, so this deferral is belt-and-suspenders.)

### Gate 5: powerable (FM3, feasibility / power enforcement)

Consume `construct.md` Step 5b (Test Feasibility) output: the per-variant MDE / "unpowerable" determination, computed on the segmented (not pooled) denominator when Step 5 pre-registered a segment, and covering the guardrail metric as well as the primary.

- Step 5b produced a per-variant MDE within a feasible or extended window for the thesis metric: `pass`.
- Step 5b returned "unpowerable" on the thesis metric (the target surface cannot reach a readable per-variant sample on the primary metric, or the segmented denominator is too small): `fail`. `score.md` Step 5b (Infeasible Routing) routes an unpowerable-on-thesis-metric hypothesis to "What's Not Here."
- No performance profile (Step 5b was skipped): `not-assessed`. Neutral.

This gate enforces what construct estimates: construct computes the MDE, validate makes "unpowerable" actually block the score rather than sit as an advisory note.

### Gate 6: segmentation_satisfied (FM6 enforcement leg)

When `construct.md` Step 5 pre-registered the primary read as a segment (because the performance profile showed audience dilution, or the mechanism is sub-audience-only), check that the segment can actually be isolated and instrumented.

- The pre-registered segment is isolable in the available instrumentation (a defined traffic source, device, or audience cut the platform can target and read): `pass`.
- The segment cannot be isolated or instrumented (no way to deliver the variant to only that segment, or no way to read the metric for that segment alone): `fail`, and route the segmentation requirement to Prerequisites as an instrumentation block. A non-isolable required segment means the test cannot be run as designed.
- No segment was pre-registered (the hypothesis is correctly all-visitors, or no dilution signal exists): `pass` (nothing to satisfy), or `not-assessed` when no performance profile exists to judge dilution. Either way, neutral; an all-visitors hypothesis on a non-diluted page is not penalized.

---

## Strategic Lane Gates

Strategic-lane hypotheses (from Phase 2c, carrying `lane: "strategic"`) now pass through this phase. They receive a strategic gate subset, not the full tactical six: the tactical gates `powerable` and `segmentation_satisfied` are A/B-formula constructs and read `not-assessed` for non-A/B designs (they still apply when the finalized design is `randomized_ab`). Tri-state semantics are identical to the tactical gates: pass / fail / not-assessed; only an affirmative fail caps; not-assessed is neutral and never penalizes.

Emit a `validation_gates` record per strategic hypothesis with these gates:

### Strategic Gate 1: baseline_reliable

Applies when the finalized `measurement_design` is `pre_post`, `cohort`, or a matched (non-randomized) `holdout` whose matching depends on historical data.

- The loaded performance context carries an affirmative unreliable-baseline statement bearing on the design's comparison window (a documented tracking discontinuity, a period-over-period comparison the profile itself flags as unreliable, a conversion event documented as having stopped firing, or an unreconciled contradiction in the baseline data the design would read against): `fail`. A `fail` here does two things: (a) it triggers the design-forcing branch in `construct.md` Step 4c (re-finalize toward a forward-only read, a randomized holdout, or another design that does not consume the disqualified baseline); and (b) if no alternative design exists, Confidence is capped at 2 by the Step 6b ceiling and the rendered read condition must state that the comparison window is directional only.
- The performance context is present and does not disqualify the baseline: `pass`.
- No performance context, or the design consumes no historical baseline (`operational_metric`, forward-only reads, randomized designs): `not-assessed`. Neutral.

The gate reads what the skill already writes: a run that discloses "treat the pre-change window as directional only" in prose while scoring Confidence 3 on that same window is the defect this gate closes. Disclosure without enforcement is the failure mode.

### Strategic Gate 2: metric_instrumented (strategic application)

Reuse tactical Gate 2's logic in full, including the live-elsewhere posture and the no-performance-profile precedence, applied to the strategic experiment's business metric. One strategic-specific extension: when the primary business metric's instrumentation IS the run's own Measurement Foundation entry (the metric becomes readable only after a Foundation stand-up in this same deliverable), the gate reads `fail` for read-today purposes, the hypothesis cannot reach Confidence 4-5, and the dependency is rendered as the stand-up (this is expected and correct for Foundation-dependent bets; the cap prices the dependency honestly rather than routing the bet out).

### Strategic Gate 3: premise_contradicted (strategic application)

Reuse tactical Gate 1's triangulation procedure and authority order unchanged. The strategic-specific note: an unresolved quantitative contradiction in the loaded data that the bet's scoping depends on (e.g., a measured average order value wildly inconsistent with the segment the bet targets, disclosed but unreconciled) is an affirmative `fail`, not a risk footnote. Disclosing the contradiction in the Key risk block does not clear the gate; reconciling it or re-scoping the bet does.

### Confirm-first Confidence treatment

A hypothesis carrying `confirm_first: true` (from `phases/detect-strategic.md`) takes a Confidence contingency: the raw Confidence computed by the soft modifiers is reduced by 1 for the unverified existence assumption. This is a soft modifier, not a gate, and it is lifted only when the verification step lands (a later run with the capability's status documented re-scores without it). Record it in the gate-record notes so Step 6b applies it.

---

## Output

**Output to Phase 4 (score):** one `validation_gates` record per hypothesis, plus any Prerequisites additions (genuinely-dark metrics, "verify current before launch" notes, non-isolable-segment instrumentation blocks), any per-surface confirmation note for a `live-elsewhere` metric (a readiness/verification note, NOT a Prerequisites build entry; rendered via the SKILL.md `Readiness` field), and any "What's Not Here" routing flags (unpowerable thesis metric, genuinely-dark primary metric) for `score.md` Step 5b to apply. The records are internal; `score.md` Step 4 applies them as hard caps on the raw Confidence the soft modifiers compute, per the order-of-operations contract in `score.md` Step 4. Strategic-lane gate records (from `Strategic Lane Gates` above) flow to `score.md` Step 6b instead, which applies the same ceiling rule to the strategic scoring pass.
