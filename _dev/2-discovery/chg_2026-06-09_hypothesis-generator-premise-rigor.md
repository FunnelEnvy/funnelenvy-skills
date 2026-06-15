---
fe-managed: true
name: hypothesis-generator-premise-rigor
description: >
  Make hypothesis-generator's rigor actually bite. Folds two tranches into one change. Tranche 1
  (built): consume the silver-structural-observation artifact (extraction stanza, gated Step 1e
  field-keyed triggers, construct mobile/site-wide routing, CTR-14 structural signals). Tranche 2
  (this fold): enforce premise/measurement rigor that currently exists only as scattered, ungated
  modifiers. Adds a dedicated validation phase (triangulation, staleness/control-stability,
  instrumentation, feasibility-power), a gated Confidence rubric, segmentation pre-registration,
  bundle interpretability, and consequential self-critique. All KB-internal; no new research.
governed_by: change-management/change-document
status: Discovery
resource_name: hypothesis-generator
resource_version: "TBD"
impact: 5
confidence: 4
ease: 2
initiative: cro-kb-path-b
status_note: Discovery: 11 Open Issues incl 3 folded scope OQs; awaiting resolution + Approach approval
version: "0.5.0"
created: 2026-06-09
updated: 2026-06-14
---

# hypothesis-generator: Premise & Measurement Rigor (+ Structural Observation Consumption)

## Open Issues

**Source:** Discovery review  *(most-recent write; per-row Source cell is authoritative for source-of-row attribution)*
**Generated:** 2026-06-11 16:45 PT

### Findings Detail

