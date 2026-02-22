# Experiment Patterns Library

Version: 1.0.0
Last updated: 2026-02-20
Pattern count: 13
Categories: 6

This module contains the CRO experiment patterns that drive the hypothesis generator. Each pattern encodes a testable opportunity type, its trigger conditions, causal reasoning, ICE baselines, and contextual modifiers.

The hypothesis generator matches signals from context files against the "Applies when" trigger conditions. When a match is found, the pattern provides the reasoning framework for constructing and scoring the hypothesis.

---

## Pattern Schema

Each pattern follows this structure:

- **Pattern ID:** Category prefix + number (e.g., HM-01). Internal reference only. Never appears in deliverables.
- **Category:** One of: Headline/Messaging, Form Optimization, Navigation/UX, Personalization, Page Structure/Layout, Pricing
- **Applies when:** Trigger conditions matched against context files. All conditions must be true for a full match. Any single condition = partial match.
- **Typical test:** The default experiment design. Adapted to specific context during hypothesis construction.
- **Causal mechanism:** The behavioral or psychological principle that makes this test work. Starting point for hypothesis-specific reasoning.
- **ICE baseline:** Starting scores before modifiers. Represents the typical case.
- **Modifiers:** Conditional adjustments to ICE scores based on available context.
- **Common mistakes:** What to avoid. Used during hypothesis construction to improve quality.
- **Sequencing notes:** Dependencies and ordering considerations.

---

## Category: Headline/Messaging

### HM-01: Value Prop Clarity Test

**Category:** Headline/Messaging
**Applies when:**
- Positioning scorecard rates Clarity as "Needs Work" or "Missing"
- Homepage headline uses jargon, category language, or feature-first framing instead of outcome language
- Gap between the company's strongest value prop (from L0 differentiators) and what the homepage actually says

**Typical test:** Replace feature/category headline with outcome-oriented headline adapted from the primary value theme in audience-messaging.

**Causal mechanism:** B2B buyers scanning above the fold decide in 3-5 seconds whether a page is relevant. Category language ("AI-powered revenue platform") forces cognitive work to translate features into personal value. Outcome language ("Close deals 40% faster") self-qualifies the visitor immediately.

**ICE baseline:** Impact 8 | Confidence 7 | Ease 9
**Modifiers:**
- Confidence +1 if audience-messaging provides specific channel adaptation for homepage
- Confidence -2 if no exact current headline copy available in context
- Impact +1 if scorecard rates Clarity as "Missing" (not just "Needs Work")

**Common mistakes:**
- Testing two vague headlines against each other instead of testing clarity vs. ambiguity
- Changing headline without aligning subhead, creating a disconnect
- Using outcome language that isn't supported by any proof point (credibility gap)

**Sequencing notes:** Run early. Headline clarity is foundational. Results inform all downstream copy experiments.

---

### HM-02: Specificity Injection

**Category:** Headline/Messaging
**Applies when:**
- Positioning scorecard rates Proof as "Needs Work" or "Missing"
- Page claims exist without quantified evidence nearby (e.g., "trusted by hundreds" instead of "trusted by 340+ B2B SaaS companies")
- L0 proof point registry has "verified" or "supported" proof points that don't appear on the page where the related claim is made

**Typical test:** Add specific metric, customer name, or timeframe adjacent to the primary claim. Replace vague social proof with concrete numbers.

**Causal mechanism:** Specificity signals credibility. "Trusted by hundreds of companies" triggers skepticism (why not say the number?). "Trusted by 340+ B2B SaaS companies including [Logo]" activates a different trust evaluation: the specificity implies confidence in the claim.

**ICE baseline:** Impact 6 | Confidence 8 | Ease 9
**Modifiers:**
- Impact +2 if the company has "verified" proof points (named customer + metric) not currently displayed on the page
- Confidence -1 if proof points are only "claimed" strength
- Impact +1 if applied to pricing or demo request page (high-intent context where proof reduces last-mile friction)

**Common mistakes:**
- Adding proof that doesn't match the claim it sits next to (e.g., a logo from a different industry than the one being targeted)
- Generic logos that don't signal the target segment
- Specificity without relevance (impressive numbers that don't address the buyer's actual concern)

**Sequencing notes:** Pairs well with HM-01. Run after headline clarity is established so proof supports the right message.

---

## Category: Form Optimization

### FO-01: Form Field Reduction

