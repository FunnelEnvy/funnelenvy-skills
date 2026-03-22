# ICE Scoring: Calibration Anchors and Rules

Version: 1.1.0
Last updated: 2026-03-20

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

## Empirical Calibration Data

The anchors above are heuristic. The data below provides empirically observed effort-to-impact ratios from real A/B tests, drawn from empirical CRO testing data (35,000+ experiments across verticals). Use these as reference points when the heuristic anchors feel uncertain.

### Effort-Impact Reference Points

| Test Pattern | Implementation Effort | Observed Lift | Key Metric | ICE Calibration Note |
|---|---|---|---|---|
| Form field label micro-copy change | 3 hours | +7.3% | Referred leads (deep funnel) | Ease 5, Impact 3-4. Do not cap Impact at 2 just because Ease is 5. |
| Hero text alignment (CSS only) | Minutes | +4% leads, +20% clicks | Leads + engagement | Ease 5, Impact 3. |
| Icon to "Log In" text label | Single element change | +4.1% orders, +5.3% RPV | Revenue | Ease 5, Impact 4. Described as biggest client win in 2 years. |
| Placeholder example text in form fields | Minimal | +19% | Leads (directional significance) | Ease 5, Impact 3. Directional but consistent with validated pattern on same site. |
| CTA copy "Subscribe" to "View Demo" | Trivial text change | +249% CTA clicks | SaaS engagement | Ease 5, Impact 4-5 for engagement metric. Downstream conversion impact varies. |
| CTA copy "Subscribe" to "Free Trial" | Trivial text change | +68% CTA clicks | SaaS engagement | Ease 5, Impact 4. |
| Social proof relocation above fold | Low (content move) | +22% | Form submissions | Ease 4, Impact 3-4. |
| Countdown calendar + hero shrink | Moderate (auto-updating element) | +45-65% | Subscriptions | Ease 3, Impact 5. Combined with ad creative parity (see EIE-03). |
| Conversational form replacement | Moderate (new form build) | +12% conversions, then 17% CAC reduction | Conversions + CAC | Ease 3, Impact 4. Compounded when replicated site-wide. |
| Button enlargement (donation page) | Low | +35% conversion, +13% revenue | Revenue | Ease 5, Impact 4. |
| Handwritten text + arrow to checkbox | Low (design asset) | +207% monthly donations | Monthly conversion | Ease 4, Impact 5. Outlier but reproducible on donation/selection pages. |

**Key calibration correction:** Micro-copy and UI label changes (Ease 5) routinely produce 4-20% lifts in primary metrics. The heuristic assumption that high-Ease tests have low Impact is empirically wrong for this pattern category. When scoring FO-04 (micro-copy), NX-07 (login prominence), EE-03 (commitment language), or any label/micro-copy hypothesis: do NOT automatically cap Impact at 2-3 just because Ease is 5.

### Industry Win Rate Baselines

Use these as Confidence calibration anchors:

| Context | Win Rate | Confidence Calibration |
|---|---|---|
| Industry average (all verticals) | 20-40% | A randomly selected hypothesis has ~30% chance of winning. Confidence 3 is the neutral starting point. |
| Pattern-matched with confirmed triggers | Substantially higher than baseline | Hypotheses matching validated patterns with full trigger conditions confirmed in context should start at Confidence 3-4, not 2-3. The pattern library filters for higher-probability tests. |
| Novel/untested pattern (no library match) | ~20-25% | Context-derived hypotheses (Phase 2b) without pattern library support should start at Confidence 2. |

**Scoring implication:** Pattern-matched hypotheses (Phase 2a) with full trigger confirmation have meaningfully higher probability than context-derived hypotheses (Phase 2b). Consider these Confidence floors:
- Pattern-matched with full trigger match: Confidence floor of 3
- Pattern-matched with partial trigger match: Confidence floor of 2
- Context-derived (Phase 2b): Confidence cap of 3 unless strong corroborating evidence exists (consistent with existing context-derived scoring rules)

### Minimum Test Thresholds

These thresholds complement the feasibility estimation in phases/construct.md (Step 5b). Use them as hard gates before finalizing any hypothesis:

- **100 conversions per variant** minimum (below this, effect sizes are unreliable)
- **7 days minimum** test duration (one full business cycle to capture day-of-week variation)
- If the page cannot produce 100 conversions per variant within the feasibility tier's time window: route to the next longer tier or to "What's Not Here" with a traffic requirement note
- If 3+ hypotheses in the roadmap target the same low-traffic page: flag as a prioritization conflict. Only the highest-ICE hypothesis should run; others queue behind it.

---

## B2B SaaS Calibration Anchors

These benchmarks apply specifically when `company-identity.md` category indicates a SaaS or B2B SaaS company. They supplement, not replace, the general calibration anchors.

### CTA Commitment Language (EE-03 Calibration)

| CTA Change | Observed Lift | Context |
|---|---|---|
| "Subscribe" to "Free Trial" | +68% CTA clicks | SaaS |
| "Subscribe" to "View Demo" | +249% CTA clicks | SaaS |
| Specific CTA ("Get Your Free Assessment") vs. generic ("Learn More") | +202% | All verticals (HubSpot, 330K CTAs) |

**Scoring rule:** When a B2B SaaS company's primary CTA uses high-commitment language (Subscribe, Buy, Purchase) and the audience is solution-aware or earlier, the Impact baseline for EE-03 should be 4 (not 3). The commitment gap in SaaS is larger than in other verticals because "Subscribe" implies ongoing financial obligation.