| # | Source | Finding | Description | Recommendation |
|---|---|---|---|---|
| 1 | Approach OQ | Fold vs separate blocked_by doc | Tranche 1 (structural consumption) was Build-complete / ready-for-QA before this fold. Folding reopens it to Discovery and prevents it closing on its own near-done state; its branch-reconciliation note carries forward. | User chose FOLD at the plan gate. The fold is technically justified: tranche 2's triangulation and `control_stable` gates lean directly on the structural facts tranche 1 makes consumable, and both tranches edit the same four files (`detect.md`, `construct.md`, `score.md`, `SKILL.md`), so a split would force the same files through two overlapping QA passes. Cost is real but bounded: the near-done structural work re-enters the lifecycle and its branch-reconciliation note (working tree switched to `dj_live-capture-skill` mid-build) must be resolved at commit time. Proceed as folded unless the user prefers to ship structural as-is and carry rigor as a `blocked_by` follow-on (a one-line redirect). |
| 2 | Approach OQ | New `phases/validate.md` vs consolidating the gate in construct.md | The rigor gates (triangulation, staleness, instrumentation, feasibility-power) can live in a dedicated Phase 3.5 file or as a consolidated construct Step 5d. A new phase bumps the validator phase count 4 to 5. | Adopt `phases/validate.md`. The diagnosed root cause is "scattered, ungated modifiers the agent satisfies on paper." construct.md is already 643 lines with Steps 1-10 plus lettered sub-steps 3b/3c/4b/5a/5b/5c; a Step 5d would bury the gate inside the exact phase whose diffuse structure is the problem and re-enable paper-satisfaction. A separate phase that emits a `validation_gates` record consumed by score.md as hard caps is the legible, hard-to-skip placement, and the validator count bump is trivial (one number). Confirm at the gate. |
| 3 | Approach OQ | Dilution thresholds for segmentation pre-registration | The evidence dossiers used >75% Direct, >60% bounce, >80% new as the mixed-audience dilution triggers. These need to be either adopted verbatim or calibrated. | Adopt the dossier values (>75% Direct, >60% bounce, >80% new) as defaults and place them in `construct.md` Step 5 as the firing condition, with the numeric cutoffs surfaced as a tunable note in `ice-scoring.md` (single source of truth for calibration constants). These are starting heuristics from one engagement, not validated thresholds; mark them as such so a later run can recalibrate without a code-spelunk. Calibrate during Design only if a broader sample is available. |
| 4 | Approach OQ | `ice-scoring.md` insertion points for base-rate and evidence-quality anchors | The base-rate framing (~70% of A/B effects are true nulls; do not anchor on vendor case-study lifts) and the evidence-source-quality note need homes in the calibration module. | Defer exact insertion to Design (correct lifecycle placement: insertion points are Requirements detail, not Approach). The natural homes given the validator's existing anchors: base-rate framing under `## Confidence Calibration` (the validator already greps for that H2), the evidence-source-quality note adjacent to it, and the gated-Confidence anchor co-located with the same H2 so score.md Step 4's rewrite has one calibration reference. Verify against the live `ice-scoring.md` structure when authoring Requirements. |
| 5 | Discovery review | "Step 5b" collides across two phases | `construct.md` already has `Step 5b: Test Feasibility Estimation` and `score.md` already has a separate `Step 5b: Infeasible Routing`. Requirements 8 and 9 both say "Step 5b" (`construct.md` 5b power-check extension; `score.md` extend "Step 5b routing"), and the failure-mode map row FM3 lists `construct.md 5b + validate.md + score.md` without disambiguating which phase's 5b each edit targets. A Build agent could edit the wrong step. | Disambiguate in the Requirements during Design: always qualify as "`construct.md` Step 5b (Test Feasibility)" vs "`score.md` Step 5b (Infeasible Routing)". No renumbering needed; the collision is cosmetic but the Requirements language must name the phase every time. (needs user judgment on whether to renumber, but the low-risk default is qualify-don't-renumber.) |
| 6 | Discovery review | FM2 `control_stable` vs the existing CTR-14 mobile-render gate (boundary) | Tranche 1 already routes `mobile_render_clean: false` to fix-and-monitor via the `construct.md` mobile branch and CTR-14. The new FM2 `control_stable` gate (validate.md) adds a "verify current before launch" prerequisite for stale or cross-artifact-contested structure. For a mobile-render observation these can both fire, risking double-gating or contradictory routing (CTR-14 reframe vs `control_stable` prerequisite). The Approach assigns FM2 to `detect.md` + `validate.md` but does not state the boundary against the existing CTR-14 gate. | Design must state the boundary: CTR-14 owns the rendering-defect-class reframe (broken render = fix, do not test); `control_stable` owns staleness and cross-artifact element disagreement (the captured structure may be out of date or contested, so verify current before launch). A broken render is not a staleness signal, so they should not co-fire on the same observation. Make `validate.md` defer to CTR-14 when `mobile_render_clean: false` is the only signal, and reserve `control_stable` for capture-date and element-disagreement signals. |
| 7 | Discovery review | FM5 gated rubric vs existing scattered Confidence modifiers (boundary) | `score.md` Step 4 currently carries ~10 Confidence modifiers (lines 59-69: inferred-before -1, partial-trigger -1, proof-integrity cap 3, proxy -1, traffic-adequacy +/-1, failure-mode +/-1) plus graceful-degradation caps (lines 17-22). Requirement 9 says "rewrite Step 4 Confidence handling into the gated rubric" but does not specify whether the new hard gate subsumes, layers above, or runs alongside these existing soft modifiers. Two scoring systems on the same dimension with unspecified interaction is a drift risk. | Design must specify the order of operations: the gated rubric should run as a hard ceiling applied AFTER the existing soft modifiers compute a raw Confidence (gate fail caps at 3, multiple fails cap at 2, per the Approach). The existing proof-integrity cap-at-3 (line 63) is a near-duplicate of one gate and should be reconciled (fold into the rubric or explicitly cross-reference) to avoid two rules doing the same job. Specify in Requirements. |
| 8 | Discovery review | Absence/legacy degradation must be explicit in the gated rubric itself | The Approach states the graceful-degradation rule (absent-artifact gate = "not assessed", never penalizes; legacy degrades to whatever artifacts exist). But the rule lives only in the Approach narrative and the FM-map is silent on it per-gate. The risk: a Build agent authoring the gated rubric (FM5) reads "Confidence 4-5 REQUIRES all gates pass" literally and treats a not-assessed gate (absent performance profile = no `baseline_exists`, absent structural artifact = no `control_stable`) as a fail, which would silently penalize legacy mode and violate the skill's load-bearing absent-never-penalizes invariant (SKILL.md lines 175, detect.md degradation table). | Design must encode the tri-state explicitly in the rubric: each gate is pass / fail / not-assessed; only an affirmative fail caps Confidence; not-assessed is neutral and never blocks Confidence 4-5 on its own. State this in Requirement 6 (validate.md) and Requirement 9 (score.md gated rubric) verbatim, not just in the Approach. This is the single highest-consequence correctness risk in the fold. |
| 9 | Approach OQ | Bot/synthetic-traffic correction before sizing and Impact scoring (proposed scope addition) | The performance triggers (`detect.md` Step 1c) and Impact modifiers (`score.md` Step 4) fire on raw traffic and bounce figures with no data-hygiene gate. When a performance profile flags bot or synthetic-monitoring contamination on a surface, the uncorrected figure inflates opportunity sizing and Impact. Adjacent to this change's measurement-rigor theme but absent from the current eight failure-modes. | Decide in Discovery: absorb as a 9th failure-mode (a data-hygiene gate that discounts contamination-flagged figures before sizing and scoring, and surfaces the correction) or spin out as a separate backlog item per the Simplicity Bias. Leaning absorb: shares the `validate.md`/`score.md` surface and the same rigor-that-bites thesis. (needs user judgment) |
| 10 | Approach OQ | Forced-spread when a Confidence dimension clusters (proposed scope addition; interacts with FM5) | `score.md` Step 5 anti-pattern checks detect score clustering, all-high, and Impact inflation but provide no remedy when a dimension genuinely pins. The FM5 gated Confidence rubric in this change can increase Confidence clustering (more caps at 3), so the missing forced-spread procedure becomes more relevant under this change, not less. | Decide in Discovery: absorb (add a forced-spread procedure to `score.md` Step 5: when one dimension is effectively constant across the portfolio, require the other two to span a minimum range and at least one hypothesis a full tier below the top) or spin out. Leaning absorb: FM5 worsens the clustering this addresses and both edit `score.md`. (needs user judgment) |
| 11 | Approach OQ | Delivery/segment under-delivery as an interpretation threat, not only a launch gate (proposed scope addition) | When a delivery constraint biases the exposed population away from the intended segment (the variant under-delivers to the cohort the change is for), a metric win can concentrate in the wrong cohort. The engagement-constraint reasoning treats delivery-match as a launch gate but does not carry the skew into each hypothesis's interpretation or loss branch. | Decide in Discovery: absorb (carry a known delivery or segment skew into the affected hypothesis's win/loss interpretation in `construct.md` Step 6, not only into Prerequisites) or spin out. Lighter than FM1-FM8; could ride along or defer. (needs user judgment) |
## Background