**Category:** Form Optimization
**Applies when:**
- Lead gen form observed with 5+ fields
- No progressive profiling detected in context
- Form is for a mid-funnel action (content download, webinar signup, newsletter)

**Typical test:** Reduce to 3-4 essential fields (name, email, company). Capture remaining data via enrichment tools or follow-up sequences.

**Causal mechanism:** Each additional form field increases perceived effort and triggers a cost-benefit reevaluation. For mid-funnel actions where the visitor hasn't committed to a purchase decision, the perceived value of the content often doesn't justify the effort of filling out 7+ fields.

**ICE baseline:** Impact 7 | Confidence 8 | Ease 7
**Modifiers:**
- Confidence -3 if form is for high-intent action (demo request, consultation) where qualification matters more
- Impact +2 if mobile traffic represents >40% of page visits
- Ease -2 if form is embedded third-party (Marketo, HubSpot) with limited field customization
- Impact diminishing: if form already has 4-5 fields, reducing to 3 has smaller effect than reducing from 8 to 4

**Common mistakes:**
- Removing fields the sales team actively uses for qualification without setting up enrichment
- Diminishing returns past the third field removed
- Treating all fields equally (email and phone have very different friction profiles)

**Sequencing notes:** Independent of most other experiments. Can run in parallel with page-level tests on different pages.

---

### FO-02: Multi-Step Form Conversion

**Category:** Form Optimization
**Applies when:**
- Single-page form with 5+ fields
- The form is for a high-intent action (demo, consultation, free trial) where field reduction would sacrifice qualification
- Progressive disclosure would allow low-friction entry with qualification deferred to later steps

**Typical test:** Break into 2-3 steps. Step 1: lowest friction fields (email, use case selection). Step 2: qualification fields (company size, role). Step 3: scheduling or details. Show progress indicator.

**Causal mechanism:** Commitment and consistency bias. Once someone completes Step 1, they've invested effort and are more likely to finish. The multi-step structure also reduces perceived effort at the moment of decision: the visitor sees "Step 1 of 3" with two fields, not a wall of seven fields.

**ICE baseline:** Impact 7 | Confidence 7 | Ease 5
**Modifiers:**
- Ease -3 if form is embedded third-party with limited step/flow customization
- Confidence +2 if baseline form abandonment data is available
- Impact +1 if current single-page form has a measurably low completion rate

**Common mistakes:**
- Putting the highest-friction question (budget, phone number) in Step 1
- Not tracking step-level abandonment, which makes the test unreadable
- Too many steps (4+ steps for 7 fields is worse than a single page)

**Sequencing notes:** Choose either FO-01 or FO-02 for a given form, not both. FO-01 reduces fields, FO-02 restructures them. Decide based on whether field count can actually be reduced.

---

### FO-03: Form Context Reinforcement

**Category:** Form Optimization
**Applies when:**
- Form page or modal has no value reinforcement around the form itself
- No reminder of what the visitor gets, no trust signals near the submit button, no expectation-setting for what happens next

**Typical test:** Add contextual reinforcement adjacent to the form: "What you'll get" summary, relevant testimonial or proof point, security/privacy reassurance, expected next step ("We'll email your report within 24 hours").

**Causal mechanism:** At the moment of form submission, the visitor re-evaluates their decision. Reinforcement at the point of action addresses the implicit question "Is this worth my information?" Trust signals and expectation-setting reduce last-moment abandonment.

**ICE baseline:** Impact 5 | Confidence 7 | Ease 9
**Modifiers:**
- Impact +3 if form is for high-commitment action (demo, consultation) where the ask feels larger
- Impact -1 if form is for low-friction content download
- Confidence +1 if L0 proof point registry has "verified" proof points available to display

**Common mistakes:**
- Adding generic trust badges that don't address the actual objection ("SOC 2 certified" next to a newsletter signup is noise)
- Reinforcement that introduces new information rather than echoing the page's existing value prop (creates cognitive dissonance)
- Omitting the "what happens next" expectation (leads to post-submission anxiety and lower follow-through)

**Sequencing notes:** Complements FO-01 and FO-02. Can be combined with either. Adding context around a reduced-field form is an especially strong combination.

---

## Category: Navigation/UX Flow

### NX-01: Navigation Intent Mismatch

**Category:** Navigation/UX Flow
**Applies when:**
- Audience-messaging identifies 2+ distinct personas with different primary challenges
- Site navigation doesn't segment by persona or use case (feature-only navigation)
- Positioning scorecard rates Specificity as "Needs Work" (generic messaging for diverse audiences)

