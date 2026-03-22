# Contrarian Trigger Matrix

Version: 1.1.0
Last updated: 2026-03-20
Trigger count: 13

This module defines context conditions where standard CRO recommendations are wrong, counterproductive, or actively harmful. The hypothesis construction phase checks every hypothesis against this matrix before finalizing.

## How This Module Works

For each constructed hypothesis, check the "Detection Signal" column. If any signal matches the current context, apply the specified action:

- **Reframe:** Replace the standard recommendation with the "Recommend Instead" alternative. Keep the hypothesis in the roadmap with the reframed content.
- **Suppress:** Remove the hypothesis from the roadmap. Route to "What's Not Here" with explanation.
- **Gate:** Keep the hypothesis but add a mandatory context verification note. The hypothesis cannot be a Quick Win (cap tier at Strategic Bet minimum).

---

### CTR-01: Form Field Reduction in Enterprise B2B

**Standard advice:** Reduce form fields to minimize friction.
**When wrong:** Enterprise B2B demo/consultation requests where qualifying friction filters unqualified leads and signals seriousness to the visitor.

**Detection signals (ANY match triggers):**
- `company-identity.md` target_market.company_size includes "enterprise" or "mid-market"
- Campaign brief (if present) offer_type = "demo" or "consultation"
- `audience-messaging.md` personas include roles with "VP," "Director," "C-suite" seniority
- Deal size context suggests >$25K ACV (inferred from pricing model, target market, or competitive landscape)

**Action:** Reframe
**Recommend instead:** Test qualifying friction: add a qualifying step (role selector, use case dropdown, company size) that builds investment and filters tire-kickers. Pair with data enrichment (ZoomInfo, Clearbit, Apollo) to capture firmographic data without asking. Measure pipeline quality (SQL rate, close rate) not just form submissions. Frame as "smart friction" in the deliverable.

**Evidence basis:** Michael Aagaard (CXL): shortening a B2B form by 3 fields decreased conversions 14%. Adding a qualifying step to a B2B software form increased CVR 20%. Directive Consulting CRO2: "Friction can act as a quality filter." Unbounce data: conversion rates climb again at 10 fields after leveling off at 4-7.

---

### CTR-02: Above-the-Fold CTA Placement for Complex Products

**Standard advice:** Place CTA above the fold for maximum visibility.
**When wrong:** Complex products, technical audiences, or uncertain visitors who need context before committing.

**Detection signals (ANY match triggers):**
- `company-identity.md` lists 5+ product features or capabilities
- `audience-messaging.md` personas include technical roles (engineers, architects, developers)
- `audience-messaging.md` complexity = "jargon-heavy" (technical audience signal)
- `performance-profile.md` shows average session duration >2.5 minutes on target page (visitors are reading, not bouncing)

**Action:** Reframe
**Recommend instead:** Promise above the fold (clear headline + value prop), but test CTA placement at multiple scroll depths. The hypothesis becomes: "Visitors to [page] need context before committing. Moving the primary CTA to post-proof position (after the first proof section) will increase click-through by matching the CTA to the visitor's readiness state." Include both above-fold and mid-page CTA, but test which drives more conversions as the primary.

**Evidence basis:** Aagaard (CXL): moving CTA below fold on a service LP increased conversions 304%. Nielsen Norman Group (2018): above-fold viewing dropped from 80% to 57%. 76% of users scroll when design enables it (CX Partners eye-tracking).

---

### CTR-03: Generic Social Proof Addition

**Standard advice:** Add testimonials, logos, and social proof to build trust.
**When wrong:** When proof doesn't match the target segment, is outdated, or is stacked too densely.

**Detection signals (ALL must match):**
- Hypothesis recommends adding social proof (matches patterns SP-01, SP-02, SP-03, HM-02, or any hypothesis with "social proof," "testimonial," "logo," or "case study" as the proposed change)
- AND any of:
  - L0 proof point registry has <3 proof points matching the target persona's industry/segment
  - Proof points are >2 years old (check dates in proof registry if available)
  - Hypothesis proposes placing 4+ proof elements in a single page section

**Action:** Gate
**Gate condition:** Add verification note: "Before implementing, confirm proof points match the target persona's segment and industry. Mismatched social proof decreases conversion. One relevant case study outperforms ten generic quotes." Cap at Strategic Bet tier if proof matching cannot be verified from context.