Two efforts converge here.

**Tranche 1 (structural observation consumption, Phase C).** Phase A added the optional
`silver-structural-observation` row to the KB Read-side Mapping (commit `aeaf19f`), so
`reference/cro-{scope}/live-structure.md` loads into detect's context in KB mode. Phase B built the
producer (live-capture). But loading is not consumption: `phases/detect.md` Step 1 signal extraction
is file-keyed and had no stanza for the structural artifact, so its fields never became signals, and
the Tier 2 reframing gates (mobile defect-vs-layout, site-wide scope correction) did not exist.
Tranche 1 closes that gap. It is implemented and passed a KB chain run (see `Verification Results`).

**Tranche 2 (premise & measurement rigor, this fold).** The skill produced a 9-hypothesis gold
roadmap for a B2B enterprise client (the pilot, 2026-06-09). An independent evidence review (external
research + adversarial red-team + a fresh live re-capture) examined 5 of 9 hypotheses. Four of five
high-confidence "Quick Wins" did not survive contact with the skill's own source KB:

- #1 specific-claim hero: ICE 13 to 9 (stale control, no baseline, thesis not in the dominant element)
- #2 proof hierarchy: 13 to 7, demoted (premise contradicted by capture instability + below-fold dilution)
- #3 returning-user login: 12 to 8, reframed to an IA fix (audience is 68-97% NEW, not returning; control stale; metric off-domain)
- #4 single primary CTA: 12 to 6, demoted (performance profile classifies these pages as demand problems, not clutter; ~4-5 year test)
- #5 progressive demo form: 11 to 10, CONFIRMED (grounded in a stable, quantified analytics fact the KB confirmed)

