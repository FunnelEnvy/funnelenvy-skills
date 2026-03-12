# Landing Page Audit Taxonomy

Module for `skills/lp-audit/`. Shared by both audit mode (diagnostic) and construct mode (generative). Audit mode scores each dimension; construct mode uses dimensions as a generation checklist.

**Version:** 1.0.0
**Sources:** Demand Curve ATF Playbook, Julian Shapiro LP Guide, Harry Dry / MarketingExamples, CopyHackers / Joanna Wiebe, Cialdini (Influence + Pre-Suasion), Schwartz (Breakthrough Advertising), Brunson (Dotcom Secrets), Unbounce Conversion Benchmark Report (Q4 2024, 41K pages / 57M conversions / 464M visits), Baymard Institute (checkout/form UX research)

---

## Audit Scoring System

Each dimension scored on a 3-point scale matching positioning-scorecard conventions:

| Rating | Meaning | Audit interpretation |
|--------|---------|---------------------|
| Strong | Dimension is well-executed | No action needed; document what's working |
| Needs Work | Partially present or misaligned | Specific improvement recommendations |
| Missing | Absent or fundamentally broken | Critical gap; high-priority fix |

Overall LP health = count of Strong / Needs Work / Missing across all 10 dimensions. No composite score. Dimensions are not weighted equally in every context (see "Context-Dependent Weighting" at bottom).

---

## Dimension 1: Awareness-Stage Alignment

**What it checks:** Whether the page copy matches the awareness level of the traffic it receives.

**Framework:** Eugene Schwartz's 5 Stages of Awareness (Breakthrough Advertising, 1966):

| Stage | Visitor knows... | LP should lead with... |
|-------|-----------------|----------------------|
| Unaware | Nothing about the problem | Story, pattern interrupt, or provocative question |
| Problem Aware | They have a problem, not what solves it | Problem agitation, then bridge to solution |
| Solution Aware | Solutions exist, not your product specifically | Differentiation, why-us, category positioning |
| Product Aware | Your product, not sure it's right for them | Proof, objection handling, risk reversal |
| Most Aware | Your product is right, need a nudge | Offer, urgency, simplified CTA |

**Checks:**

1. **Traffic source inference.** Determine likely awareness stage from traffic source:
   - Branded search / retargeting / email = Product Aware or Most Aware
   - Non-branded search with solution keywords = Solution Aware
   - Non-branded search with problem keywords = Problem Aware
   - Paid social (cold) / display = Unaware or Problem Aware
   - Referral from comparison site (G2, Capterra) = Product Aware
2. **Headline-to-stage match.** Does the headline address the visitor at their inferred stage? A Product Aware visitor hitting a page that opens with problem education is wasting their intent. A Problem Aware visitor hitting a product-feature dump will bounce.
3. **Copy arc progression.** Does the page walk the visitor forward through remaining stages? A Solution Aware LP should progress: differentiation (why us) -> proof (it works) -> offer (act now). Skipping stages causes confusion or distrust.
4. **CTA commitment level.** Does the ask match the awareness level? Unaware/Problem Aware visitors should get low-commitment CTAs (learn more, see how). Product/Most Aware should get direct conversion CTAs (start trial, request demo, buy now).

**Context file dependencies:**
- `audience-messaging.md` -> persona awareness levels, if documented
- `company-identity.md` -> category (buyer language) for keyword inference
- `competitive-landscape.md` -> whether differentiation copy is needed (high overlap = Solution Aware visitors need more of it)

**Strong:** Headline, body arc, and CTA all calibrated to a single identifiable awareness stage. Copy progresses visitor forward without skipping stages.
**Needs Work:** Headline matches but body copy drifts to a different stage, or CTA commitment is mismatched.
**Missing:** Page attempts to address all awareness stages simultaneously (the "everything to everyone" trap), or headline and CTA target opposite ends of the spectrum.

---

## Dimension 2: Value Proposition Clarity

**What it checks:** Whether a visitor can understand what the product/service is, who it's for, and why it matters within 5 seconds of landing.

**Framework:** Julian Shapiro's desire-minus-labor formula + Demand Curve ATF specificity rules.

The header must answer: What value do you provide, and how do you deliver it? Three headline approaches (test-worthy variants, not exclusive):

