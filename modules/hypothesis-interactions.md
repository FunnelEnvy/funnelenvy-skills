# Hypothesis Interaction Model

Version: 1.0.0
Last updated: 2026-03-20

This module defines interaction effects between hypothesis categories. When two hypotheses target the same page, their interaction type determines whether they should be bundled, sequenced with explicit dependencies, or run independently.

## Interaction Types

**Multiplicative (AND-gate):** Both problems must co-occur to produce the observed failure mode. Fixing one alone yields diminishing returns because the remaining problem continues to suppress conversion. These pairs should be bundled into a single experiment or sequenced with an explicit dependency note.

**Additive (OR-gate):** Problems are independent. Each contributes to conversion loss proportionally. Fixing either helps. These pairs can be sequenced by ICE score without dependency constraints.

## Interaction Matrix

This matrix defines the default interaction type when two hypothesis categories target the same page. "Category" maps to the pattern categories in experiment-patterns.md.

| Category A | Category B | Interaction | Rationale | Implication |
|---|---|---|---|---|
| Headline/Messaging | Page Structure/Layout | Multiplicative | Unclear headline AND poor visual hierarchy means visitors neither understand nor find the value prop. Fixing the headline without restructuring the ATF leaves the message buried. Restructuring without fixing the headline amplifies a bad message. | Bundle into single experiment when both target ATF. If different page zones, sequence: messaging first (visitor must understand before structure matters). |
| Headline/Messaging | Form Optimization | Additive | Messaging clarity and form friction are independent conversion barriers. A visitor who understands the value prop may still abandon a high-friction form, and vice versa. | Sequence by ICE score. No dependency constraint. |
| Headline/Messaging | Social Proof | Multiplicative | Proof supports claims. If the headline claims an outcome and proof is absent or mismatched, the claim lacks credibility. If proof exists but the headline is vague, proof has nothing to anchor to. | Sequence: messaging first (establish the claim), then proof (support it). Note the dependency in Sequencing Rationale. |
| Headline/Messaging | Trust/Credibility | Additive | Trust signals (team credentials, certifications) operate independently of headline messaging. A visitor can trust the company but not understand the value prop, or vice versa. | Sequence by ICE score. |
| Headline/Messaging | Pricing | Additive | Pricing and messaging are independent evaluation dimensions. Unclear messaging doesn't make pricing feel wrong; it makes relevance unclear. | Sequence by ICE score. Exception: if the messaging hypothesis involves price anchoring or value framing, reclassify as Multiplicative. |
| Headline/Messaging | Navigation/UX Flow | Additive | Navigation affects pathfinding. Messaging affects comprehension. Independent channels. | Sequence by ICE score. Exception: NX-04 (paid landing page) has a Multiplicative interaction with messaging because ad-message match and navigation removal compound. |
| Page Structure/Layout | Form Optimization | Additive | Layout and form friction are independent barriers at different stages of the page experience. | Sequence by ICE score. |
| Page Structure/Layout | Trust/Credibility | Multiplicative | Structure determines what the visitor sees first. If proof is buried by poor structure, adding more proof doesn't help. If structure surfaces proof but the proof is weak, restructuring amplifies weakness. | Bundle when both target the same page section. Otherwise sequence: structure first (expose the right content), then strengthen the content. |
| Form Optimization | Trust/Credibility | Multiplicative | Form submission is a trust moment. If the form asks for info AND no trust signals exist near the form, both barriers compound. Reducing fields helps, but adding form-adjacent trust signals also helps, and doing both is more than the sum. | Bundle FO-03 (form context reinforcement) with any trust hypothesis targeting the same form. Sequence: trust signals near form first if not bundling. |
| Social Proof | Trust/Credibility | Additive | Both build trust but through different mechanisms (external validation vs. internal credibility). Independent contributions. | Sequence by ICE score. |
| Content/Resource | Headline/Messaging | Additive | Content pages (comparison, case study, ROI calculator) and messaging experiments operate on different pages or different visitor journey stages. | Sequence by ICE score. |
| Personalization | ANY | Multiplicative (conditional) | Personalization amplifies whatever it personalizes. If the base experience is broken (bad messaging, poor structure), personalization makes a bad experience feel targeted, which is worse than a generic bad experience. | Hard dependency: ALL page-level hypotheses on the target page must be resolved before testing personalization on that page. Personalization is always sequenced last for any given page. |
| Element Engagement | Headline/Messaging | Multiplicative (conditional) | When the element is a CTA, CTA performance depends on the preceding copy. A CTA optimization without fixing upstream messaging tests button design, not conversion strategy. | If both target the same page: sequence messaging first. CTA optimization follows, informed by winning message. If different pages: independent. |
| Element Engagement | Page Structure/Layout | Additive | Element-level interaction (CTA size, carousel structure) and page-level layout are different scopes. | Sequence by ICE score. Exception: EE-02 (element drop-off) + PS-01 (ATF reset) on the same page = Multiplicative. Bundle if the dropped-off element is above the fold. |

## Same-Page Interaction Analysis Process

When two or more hypotheses target the same page:

1. Look up the category pair in the matrix above
2. Check for exception conditions noted in the Implication column
3. Apply the interaction ruling:

**For Multiplicative pairs:**
- If targeting the same page section (e.g., both ATF): BUNDLE into a single experiment. The combined hypothesis tests whether fixing both together lifts conversion. Individual element changes serve the combined hypothesis.
- If targeting different sections of the same page: SEQUENCE with explicit dependency. Note in Sequencing Rationale: "Experiment [A] should run before [B] because [interaction rationale]. If [A] wins, [B]'s expected impact increases. If [A] loses, re-evaluate [B]'s causal mechanism."

**For Additive pairs:**
- Sequence by ICE score within their tier. No dependency constraint.
- Note in Sequencing Rationale only if running them simultaneously on the same page would confound measurement.

4. When bundling, the combined hypothesis:
   - Uses the higher Impact baseline of the two originals
   - Uses the lower Confidence of the two (more uncertainty in a multi-element test)
   - Uses the lower Ease of the two (more implementation work)
   - Gets a single "What a win proves" and "What a loss teaches" that addresses the combined mechanism, not each element separately

## Cross-Page Interaction Rules

Hypotheses targeting different pages are independent by default. Exceptions:

- If both hypotheses test the same messaging strategy on different pages (e.g., outcome-led headline on homepage AND outcome-led headline on product page), note the learning dependency: "Results from [page A] test inform whether the same strategy applies to [page B]."
- If one hypothesis creates content consumed by another (e.g., CR-01 comparison page feeds NX-03 exit-intent offer), note the content dependency.
