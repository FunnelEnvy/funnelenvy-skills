# Conversion Playbook: Paid Landing Pages

> **Module type:** Shared cross-skill reference
> **Used by:** landing-page-generator (phases/copy.md, phases/design.md, phases/qa.md), hypothesis-generator (CRO pattern reference)
> **Scope:** Client-agnostic structural rules for B2B paid landing pages. Defines what stays constant across all clients and campaigns.
> **Evidence basis:** Conversion research from Unbounce, HubSpot, VWO, CXL, Instapage, KlientBoost, Shopify, and industry benchmarks (2024-2026).
> **Last updated:** March 2026

---

## 1. Navigation

**Rule: Remove all site navigation from paid landing pages.**

Only 16% of landing pages remove their navigation menu, yet doing so consistently lifts conversion rates. A/B tests from VWO (Yuppiechief: 3% to 6%, a 100% lift), HubSpot (16-28% lift on mid-funnel pages), SparkPage (9.2% to 17.6%), and Shopify (up to 336% lift) all confirm the same directional finding: fewer exit routes = more conversions.

**Implementation:**
- Top nav: Remove entirely. Show logo only. Logo should be non-clickable or link back to the landing page itself (not the main website).
- Footer: Minimal. Logo + copyright + required legal links (Privacy Policy, Terms) + any client-specific regulatory disclaimers. No sitemap, social icons, blog links, or service page links.

**When to override**: Never for paid traffic pages. If the page must also serve organic traffic, build a separate SEO version with navigation.

---

## 2. CTA Strategy

### Placement

**Rule: Repeat the same primary CTA in at least 3 locations.**

Unbounce data shows pages with 2-4 CTA links average 11.9% conversion vs. 10.5% for pages with 5+ links. Visitors convert at different scroll depths. Three placements ensure every visitor encounters the CTA after they've seen enough to decide.

| Location | Section | Visitor State |
|----------|---------|--------------|
| 1 | Hero (above the fold) | Arrived ready to act. Convinced by the ad. |
| 2 | Mid-page (after proof/social proof) | Needed social proof and problem/solution framing first. |
| 3 | Final block (bottom, high-contrast background) | Consumed the full page. Now convinced. |

### Copy

**Rule: CTA copy must be specific, benefit-oriented, and consistent across all placements.**

Personalized CTAs perform 202% better than generic ones (HubSpot, 330,000 CTAs studied). Specificity means: include the time commitment if applicable, name what happens next, and frame the action as valuable to the visitor.

**Strong:** "Schedule a 15-Minute Strategy Call" / "Get Your Free Assessment" / "See Pricing for Your Team" / "Download the Checklist"
**Weak:** "Submit" / "Learn More" / "Get Started" / "Contact Us" / "Send" / "Get in Touch"

**Rule: One action, repeated. No competing CTAs.**

48% of landing pages contain more than one offer, and multiple offers reduce conversion. Do not pair a primary CTA with a secondary action (e.g., "Learn more" alongside "Book a demo"). One page, one goal, one button.

### Interaction

**Default: CTA click opens a lightbox form overlay.**

KlientBoost cites an Aweber study where putting a form behind a popup button (instead of embedding it) increased conversions by 1,375%. HubSpot found replacing an embedded form with a CTA-to-conversion-step pattern produced a 59.2% lift. The psychology: a button click is a micro-commitment. The visitor decides to act before they see the form.

**When to override:**
- 1-field forms (email only, e.g., gated content): embedded inline form in the hero is acceptable because friction is already minimal.
- Multi-step forms with 5+ fields: can be embedded on-page if the first step is visually lightweight (1-2 low-threat fields visible).

---

## 3. Form Strategy

### Field Count

**Rule: Use the minimum number of fields required to follow up. Every unnecessary field costs conversions.**

Forms with 5 or fewer fields convert 120% better than longer forms. Each additional field beyond 5 creates a 20-30% conversion penalty. Reducing fields from 11 to 4 can increase conversions by 120%.

**Defaults by scenario:**