**Typical test:** Add persona or use-case-based navigation paths ("For [Role]" or "By Use Case") alongside or replacing feature-based navigation.

**Causal mechanism:** When a B2B site serves multiple buyer personas, feature-based navigation forces each persona to self-filter through features to find what's relevant. Use-case or role-based navigation acts as a shortcut: "For VP Sales" immediately signals "this section is about my problems." It reduces navigation effort and increases perceived relevance.

**ICE baseline:** Impact 7 | Confidence 5 | Ease 4
**Modifiers:**
- Confidence +2 if analytics show high bounce from current navigation pages
- Ease -2 if CMS doesn't support dynamic navigation or dropdown customization
- Impact +1 if 3+ distinct personas identified (more audience diversity = more navigation friction)
- Confidence +1 if competitor sites already use persona-based navigation successfully

**Common mistakes:**
- Creating persona pages that are just filtered feature lists instead of reframed value propositions
- Too many persona categories in nav (5+ creates its own decision paralysis)
- Not testing whether visitors actually identify with the persona labels used

**Sequencing notes:** Structural change. Plan for longer implementation timeline. Results inform all page-level messaging experiments (if persona nav works, each persona page becomes its own testing surface).

---

### NX-02: CTA Clarity and Hierarchy

**Category:** Navigation/UX Flow
**Applies when:**
- Page has multiple competing CTAs with similar visual weight
- Primary CTA uses vague language ("Learn More," "Get Started," "Contact Us")
- Positioning scorecard rates Clarity as "Needs Work" (CTA ambiguity is a clarity symptom)

**Typical test:** Establish single primary CTA with specific outcome language ("See Pricing," "Book a 15-min Demo," "Get Your Audit"). Demote secondary CTAs visually.

**Causal mechanism:** Hick's Law: decision time increases logarithmically with the number of choices. Multiple equal-weight CTAs create decision paralysis. A single, specific CTA reduces cognitive load. Specific language ("Book a 15-min Demo") also sets expectations, reducing the fear of unknown commitment that vague CTAs ("Contact Us") create.

**ICE baseline:** Impact 6 | Confidence 8 | Ease 8
**Modifiers:**
- Impact +2 if page has 3+ CTAs of equal visual prominence
- Confidence +1 if A/B testing platform already configured on the page
- Impact +1 if CTA change addresses the primary conversion action (not a secondary engagement)

**Common mistakes:**
- Making the CTA specific but not matching what happens next ("Book a 15-min Demo" that leads to a generic "Contact Us" form destroys trust)
- Demoting secondary CTAs so aggressively that visitors who aren't ready for the primary CTA have no path forward
- Specific but jargon-heavy CTAs ("Request an Enterprise POV") that only insiders understand

**Sequencing notes:** Quick implementation. Pairs well with HM-01 (clarity at headline level + CTA level). Run after headline test if both are identified, so CTA copy aligns with winning headline direction.

---

### NX-03: Exit Path Optimization

**Category:** Navigation/UX Flow
**Applies when:**
- High-traffic page with significant drop-off
- No secondary conversion path for visitors who aren't ready for the primary CTA
- Audience-messaging identifies a content or resource offer that could serve as a lower-commitment entry point

**Typical test:** Add a lower-commitment secondary CTA (content offer, newsletter, ROI calculator) for visitors who scroll past the primary CTA or show exit intent.

**Causal mechanism:** Not every visitor is ready to buy, demo, or talk to sales. Offering a lower-commitment action captures visitors who are interested but not ready, moving them into a nurture path instead of losing them entirely. The secondary offer acts as a safety net for the conversion funnel.

**ICE baseline:** Impact 5 | Confidence 6 | Ease 6
**Modifiers:**
- Impact +3 if page traffic is high and primary conversion rate is <1%
- Ease +2 if exit-intent tooling already deployed
- Confidence +1 if the secondary offer already exists (content, calculator, etc.) and just needs placement

**Common mistakes:**
- Making the secondary offer so compelling it cannibalizes primary conversions (the secondary should feel like a consolation, not a better deal)
- Triggering exit-intent popups too aggressively (immediately on page load, multiple times per session)
- Secondary offer that doesn't relate to the page's topic (generic newsletter popup on a pricing page)

