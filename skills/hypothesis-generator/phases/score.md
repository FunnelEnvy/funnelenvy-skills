# Phase: ICE Scoring and Sequencing

## Required Inputs

- Hypothesis list from Phase 3 (construct), including each hypothesis's `self_critique.score_effect` block (Step 10) and Test Feasibility output (Step 5b)
- The per-hypothesis `validation_gates` record from Phase 3.5 (`phases/validate.md`), consumed by the Step 4d gated Confidence rubric, the Step 5b blocked/unpowerable routing, and the Step 6 Quick Win gate
- detect's Step 1f FM9 contamination flag (when present), consumed by the FM9 discount in Step 4 before the Impact modifiers
- `modules/ice-scoring.md` (calibration anchors and scoring rules)
- `modules/experiment-patterns.md` (for ICE baselines and modifiers)
- Calibration data from evidence modules (if any were loaded in Phase 2)

## Depth Behavior

This phase does not vary by depth.

## Graceful Degradation

| Condition | Impact |
|-----------|--------|
| No positioning-scorecard.md | Confidence scores capped at 3 for all hypotheses (less certainty about gap severity). |
| No competitive-landscape.md | Impact scores for competitive-pressure hypotheses capped at 3. |
| No audience-messaging.md | Confidence scores for persona-based hypotheses capped at 3 (less certainty about messaging fit). |
| No baseline traffic/conversion data (no performance-profile.md) | Confidence scores capped at 4 globally. Add note to roadmap: "Run /ga4-audit for data-calibrated scores and traffic-driven hypotheses." This global ceiling is a separate mechanism from the per-gate `not-assessed` neutrality in `phases/validate.md` (see that phase's `Boundary: per-gate neutrality vs the global no-performance ceiling`): per-gate absence applies no cap, while whole-profile absence applies this portfolio-wide ceiling. Both can hold in the same run; they do not conflict. |
| Performance data present but conversions lack page attribution | Cap revenue-attribution confidence only; do NOT apply a blanket Confidence cap. Default the target metric to a variant-instrumented proxy. Emit one measurement-enablement item as a scored prerequisite-experiment (named, with the enablement vehicle and date if engagement-constraints supply one). |
| Calibration data from evidence modules | Override pattern baselines with calibrated scores where available. Calibrated scores take precedence. |

---

## Scoring Process

### Step 1: Apply Pattern Baselines

Start each hypothesis with the ICE baseline from its matched pattern in `modules/experiment-patterns.md`.

If a hypothesis was triggered by multiple patterns, use the baseline from the pattern with the strongest trigger signal.

**Context-derived hypotheses:** Start at 3/3/3 (neutral midpoint) instead of a pattern baseline. Apply Confidence -1 immediately (no pattern precedent = lower structural certainty). This penalty can be neutralized with an explicit +1 annotation explaining why the evidence is strong enough to override the lack of pattern precedent. The annotation must reference a specific piece of evidence from context, not a general argument.

### Step 2: Apply Pattern Modifiers

Each pattern in `modules/experiment-patterns.md` defines conditional modifiers. Evaluate each modifier against available context:

- If the modifier condition can be confirmed from context, apply the adjustment
- If the modifier condition can't be evaluated (data not available), do not apply it
- Modifiers are additive. Multiple modifiers can apply to the same hypothesis.
- Scores are clamped to 1-5 after all modifiers are applied

### Step 3: Apply Calibration Overrides

If evidence modules provided calibration data for specific patterns:
- Replace the pattern baseline + modifier result with the calibrated score
- Calibration data represents empirical evidence and always takes precedence over theoretical baselines
- If calibration data exists for only some dimensions (e.g., calibrated Impact but no calibrated Confidence), use the calibrated dimension and keep the baseline-derived score for the rest

### Step 4: Apply Contextual Adjustments

These adjustments are based on the overall context quality, not individual patterns:

**Confidence adjustments:**
- If the "before" state for a copy experiment is exact text from context: no adjustment
- If the "before" state is inferred/described rather than exact: Confidence -1
- If the hypothesis was triggered by a partial trigger: Confidence -1
- If audience-messaging.md provided the "after" copy: no adjustment
- If the "after" copy was derived from L0 value props instead: Confidence -1
- If `metric_classification` is "proxy" (from Phase 3 Step 5a): Confidence -1 (indirect measurement adds uncertainty)
- If performance-profile.md exists and `traffic_adequacy` is "high": Confidence +1
- If performance-profile.md exists and target page has conversion data: Confidence +1
- If performance-profile.md exists and `traffic_adequacy` is "low": Confidence -1
- If target page has `failure_mode` matching the hypothesis mechanism (e.g., messaging hypothesis + `shallow_engagement`): Confidence +1 (data confirms mechanism)
- If target page has `failure_mode` contradicting the hypothesis mechanism (e.g., messaging hypothesis + `deep_engagement`): Confidence -1 (data suggests different root cause)
- If the hypothesis is a validated-mechanism replication (a `prior_winner` from the bound experiment-history input carries a rollout/replication next-experiment that this hypothesis executes, and the replicated mechanism is the dominant change): Confidence +1 (the mechanism is empirically validated, not inferred). This lift applies to the raw Confidence; see the order-of-operations note below.
- If the Phase 3 Step 10 `self_critique.score_effect` block sets `confidence_delta: -1` (an unmitigated thesis-level counterargument, FM8): Confidence -1. This is a soft modifier on the raw Confidence, applied here before the gated rubric's hard ceiling.

**Impact adjustments:**
- If the targeted page is the homepage: Impact +1 (highest traffic page for most B2B sites)
- If the hypothesis addresses the scorecard's "top gap": Impact +1
- If the hypothesis targets a page not mentioned in any context file: Impact -1 (uncertain traffic)
- If performance-profile.md exists and target page has >500 sessions/mo: Impact +1
- If performance-profile.md exists and target page has bounce rate >50%: Impact +1
- If performance-profile.md exists and target page conversion rate <50% of site average: Impact +1
- If performance-profile.md exists and target page has <100 sessions/mo: Impact -1
- If `top_opportunities` lists the target page with impact "large": Impact +1
- If `top_opportunities` lists the target page with impact "small": no modifier (already accounted for)
- If `trends` shows the target metric worsening (has `[WORSENING]` tag): Impact +1 (urgency)
- If the Phase 3 Step 10 `self_critique.score_effect` block sets `impact_delta: -1` (an unmitigated business-outcome counterargument with no guardrail added, FM8): Impact -1. When `guardrail_added` is set instead, apply no Impact modifier (the guardrail is the mitigation).

**Method scope for the low-traffic Impact demotion (testing_method).** The `<100 sessions/mo -> Impact -1` demotion above is premised on A/B per-arm sample adequacy. It does NOT fire when the run-level `testing_method` (detect Step 1h) is `pre_post`, `cohort`, or `operational`: a pre/post read applies the treatment to the full traffic (no per-arm split), so a low-traffic page is not demoted on A/B-sample grounds. The reach-based Impact modifiers (`>500 sessions/mo`, `bounce >50%`, `top_opportunities` large) are unchanged under any method: they reflect page reach and genuine impact, not A/B power. Under `testing_method: ab` (the default) every Impact modifier above is unchanged.

**FM9 data-hygiene discount (apply BEFORE the Impact modifiers above).** When detect's Step 1f carried an FM9 contamination flag for the target surface (documented bot or synthetic-monitoring traffic), discount the contaminated sessions/bounce figure to its corrected value BEFORE evaluating the session-threshold and bounce-rate Impact modifiers above (the >500 sessions/mo, <100 sessions/mo, and bounce >50% lines all read these figures). A surface whose 600 reported sessions are 70% synthetic-monitoring pings has ~180 real sessions and must score Impact against 180, not 600. Surface the correction in the deliverable in natural language ("traffic figures exclude an estimated [share] of automated monitoring traffic on this page"); never name the internal contamination flag. This discount operates on the inputs to the Impact modifiers, so the modifiers see the corrected figure; it is not itself an Impact modifier.

**Ease adjustments:**
- If the hypothesis requires only copy changes: Ease +1
- If the hypothesis requires structural/layout changes: no adjustment
- If the hypothesis requires personalization infrastructure: Ease -1 (unless context suggests it exists)
- If the hypothesis requires changes to third-party embedded elements (forms, chatbots): Ease -1
- If the hypothesis replicates a proven variant from the experiment-history input (the winning design exists and is being re-applied): Ease +1 (proven variant lowers implementation cost)

**Order of operations (replication modifier).** The replication Confidence +1 above applies to the **raw Confidence** computed by the soft modifiers in this `score.md` Step 4. The **gated Confidence rubric (Step 4d) runs as a hard ceiling AFTER all soft Step 4 modifiers** (a single affirmative gate fail caps Confidence at 3, multiple fails at 2). Therefore the replication +1 **never bypasses an affirmative gate failure**: a replication of a proven mechanism whose primary metric is uninstrumented on the target surface, or whose premise is contradicted by another loaded artifact on the target surface, is still capped by the gate. The replication modifier is a soft lift on raw Confidence, not a gate override. Scores remain clamped to 1-5 after all modifiers (existing Step 2 rule).

**Outcome-aware experiment-history posture.** When a hypothesis was minted from the bound experiment-history source (`signal_source: experiment-history`, tagged with `history_type` and `parent_outcome` in `phases/detect.md` Step 1g -- from either the external producer `gold-experiment-index` source or the in-output-KB `schema: experiment-history` fallback; the posture is identical for both), score it with the posture matrix below instead of the single winner-rollout case above. The matrix supersedes the winner-rollout line for experiment-history-derived hypotheses; the winner-rollout row reproduces the existing `+1`/`+1` behavior unchanged.

| history_type | parent_outcome | Confidence | Ease | Impact | Typical tier |
|---|---|---|---|---|---|
| rollout | winner | +1 (validated mechanism) | +1 (proven variant) | per surface | Quick Win capable (existing behavior, keep) |
| discriminating_test | any | +1 (isolates a variable, designed to read cleanly) | 0 | modest (isolation informs, rarely moves revenue alone) | Strategic Bet / Exploration |
| iteration | loser/flat | 0 (mechanism not yet validated; naive version failed) | per design | per surface; prior loss is evidence the obvious version fails, so the bolder iteration carries learning value | Strategic Bet / Exploration |
| follow_up | winner | 0 to +1 if it re-applies the proven mechanism; else 0 | per design | per surface | per ICE |
| follow_up | loser/flat | 0 | per design | per surface | per ICE |

Encode these rules with the table:
- **Winner-rollout `+1`/`+1` is the ONLY path to a replication-grade Quick Win.** Do NOT extend the Ease `+1` to non-winner iterations: no proven variant exists, so the implementation-cost reduction does not apply. This keeps the existing winner-rollout Quick-Win path (the lines 70/89 behavior) intact and unchanged.
- **The posture is a soft modifier on raw Confidence and never bypasses an affirmative gate failure.** All soft modifiers in this Step 4 compute the raw Confidence: proxy `-1`, traffic caps, failure-mode contradiction `-1`, the FM8 self-critique `-1`. The order-of-operations contract above governs: soft modifiers compute the raw Confidence; the gated rubric (Step 4d) is the hard ceiling applied after, and it folds in the proof-integrity fail as one of its gate conditions. The posture modifiers are part of the soft layer, clamped to 1-5, then subject to the Step 4d ceiling.
- **Confidence semantic (explicit).** In this skill, **Confidence means "how certain we are this produces a measurable result," not "probability the variant wins."** This is what lets a discriminating test designed off a loss reasonably carry a `+1` Confidence: a clean-reading isolation test reliably produces an interpretable result even though no winning variant is yet known. (Consistent with the `How to Read This Roadmap` Confidence definition in `SKILL.md`.)
- Scores remain clamped to 1-5 after all modifiers (existing Step 2 rule).

**Quick Win reachability.** With this Step 4 +1 on Confidence and +1 on Ease, a replication of a proven winner can reach Confidence >= 4 AND Ease >= 4 and clear the Quick Win bar (subject to the <= 6-week duration rule in Step 6 and any gate ceiling). This is the intended outcome: it is what the Step 7 sequencing reorder alone cannot produce.

#### Step 4d: Gated Confidence Rubric (FM5, hard ceiling)

This rubric runs LAST in Step 4, as a hard ceiling applied AFTER all the soft modifiers above have computed a raw Confidence (the proxy `-1`, the traffic caps, the failure-mode `-1`, the replication `+1`, the FM8 `-1`, and all the rest). The soft modifiers decide the raw Confidence; this rubric can only LOWER it, never raise it. Read the per-hypothesis `validation_gates` record from `phases/validate.md` (Phase 3.5).

**Tri-state (Boundary 4, stated verbatim, same as `phases/validate.md`):** *Each gate is pass / fail / not-assessed. Only an affirmative fail caps Confidence. Not-assessed (backing artifact absent) is neutral and never penalizes.*

The rubric phrasing is "Confidence 4-5 requires all gates pass (no affirmative fail)." This MUST be read with the tri-state rule: a `not-assessed` gate (legacy mode, or any run where the backing artifact is absent) does NOT block Confidence 4-5. Only an affirmative `fail` does. A run with every gate `not-assessed` (e.g., no performance profile, no structural artifact) takes NO gate-driven Confidence penalty here; its Confidence is whatever the soft modifiers and the existing graceful-degradation caps produced.

**The six gates** (from `validation_gates`): `premise_contradicted` (an affirmative fail means the premise IS contradicted), `metric_instrumented`, `baseline_exists`, `control_stable`, `powerable`, `segmentation_satisfied`.

**Ceiling rule (apply to the raw Confidence):**
- Zero affirmative gate fails: no ceiling. Confidence stays at the raw value (a hypothesis with all gates pass or not-assessed can hold Confidence 4 or 5 if the soft modifiers earned it).
- Exactly one affirmative gate fail: cap Confidence at 3.
- Two or more affirmative gate fails: cap Confidence at 2.

A cap is a ceiling, not a floor: if the raw Confidence is already at or below the cap, it is unchanged. Not-assessed gates are not counted as fails for either threshold.

**Proof-integrity reconciliation (Boundary 3).** The former standalone "proof_integrity_passed false caps Confidence at 3" rule (previously a soft modifier in this Step 4) is FOLDED INTO this rubric so two rules do not independently cap the same dimension. Treat `proof_integrity_passed: false` (from Phase 3 Step 4b) as an affirmative fail on a premise-integrity condition counted alongside the six gates: it contributes one fail to the count above (one fail caps at 3, and it stacks toward the two-fail cap-at-2 if another gate also fails). This is the single place the proof-integrity cap is applied; it is no longer applied separately as a soft modifier. The cap-at-3 outcome for an isolated proof-integrity failure is identical to the old behavior, so nothing regresses; what changes is that it now composes with the other gate fails instead of running as a parallel independent cap.

### Step 5: Score Validation

Before finalizing, check for scoring anti-patterns:

**Anti-pattern: Score clustering.** If >70% of hypotheses have ICE totals within 2 points of each other, the scoring is too flat. Re-examine: are you defaulting to safe middle scores? Force differentiation by re-evaluating the strongest and weakest hypotheses first, then spreading the rest.

**Forced-spread procedure (FM10).** The gated rubric (Step 4d) drives more Confidence caps at 3, so across a portfolio Confidence can become effectively pinned (one dimension nearly constant). When one ICE dimension is effectively constant across the portfolio (>70% of hypotheses share the same value on it, or the gated rubric capped most Confidence scores at 3), do not stop at detecting the clustering: remedy it. Require BOTH of the following on the remaining two dimensions:
- The other two dimensions must each span a minimum range of 2 points across the portfolio (a top and a bottom that differ by at least 2), so the ranking is not flat on every axis at once.
- At least one hypothesis must land a full tier below the top tier present (if the portfolio has Quick Wins or Strategic Bets, at least one hypothesis sits in Exploration or Cut), so the roadmap is not uniformly "all worth running."

Achieve the spread by re-evaluating the strongest and weakest hypotheses on the two unpinned dimensions first (Impact and Ease when Confidence is the pinned one), then placing the rest between them, exactly as the clustering remedy above does. Do NOT manufacture spread by relaxing a gate cap or inflating Impact past its anchor: the spread comes from honest differentiation on the unpinned dimensions, not from undoing the rubric. This extends the detection above with a remedy; the detection alone offered none.

**Anti-pattern: All high scores.** If no hypothesis scores below 3 on any dimension, you're being too generous. At least one hypothesis should have a low-Confidence or low-Ease score. Real experiment portfolios have range.

**Anti-pattern: Impact inflation.** If every hypothesis has Impact >= 4, recalibrate. Impact 4+ means "measurable revenue effect." Most copy changes on secondary pages are Impact 2-3.

Read the full calibration anchors in `modules/ice-scoring.md` to ground your scores.

### Step 5b: Infeasible Routing

**Method scope (testing_method).** The A/B-traffic-based routing in this step, the duration-based `feasibility: "infeasible"` removal below and the `powerable: fail` routing, applies only on an `ab`-method run (detect Step 1h; the default). On a non-A/B run (`pre_post` / `cohort` / `operational`) tactical hypotheses take construct Step 5b's non-A/B feasibility branch, so they are never marked `feasibility: "infeasible"` on A/B-traffic grounds and their `powerable` gate reads `not-assessed`: no tactical hypothesis routes to the tactical "What's Not Here" for A/B-power or traffic reasons. The structurally-untestable-differentiator routing and the strategic routing below are unchanged.

Before tiering, remove hypotheses marked `feasibility: "infeasible"` from Phase 3 Step 5b. These experiments have insufficient traffic for A/B testing at current levels.

**Strategic experiments are judged by their own design, not the A/B formula.** A strategic experiment with a stand-up-able non-A/B measurement design (holdout / pre/post / cohort / geo split / switchback / operational tracking) is feasible and proceeds to the separate strategic scoring and tiering pass (Step 6b), which renders it into the strategic deliverable. Route a strategic experiment to the strategic deliverable's own "What's Not Here" only if its measurement design cannot be stood up or read at any altitude (no baseline data for a holdout, no instrumentation possible, out of scope), NOT merely because it is not a clean A/B test. The two-proportion A/B formula and the infeasible-removal step above govern tactical hypotheses only.

For each infeasible hypothesis:
1. Remove from the scoring pipeline (do not compute ICE total or assign a tier)
2. Record for the "What's Not Here" section: hypothesis name, target page, reason for infeasibility (estimated duration or traffic level), and suggested alternative approach (pre/post analysis, proxy metric, qualitative testing)

**Blocked / unpowerable routing (FM3 score side).** Beyond the duration-based `feasibility: "infeasible"` removal above, also route to "What's Not Here" any hypothesis whose `validation_gates` (from `phases/validate.md`) carry an affirmative fail that makes the test un-runnable as designed:
- `powerable: fail` (the thesis metric is unpowerable on the target surface or the segmented denominator). Record the reason as "unpowerable on the thesis metric at current traffic" with the alternative (micro-conversion proxy, pre/post, or a pooled read if the segment was the constraint), exactly as the duration-based infeasible case is framed. (Under a non-A/B `testing_method` the `powerable` gate reads `not-assessed`, not `fail`, so this bullet never fires; see the Method scope note above.)
- `metric_instrumented: fail` on the PRIMARY metric (the primary is dark). Record the reason as "primary metric not instrumented" with the alternative being the instrumentation prerequisite that would unblock it.

These route the same way duration-infeasible hypotheses do (removed from the tactical tiers, presented as future opportunities in "What's Not Here," not rejects). A `metric_instrumented: fail` on the GUARDRAIL only (primary is instrumented) does NOT route to "What's Not Here"; it stays in the roadmap, capped by the Step 4d rubric, with the guardrail-instrumentation gap recorded in Prerequisites.

Infeasible hypotheses are NOT failures. They are real opportunities that require either more traffic, a different measurement approach, or a different test design. The "What's Not Here" section should present them as future opportunities, not rejects.

**Structurally-untestable page-element differentiator (distinct from low-traffic infeasibility).** This routing fires ONLY for **page-element-altitude** items. When a signal routed from Phase 2b (detect-contextual.md criterion 5, untestable-differentiator branch) points to a page-element-scoped differentiator that cannot be A/B tested at current scope, record it in the tactical roadmap's "What's Not Here" framed as a productization/positioning decision with its demand evidence (who is asking, how often) and blocker (data coverage, entitlement scope, compliance), not as a low-traffic infeasible experiment. The recommendation is a business-model or data-coverage decision, not a test design. Do not assign it a traffic-based infeasibility reason or an alternative measurement approach as if more traffic would unlock it.

**A business-level lever never lands in the tactical "What's Not Here."** A program-, offer-, audience-motion-, or asset-level lever is Phase 2c's responsibility, not this routing's. It is either a scored strategic experiment (when some design can measure it) in the strategic deliverable, or it lands in the strategic deliverable's own "What's Not Here" (when no design at any altitude can measure it). This altitude split, decided here at the routing site, is the precedence the in-tier design lacked: score.md does not route business-altitude items to the tactical "What's Not Here" at all, so the run-to-run collision between Phase 2b's untestable-differentiator routing and Phase 2c is removed. A page-element differentiator that CAN be A/B tested is a normal tactical hypothesis, not an exclusion.

**Count:** Track the number of infeasible-routed hypotheses for the completion summary.

### Step 6: Compute ICE Totals and Tier

**ICE Total** = Impact + Confidence + Ease (range: 3-15)

**Tiering rules:**

| Tier | Criteria | Purpose |
|------|----------|---------|
| **Quick Win** | Confidence >= 4 AND Ease >= 4 AND estimated_duration_weeks <= 6 AND no affirmative validation-gate fail | Build testing momentum. Low risk. Fast signal. |
| **Strategic Bet** | Impact >= 4 AND ICE Total >= 10 AND not Quick Win | Move the needle. Worth the effort. |
| **Exploration** | Everything else with ICE Total >= 7 | Learn something. Run when bandwidth allows. |
| **Cut** | ICE Total < 7 | Not worth running. Exclude from roadmap. |

**Calendar-duration override.** If `estimated_duration_weeks` (from Phase 3 Step 5b) exceeds 6 weeks, the hypothesis cannot be tiered as Quick Win regardless of Confidence and Ease scores. Re-tier using the remaining rules:
- Strategic Bet if Impact >= 4 AND ICE Total >= 10
- Exploration if ICE Total >= 7
- Cut if ICE Total < 7

Add annotation to downgraded hypotheses: "Meets Quick Win scoring but estimated test duration ([N] weeks) exceeds the 6-week Quick Win ceiling. Reclassified as [new tier]."

Quick Wins exist to build organizational testing momentum. A 10-week test, regardless of implementation ease, does not build momentum. Mislabeling it burns stakeholder trust when the "quick" win takes a full quarter to read out.

**Validation-gate requirement for Quick Win.** A hypothesis with ANY affirmative `validation_gates` fail (from `phases/validate.md`) cannot tier as Quick Win regardless of its Confidence and Ease, because Step 4d has already capped its Confidence at 3 (one fail) or 2 (multiple fails), so it cannot meet Confidence >= 4 anyway. The explicit gate condition in the tier table above makes this non-bypassable even if a future modifier were to lift Confidence: a Quick Win must be a hypothesis whose premise, metric, baseline, control, power, and segmentation all hold (gates pass or not-assessed, never an affirmative fail). Not-assessed gates do NOT block Quick Win eligibility (tri-state: only an affirmative fail does).

The Step 6 tiering above (the tier table, the calendar-duration override, the `--max` cut rules) applies to **tactical hypotheses only**. Strategic experiments are scored and tiered on the separate pass below; they never enter the tactical roadmap's tiers and never share its ICE table.

**Duration not available.** If `estimated_duration_weeks` is absent (no `performance-profile.md`), the duration constraint does not apply. Quick Win eligibility uses only Confidence >= 4 AND Ease >= 4. The absence of performance data already caps Confidence via Phase 3 graceful degradation rules, which naturally limits Quick Win qualification.

**Method scope (testing_method).** Under a non-A/B `testing_method` (from `detect.md` Step 1h), the two-proportion z-test does not run, so `estimated_duration_weeks` is never produced; the `construct.md` Step 5b non-A/B branch yields a read-window length instead. Substitute that read-window length for `estimated_duration_weeks` in the Quick Win tier condition and the Calendar-duration override above, so the <= 6-week fast-signal bar (Quality Rule 16) is enforced mechanically rather than dropped. The "Duration not available" clause applies only when there is no duration estimate of either kind (no performance profile at all), NOT to a non-A/B run that has a read-window estimate: a 15-week pre/post read cannot tier Quick Win.

If `--max` cap is hit after tiering, cut from the bottom of Explorations first, then Strategic Bets. Never cut Quick Wins (they build organizational confidence in testing). **Within-tier retention for experiment-history continuations:** when cutting within Explorations to satisfy `--max`, drop `source_priority: medium` experiment-history continuations before `recommended_lead` / `high` ones. This is a tiebreaker applied within the Explorations cut set; it composes with (does not replace) the never-cut-Quick-Wins / cut-bottom-of-Explorations-first ordering.

### Step 6b: Strategic Scoring and Tiering (separate pass)

**This pass runs ONLY on strategic opportunities (those from Phase 2c, routed via `detect-strategic.md` > `Output to the strategic path`).** It is a separate pass from the tactical Steps 1-6 above: strategic experiments and tactical hypotheses never share one ICE table, so the tactical Impact/Confidence/Ease anchors are untouched by construction.

**Strategic scoring.** Score each strategic experiment on its own ICE using the strategic-scoped anchors in `modules/ice-scoring.md`: business-outcome Impact (the Impact-5 anchor admits off-page levers measured by a non-A/B design; a lever does not score lower merely because it is not an on-page A/B) and measurement-rigor Confidence (Confidence reflects the interpretability of the chosen design, not the absence of an A/B; a clean holdout with an adequate baseline reads near a well-powered A/B, an uncontrolled before-and-after with confounds reads lower). The de-novo no-precedent Confidence -1 penalty applies, the same as for context-derived opportunities. A `lever_family: catch-all` survivor (from the Catch-All Leg in `phases/detect-strategic.md`) takes one additional -1 raw-Confidence modifier for family-less structural uncertainty; it stacks with the de-novo -1 and, when the record also carries `confirm_first: true`, with the confirm-first contingency (independent uncertainties: lever shape vs capability existence). All are soft modifiers applied before the gated ceiling. ICE-range discipline (Quality Rule 4) holds: no blanket Impact-5 for being "strategic"; each score is earned against the anchors. The portfolio spread rules in `modules/ice-scoring.md` (the Impact spread, the at-least-one-low rule, the forced-spread remedy) are tactical-portfolio rules: on this pass they apply proportionally and are never used to force artificial variance at three or fewer experiments.

**Strategic gated-Confidence ceiling.** Read the strategic `validation_gates` record (`phases/validate.md` > Strategic Lane Gates). Apply the same ceiling rule as the tactical Step 4d, after all soft modifiers including the de-novo -1 and any confirm-first contingency: zero affirmative fails, no ceiling; one fail, cap Confidence at 3; two or more, cap at 2. Tri-state semantics identical: not-assessed is neutral. This is the enforcement leg for measurement rigor on the strategic lane; the soft "measurement-rigor Confidence" consideration above computes the raw value, and this ceiling binds it.

**Dependency-count ordering (replaces any per-gate stand-up-depth cap).** Stand-up depth is a sequencing property, not a score gate, and it is not double-priced into Ease (Ease already carries stand-up effort). Within each strategic tier, order experiments by ascending count of unmet stand-up dependencies: bets readable today sort ahead of bets readable only after N prerequisite builds land, regardless of ICE order within the tier. Render the ordering rationale in the Sequencing Rationale prose. This codifies dependency-first sequencing as a rule rather than a per-run judgment call.

**Strategic feasibility.** A strategic experiment with a stand-up-able non-A/B measurement design (a holdout, before-and-after window, cohort comparison, geographic split, alternating on/off windows, or operational tracking) is feasible and proceeds to tiering. Route a strategic experiment to the strategic deliverable's own "What's Not Here" (below) only when no measurement design can read it at any altitude (no baseline for a holdout, no possible instrumentation, out of scope), NOT merely because it is not a clean A/B test. This is the carry-forward of the Step 5b non-A/B feasibility judgment, applied to the strategic deliverable's tiering rather than a shared one.

**Strategic tiering.** Tier the strategic experiments into the strategic deliverable's OWN Quick Wins / Strategic Bets / Explorations using the same thresholds as the tactical pass (Quick Win = Confidence >= 4 AND Ease >= 4 [AND <= 6-week read when a duration estimate exists]; Strategic Bet = Impact >= 4 AND ICE Total >= 10 AND not Quick Win; Exploration = everything else with ICE Total >= 7; Cut = ICE Total < 7). Reusing the tier labels keeps the deliverable legible without inventing new vocabulary; most strategic levers land in Strategic Bets. These tiers populate the strategic deliverable (`SKILL.md` > `Strategic Roadmap Output Format`), never the tactical roadmap.

**Strategic Cut disposition.** A strategic experiment that scores below the Cut threshold is dropped exactly as a tactical Cut is (Step 6: excluded from the roadmap): it is not rendered as a scored experiment and it is NOT listed in the strategic deliverable's "What's Not Here," which is reserved for the not-measurable / existing-capability / decision-blocked cases below, not for a measurable lever this run's evidence scored too low to run now.

**Optional within-strategic-deliverable asset/instrumentation cluster.** When 2+ strategic experiments in the same strategic tier share a stand-up dependency (an asset or instrumentation that must be built first), they MAY be rendered as a labeled cluster within that tier to make sequencing legible. This is a visual grouping inside the strategic deliverable, not a separate tier; ICE ranking and tier assignment are unchanged.

**Strategic "What's Not Here."** The strategic deliverable has its OWN exclusions list, distinct from the tactical roadmap's. It holds levers not measurable by any design at any altitude, framed as productization / positioning / data-coverage decisions with demand evidence and blocker, NOT as low-traffic A/B infeasibility. A business-level lever is never recorded in the tactical roadmap's "What's Not Here" (per Step 5b's altitude split).

### Step 7: Sequencing

Sequencing applies the layers below in priority order. When an `engagement-constraints` input is present, the engagement-derived constraints from Phase 2 Step 1d apply first as real-world gating; the remaining layers order experiments within that gating. When no engagement-constraints input is present, skip Layer 0 and sequence on LIFT and dependencies exactly as before.

**Layer 0: Engagement-derived constraints (from Phase 2 Step 1d, only when an engagement-constraints input is present)**
Apply the sequencing and tier constraints derived in Step 1d:
- **Release-window timing overrides ordering.** Where a committed release touches a surface an experiment targets, that experiment must read out fully before the release or start after it (a surface touched by a release cannot hold a baseline across it). This timing constraint overrides LIFT and tiebreak ordering for the affected experiments.
- **Concurrency ceiling.** Cap how many experiments launch together at the approval-bandwidth ceiling derived in Step 1d. Queue the remainder by tier and ICE.
- **Tier ceiling on high-risk surfaces.** Where Step 1d derived a tier ceiling (e.g., a freshly cautious governance gate), cap the tier that high-risk-surface experiments can reach.

Render the engagement reasoning in the Sequencing Rationale prose (the "why this order"), not as raw constraint text. For example: "The PDP-and-cart experiment starts after the August release because the release touches both surfaces and a baseline cannot hold across it; copy-light, off-configurator tests run first, two to three concurrent at most, reflecting current approval bandwidth." The derived implication reaches the roadmap, not the calendar entry or the incident history.

**Layer 1: Interaction dependencies (from Phase 3 Step 9)**
Multiplicative dependencies are hard constraints. If hypothesis A has `interaction_dependency.depends_on = B`, then B runs before A regardless of tier or LIFT category. Render these dependencies explicitly in the Sequencing Rationale.

Stand-up dependencies are part of this layer: a strategic-lane experiment that needs an asset or instrumentation built first cannot run before that dependency exists, so the stand-up sequences before the experiment that needs it. Render this in the Sequencing Rationale prose alongside the interaction dependencies; do not add a separate sequencing layer for it.

**Layer 2: LIFT-model ordering (from Phase 3 Step 4)**
Within each tier, after satisfying interaction dependencies, sort by `lift_category` priority: Relevance (1) > Clarity (2) > Anxiety (3) > Distraction (4) > Urgency (5). This ensures upstream conversion barriers are addressed before downstream ones.

**LIFT violation flag:** If a hypothesis addressing Distraction or Urgency would run before a hypothesis addressing Relevance or Clarity on the same page, flag this in the Sequencing Rationale: "Note: [Experiment X] addresses [downstream barrier] on [page] while [Experiment Y] addresses [upstream barrier] on the same page. Recommend running [Y] first. If [Y] wins, re-evaluate whether [X] is still needed."

**Layer 3: Within-LIFT-category tiebreaking**

**Quick Wins: Ease-first ordering.**
Run the easiest wins first. Build momentum. Get the team comfortable with the testing process. If two Quick Wins have similar Ease and LIFT category, prioritize the one with higher Impact.

**Strategic Bets: Learning-chain ordering.**
- If experiment A's result changes how you'd design experiment B, A goes first
- If two experiments target the same page, group them (reduces implementation overhead) but run them sequentially (don't confound variables)
- If a Strategic Bet validates a positioning assumption that other experiments depend on, it moves up
- Cross-page learning dependencies (from Phase 3 `informs` annotations) are soft constraints: note the relationship in Sequencing Rationale but don't enforce ordering unless the dependency is strong

**Explorations: Learning-first ordering.**
- Explorations that test fundamental assumptions (e.g., "does this audience prefer outcome language or proof language?") go before explorations that test tactical variations
- Explorations that could become Quick Wins if they succeed go early

**Layer 4: Empirical tiebreakers (within same LIFT category and tier)**

When two or more hypotheses share the same tier, LIFT category, and have similar ICE scores, apply these tiebreakers in order:

1. **Experiment-History Continuation Priority.** Active when the experiment-history input is bound (the bound experiment-history source: the external producer's `gold-experiment-index` + linked silver insights, OR the in-output-KB `schema: experiment-history` artifact + linked gold insight guides, resolved per SKILL.md `KB Mode (Dual-Mode Output)` > `Read-side Mapping`). Covers all outcome-derived continuations minted in `phases/detect.md` Step 1g (rollouts off winners, plus iterations, discriminating tests, and follow-ups off losses and flats), each carrying its source record's target surfaces and priority. Within the same tier and LIFT category, sort winner rollouts highest, then other in-scope continuations (discriminating tests, iterations, follow-ups) near their parent surface, then untested hypotheses. This is a within-tier sequencing reorder only; it does not by itself change any ICE score (the Confidence/Ease scoring lift is `score.md` Step 4 and its outcome-aware posture). The item is tri-state-safe: when the experiment-history input is absent, it is inert and all hypotheses are treated as untested, with no penalty, exactly as before.

2. **Proximity-to-Conversion Ordering.** Within the same LIFT category and ICE tier, pages closer to the conversion event run first. Priority order: checkout/booking > pricing > demo request/signup > product pages > homepage > category/solutions pages > content/blog pages. Rationale: conversion-adjacent pages have tighter feedback loops (shorter path from test to measurable outcome) and changes compound less with upstream variables. **Override:** If two hypotheses differ by >= 3 ICE points, the higher-ICE hypothesis takes precedence regardless of page proximity. Proximity is a tiebreaker, not a trump card.

3. **Cross-Channel Insight Propagation.** After the main sequenced roadmap, add a separate "Cross-Channel Propagation Candidates" subsection. This subsection lists hypotheses whose winning patterns could be tested in other channels (email, paid ads, in-app messaging) but are NOT scored or sequenced within the main roadmap. Format:
   ```
   ## Cross-Channel Propagation Candidates

   These are not scored experiments. They are contingent suggestions that become actionable
   only if the source experiment wins.

   - If [Experiment X] wins: test the same [pattern] in [channel]. Rationale: [why the mechanism transfers].
   - If [Experiment Y] wins: test [adaptation] in [channel]. Rationale: [why].
   ```
   This subsection is informational. It does not affect the main roadmap's scoring, tiering, or sequencing.

**Cross-tier dependencies:**
- Interaction dependencies can cross tiers. If a Quick Win has a multiplicative dependency on a Strategic Bet (unusual but possible), note the dependency but do not delay the Quick Win. Instead, note in Sequencing Rationale: "Quick Win [X] will produce a cleaner result if Strategic Bet [Y] runs first, but the momentum value of running [X] early outweighs the measurement risk."
- LIFT ordering does not cross tiers. A Relevance-category Strategic Bet does not jump ahead of a Distraction-category Quick Win.
- Never delay a Quick Win because of a Strategic Bet dependency (Quick Wins build organizational confidence in testing).

### Step 8: Prerequisites and Data Gaps Compilation

After sequencing, compile a structured list of data gaps and prerequisites that affected coverage and scoring. This section appears in the final deliverable and tells the reader what's missing and how to get it.

**Three categories:**

**1. Missing baseline data (analytics, form metrics).**
For each data gap that prevented higher-confidence scoring:
- What data is missing (e.g., "baseline form completion rate," "page-level traffic data," "scroll depth metrics")
- Which experiments are affected (name them)
- How to collect it (specific analytics setup or measurement action)

**2. Context verification needed (claims needing client confirmation).**
From the context quality flags (Phase 2, Step 1b):
- Proof points marked "claimed" that affect specific hypothesis confidence
- Sections marked `[NEEDS CLIENT INPUT]` or `[NEEDS CONFIRMATION]`
- Suggested verification action (e.g., "confirm customer count with marketing team")

**3. Infrastructure prerequisites (personalization tools, CMS capabilities).**
For each experiment that requires specific tooling:
- What tooling is needed
- Which experiments depend on it
- Whether the tooling was detected in context or assumed missing

**Also include:**
For each pattern that was SKIPPED entirely due to missing data (not just scored lower):
- Pattern name and category
- What data would need to exist to evaluate it
- Which context file or data source would provide it

This gives the reader a clear action list: "collect these 5 things, and your next hypothesis generation run will produce more and better-scored experiments."

**Output to Phase 5:** Prerequisites and data gaps list, alongside the scored hypothesis list.