| Scenario | Recommended Fields | Format | Rationale |
|----------|-------------------|--------|-----------|
| Client uses enrichment tool (ZoomInfo, Clearbit, Apollo, etc.) | 2: first name + work email | Single-step lightbox | Enrichment fills company, title, size, revenue, tech stack from work email. Don't ask humans for data machines provide. |
| No enrichment, low-friction offer (content download, newsletter) | 1: work email | Inline embed or lightbox | Minimize friction for top-of-funnel. Qualify later. |
| No enrichment, high-value offer (demo, consultation, quote) | 3-5, multi-step | Multi-step lightbox or embedded | Multi-step forms convert up to 86-300% higher than single-step for complex offers. Lead with low-threat fields. |
| Enterprise / high ACV ($100K+) | 4-6, multi-step | Multi-step | Intentional friction to filter unqualified leads. Still use progressive disclosure. |

### Multi-Step Form Rules (when applicable)

- **Step 1**: Low-threat, non-personal questions (role, company size, use case). Easy to answer. Creates psychological investment via sunk cost.
- **Final step**: Personal info (name, email, phone). By now the visitor is committed.
- Include a progress indicator.
- Multi-step forms convert up to 300% higher than single-step long forms (Venture Harbour). KlientBoost reports 74% conversion increase + 51% CPA drop in client tests.

### Form UX

- Single-column layout always.
- Submit button copy echoes the CTA value ("Book My Call" not "Submit").
- Micro-copy below submit sets expectations ("We'll confirm your time on the next screen").
- Prefer dropdowns and selection buttons over free-text where possible.
- Mark required vs. optional fields explicitly.

---

## 4. Post-Submit Flow

**Rule: The post-submit experience must immediately move the visitor forward. Never redirect to a dead-end.**

Peak intent occurs at the moment of form submission. Every hour of delay between "submit" and "next step" (meeting booked, asset accessed) erodes conversion from lead to opportunity.

### Flow Options (specify in Campaign Brief)

**Option A: Instant calendar booking (preferred for demo/consultation offers)**
```
Form submit -> Enrichment runs in background -> CRM record created ->
Immediate redirect to inline calendar embed -> Visitor books own slot ->
Confirmation page with details + nurture content
```

**Option B: Instant asset delivery (for gated content offers)**
```
Form submit -> Immediate redirect to the asset (PDF, video, template) ->
Optional email follow-up with related resources
```

**Option C: Thank-you page with follow-up commitment (fallback)**
```
Form submit -> Thank-you page with specific response timeframe
("We'll reach out within [X hours/minutes]") -> Nurture content link
```

Option C is the weakest. Use only when no calendar tool or instant-delivery asset is available. Always include a specific timeframe. "We'll be in touch" with no timeline is unacceptable.

### Confirmation Page Elements
- Confirmation headline
- What to expect next (1-2 sentences, specific)
- "Add to Calendar" button (if meeting booked)
- Link to ONE relevant piece of content (case study, guide) as pre-meeting/pre-read nurture
- This is the ONLY place to link to external content. The landing page itself has zero exit routes.

---

## 5. Page Structure and Ordering

Section selection and variant choice are defined in `modules/section-taxonomy.md`. This section defines ordering constraints that apply after sections are selected. The design agent validates these constraints when rendering. QA validates them during review.

### Hard Rules (violating any of these is a QA failure)

1. **Hero is always Section 1.** No exceptions.
2. **Primary CTA placement is within or immediately after Hero.** The CTA mechanism (inline form, modal trigger, multi-step) is part of the hero block, not a separate section below it.
3. **Social Proof Bar, if present, is Section 2 or 3.** It appears immediately after hero/CTA. Never below the fold on desktop.
4. **Final CTA is always the last content section.** Only Footer follows it.
5. **Footer is always last.**
6. **No two CTA sections adjacent.** Mid-Page CTA cannot be directly above Final CTA. At least one content section must separate any two CTA blocks.
7. **Problem Framing precedes Solution Overview.** If both are present, problem comes first. You don't explain the fix before establishing the pain.
8. **At least one proof section (Quantified Proof, Testimonial, or Comparison) precedes the Final CTA.** Never ask for the conversion without having made the case.
9. **Proof elements adjacent to CTA must not visually compete with it.** Grayscale logos, subdued testimonial styling.
10. **All CTA instances on a page must be the same action.** Never mix "Book a Demo" with "Download Whitepaper" on a single LP.