| Approach | Structure | Best when... |
|----------|-----------|-------------|
| Pain-led | Name the specific pain, then present relief | Problem Aware traffic, high-urgency problems |
| Keyword-led | Mirror the search term / ad copy, add specificity | Paid search, high-intent queries |
| Proof-led | Lead with a specific result or metric | Product Aware traffic, strong case studies |

**Checks:**

1. **Caveman test (Donald Miller / Harry Dry).** Could someone unfamiliar with the product glance at the ATF and grunt back what you offer? If the headline uses jargon, abstractions, or self-congratulatory language ("The leading platform for..."), it fails.
2. **Specificity audit.** Replace vague claims with the "so what" test:
   - "Save time" -> How much time? Compared to what?
   - "Grow your business" -> What metric? By how much?
   - "AI-powered" -> What does the AI actually do for the user?
3. **Subheader function.** Subheader should expand on exactly one of: (a) what the product is, or (b) how the headline claim is possible. Not both. One to two sentences max.
4. **Value prop vs. feature list.** The ATF should communicate value (outcome for user), not features (what the product does). Features belong below the fold.

**Context file dependencies:**
- `company-identity.md` -> core value proposition, category, target market
- `audience-messaging.md` -> value themes, persona primary challenges
- `positioning-scorecard.md` -> "Differentiation Clarity" and "Value Proposition" dimension ratings

**Strong:** Headline is specific, benefit-focused, and immediately comprehensible to the target persona. Subheader expands without repeating. No jargon.
**Needs Work:** Headline is comprehensible but generic (could apply to competitors), or subheader repeats instead of expanding.
**Missing:** Headline is abstract, self-referential ("Welcome to [Company]"), or requires domain knowledge to parse. Visitor cannot determine what the product does within 5 seconds.

---

## Dimension 3: Message Match / Scent Trail

**What it checks:** Whether the LP maintains continuity from the traffic source that sent the visitor.

**Framework:** Unbounce "message match" principle + Cialdini's commitment/consistency principle.

A visitor who clicks an ad making a specific promise and lands on a page that doesn't immediately echo that promise experiences a scent break. Scent breaks destroy trust and trigger bounces.

**Checks:**

1. **Headline echo.** Does the LP headline contain the core phrase, keyword, or promise from the referring ad / email / link? Not word-for-word duplication, but clear thematic continuity.
2. **Visual continuity.** If the ad used a specific image, color scheme, or visual motif, does the LP continue it? Jarring visual transitions create subconscious distrust.
3. **Offer consistency.** If the ad promised "free trial" / "50% off" / "free audit," does the LP deliver exactly that offer above the fold? Bait-and-switch (even unintentional) is the fastest way to kill conversions.
4. **One page, one source (ideal).** High-performing campaigns use dedicated LPs per ad group or traffic source, not a generic page receiving all traffic. Flag when a single LP serves wildly different traffic sources.

**Context file dependencies:**
- `performance-profile.md` -> top traffic sources, channel breakdown (informs which scent trails matter most)
- `company-identity.md` -> product names, offer types

**Scoring note:** This dimension is often unscoreable in a standalone LP audit without access to the referring ads/emails. If traffic source data is unavailable, flag as "Not Assessed" rather than guessing. When constructing a new LP, this dimension becomes a constraint: the brief must specify the traffic source and the construct phase must maintain scent.

**Strong:** LP headline and offer directly echo the ad/email/link copy. Visual continuity maintained. Dedicated LP per traffic source.
**Needs Work:** Core message is present but buried below the fold, or visual tone shifts noticeably from the ad.
**Missing:** No discernible connection between ad copy and LP headline, or offer differs from what was promised.

---

## Dimension 4: Page Structure and Content Hierarchy

**What it checks:** Whether the page sections are ordered to match the visitor's decision-making sequence and whether content is scannable.

**Framework:** Harry Dry's two-part LP structure + CopyHackers messaging hierarchy + PAS/AIDA frameworks.

### Above the Fold (ATF) Checklist

The ATF has one job: earn the scroll. Five elements, all visible without scrolling:

| Element | Purpose | Failure mode |
|---------|---------|-------------|
| Headline | Communicate core value | Vague, clever, or self-referential |
| Subheader | Expand or substantiate headline | Repeats headline, adds no info |
| Visual | Show product in action or outcome | Stock imagery, abstract graphics |
| CTA | Make next step obvious and low-friction | Below the fold, vague ("Learn More" for Most Aware traffic) |
| Social proof micro-signal | Establish immediate credibility | Missing entirely from ATF |

### Below the Fold (BTF) Section Order