**Evidence basis:** Getmany: 83% of agencies use social proof wrong, decreasing conversion. Volume diminishing returns: 1 piece = +15%, 2 = +45%, 3 = +127%, 4+ = -23%. Enterprise buyers seeing SMB testimonials are actively repelled.

---

### CTR-04: Page Simplification for Complex B2B

**Standard advice:** Simplify the page. Remove content. Reduce cognitive load.
**When wrong:** Complex B2B products with technical audiences and multi-stakeholder buying committees.

**Detection signals (ANY match triggers):**
- `company-identity.md` target_market.company_size includes "enterprise"
- `competitive-landscape.md` indicates competitors with detailed, information-rich pages
- `audience-messaging.md` identifies 3+ distinct personas (multi-stakeholder signal)
- `company-identity.md` pricing model or deal context suggests >$25K ACV

**Action:** Reframe
**Recommend instead:** Information-rich pages with clear progressive disclosure. The hypothesis becomes about information architecture, not information removal. Test: progressive disclosure (expandable sections, tabs, anchor navigation) vs. current layout. The goal is reducing cognitive load without reducing information availability. Frame: "B2B buyers evaluating [product] need ammunition for internal stakeholders. Removing information removes their ability to sell internally."

**Evidence basis:** Clearbit: "B2B users tend to be high-intent and high-knowledge. More information may be positive." Forrester 2024: average B2B purchase involves 13 stakeholders. PathFactory: average 10.4 content pieces consumed before purchase.

---

### CTR-05: Urgency/Scarcity in Enterprise B2B

**Standard advice:** Add countdown timers, limited-time offers, or scarcity signals.
**When wrong:** Enterprise B2B, professional services, high-trust-required purchases, long sales cycles.

**Detection signals (ANY match triggers):**
- `company-identity.md` target_market.company_size includes "enterprise" or "mid-market"
- `company-identity.md` category suggests professional services, consulting, or advisory
- `competitive-landscape.md` or `audience-messaging.md` indicates sales cycles >3 months
- Hypothesis proposes countdown timers, limited-time discounts, or "only X spots remaining" language

**Action:** Suppress
**Route to "What's Not Here":** "Urgency and scarcity tactics were evaluated but suppressed. Enterprise B2B buyers are 34% more likely to abandon when they perceive artificial scarcity (Invoke Media, 2023), and 40% distrust vendors who rely on fabricated urgency (B2B Rocket). If genuine scarcity exists (limited client roster, cohort-based onboarding, budget-cycle alignment), frame it as a structural reality, not a pressure tactic."

**Evidence basis:** Tuncer et al. (2023): countdown timers significantly increase frustration. UK shoppers 34% more likely to abandon with artificial scarcity. B2B: genuine capacity constraints ("We maintain a maximum client roster of 12 companies") convert 3x better than discount urgency.

---

### CTR-06: Personalization Without Infrastructure

**Standard advice:** Personalize the page experience by visitor segment.
**When wrong:** When first-party data strategy is weak, segmentation is untested, or the buying committee is treated as a single persona.

**Detection signals (ALL must match):**
- Hypothesis requires personalization infrastructure (matches patterns PE-01, PE-02, or any hypothesis with "personalization," "segment-based," or "dynamic content" as the proposed change)
- AND any of:
  - No `performance-profile.md` present (no behavioral data to segment on)
  - `audience-messaging.md` has only 2 personas with overlapping challenges (weak segmentation basis)
  - No evidence of existing personalization tooling in context (no mention of Optimizely, VWO, Dynamic Yield, or similar)

**Action:** Gate
**Gate condition:** Add prerequisite note: "Personalization requires clean first-party data and defined stakeholder personas. 53% of personalization implementations harm conversion rates (Gartner). Before testing personalization, verify: (1) segment detection accuracy (UTMs, reverse IP, or self-selection), (2) distinct messaging exists per segment, (3) traffic per segment supports statistical significance." Cap tier at Strategic Bet.

**Evidence basis:** Gartner: 53% of personalization implementations harm conversion. 77% of B2B buyers want personalized content but 53% say brands do it wrong. MarketingProfs: "most third-party data is garbage."

---

### CTR-07: Navigation Removal for Research-Stage Visitors

