# Contrarian Trigger Matrix

Version: 2.0.0
Last updated: 2026-11-11
Trigger count: 14

This module lists context conditions where standard CRO advice is wrong or harmful. The lenses check every card against it while they build the card. A trigger never removes a card. It changes the recommendation or adds counter-evidence that rides on the card into the backlog, where the reader decides.

## Actions

- **Reframe:** Emit the card with the `Recommend instead` test in place of the standard one. Add the annotation `reframed: <standard advice> replaced because <trigger condition>`.
- **Counter-evidence:** Keep the card as proposed. Add the annotation `counter-evidence: <trigger name>: <why this may not work here>`. The write-up renders it under `**Notes:**`.
- **Verify first:** Keep the card. Add the annotation `verify first: <the check>`. `phases/validate.md` adds the check to the prerequisites list.

Annotations are plain words. They never name a trigger ID.

---

### CTR-01: Form Field Reduction in Enterprise B2B

**When wrong:** Enterprise demo or consultation requests, where qualifying friction filters weak leads and signals seriousness.
**Signals (any):** target market includes enterprise or mid-market; the offer is a demo or consultation; personas are VP, Director or C-suite; deal context suggests over $25K ACV.
**Action:** Reframe. Test qualifying friction (a role, use-case or size step) paired with enrichment, read on pipeline quality (SQL or close rate), not raw submits.
**Evidence basis:** Shortening one B2B form by 3 fields cut conversions 14%; adding a qualifying step to another raised conversion 20%.

### CTR-02: Above-the-Fold CTA for Complex Products

**When wrong:** Complex products and technical audiences who need context before committing.
**Signals (any):** 5 or more listed capabilities; technical personas; jargon-heavy audience profile; average time on the page over 2.5 minutes.
**Action:** Reframe. Keep the promise above the fold and test the primary CTA after the first proof section against the current placement.
**Evidence basis:** Moving a CTA below the fold on one service page lifted conversions 304%. Above-fold viewing share fell from 80% to 57% in later eye-tracking research.

### CTR-03: Generic Social Proof Addition

**When wrong:** Proof that misses the segment, is stale, or is stacked too densely.
**Signals (all):** the card adds social proof, AND one of: fewer than 3 proof points match the persona's segment; proof older than 2 years; 4 or more proof elements in one section.
**Action:** Verify first: confirm the proof matches the persona's segment and industry. One relevant case study beats ten generic quotes.
**Evidence basis:** Agency data shows proof volume turning negative at 4 or more pieces in one section, and enterprise buyers repelled by SMB testimonials.

### CTR-04: Page Simplification for Complex B2B

**When wrong:** Complex products bought by multi-stakeholder committees.
**Signals (any):** enterprise target market; information-rich competitor pages; 3 or more personas; deal context over $25K ACV.
**Action:** Reframe. Test progressive disclosure (sections, tabs, anchors) instead of removing information. Champions need material to sell internally.
**Evidence basis:** Large B2B purchases involve about 13 stakeholders and about 10 content pieces before purchase.

### CTR-05: Urgency or Scarcity in Enterprise B2B

**When wrong:** Enterprise, professional services and long sales cycles.
**Signals (any):** enterprise or mid-market target; services or advisory category; sales cycles over 3 months; the card proposes countdowns, limited-time discounts or "only X left".
**Action:** Counter-evidence: artificial scarcity raises abandonment and distrust with these buyers. Genuine capacity limits (a capped client roster, cohort onboarding, budget-cycle timing) may be stated as structural facts instead.
**Evidence basis:** Shoppers were 34% more likely to abandon under artificial scarcity; genuine capacity statements converted about 3 times better than discount urgency.

### CTR-06: Personalization Without Infrastructure

**When wrong:** Weak first-party data, untested segmentation, or a buying committee treated as one persona.
**Signals (all):** the card needs personalization, AND one of: no performance profile; only 2 overlapping personas; no personalization tooling in context.
**Action:** Verify first: confirm segment detection accuracy, distinct messaging per segment, and enough traffic per segment.
**Evidence basis:** Industry research reports a majority of personalization implementations hurting conversion.

### CTR-07: Navigation Removal for Research-Stage Visitors

**When wrong:** Pages that serve research-stage visitors, not only paid traffic.
**Signals (all):** the card removes or reduces navigation, AND one of: over 50% organic traffic; technical evaluators as a primary persona; over 3 pages per session.
**Action:** Reframe. Keep navigation to the 3 to 5 highest-value pages; test full removal only for paid visitors through targeting.
**Evidence basis:** Research-stage buyers use navigation as a legitimacy signal and explore across many pages.