Recommended progression (adapt per awareness stage):

1. **Make value concrete.** Features with outcomes, not feature lists. Each feature section answers "so what does this mean for me?"
2. **Show proof.** Deeper social proof: case studies, specific metrics, named customers, logos.
3. **Handle objections.** Address the 2-3 most common reasons people don't buy. FAQ section or dedicated objection-handling copy.
4. **Inspire action.** Benefit recap, transformation narrative, or comparative before/after.
5. **Repeat CTA.** Same CTA as ATF, potentially with added urgency or risk reversal.

### Structural Anti-patterns

- **Feature graveyard.** Page is a list of features with no benefit framing.
- **Social proof desert.** No testimonials, logos, case studies, or metrics anywhere on page.
- **CTA cliff.** Single CTA only at the very bottom after thousands of words.
- **Navigation leak.** Full site navigation present on a dedicated LP, giving visitors 10+ exit paths before converting.
- **Wall of text.** No visual breaks, subheadings, or whitespace between sections.

**Checks:**

1. **ATF completeness.** Are all 5 ATF elements present and visible without scrolling on both desktop and mobile?
2. **Section progression.** Does the BTF follow a logical persuasion arc, or is it a random collection of content blocks?
3. **Scanability.** Can a visitor who scrolls quickly (2-3 seconds full page) identify the core argument? Subheadings should tell the story independently.
4. **Navigation removal.** For dedicated campaign LPs: is the main site navigation removed or minimized? (Not applicable for homepages or product pages serving organic traffic.)
5. **CTA frequency.** Is there a CTA visible at every scroll-depth where a visitor might be ready to act? Rule of thumb: CTA should appear every 2-3 scroll heights.

**Context file dependencies:**
- `audience-messaging.md` -> persona primary challenges (inform section order)
- `company-identity.md` -> proof points registry (are available proof points actually used?)
- `competitive-landscape.md` -> white spaces and overlap zones (differentiation sections should address these)

**Strong:** ATF has all 5 elements. BTF sections follow a logical persuasion arc. Page is scannable. Navigation minimized on campaign LPs. CTAs at regular intervals.
**Needs Work:** Most elements present but ordering is suboptimal (e.g., features before proof), or ATF is missing one element.
**Missing:** No discernible structure. Feature dump with no persuasion arc. Single CTA at bottom only.

---

## Dimension 5: Social Proof Strategy

**What it checks:** Whether the page deploys the right types, quantity, and placement of credibility signals.

**Framework:** Cialdini's social proof + authority principles + Demand Curve proof placement rules.

### Social Proof Taxonomy (ordered by persuasion strength for B2B)

| Type | Example | Strength | Best placement |
|------|---------|----------|---------------|
| Specific metric + named customer | "Reduced churn 40% - VP Marketing, Acme Corp" | Highest | Near CTA, proof section |
| Named customer praise (no metric) | "Game-changer for our team - Jane Doe, Acme" | High | Proof section, near features |
| Logo bar | Row of recognizable client logos | Medium-high | ATF or just below |
| Aggregate social proof | "10,000+ teams trust [Product]" | Medium | ATF subtext |
| Star ratings / review scores | "4.8/5 on G2, 200+ reviews" | Medium | ATF or near CTA |
| Industry awards / certifications | "SOC 2 compliant, ISO 27001" | Medium | Footer or trust section |
| Media mentions | "As seen in Forbes, TechCrunch" | Low-medium | ATF or logo bar |
| Generic testimonials (no name/company) | "Great product!" | Low | Avoid; low credibility |

**Checks:**

1. **ATF social proof.** Is at least one social proof signal visible above the fold? Logo bars and aggregate numbers are minimum viable. Absence is a critical gap.
2. **Proof-to-claim pairing.** Every major claim on the page should have a corresponding proof point nearby. A claim of "50% faster" needs a testimonial or case study metric within visual proximity.
3. **Specificity gradient.** Proof should get more specific as the visitor scrolls deeper. ATF: logos and aggregate numbers. Mid-page: named testimonials. Bottom: detailed case study or metric.
4. **Proof type diversity.** At least 2 distinct types of social proof on the page. A single logo bar is not sufficient.
5. **Objection-aligned proof.** If the primary objection is ease of implementation, the most prominent testimonial should address implementation. If it's ROI, lead with metrics. Proof should counter the dominant objection, not just praise the product generically.

