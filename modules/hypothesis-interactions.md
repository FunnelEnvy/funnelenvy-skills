# Hypothesis Interaction Model

Version: 1.1.0
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

## Empirical Interaction Effects

The category-level matrix above provides default interaction types. The effects below are empirically validated pattern-level interactions that override or supplement the matrix when specific hypothesis pairs co-occur. Each has a defined gate type, conditions, and action.

When the interaction matrix says "Additive" for a category pair but an empirical effect below applies to the specific hypothesis pair, the empirical effect takes precedence.

---

### EIE-01: Login Account Value x Login Prominence

**Interacting hypotheses:** NX-07 (Return Visitor Intent Optimization) + any hypothesis that depends on the quality of the logged-in experience.

**Gate type:** Multiplicative (both conditions must be true for positive outcome)

**Rule:** Making login more discoverable (icon to text, link to button, "Welcome back" banner) only lifts revenue when the logged-in experience genuinely improves conversion (saved payment info, streamlined checkout, personalized dashboard). If account value is low, more logins do not equal more revenue.

**Conditions:**
- Login prominence change = TRUE
- Logged-in experience has conversion value = TRUE
- Expected outcome: Positive (revenue lift proportional to account experience quality)

If login prominence = TRUE but account value = LOW:
- Expected outcome: Neutral to negative. Increased logins with no downstream value improvement.
- Action: Gate NX-07 until account experience is improved, or reframe as a two-phase test: (1) improve account value, then (2) increase login prominence.

**Evidence:** Apparel retailer (high account value): +4.1% orders, +5.3% RPV from login text change. Fundraising site (low account value): same login prominence change completely failed.

---

### EIE-02: Funnel Position x Messaging Type (Polarity Flip)

**Interacting hypotheses:** Any urgency/scarcity/confidence messaging hypothesis + page funnel position.

**Gate type:** Multiplicative with polarity flip (same hypothesis flips from positive to negative based on funnel position)

**Rule:** Urgency/confidence messaging multiplies conversion when deployed mid-to-high funnel but suppresses conversion on homepages and discovery pages. The same messaging variant produces opposite effects based on funnel position.

**Matrix:**
| Messaging Type | High-Intent Page (checkout, booking, pricing) | Low-Intent Page (homepage, category, browse) |
|---|---|---|
| Urgency (countdown, scarcity, limited-time) | Positive (+4-14%) | Negative (-8-11%) |
| Confidence (price-match, guarantee, money-back) | Positive | Negative |
| Social proof (reviews, testimonials) | Positive | Neutral to Positive |

**Action:** When urgency or confidence messaging hypotheses are generated, tag them with funnel position. If targeting a low-intent page, flip the expected outcome to negative and route through CTR-08 (contrarian trigger). Cross-references: CTR-05 (enterprise urgency suppression), CTR-08 (homepage urgency suppression).

**Evidence:** Hospitality client (agency test): +10% bookings for urgency/confidence in booking funnel; -8% to -11% bookings when same messaging placed on homepage.

---

### EIE-03: Ad Creative Parity x Urgency x Hero Reduction (Synergistic Bundle)

**Interacting hypotheses:** NX-04 (Paid Landing Page Optimization) + urgency messaging + hero content reduction, all targeting the same paid landing page.

**Gate type:** Multiplicative (synergistic, not additive). Combined effect exceeds sum of individual effects.

**Rule:** Three changes that individually have modest evidence can produce outsized combined lifts when deployed together on a paid landing page: (a) matching ad creative on the landing page, (b) adding urgency element (countdown, time-sensitive offer), (c) reducing hero size to prioritize the matched content.