**Standard advice:** Remove navigation from landing pages.
**When wrong:** When the page serves research-stage B2B visitors in a multi-stakeholder buying process, not just paid traffic.

**Detection signals (ALL must match):**
- Hypothesis recommends removing or reducing navigation
- AND any of:
  - Page receives >50% organic traffic (research-stage visitors need navigation to explore)
  - `audience-messaging.md` identifies technical evaluators as a primary persona (they research before converting)
  - `performance-profile.md` shows pages/session >3 for visitors to this page (visitors actively exploring)

**Action:** Reframe
**Recommend instead:** Test reduced-but-present navigation rather than full removal. Keep navigation links to 3-5 highest-value pages (pricing, case studies, product). Remove footer navigation and secondary links. For paid traffic specifically, test full removal (scope variant to paid visitors only using UTM targeting). Frame: "Research-stage visitors use navigation as a trust signal: 'this is a real company with real pages.' Removing it can trigger suspicion."

**Evidence basis:** Conversion playbook already specifies "never for paid traffic pages" but the hypothesis generator may fire on pages with mixed traffic. CX Partners: 76% of users scroll and navigate when design enables it. Multi-stakeholder B2B buying involves deep research across multiple pages.

---

### CTR-08: Homepage Urgency/Confidence Messaging

**Standard advice:** Add urgency messaging (countdown timers, limited-time offers) or confidence messaging (price-match guarantees, money-back guarantees) to increase conversions.
**When wrong:** When deployed on homepages, category pages, or any discovery/browse-intent page regardless of company type.

**Detection signals (ANY match triggers):**
- Hypothesis recommends urgency messaging (countdown timers, limited-time offers, scarcity signals) or confidence messaging (price-match guarantees, money-back guarantees) on a homepage or category-level discovery page
- Target page's primary traffic is browse-intent, not purchase-intent (detectable from `performance-profile.md`: high sessions, low conversion rate, high pages/session originating from this page)
- Target page is classified as homepage, category page, resource hub, or any top-of-funnel discovery surface

**Relationship to CTR-05:** CTR-05 suppresses urgency/scarcity specifically in enterprise B2B contexts. CTR-08 fires on funnel position regardless of company type. A DTC ecommerce homepage triggers CTR-08 but not CTR-05. An enterprise SaaS homepage triggers both. CTR-05 takes precedence when both fire (suppress overrides gate).

**Action:** Gate (on discovery pages) / Reframe (specify funnel position constraint)
**Recommend instead:** Restrict urgency/confidence messaging to mid-to-high funnel pages only: checkout, booking, pricing, demo request, cart. Rewrite the hypothesis to specify funnel position as a deployment condition. If the target page serves both browse and purchase intent, gate with audience targeting: serve urgency messaging only to visitors who have already visited a high-intent page (pricing, product detail) in the same session.

**Evidence basis:** Hospitality client tests (agency test): +10% bookings when urgency/confidence messaging placed in booking funnel; -8% to -11% bookings when same messaging placed on homepage. Mechanism: urgency does not create demand, it accelerates existing intent. On homepages where visitors are exploring, urgency messaging suppresses exploration behavior.

---

### CTR-09: Navigation Label Specificity for Premium/Aspirational Brands

**Standard advice:** Make navigation labels specific and action-oriented (e.g., "Gifts" over "Holiday," "Shop Now" over "Explore").
**When wrong:** When the brand is positioned as premium, luxury, or aspirational and browsing/discovery behavior is itself a conversion driver.

**Detection signals (ALL must match):**
- Hypothesis recommends making navigation labels more specific, transactional, or action-oriented
- AND any of:
  - `company-identity.md` category or `audience-messaging.md` tone indicates premium, luxury, or aspirational brand positioning
  - `audience-messaging.md` tone descriptors include "elevated," "premium," "luxury," "aspirational," or similar
  - `competitive-landscape.md` shows competitors using broad, aspirational navigation labels (industry convention for premium)
  - Brand's value proposition depends on browsing/discovery behavior (fashion, lifestyle, high-end services, curated experiences)

**Action:** Gate
**Gate condition:** Add verification note: "Premium/aspirational brands often benefit from broader, browsing-friendly navigation labels that invite exploration. Specific, transactional labels can narrow intent prematurely, filtering out exploratory visitors who would have converted through the discovery path. Before defaulting to transactional labels, test aspirational labels first with transactional as the challenger, not the default." Cap at Strategic Bet tier. If brand positioning is utilitarian/value/functional, this trigger does not apply and the standard specificity recommendation proceeds.