**Sequencing notes:** Run after primary CTA experiments (NX-02). You want to optimize the primary path first, then add the safety net.

---

## Category: Personalization

### PE-01: Segment-Based Hero Personalization

**Category:** Personalization
**Applies when:**
- Audience-messaging identifies 2+ personas with distinct primary value propositions
- Site serves a single generic hero experience to all traffic regardless of segment
- Positioning scorecard rates Specificity as "Needs Work" or "Missing"

**Typical test:** Serve persona-matched hero copy (headline, subhead, CTA) based on available signal: UTM parameters, referral source, industry via reverse IP, or self-selection modal.

**Causal mechanism:** Relevance drives conversion. A CFO and a VP of Engineering visit the same homepage but evaluate through completely different lenses. The CFO cares about ROI and risk reduction. The VP of Engineering cares about integration complexity and team adoption. Matching the opening message to their frame reduces cognitive distance between "this page exists" and "this page is for me."

**ICE baseline:** Impact 9 | Confidence 5 | Ease 3
**Modifiers:**
- Confidence +3 if traffic segments are identifiable via existing UTM structure or ad campaign segmentation
- Ease +3 if the testing/personalization platform supports audience targeting natively (Optimizely, VWO, etc.)
- Ease -4 if no personalization infrastructure exists and this would be the first implementation
- Confidence -2 if personas are loosely defined (only 2 personas with overlapping challenges)

**Common mistakes:**
- Personalizing the headline but leaving everything else generic, creating a jarring relevance mismatch below the fold
- Over-segmenting with too little traffic per variant (need statistical significance for each segment)
- Assuming segment detection is accurate (reverse IP is ~60-70% reliable; UTMs depend on campaign discipline)

**Sequencing notes:** High effort, high reward. Run after headline clarity and CTA experiments establish the baseline. Personalization builds on proven messaging, not untested copy.

---

### PE-02: Industry/Vertical Social Proof Matching

**Category:** Personalization
**Applies when:**
- Company has customers across multiple industries (visible in L0 proof point registry)
- Social proof (logos, testimonials, case studies) is displayed generically regardless of visitor segment
- At least 3 proof points per target vertical exist in the proof point registry

**Typical test:** Match displayed social proof to visitor's industry based on available signal (UTM, IP lookup, self-selection, ad source).

**Causal mechanism:** "Companies like mine use this" is a stronger trust signal than "companies use this." Industry-matched proof reduces perceived risk by making the buyer's context feel understood. A fintech buyer seeing fintech logos and a fintech case study gets implicit validation that the product handles their specific regulatory and scaling challenges.

**ICE baseline:** Impact 7 | Confidence 6 | Ease 4
**Modifiers:**
- Confidence +2 if company has 3+ case studies per target vertical
- Ease +3 if CMS supports dynamic content blocks or personalization rules
- Confidence -2 if proof points are only "claimed" strength (logos without testimonials)
- Impact -1 if the company operates in a single vertical (personalization adds no differentiation)

**Common mistakes:**
- Only having 1-2 customers in a vertical and personalizing anyway, which looks thin instead of impressive
- Minimum threshold: 3 logos or 1 strong case study per segment before enabling
- Matching industry but not company size (showing enterprise logos to SMB visitors can backfire)

**Sequencing notes:** Requires personalization infrastructure. If PE-01 is implemented, add industry proof matching as an extension of the same system. Don't build separate infrastructure for each.

---

## Category: Page Structure/Layout

### PS-01: Above-the-Fold Hierarchy Reset

**Category:** Page Structure/Layout
**Applies when:**
- Homepage or key landing page leads with feature list, product screenshot, or navigation-heavy layout instead of clear value prop + single CTA
- Positioning scorecard rates Clarity as "Needs Work" or "Missing"
- The above-the-fold experience doesn't answer "what does this company do and why should I care?" within 5 seconds

**Typical test:** Restructure above-the-fold to: headline (outcome) + subhead (how) + single primary CTA + trust signal. Push feature details, product tours, and secondary content below fold.

**Causal mechanism:** B2B buyers arrive with a question: "Is this for me?" Feature-first layouts answer a different question: "What does it do?" The hierarchy should match the buyer's decision sequence. Relevance first (am I in the right place?), then capability (what does it do?), then proof (can I trust this?). Violating this sequence forces visitors to work backward through the page to answer their first question.