The failures are not random. The hypotheses that fell apart were grounded in volatile structural
snapshots and unverified causal premises; the one that survived was grounded in a stable, quantified
analytics fact the KB itself confirmed. The skill already has Test Feasibility estimation, a
self-critique meta-pass, proxy guardrails, bundled disclosure, and Confidence caps. These exist as
scattered, ungated modifiers the agent can satisfy on paper while the premise, metric, or statistical
power does not actually hold on the page. The fix is to make that rigor binding. Every check is
KB-internal (triangulate artifacts already loaded, do arithmetic on numbers already loaded, gate the
score), so the no-research charter is preserved.

Folding rationale: tranche 2's triangulation and staleness gates lean directly on the structural
facts tranche 1 makes consumable, and both tranches edit the same files (`detect.md`,
`construct.md`, `SKILL.md`). The user elected to carry both as one change (see Open Issue 1).

## Current State

**Tranche 1 (built).**
- Read-side row + note exist ([SKILL.md](../../skills/hypothesis-generator/SKILL.md)); the body loads and is consumed via the Step 1 structural extraction stanza and the Step 1e field-keyed trigger table.
- [construct.md](../../skills/hypothesis-generator/phases/construct.md) has the mobile defect-vs-layout red-flag branch and the Step 1 site-wide scope generalization.
- `modules/contrarian-triggers.md` CTR-14 carries the structural detection signal (`mobile_render_clean: false`) and gate-clearing observation (`true`).

**Tranche 2 (rigor gaps to close).**
- **No triangulation.** A hypothesis's causal premise is built from one artifact and never cross-checked against the others. [construct.md](../../skills/hypothesis-generator/phases/construct.md) Step 4 (causal mechanism) does not validate the premise against performance / audience / competitive / structural artifacts. The pilot roadmap's #4 asserted "clutter suppresses form-opens" while the same KB's performance profile classified those pages as demand problems.
- **No staleness awareness.** [detect.md](../../skills/hypothesis-generator/phases/detect.md) reads structural facts but does not tag their capture date or detect when artifacts disagree on the same element (redesign-in-progress). The pilot's #1/#3/#4 built on stale or contested current-state.
- **Feasibility/power is partial.** [construct.md](../../skills/hypothesis-generator/phases/construct.md) Step 5b estimates duration for hypotheses that have a Baseline, with 100-conversion and 7-day hard gates, but it does not check the guardrail/secondary metric, does not use the segmented denominator, and does not gate Confidence. Pages with no baseline (homepage, uninstrumented) slip through. The pilot's #1 (no baseline) was the top Quick Win; its #2/#4 guardrails were statistically unreadable.
- **Instrumentation-blind metrics.** [construct.md](../../skills/hypothesis-generator/phases/construct.md) Step 5/5a select and classify metrics but never check the metric is actually instrumented. The pilot roadmap named element-click, scroll-section, qualified-lead, and homepage analytics as read metrics while its own Prerequisites listed them as missing.
- **Confidence inflation.** [score.md](../../skills/hypothesis-generator/phases/score.md) Step 4 has scattered caps (proof integrity, proxy, low traffic, contradicting failure-mode) but no hard gate: Confidence 4 was assigned to hypotheses with no baseline, contradicted premises, or uninstrumented metrics.
- **All-visitors design on diluted pages.** [construct.md](../../skills/hypothesis-generator/phases/construct.md) Step 5 allows "all visitors" and defers segmentation to the post-hoc "if inconclusive" path (Step 6), even when the KB shows the persuadable segment is a diluted minority.
- **Bundling without interpretability.** The Experiment Scope Rule + Step 5c disclosure exist, but nothing checks the thesis-bearing element is the dominant change or that a bundled element is seen by most visitors. The pilot's #1 bundled an H1 carrying no specific claim under a "specificity" thesis.
- **Self-critique without consequence.** [construct.md](../../skills/hypothesis-generator/phases/construct.md) Step 10 names counterarguments and has fail states, but the fail states do not reliably change the score. The pilot's self-critiques named the decisive weakness and left Confidence at 4.