**Context file dependencies:**
- `company-identity.md` -> proof point registry (P1, P2, etc.) with verification tiers
- `audience-messaging.md` -> primary objections per persona (inform proof alignment)
- `competitive-landscape.md` -> competitor proof strategies (are they out-proofing you?)

**Strong:** 3+ types of social proof. ATF includes at least one signal. Specific metrics from named customers near key claims. Proof aligned to primary objections.
**Needs Work:** Social proof present but generic (no names, no metrics), clustered in one section instead of distributed, or misaligned with primary objections.
**Missing:** No social proof on page, or only unverifiable generic quotes.

---

## Dimension 6: CTA Strategy and Form Design

**What it checks:** Whether the call-to-action and any associated forms are optimized for conversion rather than data collection.

**Framework:** Unbounce form friction data + Baymard Institute form UX research + CopyHackers CTA copy rules.

### CTA Copy Rules

- **Action-specific, not generic.** "Get My Free Audit" > "Submit." "Start 14-Day Trial" > "Sign Up." "See Pricing" > "Learn More."
- **Match commitment to awareness.** Low awareness = low commitment CTA ("See How It Works"). High awareness = direct conversion CTA ("Start Free Trial").
- **First person can outperform second person.** "Start My Free Trial" sometimes outperforms "Start Your Free Trial." Test-worthy, not universal.
- **Avoid "Submit."** The word "submit" implies surrender, not action. It consistently underperforms action-oriented alternatives.
- **Button text should complete the sentence: "I want to ___."** If the button text doesn't work in that frame, it's too vague.

### Form Design Rules

| Metric | Benchmark | Source |
|--------|-----------|--------|
| Ideal field count (lead gen) | 3-5 fields | Unbounce |
| Max before severe drop-off | 7+ fields = abandonment cliff | Unbounce |
| Form abandonment rate | 81% start but don't finish | Unbounce |
| Conversion lift from field reduction | Up to 120% | Unbounce |
| Ideal checkout form elements | 12-14 (vs avg 23.48) | Baymard |

**Checks:**

1. **CTA visibility.** Is the primary CTA visible above the fold? Is it visually distinct (color contrast, size, whitespace)?
2. **CTA copy audit.** Does button text pass the "I want to ___" test? Is it action-specific?
3. **Field count.** Count all form fields. Flag if >5 for lead gen, >7 for any purpose. Each field beyond minimum should have a justification.
4. **Progressive profiling.** For B2B: is the form collecting everything upfront, or does it use multi-step / progressive disclosure? Multi-step forms that start with easy questions (email only) and escalate can outperform single long forms.
5. **Form friction signals.** Phone number field (high friction, often unnecessary). Required fields that aren't truly required. CAPTCHA visible before submission. No inline validation. No smart defaults.
6. **Secondary CTA availability.** For B2B: is there a lower-commitment alternative for visitors not ready for the primary CTA? ("Download the guide" alongside "Request a demo.") This captures leads at earlier awareness stages.
7. **Post-submit experience.** What happens after form submission? A generic "Thank you" page wastes a high-intent moment. Best: calendar booking, immediate value delivery, or clear next-step communication.

**Context file dependencies:**
- `audience-messaging.md` -> persona roles (informs which fields are necessary vs. enrichable)
- `performance-profile.md` -> form conversion rates, if available from GA4 data

**Strong:** CTA above fold with action-specific copy. 3-5 form fields max. Secondary CTA for lower-commitment visitors. Inline validation. Clear post-submit experience.
**Needs Work:** CTA present but generic text, or form has 6-7 fields with no progressive profiling.
**Missing:** CTA below the fold only, "Submit" button text, 8+ form fields, no post-submit strategy, or phone number required for a top-of-funnel offer.

---

## Dimension 7: Persuasion Psychology Execution

**What it checks:** Whether the page correctly applies behavioral psychology principles beyond social proof (which has its own dimension).

**Framework:** Cialdini's 6 principles (Influence) + Pre-Suasion + cognitive bias patterns.

### Persuasion Principles Audit

