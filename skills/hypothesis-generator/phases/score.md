# Phase: ICE Scoring and Sequencing

## Required Inputs

- Hypothesis list from Phase 3 (construct)
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
| No baseline traffic/conversion data (no performance-profile.md) | Confidence scores capped at 4 globally. Add note to roadmap: "Run /ga4-audit for data-calibrated scores and traffic-driven hypotheses." |
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
- If `proof_integrity_passed` is false (from Phase 3 Step 4b): Confidence capped at 3 (unverified proof cannot support high confidence)
- If `metric_classification` is "proxy" (from Phase 3 Step 5a): Confidence -1 (indirect measurement adds uncertainty)
- If performance-profile.md exists and `traffic_adequacy` is "high": Confidence +1
- If performance-profile.md exists and target page has conversion data: Confidence +1
- If performance-profile.md exists and `traffic_adequacy` is "low": Confidence -1
- If target page has `failure_mode` matching the hypothesis mechanism (e.g., messaging hypothesis + `shallow_engagement`): Confidence +1 (data confirms mechanism)
- If target page has `failure_mode` contradicting the hypothesis mechanism (e.g., messaging hypothesis + `deep_engagement`): Confidence -1 (data suggests different root cause)

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

**Ease adjustments:**
- If the hypothesis requires only copy changes: Ease +1
- If the hypothesis requires structural/layout changes: no adjustment
- If the hypothesis requires personalization infrastructure: Ease -1 (unless context suggests it exists)
- If the hypothesis requires changes to third-party embedded elements (forms, chatbots): Ease -1

### Step 5: Score Validation

Before finalizing, check for scoring anti-patterns:

**Anti-pattern: Score clustering.** If >70% of hypotheses have ICE totals within 2 points of each other, the scoring is too flat. Re-examine: are you defaulting to safe middle scores? Force differentiation by re-evaluating the strongest and weakest hypotheses first, then spreading the rest.

**Anti-pattern: All high scores.** If no hypothesis scores below 3 on any dimension, you're being too generous. At least one hypothesis should have a low-Confidence or low-Ease score. Real experiment portfolios have range.

**Anti-pattern: Impact inflation.** If every hypothesis has Impact >= 4, recalibrate. Impact 4+ means "measurable revenue effect." Most copy changes on secondary pages are Impact 2-3.

Read the full calibration anchors in `modules/ice-scoring.md` to ground your scores.

### Step 5b: Infeasible Routing

Before tiering, remove hypotheses marked `feasibility: "infeasible"` from Phase 3 Step 5b. These experiments have insufficient traffic for A/B testing at current levels.

For each infeasible hypothesis:
1. Remove from the scoring pipeline (do not compute ICE total or assign a tier)
2. Record for the "What's Not Here" section: hypothesis name, target page, reason for infeasibility (estimated duration or traffic level), and suggested alternative approach (pre/post analysis, proxy metric, qualitative testing)

Infeasible hypotheses are NOT failures. They are real opportunities that require either more traffic, a different measurement approach, or a different test design. The "What's Not Here" section should present them as future opportunities, not rejects.

**Count:** Track the number of infeasible-routed hypotheses for the completion summary.

### Step 6: Compute ICE Totals and Tier

**ICE Total** = Impact + Confidence + Ease (range: 3-15)

**Tiering rules:**

| Tier | Criteria | Purpose |
|------|----------|---------|
| **Quick Win** | Confidence >= 4 AND Ease >= 4 AND estimated_duration_weeks <= 6 | Build testing momentum. Low risk. Fast signal. |
| **Strategic Bet** | Impact >= 4 AND ICE Total >= 10 AND not Quick Win | Move the needle. Worth the effort. |
| **Exploration** | Everything else with ICE Total >= 7 | Learn something. Run when bandwidth allows. |
| **Cut** | ICE Total < 7 | Not worth running. Exclude from roadmap. |

**Calendar-duration override.** If `estimated_duration_weeks` (from Phase 3 Step 5b) exceeds 6 weeks, the hypothesis cannot be tiered as Quick Win regardless of Confidence and Ease scores. Re-tier using the remaining rules:
- Strategic Bet if Impact >= 4 AND ICE Total >= 10
- Exploration if ICE Total >= 7
- Cut if ICE Total < 7

Add annotation to downgraded hypotheses: "Meets Quick Win scoring but estimated test duration ([N] weeks) exceeds the 6-week Quick Win ceiling. Reclassified as [new tier]."

Quick Wins exist to build organizational testing momentum. A 10-week test, regardless of implementation ease, does not build momentum. Mislabeling it burns stakeholder trust when the "quick" win takes a full quarter to read out.

**Duration not available.** If `estimated_duration_weeks` is absent (no `performance-profile.md`), the duration constraint does not apply. Quick Win eligibility uses only Confidence >= 4 AND Ease >= 4. The absence of performance data already caps Confidence via Phase 3 graceful degradation rules, which naturally limits Quick Win qualification.

If `--max` cap is hit after tiering, cut from the bottom of Explorations first, then Strategic Bets. Never cut Quick Wins (they build organizational confidence in testing).

### Step 7: Sequencing

Sequencing uses three layers, applied in priority order:

**Layer 1: Interaction dependencies (from Phase 3 Step 9)**
Multiplicative dependencies are hard constraints. If hypothesis A has `interaction_dependency.depends_on = B`, then B runs before A regardless of tier or LIFT category. Render these dependencies explicitly in the Sequencing Rationale.

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

1. **Winner Replication Priority.** When experiment-history data is available (future: experiment-history context layer) and a pattern has produced a statistically significant win on one page, queue a replication test of the same pattern on adjacent pages ahead of untested patterns. Replication tests have structurally higher Confidence (validated mechanism) and lower implementation cost (proven variant). This tiebreaker fires ONLY when experiment-history data exists. Without it, all hypotheses are treated as untested.

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
