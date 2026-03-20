# Contrarian Trigger Matrix

Version: 1.0.0
Last updated: 2026-03-20

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
