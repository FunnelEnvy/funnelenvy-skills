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
- If performance-profile.md exists and `traffic_adequacy` is "high": Confidence +1
- If performance-profile.md exists and target page has conversion data: Confidence +1
- If performance-profile.md exists and `traffic_adequacy` is "low": Confidence -1

**Impact adjustments:**
- If the targeted page is the homepage: Impact +1 (highest traffic page for most B2B sites)
- If the hypothesis addresses the scorecard's "top gap": Impact +1
- If the hypothesis targets a page not mentioned in any context file: Impact -1 (uncertain traffic)
- If performance-profile.md exists and target page has >500 sessions/mo: Impact +1
- If performance-profile.md exists and target page has bounce rate >50%: Impact +1
- If performance-profile.md exists and target page conversion rate <50% of site average: Impact +1
- If performance-profile.md exists and target page has <100 sessions/mo: Impact -1

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

### Step 6: Compute ICE Totals and Tier

**ICE Total** = Impact + Confidence + Ease (range: 3-15)

**Tiering rules:**

| Tier | Criteria | Purpose |
|------|----------|---------|
| **Quick Win** | Confidence >= 4 AND Ease >= 4 | Build testing momentum. Low risk. |
| **Strategic Bet** | Impact >= 4 AND ICE Total >= 10 AND not Quick Win | Move the needle. Worth the effort. |
| **Exploration** | Everything else with ICE Total >= 7 | Learn something. Run when bandwidth allows. |
| **Cut** | ICE Total < 7 | Not worth running. Exclude from roadmap. |

If `--max` cap is hit after tiering, cut from the bottom of Explorations first, then Strategic Bets. Never cut Quick Wins (they build organizational confidence in testing).

### Step 7: Sequencing

Within each tier, sequence based on:

**Quick Wins: Ease-first ordering.**
Run the easiest wins first. Build momentum. Get the team comfortable with the testing process. If two Quick Wins have similar Ease, prioritize the one with higher Impact.

**Strategic Bets: Dependency-aware ordering.**
- If experiment A's result changes how you'd design experiment B, A goes first
- If two experiments target the same page, group them (reduces implementation overhead) but run them sequentially (don't confound variables)
- If a Strategic Bet validates a positioning assumption that other experiments depend on, it moves up

**Explorations: Learning-first ordering.**
- Explorations that test fundamental assumptions (e.g., "does this audience prefer outcome language or proof language?") go before explorations that test tactical variations
- Explorations that could become Quick Wins if they succeed go early

**Cross-tier dependencies:**
- If a Quick Win result would change the design of a Strategic Bet, note this dependency in the Sequencing Rationale section
- Never delay a Quick Win because of a Strategic Bet dependency (Quick Wins build momentum regardless)

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