**Evidence basis:** High-end clothing brand (agency test): changing a seasonal nav tab from aspirational label ("Holiday") to specific, action-oriented label ("Gifts") resulted in ~50% drop in navigation clicks at full statistical significance. Revenue was flat, meaning lost clicks were exploratory (browse-intent), not transactional.

---

### CTR-10: Funnel Step Removal Without Persuasion Audit

**Standard advice:** Remove unnecessary funnel steps to reduce friction and speed time-to-conversion.
**When wrong:** When the step being removed contains persuasive content (value props, social proof, upgrade messaging, feature comparisons) that contributes to downstream conversion, even though the step appears to be friction.

**Detection signals (ANY match triggers):**
- Hypothesis recommends removing, skipping, or auto-bypassing a funnel step to reduce friction (e.g., auto-redirect past a marketing page, skip an interstitial, combine two steps into one)
- Target step contains any of: value propositions, social proof, upgrade/premium messaging, feature comparisons, or pricing context
- Hypothesis is motivated by observed user behavior (e.g., "30% of users immediately click through this page, so skip it") without measuring downstream conversion of users who engage with vs. skip the step

**Action:** Gate
**Gate condition:** Add prerequisite assessment: "Before removing this funnel step, verify it has no persuasive value. Does the step contain content that contributes to downstream conversion? Check: (1) Do visitors who engage with this step convert at higher rates downstream than those who skip/bounce? (2) Does the step surface value props, proof, or upgrade messaging that visitors wouldn't see otherwise? If yes to either: reframe as a step optimization hypothesis (improve efficiency) rather than a step removal hypothesis." Cap at Strategic Bet tier until persuasion value is assessed.

**Evidence basis:** SaaS scheduling tool (agency test): auto-redirecting logged-in freemium users straight to the product (bypassing marketing pages) produced -4% decline in subscriptions. The marketing site was surfacing value props that motivated upgrades. Removing the "friction" removed the persuasion.

---

### CTR-11: Product Recommendation Quantity Expansion

**Standard advice:** Show more product recommendations in a more prominent position to increase discovery and engagement.
**When wrong:** When expanding visible options on homepages, category pages, or any page where the visitor hasn't yet narrowed intent. More options in a more visible position compounds into choice paralysis.

**Detection signals (ANY match triggers):**
- Hypothesis recommends increasing the number of visible product/service recommendations
- Hypothesis recommends expanding a carousel to show more items or making a recommendation widget more prominent
- Hypothesis recommends replacing a compact recommendation element with a larger, more prominent one showing more options
- Target page is a homepage, category page, or any page where visitor intent is not yet narrowed

**Action:** Suppress (expansion) / Reframe (test reduction)
**Recommend instead:** Test reducing visible options while increasing relevance of shown items. Fewer, better-matched recommendations outperform more, generic recommendations. If engagement metrics (clicks, carousel interactions) are cited as justification for expanding: flag that engagement and conversion can move in opposite directions for recommendation elements. Require conversion (add-to-cart, transactions, revenue) as the primary metric, not engagement.

**Route to "What's Not Here" (if suppressed):** "Expanding product recommendations was evaluated but suppressed. Engagement metrics for recommendation elements are misleading proxies for conversion. More visible options in a more prominent position compounds choice paralysis. Carousel elements on homepages have never won an A/B test in extensive A/B testing history."

**Evidence basis:** E-commerce shoe brand (agency test): expanded "shop by style" carousel from compact below-accordion to larger, more prominent placement showing more products. Engagement surged +194%, but add-to-carts, transactions, and revenue all declined. Testing data shows they have "never seen a carousel win an A/B test" on homepages.

---

### CTR-12: Contrasting Navigation Item Highlighting

**Standard advice:** Highlight important navigation items with contrasting colors or visual treatments to draw attention.
**When wrong:** When the highlighting uses color contrast to differentiate a text navigation link from other text navigation links (not CTA-styled buttons).

**Detection signals (ANY match triggers):**
- Hypothesis recommends giving a specific navigation item a contrasting color, badge, or visual treatment to make it stand out from the rest of the navigation
- The target element is a text navigation link (not a CTA button that is already expected to have different styling)
- The proposed change differentiates the item from its navigation siblings primarily through color contrast