### Soft Rules (prefer these; deviate only with clear rationale)

11. **Proof sections appear in the middle third of the page.** After problem/solution framing, before objection handling and final CTA.
12. **Comparison Table appears after at least one proof section.** Show your own results before positioning against competitors.
13. **Objection Handling (Pattern B consolidated FAQ) appears in the bottom third.** It's a pre-conversion cleanup, not a storytelling device. Pattern A inline objections appear wherever the friction arises.
14. **Trust / Security Signals appear near the form.** Whether the form is inline in the hero or in a modal, trust signals should be visually proximate to the input fields.
15. **Mid-Page CTA goes after the first major proof block,** not at a fixed halfway point. Once the strongest evidence has been presented, offer the action.
16. **Pricing Preview precedes Final CTA but follows proof sections.** Show value, then show price, then ask for conversion.

### Default Section Sequence

Fallback when signals are ambiguous. Only include sections whose selection signals are met:

```
Hero (with Primary CTA)
Social Proof Bar
Problem Framing
Solution Overview
Quantified Proof Block
Mid-Page CTA (after first proof block, if page is long enough)
Testimonial Block
Comparison Table
Pricing Preview
Objection Handling (Pattern B, if needed)
Trust / Security Signals (near form, wherever form appears)
Final CTA
Footer
```

This is NOT a template. It's a tiebreaker. If context provides a reason to reorder, deviate.

### Section Count Guidance

The governing principle is from MECLABS: **match page length to the visitor's perceived cost/risk and their current awareness level.** High-commitment decisions warrant longer pages. Low-risk actions warrant shorter pages. Section count is a consequence of this principle, not a target.

- **Short page (4-5 sections):** Hero + Primary CTA, one content/proof section, Final CTA, Footer. Appropriate for `traffic_awareness_stage` = most_aware with a low-friction offer.
- **Standard page (6-8 sections):** Most campaigns land here. Covers problem/solution framing, proof, and CTA with room for one or two contextual sections.
- **Long page (9-12 sections):** Complex offers, unaware/problem-aware traffic, or high-commitment actions (enterprise demos with 5+ field forms).

If selecting 12+ sections, cut the weakest proof section or collapse Solution Overview into Problem Framing as a contrast variant. Beyond 12, audit each section for whether it adds conversion-relevant information the visitor doesn't already have.

For section type definitions, selection signals, and variant tables, see `modules/section-taxonomy.md`. Do NOT duplicate selection logic here.

---

## 6. Mobile

**Rule: Design mobile-first. Desktop is the responsive adaptation.**

83% of landing page traffic comes from mobile. Mobile-responsive pages convert at ~11.7% vs ~10.7% for desktop-only. Over 80% of B2B buyers research on mobile. However, desktop converts ~8% better, so both must work.

**Requirements:**
- Single-column layout on mobile
- CTA buttons: full-width on mobile, minimum 44x44px tap target
- Page load: under 3 seconds. A 1-second delay drops conversions ~7%. 47% of users expect load in under 2 seconds.
- Forms: large thumb-friendly fields
- Logo bar: 2 rows max on mobile. Reduce to 3-4 logos if needed.
- Images: compressed. Pages with 1MB+ images average 9.8% CVR vs 11.4% for compressed.

---

## 7. Benchmarks

### Conversion Rate Reference Points

| Context | Benchmark | Source |
|---------|-----------|-------|
| Average landing page (all industries) | 2.35% | WordStream |
| B2B landing pages (median) | ~3.8% | Unbounce |
| B2B paid search | ~1.5% | Ruler Analytics |
| Dedicated LP vs. website page | 5-15% vs. 2-3% | Multiple |
| Top 10% of landing pages | 11.45%+ | Unbounce |
| B2B cold email traffic (healthy) | 3-5% | SalesHive / Unbounce |

### A/B Testing Priorities

For every new landing page, run these tests in order. One variable at a time.