**ICE baseline:** Impact 8 | Confidence 6 | Ease 5
**Modifiers:**
- Impact +2 if current bounce rate >60% (suggests visitors aren't finding relevance quickly)
- Ease -3 if page is template-locked in CMS or requires developer involvement for layout changes
- Confidence +1 if audience-messaging provides a clear primary message hierarchy to implement

**Common mistakes:**
- Moving features below fold but replacing with vague aspirational copy instead of specific outcomes
- Removing all visual product cues, which hurts credibility for technical buyers who want to see the product
- Over-simplifying: a single headline and CTA with nothing else above the fold can feel empty on desktop

**Sequencing notes:** Structural change. Higher effort than copy-only experiments. Run HM-01 first to validate the right headline, then restructure the page around the winning message.

---

### PS-02: Long-Form vs. Short-Form Page Test

**Category:** Page Structure/Layout
**Applies when:**
- Key conversion page is either very long (scrolling fatigue observed or inferred) or very short (insufficient information for B2B decision-making complexity)
- Page serves both early-funnel (exploring) and late-funnel (ready to act) visitors

**Typical test:** If currently long: test a condensed version with progressive disclosure (expandable sections, tabs, or anchor links). If currently short: test adding proof sections, objection handling, comparison tables, and implementation details below the fold.

**Causal mechanism:** B2B purchase decisions involve multiple stakeholders and higher risk than B2C. Short pages often under-serve the "convince my boss" use case: the champion who needs ammunition to sell internally. Overly long pages lose the already-convinced buyer who just wants to find the CTA. The test reveals which audience dominates and what information architecture serves both.

**ICE baseline:** Impact 6 | Confidence 5 | Ease 4
**Modifiers:**
- Confidence +2 if scroll depth data is available (confirms whether visitors engage with or abandon long content)
- Impact +2 if page serves both early and late funnel traffic (validated by mixed-intent traffic sources)
- Ease -2 if the change requires significant content creation (not just restructuring existing content)

**Common mistakes:**
- Treating page length as the variable when the real issue is information architecture (a long page with clear sections outperforms a short page missing critical info)
- Removing content without understanding what the page needs to accomplish for different visitors
- Not measuring scroll depth or section engagement, which makes the results uninterpretable

**Sequencing notes:** Run after higher-confidence copy and CTA experiments. This is a bigger structural bet with more implementation effort and less predictable results.

---

## Category: Pricing

### PZ-01: Pricing Transparency Test

**Category:** Pricing
**Applies when:**
- Competitive landscape shows competitors publish pricing and the target company doesn't (or vice versa)
- "Contact us for pricing" or no pricing page exists
- Positioning scorecard indicates Specificity gap related to pricing or purchase evaluation

**Typical test:** Add pricing indicator (starting-at price, price range, tier comparison, or full transparency) to pricing page. If no pricing page exists, create one. Test against the current "contact us" approach.

**Causal mechanism:** B2B buyers increasingly self-serve through the evaluation process. Hiding pricing creates friction: the buyer can't assess fit without talking to sales, which many buyers (especially technical evaluators) resist. Competitors who publish pricing gain an evaluation advantage. Conversely, transparent pricing anchors expectations and filters unqualified leads, improving sales efficiency.

**ICE baseline:** Impact 8 | Confidence 4 | Ease 6
**Modifiers:**
- Confidence +3 if competitors already publish pricing and the company is losing on "ease of evaluation" signals
- Impact -2 if deal sizes are highly variable (enterprise custom pricing is legitimately hard to publish)
- Ease -2 if pricing requires internal stakeholder alignment before publishing
- Confidence +1 if company has clear tiers or packages that map to published pricing

**Common mistakes:**
- Publishing pricing without anchoring to value (raw numbers without context invite unfavorable comparison)
- Pricing page that lists numbers but doesn't explain what each tier includes or who it's for
- Not testing partial transparency (price ranges or "starting at") as a middle ground

**Sequencing notes:** Often politically sensitive internally. May require stakeholder buy-in before testing. Flag this as needing business discussion, not just CRO decision. If approved, run early because results significantly inform competitive positioning.

---

## Extending This Library

New patterns can be added following the schema above. Each pattern must have:
1. At least one trigger condition that can be evaluated from context files
2. A causal mechanism grounded in behavioral science, UX principles, or established CRO methodology
3. ICE baselines and at least 2 modifiers
4. At least 2 common mistakes
5. Sequencing notes

Patterns without all five components are drafts and should not be matched during opportunity detection.
