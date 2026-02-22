# ICE Scoring: Calibration Anchors and Rules

Version: 1.0.0

This module defines the scoring calibration for the ICE framework used by the hypothesis generator. Read this before scoring any hypothesis. The purpose of calibration anchors is to prevent score inflation and ensure consistency across runs.

---

## Scoring Philosophy

ICE scores are relative within a single roadmap, not absolute across companies. A "4 Impact" for Company A doesn't need to mean the same thing as a "4 Impact" for Company B. What matters is that within a single roadmap, the scores differentiate hypotheses from each other meaningfully.

The most common failure mode is score clustering: everything lands at 3-4, making the roadmap useless for prioritization. The anchors below exist to prevent this.

---

## Impact Calibration (1-5)

Impact measures the expected effect on conversion, revenue, or strategic learning if the variant wins.

| Score | Anchor Description |
|-------|--------------------|
| 1 | Cosmetic change. No measurable conversion effect expected. (These shouldn't be in the roadmap.) |
| 2 | Minor improvement. Affects a secondary metric or low-traffic page. Measurable but not material. |
| 3 | Moderate improvement. Affects a primary metric on a secondary page, or a secondary metric on a primary page. |
| 4 | Significant improvement. Affects the primary conversion metric on a high-traffic page. Would change quarterly numbers. |
| 5 | Transformational. Changes the company's core conversion rate, repositions against competitors, or opens a new revenue path. Reserved for 1-2 hypotheses per roadmap at most. |

**Calibration rules:**
- No more than 2 hypotheses should score Impact 5 in a single roadmap
- At least 1 hypothesis should score Impact 2 or below
- Homepage experiments default to Impact 3+ (highest-traffic page). Secondary pages default to Impact 2-3 unless evidence suggests otherwise.
- Impact scores should NOT all cluster in the 3-4 range. If they do, force differentiation.

---

## Confidence Calibration (1-5)

Confidence measures how certain you are that the experiment will produce a measurable, interpretable result. This is NOT "how sure are you it will win." Even a well-designed experiment that loses can produce high-value learning.

| Score | Anchor Description |
|-------|--------------------|
| 1 | Pure speculation. No data supporting the hypothesis. Testing a hunch. |
| 2 | Informed guess. Pattern is common in CRO, but trigger conditions are partially confirmed. Limited context support. |
| 3 | Solid reasoning. Trigger conditions confirmed in context. Causal mechanism is sound. But no baseline data to estimate effect size. |
| 4 | Strong basis. Full context support, clear causal chain, and either baseline data or strong historical precedent for this type of test. |
| 5 | Near certainty. Confirmed trigger, strong causal chain, historical data showing this pattern wins frequently. Reserved for patterns with calibration data from evidence modules. |

**Calibration rules:**
- Without any baseline analytics data, Confidence is capped at 4 globally
- Without audience-messaging.md, persona-based hypothesis Confidence is capped at 3
- Without positioning-scorecard.md, gap-triggered hypothesis Confidence is capped at 3
- Partial triggers (from Phase 2) reduce Confidence by 1
- Confidence 5 should only appear when calibration data from evidence modules is present
- "Before" state based on exact copy from context: no adjustment. "Before" state inferred: Confidence -1.

---

## Ease Calibration (1-5)

Ease measures implementation effort. Higher = easier.

| Score | Anchor Description |
|-------|--------------------|
| 1 | Major engineering effort. New infrastructure, cross-team coordination, multi-sprint implementation. |
| 2 | Significant effort. Structural page changes, CMS modifications, new tooling integration. Likely requires developer involvement. |
| 3 | Moderate effort. Layout restructuring, multi-step form implementation, or changes requiring both design and development. |
| 4 | Low effort. Copy changes, image swaps, minor layout adjustments. Can be done by a marketer with CMS access. |
| 5 | Trivial. Single text change. Copy-paste into CMS. Deployed in under an hour. |

**Calibration rules:**
- Copy-only changes: Ease 4-5
- Layout restructuring: Ease 2-3
- Personalization requiring new infrastructure: Ease 1-2
- Personalization with existing tooling: Ease 2-3
- Form changes on owned forms: Ease 3-4
- Form changes on embedded third-party (Marketo, HubSpot): Ease 2-3
- If implementation requires stakeholder approval beyond the testing team (e.g., pricing changes): Ease -1

---

## Anti-Patterns (Check Before Finalizing)

### Score Clustering
**Symptom:** >70% of hypotheses have ICE totals within 2 points of each other.
**Fix:** Re-examine the strongest and weakest hypotheses. Score those two first, then spread the rest between them.

### Impact Inflation
**Symptom:** Every hypothesis has Impact >= 4.
**Fix:** Impact 4+ means "changes quarterly numbers." Most copy changes on secondary pages don't do that. Recalibrate against the anchors.

### Confidence Without Data
**Symptom:** Hypotheses score Confidence 4 despite no baseline analytics.
**Fix:** Without analytics, Confidence is capped at 4. Without positioning-scorecard, capped at 3. Without audience-messaging, persona hypotheses capped at 3.

### Ease Optimism
**Symptom:** Structural changes and personalization hypotheses score Ease 4+.
**Fix:** Anything requiring developer involvement is Ease 3 at most. Anything requiring new tooling or infrastructure is Ease 2 at most.

### "Everything is a Quick Win"
**Symptom:** >50% of hypotheses tier as Quick Wins.
**Fix:** Quick Wins require Confidence >= 4 AND Ease >= 4. That's a high bar. If most hypotheses clear it, either the context is unusually strong or scoring is too generous.

---

## Modifier Application Order

When multiple modifiers apply to the same dimension:

1. Start with pattern baseline
2. Apply pattern-specific modifiers (from experiment-patterns.md)
3. Apply calibration overrides (from evidence modules, if present)
4. Apply contextual adjustments (from phases/score.md)
5. Clamp to 1-5

If calibration overrides exist (step 3), they replace the result of steps 1-2 for the overridden dimension. Steps 4 still applies on top.