| Priority | Test | Expected Impact |
|----------|------|----------------|
| 1 | Lightbox form vs. embedded form | Up to 59% lift (HubSpot); extreme cases 1,375% (Aweber) |
| 2 | Headline A vs. Headline B | Well-written headline can produce 3x conversion lift |
| 3 | With video vs. without | 38.6% of marketers say video has biggest LP conversion impact (HubSpot) |
| 4 | Navigation removed vs. present | Up to 100% lift (VWO) |
| 5 | Social proof placement | Varies by audience. Test above vs. below fold. |

**Testing rules:**
- Minimum 1,000 visitors per variation before declaring a winner
- One variable at a time
- High-performing teams run 2-3 tests monthly
- Companies testing 10+ variations see 86% better results

---

## 8. Positioning Context Integration

> Defines how positioning context files feed into the campaign brief. Agents consuming this module should use these extraction rules.

### What to Extract for the Copy Agent

| From audience-messaging.md (L1) | What to Include |
|---------------------------------|-----------------|
| Brand voice (tone, person, complexity) | Full voice description, examples if available |
| Persona messaging | ONE persona section relevant to this campaign only |
| Value themes + proof strength | Full table (all tiers). Copy Agent needs complete proof library. |
| Objection handling | Full table. Becomes FAQ section. |
| Language guidance (banned/approved terms) | Full list. Non-negotiable constraints. |

| From Rendered Deliverables (executive summary, messaging guide) | What to Include |
|----------------------------------------------------------------|-----------------|
| Differentiators | Top 2-3 with supporting evidence |
| Case study outcomes | Only those with specific numbers and attribution |
| Competitive context | 2-3 most relevant competitors only |

### What NOT to Include
Full company-identity.md bodies, performance profiles, all-persona audience research, schema headers, YAML frontmatter, confidence scores, changelogs. These add noise and burn context window without improving copy quality.

---

## 9. ATF Copy Principles

Six rules for above-the-fold copy. These apply to all landing pages (paid and organic). Agents reference these by rule name.

### Rule 1: Header Specificity

The H1 must name a specific benefit. No corporate abstractions.

**Vague (fail):** "Transform your onboarding experience" / "Unlock growth" / "Empower your team" / "Streamline operations"
**Specific (pass):** "Cut onboarding time from 3 months to 3 weeks" / "Find every compliance gap before your auditor does"

**Litmus test:** Replace the company name with a competitor's. If the headline still works, it's too vague. A specific headline is true for exactly one product.

**Banned patterns:** "Transform," "Revolutionize," "Unlock," "Empower," "Streamline," "Next-generation," "World-class," "Cutting-edge," "Best-in-class." These are filler, not positioning.

### Rule 2: Value Prop Derivation (Bad Alternative Exercise)

The method for generating H1 candidates. Run this exercise before writing any headline:

1. **What bad alternative do people resort to when they lack this product?** (e.g., "manually reconciling spreadsheets," "hiring a consultant for $50K," "waiting 6 weeks for a report")
2. **How is this product specifically better than that bad alternative?** (e.g., "automated reconciliation in 10 minutes," "self-serve audit at 1/10th the cost," "real-time dashboards")
3. **Turn step 2 into an action statement.** That is the value prop and the starting point for the H1.

Source data: `company-identity.md` differentiators, category, target_market. If L0 doesn't have clear differentiators, flag as `[NEEDS CLIENT INPUT]` and use the best available data.

This exercise produces the *content* of the headline. Rules 3-5 shape *how* it's delivered.

### Rule 3: Hook -- Bold Claim

The ATF should include a bold, specific claim that triggers curiosity. This can live in the H1 itself, a second headline line, or the first sentence of the subheader.

**Requirements:**
- Must be specific and quantified when possible ("147% increase in pipeline" not "dramatically better results")
- Must be believable. If it sounds too good to be true, it is. Cap claims at what evidence supports.
- Must be traceable to an L0 proof point. Prefer `verified` tier (named customer + specific metric). Fall back to `supported` if no verified proof exists. Never use `claimed` tier for bold claims.

**Source:** `company-identity.md` Proof Point Registry. Pull the strongest verified proof point relevant to the target persona's primary challenge.