## Approach

One change, two tranches. Tranche 1 is implemented (five-file structural-consumption edit, validator counts unchanged at phase 4 / pattern 32 / CTR 14). Tranche 2 adds the rigor enforcement and is the work this fold designs and builds.

### Change Profile

- **Script-affecting: no.** No Python scripts in a skill `## Scripts` table are added, modified, or removed. The repo-level bash validator `scripts/validate-hypothesis-generator.sh` is edited (phase count, new presence checks), but it is a test harness, not a registered Python script; no `_tests/` layer applies.
- **Performance-affecting: yes.** The change alters the skill's analytical output behavior (scoring gates, validation pass). `_evals/` does not exist in this repo, so benchmarking is via the skill's validator script plus a functional KB chain regression run against a real bound-KB artifact set (the acceptance test), not the eval framework.
- **Test-eval-only: no.**

### Architecture decision (tranche 2)

Add a dedicated **`phases/validate.md` (Phase 3.5)** between construct (Phase 3) and score (Phase 4).
It is the single highest-leverage structural change the diagnosis points to: it makes "validate the
premise, metric, and power before scoring" a first-class, hard-to-skip step rather than a set of
modifiers the agent can satisfy on paper. The phase consumes detect's measurement-inventory and
staleness facts plus construct's hypothesis records, and emits a per-hypothesis `validation_gates`
record that score.md consumes as hard caps. (Alternative: consolidate into a construct Step 5d, no
new phase file. See Open Issue 2.)

### Failure-mode to fix mapping (tranche 2)

| # | Failure mode | Fix | Owner |
|---|---|---|---|
| 1 | Premise contradicted by another KB artifact | Premise triangulation gate. Cross-check each causal claim against performance / audience / competitive / structural artifacts. Authority on conflict: measured performance > observed structure > inferred positioning. Contradiction surfaces, then resolves or sets `premise_contradicted: true`. | `validate.md` |
| 2 | Structural claims treated as timeless | Staleness signals (capture-date tagging, cross-artifact element disagreement, redesign-in-progress) extracted in detect; `control_stable` gate in validate attaches a "verify current before launch" prerequisite. | `detect.md` + `validate.md` |
| 3 | No feasibility/power check on the thesis metric | Extend Step 5b math to the guardrail/secondary metric and the segmented (not pooled) denominator; emit explicit MDE or "unpowerable". Validate enforces; score routes unpowerable-on-thesis-metric to "What's Not Here". Keep the existing 100-conversion and 7-day hard gates. | `construct.md` 5b + `validate.md` + `score.md` |
| 4 | Metrics proposed without checking instrumentation | Measurement inventory (`instrumented_metrics` / `dark_metrics`) extracted in detect; `metric_instrumented` gate in validate blocks any primary/guardrail not instrumented, routes it to Prerequisites, caps Confidence. | `detect.md` + `validate.md` |
| 5 | Confidence inflation | Gated Confidence rubric. Confidence 4-5 requires all gates pass (premise not contradicted, primary metric instrumented, baseline exists, control stable, powerable, segmentation satisfied). Any fail caps at 3; multiple fails cap at 2. | `score.md` Step 4 |
| 6 | All-visitors design on a diluted page | Segmentation pre-registration. When performance shows dilution (Direct/bounce/new thresholds, or a sub-audience-only mechanism), the primary read is pre-registered as the segment, not deferred to the post-hoc path. Non-isolable segment becomes an instrumentation block. Plus a viewport/scroll-reach dilution flag for below-fold stimuli. | `construct.md` Step 5 |
| 7 | Bundling without interpretability | Bundle interpretability check. The thesis-bearing element must be the dominant change; a bundled element seen by very few visitors makes a flat result uninterpretable. Restructure or split before emission. | `construct.md` Step 5c |
| 8 | Self-critique names a flaw, changes nothing | Consequential self-critique. Each unmitigated counterargument must change the design or reduce the relevant ICE component (Counter-A to Confidence; Counter-C to Impact or add a guardrail), emitted for score.md to apply. | `construct.md` Step 10 + `score.md` |

