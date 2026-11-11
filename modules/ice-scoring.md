# ICE Scoring: Calibration Anchors

Version: 2.0.0
Last updated: 2026-11-11

This module holds the calibration anchors for ICE scoring in hypothesis-generator. Read it before scoring. Every row in the backlog gets a score. ICE orders rows within a readiness tier; it never decides whether a row appears. The anchors and adjustments below are calibration guidance, not caps, quotas or thresholds.

## Scoring Philosophy

- **Relative within one roadmap:** a 4 for one company need not equal a 4 for another. Scores must separate rows from each other.
- **Evidence-led:** each score follows from the row's evidence. Missing inputs lower certainty because there is less evidence, not because a rule demands it.
- **Clustering defeats the purpose:** when most rows land at 3 or 4, re-score the strongest and weakest rows first and place the rest between them.

## Impact (1-5)

Expected effect on conversion, revenue or strategic learning if the variant wins.

| Score | Anchor |
|---|---|
| 1 | Cosmetic. No measurable conversion effect expected |
| 2 | Minor. A secondary metric or a low-traffic page |
| 3 | Moderate. A primary metric on a secondary page, or a secondary metric on a primary page |
| 4 | Significant. The primary conversion metric on a high-traffic page; would change quarterly numbers |
| 5 | Transformational. Changes the core conversion rate, repositions against competitors, or opens a revenue path |

**Guidance:**
- Homepage rows usually start at 3 or above; secondary pages at 2 or 3 unless evidence says otherwise.
- Impact 5 should be rare. If many rows reach it, re-read the anchor.
- **Strategic rows:** an off-page lever (a proof asset, a buying-group motion, a routing change) can earn Impact 5 when its business outcome is large, whatever its read model. A lever does not score lower for not being an on-page A/B. Measurement Foundation entries are never scored: value of information is not a conversion effect.

## Confidence (1-5)

How certain it is that the experiment yields a measurable, interpretable result. It is not the probability of winning. "Measurable" means readable at the `Decision Posture` in `SKILL.md`.

| Score | Anchor |
|---|---|
| 1 | Speculation. No supporting data |
| 2 | Informed guess. A common CRO pattern with conditions only partly confirmed |
| 3 | Solid reasoning. Conditions confirmed, mechanism sound, no baseline to size the effect |
| 4 | Strong basis. Full context support, clear causal chain, and baseline data or strong precedent |
| 5 | Near certainty. Confirmed conditions, strong chain, and repeated prior wins for this mechanism on comparable surfaces |

**Guidance:**
- With no performance profile there is no baseline, so Confidence 5 is hard to justify.
- With no audience-messaging, persona rows rest on less evidence; with no scorecard, gap-triggered rows do.
- A partial pattern match, an inferred current state, or copy adapted from L0 rather than audience-messaging each weaken the basis.
- A proxy primary is less certain than a direct one, unless all three `Guarded proxy` conditions in the `Decision Posture` hold.
- **Validation gates:** read each row's `validation_gates` as evidence. A premise contradicted by another artifact, a dark metric, a missing baseline, a contested control, an unpowerable thesis or a non-isolable segment are reasons for a lower score. They are not ceilings. `not-assessed` is neutral.
- **Non-pattern rows:** a card with no pattern precedent starts with less structural certainty. Specific corroborating evidence (a quoted current state, a measured signal, a named friction finding) can make up for it.
- **Strategic rows:** Confidence reflects how interpretable the read model is. A clean holdout with an adequate baseline reads close to a powered A/B; an uncontrolled before-and-after with confounds reads lower. A confirm-first row carries an unverified existence assumption, which also lowers it.

## Ease (1-5)

Implementation effort. Higher is easier.

| Score | Anchor |
|---|---|
| 1 | Major engineering: new infrastructure, cross-team, multi-sprint |
| 2 | Significant: structural changes, CMS work, new tooling; needs a developer |
| 3 | Moderate: layout restructuring, multi-step forms, design plus development |
| 4 | Low: copy changes, image swaps, minor layout; a marketer with CMS access |
| 5 | Trivial: one text change, deployed in under an hour |

**Guidance:**
- Copy-only 4 to 5. Layout 2 to 3. Personalization 1 to 2 without tooling, 2 to 3 with it. Owned forms 3 to 4; embedded third-party forms 2 to 3.
- Approval beyond the testing team (pricing, legal) lowers Ease by 1.
- Anything needing a developer is rarely above 3; new tooling rarely above 2.
- **Strategic rows:** anchor on stand-up scope. Content or configuration 4 to 5; a cross-team operational definition 3; a new capability on contended engineering 2; a business-model, compliance or channel change 1.

## Evidence and Base Rates

- **Base rate:** most well-run A/B tests are true nulls, and many low-powered wins do not replicate. A variant beats control in roughly 20% to 40% of tests. The honest prior for a new row is "probably no effect."
- **Cited lifts:** a vendor case study is one selected outcome. Discount toward the base rate, not toward the cited number.
- **Evidence strength, strongest first:**
  - A meta-analysis or large multi-site program: can support Confidence 4 alone.
  - A prior win on the same site with controlled variance: supports a replication, strongest when that mechanism is the dominant change.
  - One case study or published result: a directional signal that justifies running the test, not Confidence 4.
  - A behavioral principle with no experiment data: about Confidence 3 at most without other support.

## Effort-Impact Reference Points

High-Ease label and micro-copy changes often move primary metrics 4% to 20%. Do not hold Impact at 2 because Ease is 5.

| Test | Effort | Observed lift | Calibration note |
|---|---|---|---|
| Form label micro-copy | 3 hours | +7.3% referred leads | E5, I3 to 4 |
| Hero text alignment (CSS) | Minutes | +4% leads | E5, I3 |
| Icon to "Log In" text | One element | +4.1% orders | E5, I4 |
| Placeholder examples in fields | Minimal | +19% leads (directional) | E5, I3 |
| "Subscribe" to "View Demo" | Trivial | +249% CTA clicks | E5, I4 to 5 on the click metric; downstream varies |
| Proof moved above the fold | Low | +22% submissions | E4, I3 to 4 |
| Countdown plus hero shrink plus ad parity | Moderate | +45% to +65% subscriptions | E3, I5; combined change |
| Conversational form | Moderate | +12% conversions | E3, I4 |
| Larger donation button | Low | +35% conversion | E5, I4 |

## B2B SaaS Anchors

Apply when `company-identity.md` places the company in SaaS.

- **Commitment language:** with "Subscribe", "Buy" or "Purchase" as the primary CTA and a solution-aware or earlier audience, the commitment-level pattern (EE-03) scores Impact 4. Specific CTAs beat generic ones broadly.
- **Form friction by visitor type:** new visitors are far more sensitive to field count. For field reduction or micro-copy on a SaaS lead form: Impact +1 when new visitors exceed 60% of form traffic, -1 when returning visitors do.
- **Copy anti-patterns:** proposed copy with meaningless jargon, vague superlatives ("the leading platform") or feature-first framing without an outcome rests on weaker ground; lower Confidence by 1.
- **Lifetime value:** rows that improve first-session onboarding or the pricing and plan-selection path weigh more (Impact +1).

## Adjustment Order

1. Start from the pattern baseline, or 3/3/3 for a non-pattern card.
2. Apply the pattern's modifiers whose conditions are confirmed.
3. Apply this module's empirical and SaaS anchors.
4. Apply the contextual adjustments in `phases/score.md`.
5. Apply interaction modifiers from `modules/hypothesis-interactions.md` (for example EIE-06).
6. Clamp each score to 1-5.