**When to use:** Most effective when the product has strong quantitative proof. If proof points are weak or only `claimed` tier, skip the bold claim and use Rule 4 (objection handling) instead.

### Rule 4: Hook -- Objection Preemption

Proactively address the #1 buying objection in the header or subheader. Don't let visitors retain unaddressed concerns that cause them to bounce before scrolling.

**Method:**
1. Identify the target persona's `primary_challenge` from `audience-messaging.md`
2. Identify likely objections: "What almost stopped existing customers from buying?" Common B2B objections: implementation time, integration complexity, requires technical skills, too expensive, requires team buy-in.
3. Address the single biggest objection in the ATF. Don't try to handle all objections here. The rest go in the FAQ/Objection Handling section below the fold.

**Example:** If the product is a website builder, the #1 objection might be "I don't know how to code." The header addresses this: "Build production websites without writing a line of code."

**Balance:** Don't bloat the header with multiple objection responses. One objection, handled cleanly.

**Source:** `audience-messaging.md` personas[].primary_challenge. If audience-messaging.md is unavailable, use `company-identity.md` target_market context to infer likely objections, but cap confidence at 3.

### Rule 5: Persona-Direct Copy

ATF copy must address the primary persona by role and context. Never write to "everyone."

**Requirements:**
- Use the persona's language, not internal product terminology
- Reference their world (their problems, their tools, their metrics) not the product's features
- If the campaign brief specifies a single persona, write exclusively to them
- If multiple personas are targeted, implement "choose your own adventure" routing: a persona selector above the fold that routes to persona-specific page sections or separate pages

**Source:** The single persona selected in the campaign brief (`brief.md` target_persona field). Cross-reference with `audience-messaging.md` for that persona's role, segment, primary_challenge, and language patterns.

**Litmus test:** Read the ATF copy aloud. Does it sound like you're talking to a specific person in a specific role? Or does it sound like a press release? If the latter, rewrite.

### Rule 6: CTA Narrative Continuation

CTA button text must continue the story the header started. It is the actionable next step to fulfilling the header's claim.

**Generic (fail):** "Get Started" / "Learn More" / "Request Demo" / "Contact Us" / "Sign Up" / "Submit"
**Narrative (pass):** "See how [outcome] works" / "Start [achieving benefit]" / "Get your [deliverable]" / "Find your [result]"

**Litmus test:** Read the CTA in isolation, without the header. If it makes sense on its own, it's too generic. A good CTA only makes sense as the next step after reading the header.

**Consistency:** All CTAs on the page (hero, mid-page, final) should use the same narrative thread. They can vary in phrasing but should point to the same action and the same promise. Don't introduce new value props in mid-page or final CTAs.

**Exception:** Form submission buttons (inside lightboxes or inline forms) should be direct and action-specific ("Book My Demo," "Download the Guide"). At that point the visitor has committed. The narrative CTA gets them to the form; the form CTA confirms the action.

---

## 10. Copy Generation Guardrails

### Headline Approach by Awareness Stage

The brief's `traffic_awareness_stage` field determines which headline approach is primary:

| Stage | Primary approach | Headline leads with... |
|-------|-----------------|----------------------|
| Unaware | Story / pattern interrupt | Provocative question or surprising stat, NOT the product |
| Problem Aware | Pain-led | Name the specific pain, then bridge to solution category |
| Solution Aware | Keyword-led + differentiation | Mirror search intent, add "the only X that Y" differentiator |
| Product Aware | Proof-led | Specific result metric from a named customer |
| Most Aware | Offer-led | The deal, the incentive, the simplified next step |

When `traffic_awareness_stage` is not set in the brief, default to Solution Aware (safest middle ground for B2B).

### Readability Target

Write all LP copy at a 7th-9th grade reading level (Flesch-Kincaid). This is not dumbing down; it is clarity optimization.

Benchmark data (Unbounce, 41K pages, 57M conversions):
- 5th-7th grade reading level: 11.1% median conversion rate
- College/university level: 5.3% median conversion rate
- Difficult vocabulary correlates with 24.3% lower conversions