### Preserve (do not break)

The four-phase scaffolding (now five with validate), the self-critique sections, the bundled-elements
disclosure, the win/loss framing, the "if inconclusive" protocols, the measurement-reality preamble in
the roadmap output, and the no-research charter. The fixes strengthen these, they do not remove them.

### Graceful degradation

A gate evaluated over an absent artifact is "not assessed" and never penalizes (mirrors the existing
absent-artifact rules). Legacy mode (fewer artifacts than KB mode) degrades to triangulating across
whatever artifacts exist; absence never lowers Confidence on its own.

### Design decisions carried from tranche 1

1. Mobile gate extends CTR-14 rather than adding CTR-15.
2. Both an extraction stanza and a gated Step 1e trigger table (stanza feeds generic matching; Step 1e carries tri-state semantics and the no-double-count boundary).
3. Site-wide scope correction lives in construct.md Step 1 (target identification, not bundling).
4. Absent structural artifact skips Step 1e with no confidence penalty.
5. Out of scope by design: PE-01/02, NX-03, NX-05, PS-02 (feeds as an ordinary signal).

## Requirements

### Tranche 1 (implemented)

1. `skills/hypothesis-generator/phases/detect.md`: Required Inputs bullet; graceful-degradation row; Step 1 structural extraction stanza (site-level + per-page, tri-state never coerced, missing field = not_checked, trust qualifiers downgrade to partial); Step 1e gated trigger table.
2. `skills/hypothesis-generator/phases/construct.md`: red-flag mobile branch on `mobile_render_clean`; Step 1 site-wide scope check; Step 2 observed current-state citation + baseline boundary echo.
3. `modules/contrarian-triggers.md` CTR-14: structural detection signal (false) and gate-clearing observation (true). Count line untouched.
4. `skills/hypothesis-generator/SKILL.md`: read-side note rewrite; KB-mode precondition bullet with no-penalty absence semantics; purity-list additions.
5. `skills/hypothesis-generator/CHANGELOG.md`: one dense Added bullet under [Unreleased].

### Tranche 2 (this fold, to be finalized in Design)