| Principle | LP application | Common failure |
|-----------|---------------|----------------|
| **Reciprocity** | Give value before asking (free tool, calculator, audit preview, useful content) | Asking for email/demo before providing any value |
| **Scarcity** | Genuine limited availability, time-bound offers, cohort caps | Fake urgency ("Only 3 left!" on a SaaS product), countdown timers that reset |
| **Authority** | Expert endorsements, credentials, media features, data-backed claims | Self-proclaimed authority with no external validation |
| **Consistency** | Micro-commitments (quiz, calculator, assessment) before macro-commitment (demo, purchase) | Jumping from zero engagement to high-commitment CTA |
| **Liking** | Conversational tone, relatable imagery, shared identity signals | Corporate jargon, stock photos of generic businesspeople |
| **Unity** | Shared identity ("Built by marketers, for marketers"), community signals | Generic "We serve businesses of all sizes" |

### Cognitive Bias Patterns

| Bias | LP application |
|------|---------------|
| **Anchoring** | Show higher price first (annual), then monthly; show competitor pricing before yours |
| **Loss aversion** | Frame value as what they'll lose by not acting, not just what they'll gain. "Stop losing 23% of qualified leads" > "Gain more leads" |
| **Decoy effect** | In pricing: add a less attractive option to make the target option look better |
| **Halo effect** | Clean, professional design signals trustworthiness before copy is even read |
| **Endowment effect** | Free trials, interactive demos, "preview your results" = psychological ownership before purchase |

**Checks:**

1. **Value-before-ask.** Does the page offer any value (insight, tool, preview, content) before requesting information or commitment? Pages that open with a form and nothing else violate reciprocity.
2. **Risk reversal.** Is there a guarantee, free trial, money-back promise, or "cancel anytime" signal? For B2B: "No credit card required" or "15-minute setup, cancel anytime" reduces perceived risk.
3. **Urgency authenticity.** If urgency or scarcity signals are present, are they genuine? Fake scarcity (perpetual countdown timers, "limited spots" on an unlimited SaaS product) erodes trust when detected.
4. **Micro-commitment path.** Does the page offer a step smaller than the primary CTA? Interactive elements (ROI calculator, assessment quiz, product configurator) create psychological investment before the big ask.
5. **Loss framing presence.** Is at least one section framed around what the visitor risks by not acting, rather than only what they gain? Loss aversion is approximately 2x stronger than gain motivation.
6. **Objection pre-emption.** Does the page address the top 2-3 objections before the visitor has to voice them? FAQ sections, "Is this right for me?" blocks, and comparison tables serve this function.

**Context file dependencies:**
- `audience-messaging.md` -> banned terms, primary objections per persona
- `competitive-landscape.md` -> competitor pricing (anchoring context), claim overlap (differentiation needs)

**Strong:** 3+ principles correctly applied. Risk reversal present. Urgency signals genuine. Objections pre-empted. At least one micro-commitment opportunity.
**Needs Work:** Some principles present but superficially applied (e.g., testimonials but no risk reversal, or urgency without authenticity).
**Missing:** No persuasion architecture. Page is purely informational with no psychological scaffolding. Or, principles applied in manipulative/deceptive ways that would erode trust.

---

## Dimension 8: Copy Quality and Readability

**What it checks:** Whether the copy is clear, scannable, appropriately complex for the audience, and free of conversion-killing patterns.

**Framework:** Unbounce readability data + CopyHackers writing rules + Schwartz copy principles.

### Readability Benchmarks

| Reading Level | Median Conversion Rate | Source |
|---------------|----------------------|--------|
| 5th-7th grade | 11.1% | Unbounce |
| 8th-9th grade | 8.2% | Unbounce |
| College/University | 5.3% | Unbounce |
| Professional/Postgraduate | 3.4% | Unbounce |

**Critical:** Difficult vocabulary correlates with 24.3% lower conversion rates. Simpler is almost always better, even for sophisticated B2B audiences.

### Copy Anti-patterns

- **Corporate speak.** "Leverage our best-in-class solution to optimize synergies." No one talks like this. No one trusts it.
- **Feature-first framing.** "Our platform has AI-powered analytics." vs. "See which leads will close this quarter, before your competitors do."
- **Hedging language.** "May help you potentially improve..." Weak verbs and qualifiers signal uncertainty.
- **Self-referential opening.** "Welcome to [Company]" or "We are the leading provider of..." The visitor doesn't care who you are. They care what you do for them.
- **Wall of text.** Paragraphs longer than 3-4 lines on desktop. No subheadings. No visual breaks.
- **Passive voice.** "Results are delivered by our platform" vs "Our platform delivers results." Passive voice weakens claims.

### The Rule of One (CopyHackers)

The most effective LPs target:
- **One reader** (one persona, one awareness stage)
- **One big idea** (one core message, not five)
- **One promise** (one primary outcome)
- **One offer** (one CTA, one next step)