### CTR-08: Urgency or Confidence Messaging on Discovery Pages

**When wrong:** Homepages, category pages and other browse-intent pages, for any company type.
**Signals (any):** the card adds urgency or guarantee messaging to a homepage or discovery page; the page's traffic is browse-intent (high sessions, low conversion, high onward page views).
**Action:** Reframe. Restrict the messaging to checkout, booking, pricing, demo or cart, or target it to visitors who already reached a high-intent page. When CTR-05 also fires, its counter-evidence applies as well.
**Evidence basis:** One hospitality test gained 10% bookings in the booking funnel and lost 8% to 11% with the same messaging on the homepage.

### CTR-09: Navigation Label Specificity for Premium Brands

**When wrong:** Premium or aspirational brands where browsing drives conversion.
**Signals (all):** the card makes navigation labels more transactional, AND one of: premium, luxury or aspirational positioning or tone; competitors use aspirational labels; the value prop depends on discovery.
**Action:** Counter-evidence: transactional labels can narrow intent too early. Test the aspirational label as control and the transactional one as challenger. Utilitarian brands are out of scope.
**Evidence basis:** One premium clothing brand lost about half its clicks on a nav tab renamed from "Holiday" to "Gifts", with revenue flat.

### CTR-10: Funnel Step Removal Without a Persuasion Audit

**When wrong:** The step being removed carries value props, proof, upgrade messaging or pricing context.
**Signals (any):** the card removes, skips or auto-bypasses a step; the step carries persuasive content; the case rests on click-through behavior without downstream conversion by engagers versus skippers.
**Action:** Verify first: compare downstream conversion for visitors who engage with the step against those who skip it. If the step persuades, reframe as a step optimization.
**Evidence basis:** One scheduling tool lost 4% subscriptions after auto-redirecting logged-in users past marketing pages.

### CTR-11: Product Recommendation Expansion

**When wrong:** More options, more prominently, on pages where intent is not yet narrow.
**Signals (any):** the card adds visible recommendations, enlarges a carousel or makes a recommendation widget more prominent on a homepage or category page.
**Action:** Reframe. Test fewer, better-matched recommendations, with conversion (add-to-cart, transactions, revenue) as the primary metric, not engagement.
**Evidence basis:** One footwear brand saw carousel engagement rise 194% while add-to-carts, transactions and revenue fell.

### CTR-12: Contrasting Navigation Item Highlighting

**When wrong:** Color-differentiating one text navigation link from the others. CTA-styled buttons in navigation are out of scope.
**Signals (any):** the card gives a text nav item a contrasting color or badge to make it stand out.
**Action:** Reframe. Test weight-based emphasis (bold, slightly larger, a subtle background) instead.
**Evidence basis:** One accessories brand lost sales with a red featured nav item and recovered when it returned to the standard color.

### CTR-13: Cross-Context Replication Without Value Validation

**When wrong:** A non-pattern card whose main justification is another company's result.
**Signals (all):** `pattern: false`; the card cites an external case study as its primary justification; it meets no pattern's conditions.
**Action:** Verify first: name the condition that made the source result work and whether it holds here. If it cannot be confirmed, the card's main learning goal is that validation.
**Evidence basis:** An icon-to-"Log In" change won where the account held real value and failed where it held only order history.

### CTR-14: Device or OS Defect Misattribution

**When wrong:** A device gap explained by an OS or browser-family error, not message fit.
**Signals (any):** error-session rate concentrates by OS or browser family; a device gap coincides with a script-error family; the card proposes a device messaging or rendering change on such a surface; the structural capture records `mobile_render_clean: false` on the target surface.
**Action:** Counter-evidence: fix the defect and re-measure the gap before reading any device-targeted test. `phases/validate.md` sets `design-change` on a broken mobile render. A clean observed render rules out the rendering family only; script-error telemetry still needs its own rule-out.
**Evidence basis:** Tests on error-degraded sessions cannot separate message effect from error effect.

---

## Context Grounding Check

After the matrix, ask of every card: would this exact recommendation apply to any B2B site, unchanged? If yes, add the specific context signal that makes it relevant here to its evidence. If no signal exists, add the annotation `counter-evidence: no company-specific evidence; generic advice`. Examples of generic advice: "add a testimonial section", "reduce form fields", "test a different headline", each without naming whose, which or why.