6. **`skills/hypothesis-generator/phases/validate.md` (NEW, Phase 3.5).** Consumes detect's measurement-inventory + staleness facts and construct's hypothesis records. Emits a per-hypothesis `validation_gates` record (`premise_contradicted`, `metric_instrumented`, `baseline_exists`, `control_stable`, `powerable`, `segmentation_satisfied`) with per-gate notes. Owns triangulation (FM1), control-stability (FM2), instrumentation enforcement (FM4), feasibility/power enforcement (FM3). Defines the authority order for contradiction resolution and the graceful-degradation rule (absent-artifact gate = not assessed, no penalty).
7. **`skills/hypothesis-generator/phases/detect.md`.** New Step 1f: measurement inventory (`instrumented_metrics` / `dark_metrics` from the performance profile's tracked events and its documented data gaps) and staleness signals (capture-date tagging of structural facts; cross-artifact element-disagreement / redesign-in-progress detection). Layers after the tranche-1 Step 1/1e.
8. **`skills/hypothesis-generator/phases/construct.md`.** Step 5 segmentation pre-registration (FM6) with dilution thresholds and the viewport/scroll-reach flag; Step 5b power-check extension to the guardrail metric, segmented denominator, and explicit MDE (FM3); Step 5c bundle-interpretability check (FM7); Step 10 consequential self-critique that emits score effects (FM8).
9. **`skills/hypothesis-generator/phases/score.md`.** Rewrite Step 4 Confidence handling into the gated rubric (FM5); extend Step 5b routing for blocked/unpowerable hypotheses; Step 6 Quick Win eligibility requires all validation gates pass.
10. **`skills/hypothesis-generator/SKILL.md`.** Register Phase 3.5 in the Execution Pipeline and Module Dependencies tree; add a per-hypothesis natural-language Readiness line to the Output Format (launch-blocking prerequisites, "verify current", pre-registered segment); reinforce the measurement-reality preamble; extend the Deliverable Purity Constraint with the new field names (`validation_gates`, `premise_contradicted`, `instrumented_metrics`, `primary_read_segment`, and the rest).
11. **`modules/ice-scoring.md`.** Add the base-rate calibration anchor (~70% of A/B effects are true nulls; do not anchor expectations on vendor case-study lifts), the evidence-source-quality note (peer-reviewed meta-analysis vs vendor case study), and the gated-Confidence anchor. Insertion points verified in Design (Open Issue 4).
12. **`scripts/validate-hypothesis-generator.sh`.** Phase-file count 4 to 5; add presence checks for the new step headers (detect Step 1f, validate.md gate record, score.md gated-rubric marker); extend the field-name purity grep set. Pattern count 32 and CTR count 14 unchanged.
13. **`skills/hypothesis-generator/CHANGELOG.md`.** Extend the [Unreleased] bullet (or add a second) covering tranche 2.

## Verification Design

### Validation

1. `bash scripts/validate-hypothesis-generator.sh`: all PASS; counts correct (phases 5, patterns 32, CTR 14); purity greps clean (no em dashes over edited files, no client strings, no new field-name leakage into the roadmap body).
2. Phase 3.5 is reachable and ordered between construct and score in SKILL.md; the `validation_gates` record is produced per hypothesis and consumed by score.md's gated rubric.
3. Tranche-1 behaviors still hold (structural trigger fires and lands; mobile gate both directions; site-wide form generalization; tri-state honored; absent structural artifact completes with no confidence penalty).
4. **Acceptance / regression (the decisive test):** re-run `/hypothesis-generator --scope <client-scope>` in the bound client KB repo (private) WITHOUT the evidence dossiers as input. Confirm the skill independently:
   - de-tiers #1-#4 (none at Confidence 4+ while its premise is contradicted by another artifact, its primary metric is uninstrumented, no baseline exists, or the control is unstable);
   - retains #5;
   - attaches staleness "verify current" prerequisites to structure-dependent hypotheses;
   - produces a feasibility/power note or an explicit "unpowerable / micro-conversion only / pool required" per experiment, derived from the KB's traffic numbers;
   - pre-registers a segment for diluted-audience hypotheses;
   - produces self-critiques that change either the design or the score;
   - keeps the deliverable body pure (no field names, pattern IDs, or system internals).
5. Absence regression: remove optional artifacts (including the structural artifact), re-run, confirm completion with no confidence penalty for absent gates and graceful legacy-mode degradation.

### Evals

No matched eval tasks (`_evals/` does not exist in this repo). Performance-affecting validation is the
functional KB chain regression run in requirement-Validation step 4, which is the empirical
acceptance test (independent reproduction of the dossier conclusions).

## Verification Results

### Validation Outcomes

Tranche 1: prior KB-repo chain run PASSED (recorded below). Tranche 2: not yet built.

### Tranche 1 results (2026-06-09, KB-repo chain run against the real artifact)

1. Validator 24/24 PASS, counts unchanged; purity greps clean.
2. Chain run PASSED: structural artifact loaded in silver reads AND gold depends_on; gold artifact superseded in place (1.0.0 to 1.0.1); kb_type_validate passed; post-write review clean.
3. Watch items all correct: FO-01/FO-02 fired on the site-wide form with the Step 1 site-wide scope correction, composed with the CTR-01 enterprise qualifying-friction reframe; TC-01 correctly did NOT fire (the only absent page was a WAF-blocked zero-content capture; trust-qualifier downgrade behaved as designed); CR-01 fired on the competitive leg only (not_checked existence tri-state neither fired nor suppressed the structural leg); 9 hypotheses (4 QW / 3 SB / 2 EX); deliverable body purity held.
4. OUTSTANDING (tranche 1): absence regression (remove the structural artifact, re-run, confirm no confidence penalty). Now folded into the tranche-2 absence regression (Validation step 5).
5. PRODUCER-SIDE FINDING (routes to live-capture, not this change): a page captured with a non-clean page_block_status asserted tri-state existence fields as absent instead of not_checked. The consumer's trust qualifiers compensated, but the artifact should not record the false assertion.

## Changelog

| Version | Changes |
|---|---|
| 0.5.0 | Folded three adjacent measurement-rigor scope questions into Open Issues as Approach OQs (#9 bot/synthetic data-hygiene gate before sizing and Impact, #10 forced-spread when a Confidence dimension clusters, #11 delivery/segment under-delivery as an interpretation threat), each framed absorb-vs-spin-out for Discovery adjudication. Sourced from an independent post-v1.6.0 gap analysis; these are the residue not already covered by the eight failure-modes. No Approach or Requirements change yet; scope decision pending. ICE unchanged at 5/4/2. |
| 0.4.0 | Discovery entry re-review (fresh context). Validated the inherited Approach against canonical guidelines: agree-and-proceed on the fold and on `phases/validate.md` (Open Issues 1-2). Refined all four Approach OQ Recommendations in place with concrete, defensible resolutions. Persisted five new `Discovery review` Open Issues: #5 the cross-phase "Step 5b" name collision (construct Test-Feasibility vs score Infeasible-Routing), #6 FM2 `control_stable` vs the existing CTR-14 mobile-render gate boundary, #7 FM5 gated rubric vs the existing scattered Confidence modifiers in score.md Step 4, #8 absence/legacy tri-state degradation must be encoded in the rubric itself (highest-consequence correctness risk), #9 named client string in the public repo. Mechanical validation clean (frontmatter, links, no em dashes). ICE re-evaluated, unchanged at 5/4/2. |
| 0.3.0 | Folded the premise & measurement rigor scope (tranche 2) into this change. Broadened name/description/title; status reset to Discovery for the new scope; re-graded ICE to 5/4/2. Added Background (rigor diagnosis from the pilot evidence review), Current State (8 rigor gaps), Approach (Change Profile, `phases/validate.md` Phase 3.5 decision, 8 failure-mode to fix mapping, preserve list, graceful degradation), Requirements tranche 2 (items 6-13), Verification Design with the bound-KB acceptance test, and an Open Issues section (4 Approach OQs). Tranche 1 (structural consumption) preserved as implemented; its outstanding absence regression folded into the tranche-2 absence test. |
| 0.2.0 | Build complete (tranche 1): all five structural-consumption file edits applied, validator 24/24 PASS, purity greps clean. Note: the working tree was switched to dj_live-capture-skill by a parallel session mid-build; Phase A's two SKILL.md lines and CHANGELOG bullet (commit aeaf19f, unmerged branch dj_hypgen-structural-observation-readside) were re-applied in the working tree so content is complete regardless of branch. Branch reconciliation required at commit time. |
| 0.1.0 | Initial change document (Backlog), created from approved plan; building in-session. |