Pages that try to serve multiple personas, communicate multiple value props simultaneously, or offer multiple CTAs at equal visual weight underperform.

**Checks:**

1. **Readability score.** Run copy through a readability check (Flesch-Kincaid or equivalent). Flag anything above 9th grade level. B2B does not mean complex writing.
2. **Anti-pattern scan.** Check for corporate speak, hedging, passive voice, self-referential openings, and feature-first framing.
3. **Scanability test.** Read only the subheadings. Do they tell a coherent story on their own? If a visitor reads nothing but subheadings, do they understand the value proposition?
4. **Rule of One compliance.** Does the page target one persona, one big idea, one promise, one offer? Or does it try to serve multiple audiences simultaneously?
5. **Voice consistency.** Does the copy maintain a consistent tone throughout, or does it shift between conversational and corporate, between first and third person?
6. **Banned term check.** Cross-reference copy against audience-messaging.md banned terms list and known jargon.

**Context file dependencies:**
- `audience-messaging.md` -> tone, voice, banned terms, customer language samples
- `company-identity.md` -> category buyer language (does the page use the buyer's words or the company's internal terminology?)

**Strong:** Readability at 7th-9th grade. Subheadings tell the story independently. One persona, one idea, one offer. Voice consistent. No anti-patterns.
**Needs Work:** Readability acceptable but copy contains 2+ anti-patterns, or page targets one persona but hedges by including tangential value props.
**Missing:** College-level readability. Multiple anti-patterns. No scannable structure. Attempts to address 3+ personas simultaneously.

---

## Dimension 9: Visual Design and UX Performance

**What it checks:** Whether the visual design supports (rather than hinders) the conversion goal, and whether technical performance meets thresholds.

**Framework:** Unbounce/Baymard UX data + Core Web Vitals benchmarks.

### Performance Thresholds

| Metric | Target | Impact |
|--------|--------|--------|
| Page load time | < 2 seconds | Every second costs 7% in conversions |
| Largest Contentful Paint (LCP) | < 2.5 seconds | Core Web Vital, affects SEO + UX |
| First Input Delay (FID) | < 100ms | Core Web Vital |
| Cumulative Layout Shift (CLS) | < 0.1 | Core Web Vital |
| Mobile responsiveness | Fully responsive | Mobile = 83% of traffic, 8% lower conversion |

### Visual Hierarchy Rules

- **Eye path.** Design should create a clear visual path: headline -> supporting visual -> subheader -> CTA. Heat map patterns (F-pattern for text-heavy, Z-pattern for visual) should inform layout.
- **Whitespace.** Sections need breathing room. Cluttered layouts trigger cognitive overload and reduce time-on-page.
- **CTA contrast.** CTA button must be the highest-contrast element on the page. If it blends into the color scheme, it's invisible.
- **Image relevance.** Product screenshots, demo GIFs, and outcome visualizations outperform stock photography. Abstract imagery ("blue people shaking hands in front of a globe") is effectively invisible to visitors.
- **Mobile-first design.** Touch targets >= 44px. No horizontal scrolling. Forms usable with thumbs. Content adapts (not just reflows) for mobile.

**Checks:**

1. **Load time assessment.** If performance data is available, check against 2-second threshold. If not, qualitative assessment: does the page load noticeably slowly? Are there large uncompressed images?
2. **Visual hierarchy.** Is there a clear eye path from headline to CTA? Or do competing visual elements fragment attention?
3. **CTA visual prominence.** Is the CTA button the most visually distinct element on the page? High contrast, adequate size, whitespace around it?
4. **Image audit.** Are images product-relevant (screenshots, demos, outcomes) or generic stock? Do images support the copy's claims or merely decorate?
5. **Mobile experience.** Does the page function well on mobile? ATF content visible without pinching? Form fields usable? CTA accessible via thumb?
6. **Accessibility basics.** Alt text on images, sufficient color contrast for text, logical heading hierarchy (H1 > H2 > H3), keyboard navigability.

**Context file dependencies:**
- `performance-profile.md` -> device split (desktop vs mobile traffic %, informs mobile priority)
- `performance-profile.md` -> element interaction data (which page elements get clicks)

**Scoring note:** This dimension has a technical sub-score (performance) and a design sub-score (hierarchy/UX). Both factor into the rating.