### Lead-Gen Benchmarks

| Metric | Value | Source |
|---|---|---|
| Average SaaS lead-gen conversion rate | ~7% | industry benchmark |
| New visitor sensitivity to form friction | 5-7x higher than returning visitors | agency testing data |
| Form field reduction (8 to 6): new visitors | +15.31% | B2B SaaS client |
| Form field reduction (8 to 6): returning visitors | +2.42% | B2B SaaS client |

**Scoring rule:** For FO-01 and FO-04 targeting SaaS lead-gen forms: if `performance-profile.md` shows new visitors >60% of form page traffic, add Impact +1. If returning visitors >60%, add Impact -1. (See also EIE-06 in hypothesis-interactions.md.)

### SaaS Copy Anti-Patterns

When constructing hypotheses for B2B SaaS companies, flag and penalize headlines that match these anti-patterns (Confidence -1 for any hypothesis that proposes copy containing them):
- Meaningless jargon: "Transform Your Business Processes!"
- Vague superlatives: "The leading platform for X"
- Feature-first framing without outcome: "AI-powered analytics dashboard"

Positive calibration: direct, specific copy consistently outperforms vague generalities. "Submit" beats clever CTAs on most signup forms.

### SaaS LTV Framework for Test Prioritization

LTV = (Avg Monthly Payment x Gross Margin %) / Churn Rate. Benchmark LTV:CAC ratio is 3:1.

When prioritizing experiments for SaaS clients, weight hypotheses that target:
- **Onboarding** (initial experience determines LTV trajectory): Impact +1 for hypotheses improving first-session experience
- **Upgrade paths** (freemium to paid, tier upgrades): Impact +1 for hypotheses on pricing/plan selection pages
- **Retention touchpoints** (in-app vs. email vs. website): note cross-channel propagation potential in Sequencing Rationale

---

## Predictive Scoring Reference

This section describes a predictive scoring system trained on 35,000+ experiments. It is included as reference for future calibration refinement. It does NOT replace ICE scoring in the current system.

### Predictive Scoring Decomposition

The system breaks prediction into three sub-scores:

1. **Predictive modeling factors:** Device targeting, page targeting, test type, and psychological principles yield a base probability (e.g., 35%)
2. **Industry comparisons:** Matching against similar tests in the same vertical adjusts probability (e.g., "similar tests have 60% win rate in eCommerce/apparel")
3. **Insight alignment:** Concordance with prior experiments on the same site adjusts further

Blended probability x estimated revenue impact = weighted impact estimate. Output actions: Prioritize / Revisit / Delete.

### Relevance to the Current System

This decomposition suggests a future refinement path for Confidence scoring:
- Sub-score 1 (predictive factors) is already partially captured by the pattern library's trigger conditions
- Sub-score 2 (industry comparisons) could be approximated with vertical-specific calibration tables (not yet built)
- Sub-score 3 (insight alignment) requires per-client experiment history data. When the experiment-history context layer is operational, Confidence scoring could be augmented with: "Prior experiments on this site that tested similar mechanisms had a Y% win rate."

Not actionable until the experiment-history system is operational. Documented here so the refinement path is visible when that system comes online.

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

### Micro-Copy Impact Underestimation (NEW)
**Symptom:** All Ease-5 hypotheses (micro-copy, label changes) score Impact 2.
**Fix:** Empirical data shows Ease-5 changes routinely produce 4-20% lifts. Reference the Effort-Impact Reference Points table above. FO-04, NX-07, and EE-03 are Ease 5 patterns that can legitimately score Impact 3-4.

---

## Modifier Application Order

When multiple modifiers apply to the same dimension:

1. Start with pattern baseline
2. Apply pattern-specific modifiers (from experiment-patterns.md)
3. Apply calibration overrides (from this module's empirical data and B2B SaaS anchors)
4. Apply contextual adjustments (from phases/score.md)
5. Apply interaction effect modifiers (from hypothesis-interactions.md EIE-06 and similar)
6. Clamp to 1-5

If calibration overrides exist (step 3), they replace the result of steps 1-2 for the overridden dimension. Steps 4-5 still apply on top.

---

## Context-Derived Hypothesis Scoring

Context-derived hypotheses (from Phase 2b) lack pattern precedent. They represent novel observations that don't fit any predefined CRO pattern. Score them with these calibration notes:

**Starting point:** 3/3/3 with Confidence -1 penalty applied at Step 1. This means context-derived hypotheses start at 3/2/3 before any adjustments.

**General calibration:**
- Context-derived hypotheses should generally score LOWER confidence than pattern-matched hypotheses. Patterns encode structural knowledge from repeated CRO observations. Novel hypotheses lack this foundation.
- If a context-derived hypothesis scores higher total ICE than most pattern-matched hypotheses in the same roadmap, re-examine. It's not impossible, but it's a signal to double-check the scoring.
- The Confidence -1 penalty can be neutralized (+1) only with a specific evidence citation from context files. "Strong evidence" as a general claim doesn't qualify. Name the context file section and the specific data point.

**Anti-pattern: Context-derived inflation.** If context-derived hypotheses are consistently scoring Confidence 3+ (after the penalty), the penalty isn't doing its job. At least half of context-derived hypotheses should remain at Confidence 2 after all adjustments.

**Skip steps 2-3:** Context-derived hypotheses have no pattern modifiers or calibration overrides. Jump from Step 1 directly to Step 4 (contextual adjustments) then Step 5 (interaction modifiers).