**Action:** When NX-04 is in the roadmap, check whether urgency and hero reduction hypotheses also target the same page. If so, flag as a bundling candidate: test all three together rather than sequentially. The combined test is harder to decompose (you won't know which change drove the lift) but the expected magnitude justifies the tradeoff.

**Caution:** This is derived from a single data point (streaming service: +45-65% subscriptions). The bundled approach is high-risk, high-reward. If the test loses, you learn nothing about which element failed. Consider running NX-04 (message match + nav removal) first as a standalone, then adding urgency and hero changes as iteration.

**Evidence:** Streaming service (agency test): hero shrink + countdown calendar + ad creative match = +45% subscriptions growing to +65% over time.

---

### EIE-04: Brand Color x Device Type (Cross-Device Polarity)

**Interacting hypotheses:** Any UI color/state hypothesis + device targeting.

**Gate type:** XOR-like (results can flip sign between desktop and mobile).

**Rule:** UI color choices, particularly for interactive state distinction (selected vs. unselected toggles, plan selectors, filter states), can produce opposite results on desktop vs. mobile. Brand-colored interactive elements may work on mobile (where the brand color is a familiar CTA color) but fail on desktop (where larger screens make ambiguous state distinctions more visible and confusing).

**Action:** When a hypothesis tests button color, toggle state styling, or interactive element visual treatment: require device-split analysis. Do not run a combined desktop+mobile test with a single winner declaration. Either:
- Run device-targeted variants from the start
- Or run combined, but segment results by device before declaring a winner

If desktop and mobile results have opposite signs, the test is not "inconclusive." It has two valid but contradictory findings that require device-specific implementation.

**Evidence:** Nonprofit donation page (agency test): brand orange on desktop = -40% donations; non-brand blue on desktop = +20%. On mobile, orange was neutral to slightly positive, blue was +3-4%.

---

### EIE-05: Carousel Item Count x Placement Prominence (Negative Compound)

**Interacting hypotheses:** EE-02 (Element Engagement Drop-off) + any hypothesis that increases carousel/recommendation prominence on the same page.

**Gate type:** Multiplicative (negative). Either change in isolation might be neutral; together they compound into choice paralysis.

**Rule:** A previously winning carousel configuration can reverse to a loss if simultaneously moved to a more prominent position AND expanded to show more items. More items + more prominent placement = more visible overwhelm.

**Action:** When the roadmap contains both a carousel restructuring hypothesis (EE-02) and a prominence/placement change for the same element:
- Do NOT bundle them. Run sequentially.
- If the carousel wins in its current position, test moving it to a more prominent position as a separate experiment.
- If moving to a more prominent position, test with the same or fewer items, not more.
- Flag the bundle as a negative interaction: "Combining expanded item count with increased prominence has reversed prior wins in testing."

Cross-references: CTR-11 (product recommendation quantity expansion).

**Evidence:** E-commerce shoe brand (agency test): "shop by style" carousel was expanded (more items) and moved to a more prominent position simultaneously. Previous engagement win reversed to a loss in add-to-carts, transactions, and revenue.

---

### EIE-06: Form Field Count x Audience Trust Level (Magnitude Moderator)

**Interacting hypotheses:** FO-01 (Form Field Reduction) + audience trust/motivation assessment from context.

**Gate type:** Moderating variable (audience trust level changes the magnitude of FO-01's effect, not its direction).

**Rule:** Form field reduction has high impact for low-trust, first-time visitor audiences and diminishing impact for high-trust, high-motivation audiences. Audience trust level moderates the effect size.

**Action:** When FO-01 fires:
- Check `performance-profile.md` for new vs. returning visitor split on the target page
- If new visitors dominate (>60%): Impact modifier +1 (high-impact audience for field reduction)
- If returning visitors dominate (>60%): Impact modifier -1 (diminishing returns from field reduction for this audience)
- If the form specifically targets high-trust, high-motivation users (existing customers, referred leads, returning evaluators): cap Impact at 3 regardless of baseline

**Relationship to CTR-01:** CTR-01 reframes field reduction for enterprise B2B. EIE-06 modifies the magnitude of field reduction based on audience trust, regardless of company type. Both can apply simultaneously: CTR-01 reframes the approach while EIE-06 adjusts the expected impact.

**Evidence:** SaaS developer tool (agency test): reducing form fields from 8 to 6 = +8% overall, but +15.31% for new visitors vs. +2.42% for returning visitors.

---

### EIE-07: Content Page Widget x User Intent Redistribution

**Interacting hypotheses:** CR-04 (Content Page Conversion Injection) + engagement metrics for existing content elements on the same page.

**Gate type:** Secondary behavioral effect (not a traditional gate). Must be measured alongside the primary metric.

**Rule:** Adding a conversion widget to a content page doesn't just add a new action. It redistributes behavior from lower-value engagement (reading more articles, clicking related content) to higher-value conversion (purchasing, signing up). Total conversion may increase while content engagement simultaneously decreases.

**Action:** When CR-04 is in the roadmap:
- Define the primary metric as the conversion action (purchase, signup, form submit), not widget clicks
- Define a secondary metric tracking engagement with existing content elements on the same page
- Expect and accept some cannibalization of lower-value engagement if higher-value conversion increases
- If total revenue or conversion value increases despite lower content engagement: the test is a win. Do not let content engagement decline overrule a conversion increase.
- Document the tradeoff explicitly in the experiment result: "Widget increased purchases +X% while reducing content clicks -Y%. Net value: [calculation]."

**Evidence:** Travel content site (agency test): adding a below-fold lodging widget increased total site-wide purchases +3% but simultaneously decreased camping content clicks.

---

## Same-Page Interaction Analysis Process

When two or more hypotheses target the same page:

1. Look up the category pair in the Interaction Matrix
2. Check the Empirical Interaction Effects section for any pattern-specific overrides that apply to the specific hypothesis pair. Pattern-specific effects take precedence over category-level defaults.
3. Check for exception conditions noted in the Implication column
4. Apply the interaction ruling:

**For Multiplicative pairs:**
- If targeting the same page section (e.g., both ATF): BUNDLE into a single experiment. The combined hypothesis tests whether fixing both together lifts conversion. Individual element changes serve the combined hypothesis.
- If targeting different sections of the same page: SEQUENCE with explicit dependency. Note in Sequencing Rationale: "Experiment [A] should run before [B] because [interaction rationale]. If [A] wins, [B]'s expected impact increases. If [A] loses, re-evaluate [B]'s causal mechanism."

**For Additive pairs:**
- Sequence by ICE score within their tier. No dependency constraint.
- Note in Sequencing Rationale only if running them simultaneously on the same page would confound measurement.

5. When bundling, the combined hypothesis:
   - Uses the higher Impact baseline of the two originals
   - Uses the lower Confidence of the two (more uncertainty in a multi-element test)
   - Uses the lower Ease of the two (more implementation work)
   - Gets a single "What a win proves" and "What a loss teaches" that addresses the combined mechanism, not each element separately

## Cross-Page Interaction Rules

Hypotheses targeting different pages are independent by default. Exceptions:

- If both hypotheses test the same messaging strategy on different pages (e.g., outcome-led headline on homepage AND outcome-led headline on product page), note the learning dependency: "Results from [page A] test inform whether the same strategy applies to [page B]."
- If one hypothesis creates content consumed by another (e.g., CR-01 comparison page feeds NX-03 exit-intent offer), note the content dependency.