**Strong:** < 2s load time. Clear visual hierarchy. High-contrast CTA. Product-relevant imagery. Fully responsive mobile experience.
**Needs Work:** Adequate load time but visual hierarchy unclear, or good design but performance issues (3-5s load).
**Missing:** > 5s load time. No visual hierarchy. CTA invisible. Stock imagery only. Mobile experience broken.

---

## Dimension 10: Competitive Differentiation

**What it checks:** Whether the page clearly communicates why the visitor should choose this product/service over alternatives.

**Framework:** Positioning-scorecard dimensions + competitive-landscape overlap analysis.

**Checks:**

1. **Explicit differentiation.** Does the page state, in clear terms, what makes this product different from alternatives? Not "We're the best" but "The only [category] that [specific differentiator]."
2. **Comparison content.** For Solution Aware and Product Aware traffic: is there a comparison table, "why us" section, or competitor acknowledgment? Ignoring competitors when the visitor is actively comparing creates a trust gap.
3. **Category ownership.** Does the page claim or imply category leadership? If so, is it substantiated with proof? Unsubstantiated category claims ("The #1 platform for...") trigger skepticism.
4. **Switching cost reduction.** For visitors evaluating a switch from a competitor: does the page address migration concerns? ("Import your data in 5 minutes," "We handle the migration for you.")
5. **White space targeting.** Does the page emphasize capabilities that sit in competitive white spaces (areas where competitors are weak or absent)? This is the highest-leverage differentiation.
6. **Claim uniqueness.** Cross-reference the page's claims against competitor claims. If 3+ claims are identical to what competitors say, the page has a differentiation problem. The claim overlap score from competitive-landscape.md directly informs this check.

**Context file dependencies (critical for this dimension):**
- `competitive-landscape.md` -> competitor positioning statements, claim overlap score, white spaces, overlap zones
- `company-identity.md` -> stated differentiators, proof point registry
- `positioning-scorecard.md` -> "Differentiation Clarity" dimension rating

**Strong:** Clear, specific differentiator stated prominently. White spaces targeted. Comparison content for aware visitors. Claims backed by unique proof.
**Needs Work:** Differentiation present but generic ("better customer service"), or positioning relies on claims shared with 2+ competitors.
**Missing:** No differentiation. Page could be any competitor with the logo swapped. Or, claims are identical to market leaders without proof of parity.

---

## Context-Dependent Weighting

Not all dimensions matter equally for every page type. The audit skill should adjust emphasis based on:

### By Page Type

| Page type | Priority dimensions | Deprioritized |
|-----------|-------------------|---------------|
| Paid search LP | D1 (Awareness), D3 (Message Match), D6 (CTA/Form) | D10 (Differentiation, if branded traffic) |
| Paid social LP (cold) | D1 (Awareness), D2 (Value Prop), D5 (Social Proof) | D3 (Message Match, less critical for cold) |
| Homepage | D2 (Value Prop), D4 (Structure), D10 (Differentiation) | D3 (Message Match, serves all traffic) |
| Product page | D4 (Structure), D5 (Social Proof), D10 (Differentiation) | D1 (Awareness, typically Product Aware) |
| Long-form sales page | D7 (Persuasion), D8 (Copy), D4 (Structure) | D9 (Performance, less critical than copy) |
| Pricing page | D10 (Differentiation), D7 (Persuasion, anchoring/decoy), D6 (CTA) | D1 (Awareness, typically Product Aware) |

### By Industry Benchmarks

Reference when setting expectations for what "good" looks like:

| Industry | Median CVR | "Good" (75th %ile) | Key characteristics |
|----------|-----------|--------------------|--------------------|
| SaaS | 3.8% | 11.6% | Long consideration, free trial critical |
| Financial Services | 8.4% | 14.2% | Trust signals paramount |
| E-Commerce | 4.2% | 8.8% | Speed + urgency + visual quality |
| Professional Services | 6.0% | 12.4% | Authority + proof + risk reversal |
| Health & Wellness | 5.8% | 11.8% | Emotional copy + testimonials |
| Events & Entertainment | 12.3% | 40.8% | Urgency + scarcity (genuine) |
| Legal | 7.1% | 12.3% | Trust + authority + empathy |

Source: Unbounce Conversion Benchmark Report Q4 2024. Median = 50th %ile. "Good" = 75th %ile.

### By Traffic Channel