**Action:** Reframe
**Recommend instead:** If the nav item genuinely needs emphasis, test weight-based emphasis (bold text, slightly larger font, subtle background) that signals importance within the navigational context rather than marking it as a different category of element. Contrasting-color highlighting in navigation can signal "ad" or "different" rather than "important," triggering banner-blindness-adjacent behavior where visitors unconsciously filter out the highlighted item.

**Exception:** CTA-styled buttons in navigation (e.g., "Sign Up" or "Get Started" rendered as a button) are expected to look different from text links. This trigger applies only to text nav links being color-differentiated from other text nav links.

**Evidence basis:** Accessories brand (agency test): making a featured nav item red to stand out from black-text navigation hurt sales. Changing it back to black (matching the rest) produced a significant increase. Validated across multiple client sites: contrasting-color nav highlighting triggers avoidance behavior.

---

### CTR-13: Cross-Context Pattern Replication Without Value Validation

**Standard advice:** Apply patterns that won in other contexts (different companies, verticals, or site sections) to the current site.
**When wrong:** When a hypothesis cites external evidence as its primary justification but has no pattern library backing to validate that the underlying conditions transfer to the current context.

**Scope:** This trigger fires ONLY on hypotheses that are NOT matched to a pattern in experiment-patterns.md. Pattern-matched hypotheses (Phase 2a) already have context-file-detectable trigger conditions that serve as built-in context validation. CTR-13 targets the gap: hypotheses where external evidence is used as a substitute for trigger validation, not a supplement to it.

**Detection signals (ALL must match):**
- Hypothesis is NOT matched to a pattern in experiment-patterns.md (i.e., it is a Phase 2b context-derived hypothesis or a human-requested test that entered the pipeline without pattern matching)
- AND the hypothesis cites external case study evidence or cross-vertical precedent as the primary justification (e.g., "Company X saw +Y% from this change")
- AND the hypothesis does not independently satisfy trigger conditions from any existing pattern (if it does, it should have been matched in Phase 2a, and the pattern's trigger validation is sufficient)

**Does NOT fire on:**
- Pattern-matched hypotheses that cite external data in their calibration references. The pattern's "Applies when" trigger conditions already validated the context. The external data is calibration, not justification.
- Hypotheses where external evidence is cited as supporting evidence alongside context-validated triggers.

**Action:** Gate
**Gate condition:** Add a "Context Validation" requirement to the hypothesis: "What underlying condition made this pattern work in the source context? Does that condition exist here? If the answer is unknown, validate the condition before testing the surface change." Cap at Strategic Bet tier until context validation is complete.

**Required validation format in the hypothesis deliverable:**
- Source context: "[Company/vertical] saw [result] because [underlying condition]."
- Target context validation: "[Underlying condition] exists/does not exist here because [evidence from context files]."
- If condition cannot be validated: "Condition is unverified. Test as exploration-tier with explicit validation as the primary learning goal."

**Evidence basis:** Apparel retailer (agency test): icon-to-"Log In" text change = +55% logins, +4.1% orders because the logged-in experience had genuine value (saved cart, payment info, streamlined checkout). Same test on a social impact fundraising site completely failed because the account had minimal value (just order history). The surface change was identical; the underlying value proposition was not.

---

## Anti-Cargo-Cult Check

After applying the trigger matrix, run this final check on every hypothesis:

**Test:** Would this exact recommendation, with no changes, apply to any B2B website regardless of context?

- If YES: Flag the hypothesis. Add a "Context Grounding" line to the deliverable that explains what specific context signal makes this recommendation relevant to THIS company. If no specific signal can be cited, suppress the hypothesis and route to "What's Not Here" with: "This recommendation was evaluated but suppressed because no company-specific evidence supports it."
- If NO: Pass. The hypothesis is context-grounded.

**Examples of cargo-cult recommendations (should trigger the flag):**
- "Add a testimonial section" (without specifying whose testimonial, why this page, what proof gap it fills)
- "Reduce form fields" (without specifying which fields, why they're unnecessary, what enrichment replaces them)
- "Test a different headline" (without specifying what's wrong with the current one and what messaging principle the new one applies)
- "Add social proof to the pricing page" (without specifying what type of proof, matched to what objection)