Rules:
- Sentences under 20 words average
- Paragraphs under 4 lines on desktop
- No jargon unless the brief's `target_keywords` contain it (mirror buyer language, not internal terminology)
- Active voice default. Passive voice only when the actor is genuinely irrelevant.

### Copy Anti-patterns (Hard Avoid List)

The copy agent must not produce any of the following patterns:

- **Corporate speak.** "Leverage our best-in-class solution to optimize synergies." Rewrite as a specific benefit in plain language.
- **Self-referential opening.** "Welcome to [Company]" or "We are the leading provider of..." The visitor does not care who you are. Open with what you do for them.
- **Feature-first framing.** "Our platform has AI-powered analytics." Rewrite as outcome: "See which leads will close this quarter."
- **Hedging language.** "May help you potentially improve..." Cut qualifiers. State the benefit directly.
- **Unsubstantiated superlatives.** "The best," "the leading," "world-class" without a proof point ID reference.

If a draft contains any of these, the copy agent must rewrite before outputting.

### Rule of One

Each LP targets:
- **One reader** (one persona from the brief's `target_persona`)
- **One big idea** (one core message derived from the brief's positioning)
- **One promise** (one primary outcome the visitor will achieve)
- **One offer** (one CTA, one next step from the brief's `offer_type`)

If the brief specifies multiple personas or offers, the copy agent asks the human to pick one or split into separate campaigns. Do not write a single page that serves multiple personas at equal weight.

### Proof Placement: Specificity Gradient

Social proof should increase in specificity as the visitor scrolls deeper:

| Page zone | Proof type | Example |
|-----------|-----------|---------|
| ATF (above fold) | Logo bar, aggregate number | "Trusted by 500+ B2B teams" + 5-8 client logos |
| Mid-page (features) | Named testimonial aligned to nearby feature | "Onboarding took 2 days, not 2 months - VP Ops, Acme Corp" |
| Pre-CTA (bottom) | Specific metric + named customer (highest-tier proof point) | "Reduced CAC 34% in Q1 - Dir. Marketing, [Client]" |

Pull proof point IDs from the L0 Proof Point Registry. Prefer `verified` tier (named customer + specific metric) near the CTA. Use `supported` tier (named customer + praise, no metric) mid-page. Never use `claimed` tier (unattributed) as standalone social proof.

When fewer than 3 proof points exist in the registry, flag in the brief's `gaps` field and note in copy output. Do not fabricate proof.

### CTA Copy Validation: "I Want To ___" Test

Every CTA button text must complete the sentence: "I want to ___."

- "Start My Free Trial" -> "I want to start my free trial." PASS.
- "Submit" -> "I want to submit." FAIL. Submit what? To whom?
- "Learn More" -> "I want to learn more." WEAK. More about what?
- "Get My Custom Audit" -> "I want to get my custom audit." PASS.

CTA commitment level must match the brief's `traffic_awareness_stage`:

| Stage | CTA commitment | Examples |
|-------|---------------|---------|
| Unaware / Problem Aware | Low | "See How It Works," "Get the Guide" |
| Solution Aware | Medium | "Compare Plans," "Watch Demo" |
| Product Aware | Medium-high | "Start Free Trial," "Book a Walkthrough" |
| Most Aware | High | "Buy Now," "Activate My Account," "Get Started" |

---

## 11. QA Checklist

### Copy QA
- [ ] Headline message-matches target keywords / ad copy
- [ ] Proof points in at least 4 sections (hero, problem/solution, proof, FAQ)
- [ ] Same CTA text in exactly 3 locations
- [ ] No banned terms from language guidance
- [ ] Required disclaimers in footer
- [ ] Named testimonial with title and company
- [ ] Headline under 10 words
- [ ] Copy at 7th grade reading level or below

### Design QA
- [ ] No site navigation
- [ ] No footer links beyond legal/disclaimers
- [ ] CTA in 3 locations
- [ ] CTA triggers lightbox (not redirect)
- [ ] Correct number of form fields
- [ ] Under 3 seconds load on mobile
- [ ] Single-column on mobile
- [ ] Full-width CTA buttons on mobile
- [ ] All images compressed

---

*Conversion Playbook v2.0 | FunnelEnvy | March 2026*