| Channel | Avg CVR | Implication for audit |
|---------|---------|---------------------|
| Email | 19.3% | Pre-qualified audience; page should be direct and conversion-focused |
| Instagram (paid) | 17.9% | Visual-first audience; imagery and design weight increases |
| Facebook (paid) | 13.0% | Awareness-stage matching critical; cold traffic dominant |
| Google Search (paid) | 10.9% | Message match paramount; keyword-headline alignment |
| YouTube | 8.2% | Video on LP may improve continuity from ad format |
| LinkedIn (paid) | 3.1% | Lower volume, higher value; B2B proof and authority critical |

Source: Unbounce Conversion Benchmark Report Q4 2024.

---

## Construct Mode: Using Dimensions as Generation Checklist

When the skill operates in construct mode (building LP content from positioning docs), each dimension becomes a generation constraint:

| Dimension | Construct-mode question |
|-----------|----------------------|
| D1 Awareness | What awareness stage is the target traffic? Set headline approach accordingly. |
| D2 Value Prop | Pull headline candidates from company-identity.md value prop + audience-messaging.md value themes. |
| D3 Message Match | What ad/email copy will drive traffic? Mirror it. |
| D4 Structure | Use ATF checklist + BTF section order as page skeleton. |
| D5 Social Proof | Pull from proof point registry (P1, P2...). Place per specificity gradient rules. |
| D6 CTA/Form | Set CTA text using "I want to ___" test. Set field count from brief's form strategy. |
| D7 Persuasion | Apply loss framing, risk reversal, micro-commitment based on persona objections. |
| D8 Copy | Write at 7th-9th grade level. Follow Rule of One. Apply audience voice/tone. |
| D9 Visual/UX | Specify image types (product screenshots, not stock). Define mobile breakpoints. |
| D10 Differentiation | Lead with white-space claims from competitive-landscape.md. Avoid overlap-zone claims unless uniquely provable. |

---

## Relationship to Existing Skills

This module is consumed by `skills/lp-audit/` and `skills/landing-page-generator/`.

- **lp-audit** reads this module in full during the audit phase. Outputs a scored assessment with per-dimension ratings, evidence, and prioritized recommendations.
- **landing-page-generator** already has `modules/conversion-playbook.md` for structural/prescriptive rules. This taxonomy adds the diagnostic layer. The generator's QA phase (`phases/qa.md`) should cross-reference this taxonomy for validation checks.
- **hypothesis-generator** can consume LP audit output to generate experiment hypotheses targeting specific weak dimensions.

### Data flow

```
LP Audit Skill
  |-- reads modules/lp-audit-taxonomy.md (this file)
  |-- reads .claude/context/ (L0 + L1) for context-dependent scoring
  |-- extracts target LP via modules/web-extract.md
  |-- scores 10 dimensions
  |-- writes .claude/deliverables/lp-audit-<slug>.md
  |       (scores, evidence, recommendations)
  +-- optionally feeds hypothesis-generator for experiment roadmap
```

---

## Source Bibliography

**Books (distilled into checks above):**
- Schwartz, E. (1966). *Breakthrough Advertising.* -- 5 Stages of Awareness, market sophistication levels, desire channeling
- Cialdini, R. (2006). *Influence: The Psychology of Persuasion.* -- 6 principles of persuasion
- Cialdini, R. (2016). *Pre-Suasion.* -- Framing, priming, attention channeling
- Brunson, R. (2015). *Dotcom Secrets.* -- Funnel architecture, traffic temperature, offer stacking, attractive character

**Online resources (distilled into checks above):**
- Demand Curve ATF Playbook (demandcurve.com/playbooks/above-the-fold) -- Header writing, specificity, hook construction
- Julian Shapiro LP Guide (julian.com/guide/startup/landing-pages) -- Page structure template, desire-minus-labor, reviewer criteria
- Harry Dry / MarketingExamples LP Guide (marketingexamples.com/landing-page/guide) -- ATF/BTF formula, caveman test, practical examples
- CopyHackers / Joanna Wiebe -- PAS framework, Rule of One, messaging hierarchy, conversion copywriting process
- Unbounce Conversion Benchmark Report Q4 2024 -- Industry benchmarks, readability data, channel performance, device split, form friction data (41K pages, 57M conversions, 464M visits)
- Baymard Institute -- Form field usability (650+ UX guidelines), checkout optimization (35% avg conversion lift), cart abandonment research (70.19% avg rate, 49-study aggregate)

---

*Module version 1.0.0. Last updated: 2026-03-12.*
