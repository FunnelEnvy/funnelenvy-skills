# Experiment Patterns Library

Version: 1.1.0
Last updated: 2026-02-22
Pattern count: 26
Categories: 9

This module contains the CRO experiment patterns that drive the hypothesis generator. Each pattern encodes a testable opportunity type, its trigger conditions, causal reasoning, ICE baselines, and contextual modifiers.

The hypothesis generator matches signals from context files against the "Applies when" trigger conditions. When a match is found, the pattern provides the reasoning framework for constructing and scoring the hypothesis.

---

## Pattern Schema

Each pattern follows this structure:

- **Pattern ID:** Category prefix + number (e.g., HM-01). Internal reference only. Never appears in deliverables.
- **Category:** One of: Headline/Messaging, Form Optimization, Navigation/UX, Personalization, Page Structure/Layout, Pricing, Social Proof, Content/Resource, Trust/Credibility
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

**ICE baseline:** Impact 4 | Confidence 4 | Ease 5
**Modifiers:**
- Confidence +1 if audience-messaging provides specific channel adaptation for homepage
- Confidence -1 if no exact current headline copy available in context
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

**ICE baseline:** Impact 3 | Confidence 4 | Ease 5
**Modifiers:**
- Impact +1 if the company has "verified" proof points (named customer + metric) not currently displayed on the page
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

**ICE baseline:** Impact 4 | Confidence 4 | Ease 4
**Modifiers:**
- Confidence -2 if form is for high-intent action (demo request, consultation) where qualification matters more
- Impact +1 if mobile traffic represents >40% of page visits
- Ease -1 if form is embedded third-party (Marketo, HubSpot) with limited field customization
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

**ICE baseline:** Impact 4 | Confidence 4 | Ease 3
**Modifiers:**
- Ease -2 if form is embedded third-party with limited step/flow customization
- Confidence +1 if baseline form abandonment data is available
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

**ICE baseline:** Impact 3 | Confidence 4 | Ease 5
**Modifiers:**
- Impact +2 if form is for high-commitment action (demo, consultation) where the ask feels larger
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

**ICE baseline:** Impact 4 | Confidence 3 | Ease 2
**Modifiers:**
- Confidence +1 if analytics show high bounce from current navigation pages
- Ease -1 if CMS doesn't support dynamic navigation or dropdown customization
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

**ICE baseline:** Impact 3 | Confidence 4 | Ease 4
**Modifiers:**
- Impact +1 if page has 3+ CTAs of equal visual prominence
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

**ICE baseline:** Impact 3 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +2 if page traffic is high and primary conversion rate is <1%
- Ease +1 if exit-intent tooling already deployed
- Confidence +1 if the secondary offer already exists (content, calculator, etc.) and just needs placement

**Common mistakes:**
- Making the secondary offer so compelling it cannibalizes primary conversions (the secondary should feel like a consolation, not a better deal)
- Triggering exit-intent popups too aggressively (immediately on page load, multiple times per session)
- Secondary offer that doesn't relate to the page's topic (generic newsletter popup on a pricing page)

**Sequencing notes:** Run after primary CTA experiments (NX-02). You want to optimize the primary path first, then add the safety net.

---

### NX-04: Paid Landing Page Optimization

**Category:** Navigation/UX Flow
**Applies when:**
- Performance-profile shows significant paid traffic to a page (>200 sessions/mo from paid channels)
- Channel-specific bounce rate gap exists (paid bounces higher than organic on same page)
- Page has full site navigation (not a dedicated landing page)
- No dedicated landing pages exist for paid campaigns (all traffic goes to site pages)

**Typical test:** Create a paid-traffic variant with (a) headline/visual/offer aligned to the ad creative that drives traffic, and (b) navigation stripped to a single conversion path. Test against the current generic page experience for paid visitors only.

**Causal mechanism:** Paid visitors arrive with a specific expectation set by the ad. Two things break that expectation simultaneously: the page headline doesn't echo the ad's promise (cognitive dissonance at arrival), and full site navigation offers escape routes before the value proposition lands. Each nav link is a competing CTA with zero conversion intent. Aligning the message and removing distractions focuses attention on the single conversion path the ad directed them toward.

**ICE baseline:** Impact 4 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +1 if paid spend on the page exceeds $5K/mo (high waste on mismatch)
- Confidence +2 if channel-specific bounce gap is >10pp (paid vs organic on same page)
- Ease +1 if testing platform supports audience targeting by UTM/traffic source
- Ease -1 if multiple ad campaigns with different messaging point to the same page (need multiple variants)
- Confidence +1 if testing both message match AND nav removal together vs. just one

**Common mistakes:**
- Matching the ad headline verbatim instead of matching the promise (the landing page should deliver on the ad's implied value, not parrot its exact words)
- Removing navigation on pages that also receive significant organic traffic without using audience targeting to scope the variant to paid only
- Ignoring that different ad campaigns set different expectations -- one landing page variant won't fix message match if 5 different ads point to it

**Sequencing notes:** Run after baseline CTA experiments (NX-02). Requires audience targeting capability in the testing platform. If platform can't target by traffic source, this test is infeasible.

---

### NX-05: Value-Before-Commitment Sequencing

**Category:** Navigation/UX Flow
**Applies when:**
- Primary CTA requires commitment before showing value (demo request, contact sales, signup)
- Product has demonstrable value that could be previewed (interactive demo, sample output, sandbox)
- Competitive landscape shows competitors offering self-serve evaluation paths

**Typical test:** Add a value-preview step before the primary conversion action: interactive product demo, sample output generator, sandbox environment, or video walkthrough. The preview replaces or precedes the gate, not supplements it below the fold.

**Causal mechanism:** Commitment before value creates an information asymmetry the buyer resists. They must invest (time, personal info, social commitment of a sales call) without knowing what they'll get. Reversing the sequence (value first, commitment second) reduces perceived risk. The endowment effect then works in your favor: once they've experienced the product, they value it more and the commitment feels smaller relative to what they've already seen.

**ICE baseline:** Impact 5 | Confidence 3 | Ease 2
**Modifiers:**
- Impact +1 if competitors already offer self-serve evaluation and company doesn't
- Confidence +1 if the company has an existing demo environment or sandbox that could be exposed
- Ease +2 if an interactive demo tool (Navattic, Reprise, Storylane) is already in use
- Ease -2 if no demo/preview asset exists and one must be built from scratch
- Confidence -1 if the product is complex enough that unsupported evaluation could confuse buyers

**Common mistakes:**
- Offering a "preview" that's actually a marketing video, not a hands-on experience (doesn't trigger the endowment effect)
- Gating the preview itself behind a form, defeating the entire purpose
- Preview that shows features without connecting to the visitor's specific use case (generic sandbox vs. guided scenario)

**Sequencing notes:** High effort, high reward. Requires a value-preview asset to exist or be buildable. Run after messaging and CTA experiments have established baseline conversion. This is a structural change that's hard to reverse, so validate messaging first.

---

### NX-06: Comparison-Mode Intervention

**Category:** Navigation/UX Flow
**Applies when:**
- Performance-profile shows meaningful segment of visitors with 5+ pages/session
- No comparison or evaluation content is surfaced contextually during browsing
- Exit-intent or time-based popups are the only current intervention (or none)

**Typical test:** Deploy a session-depth-triggered offer (comparison guide, ROI calculator, analyst report, "been researching?" prompt) that fires after the 5th pageview. Target the offer to the visitor's demonstrated behavior rather than using a generic popup.

**Causal mechanism:** Page-count correlates with evaluation intent. A visitor on their 5th page has demonstrated sustained interest but hasn't converted -- they're likely comparing options or building an internal case. An offer tailored to comparison behavior (side-by-side guide, "still evaluating?" prompt, ROI calculator) meets the visitor's actual mental state. Time-based or exit-intent triggers fire without regard to engagement depth, which means they interrupt casual browsers and miss deep evaluators equally.

**ICE baseline:** Impact 3 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +2 if 5+ pages/session segment is >15% of total sessions
- Confidence +1 if the comparison/evaluation asset already exists (just needs a trigger)
- Ease +1 if popup/overlay tooling is already deployed on the site
- Confidence +1 if session-depth segment includes visits to pricing page (strong evaluation signal)
- Confidence -1 if high pages/session is driven by blog content (reading, not evaluating)

**Common mistakes:**
- Setting the threshold too low (3 pages) and triggering on casual browsers who just clicked around
- Using a generic "sign up for newsletter" offer when the visitor is clearly deeper in the funnel
- Firing the same offer regardless of which pages were visited (someone who read 5 blog posts needs different content than someone who visited pricing + 4 product pages)

**Sequencing notes:** Low effort if popup tooling exists. Run independently of page-level experiments. Does not compete with or depend on NX-03 (exit path optimization) since NX-03 targets on-page secondary CTAs while this targets session-level behavioral triggers.

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

**ICE baseline:** Impact 5 | Confidence 3 | Ease 2
**Modifiers:**
- Confidence +2 if traffic segments are identifiable via existing UTM structure or ad campaign segmentation
- Ease +2 if the testing/personalization platform supports audience targeting natively (Optimizely, VWO, etc.)
- Ease -2 if no personalization infrastructure exists and this would be the first implementation
- Confidence -1 if personas are loosely defined (only 2 personas with overlapping challenges)

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

**ICE baseline:** Impact 4 | Confidence 3 | Ease 2
**Modifiers:**
- Confidence +1 if company has 3+ case studies per target vertical
- Ease +2 if CMS supports dynamic content blocks or personalization rules
- Confidence -1 if proof points are only "claimed" strength (logos without testimonials)
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

**ICE baseline:** Impact 4 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +1 if current bounce rate >60% (suggests visitors aren't finding relevance quickly)
- Ease -2 if page is template-locked in CMS or requires developer involvement for layout changes
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

**ICE baseline:** Impact 3 | Confidence 3 | Ease 2
**Modifiers:**
- Confidence +1 if scroll depth data is available (confirms whether visitors engage with or abandon long content)
- Impact +1 if page serves both early and late funnel traffic (validated by mixed-intent traffic sources)
- Ease -1 if the change requires significant content creation (not just restructuring existing content)

**Common mistakes:**
- Treating page length as the variable when the real issue is information architecture (a long page with clear sections outperforms a short page missing critical info)
- Removing content without understanding what the page needs to accomplish for different visitors
- Not measuring scroll depth or section engagement, which makes the results uninterpretable

**Sequencing notes:** Run after higher-confidence copy and CTA experiments. This is a bigger structural bet with more implementation effort and less predictable results.

---

### PS-03: About Page Proof Hierarchy

**Category:** Page Structure/Layout
**Applies when:**
- About page leads with mission, vision, or values statements instead of proof of capability
- Culture metrics, quality claims, or team credentials are buried below fold or in secondary sections
- Positioning scorecard rates Proof as "Needs Work" and strongest proof points (from L0 registry) don't appear until deep into the page

**Typical test:** Restructure the About page to lead with the strongest proof: quantified outcomes, named customers, team credentials, industry recognition. Push mission/vision/values to a secondary position below the proof section.

**Causal mechanism:** Visitors reaching the About page are evaluating trust, not seeking inspiration. They want to know "can this company actually deliver?" Mission statements answer a question nobody on the About page is asking. Leading with proof (team expertise, client outcomes, industry recognition) directly addresses the trust evaluation. Culture and mission provide context after trust is established, not before.

**ICE baseline:** Impact 3 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +1 if About page is in the top 5 most-visited pages (common for services companies)
- Confidence +1 if L0 proof registry has 3+ "verified" proof points not currently on the About page
- Ease +1 if the change is primarily content reordering rather than new content creation
- Confidence -1 if current About page layout can't be confirmed from context

**Common mistakes:**
- Removing mission/values entirely instead of repositioning them (some visitors do care, just not first)
- Leading with logos only instead of substantive proof (logos without context are weak signals)

**Sequencing notes:** Independent of homepage experiments. Can run in parallel with HM-01/HM-02 since it targets a different page. Complements SP-03 (Proof Hierarchy Restructure) if applied to the same page.

---

### PS-04: Service Page Differentiation Injection

**Category:** Page Structure/Layout
**Applies when:**
- Service or product pages describe capabilities without differentiating from competitors
- Competitive landscape shows claim overlap on specific services or feature categories
- Service page copy reads generically: could belong to any competitor in the space

**Typical test:** Add differentiation-specific content blocks to service pages: unique methodology callouts, comparison data points, specific proof from that service area. Position these where the page currently describes generic capabilities.

**Causal mechanism:** B2B buyers evaluating service pages are in comparison mode. They're looking at 3-5 similar companies and reading through similar service descriptions. When every vendor's service page says "we help you [outcome]," none stands out. Injecting specific differentiators (unique process steps, metrics from that service area, competitive advantages) gives the comparison-mode buyer a reason to remember this vendor. The differentiation breaks pattern and creates a mental anchor.

**ICE baseline:** Impact 3 | Confidence 3 | Ease 4
**Modifiers:**
- Impact +1 if competitive landscape identifies high claim overlap in the specific service area
- Confidence +1 if audience-messaging provides service-specific channel adaptations
- Confidence -1 if differentiators for this service area are only "claimed" not "verified"
- Impact -1 if service page traffic is low relative to homepage

**Common mistakes:**
- Adding differentiation that's actually a commodity feature everyone has (research competitor pages first)
- Differentiating on process details that buyers don't evaluate at this stage (implementation methodology on an awareness-stage page)

**Sequencing notes:** Run after homepage messaging tests (HM-01/HM-02) establish the positioning direction. Service page differentiation should extend the winning homepage message into specific service contexts.

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

**ICE baseline:** Impact 4 | Confidence 2 | Ease 3
**Modifiers:**
- Confidence +2 if competitors already publish pricing and the company is losing on "ease of evaluation" signals
- Impact -1 if deal sizes are highly variable (enterprise custom pricing is legitimately hard to publish)
- Ease -1 if pricing requires internal stakeholder alignment before publishing
- Confidence +1 if company has clear tiers or packages that map to published pricing
- Confidence +1 if testing discount/savings framing and Rule of 100 is applied (percentage for <$100, absolute for >$100)

**Common mistakes:**
- Publishing pricing without anchoring to value (raw numbers without context invite unfavorable comparison)
- Pricing page that lists numbers but doesn't explain what each tier includes or who it's for
- Not testing partial transparency (price ranges or "starting at") as a middle ground
- Showing percentage savings for high-ticket products (>$100/mo) when absolute savings would feel larger, or vice versa (Rule of 100: percentages feel bigger under $100, absolutes feel bigger over $100)

**Sequencing notes:** Often politically sensitive internally. May require stakeholder buy-in before testing. Flag this as needing business discussion, not just CRO decision. If approved, run early because results significantly inform competitive positioning.

---

## Category: Social Proof

### SP-01: Testimonial Format Optimization

**Category:** Social Proof
**Applies when:**
- Testimonials exist in L0 proof registry but are displayed as text-only blocks without attribution context (no photo, no title, no company, no metric)
- Testimonial content is generic ("great product") rather than outcome-specific
- Testimonials are present but don't match the page's target persona or use case

**Typical test:** Upgrade testimonial format to include full attribution (name, title, company, photo), outcome-specific pull quotes, and persona-page matching. If testimonials are outcome-specific, test structured format (metric + quote + attribution) vs. current text block.

**Causal mechanism:** Testimonials work through social proof and identification: "someone like me got results like this." Text-only testimonials without attribution context strip the identification signal. The reader can't evaluate "is this person like me?" without role, company type, and context. Adding attribution context transforms a generic endorsement into a credibility signal the reader can evaluate against their own situation.

**ICE baseline:** Impact 3 | Confidence 4 | Ease 4
**Modifiers:**
- Impact +1 if testimonials appear on high-intent pages (pricing, demo request)
- Confidence +1 if L0 proof registry has testimonials with named customers and metrics available
- Ease -1 if testimonial content needs to be collected/updated (not just reformatted)
- Confidence -1 if current testimonial display format can't be confirmed from context

**Common mistakes:**
- Using stock photos instead of real customer photos (destroys credibility if detected)
- Placing testimonials from irrelevant industries on segment-specific pages

**Sequencing notes:** Low effort, independent of most other experiments. Can run in parallel with headline or CTA tests on different page sections.

---

### SP-02: Case Study Structure Test

**Category:** Social Proof
**Applies when:**
- Case studies exist but use a generic format: no before/after metrics, no timeline, no specific challenge/solution structure
- Case studies exist but aren't surfaced on high-traffic pages (buried in a resources section)
- L0 proof registry has "verified" outcomes that could be structured as case studies but aren't

**Typical test:** Two variants. Variant A: restructure case studies into a challenge/approach/results format with quantified before/after metrics and timeline. Variant B: surface case study summaries (metric + company + one-line result) on high-traffic pages as proof strips.

**Causal mechanism:** Case studies serve two distinct functions: deep validation (for champions building internal cases) and social proof signals (for early evaluators scanning the site). Generic case studies fail at both: they don't provide the specific metrics a champion needs, and they don't create scannable proof signals for casual visitors. Structured format with quantified results serves the champion. Surface-level proof strips serve the scanner. Testing both identifies which audience drives more conversion.

**ICE baseline:** Impact 3 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +1 if case studies include named enterprise customers (stronger brand association)
- Confidence +1 if before/after metrics are available in L0 proof registry
- Ease -1 if case studies need to be rewritten (not just reformatted)
- Ease +1 if surfacing existing case study data on new pages (no content creation needed)

**Common mistakes:**
- Publishing case studies with vague results ("significant improvement") instead of waiting for specific metrics
- Case study subjects that don't match the target persona profile (enterprise case studies for SMB-focused pages)

**Sequencing notes:** Independent of copy experiments. Pairs well with CR-02 (ROI Evidence Integration) if both are identified. Run case study restructuring before evidence strip tests to ensure the underlying content is strong.

---

### SP-03: Proof Hierarchy Restructure

**Category:** Social Proof
**Applies when:**
- Proof points of different strengths are mixed together on key pages (verified metrics next to generic logos next to unattributed quotes)
- Strongest proof (named customer outcomes, quantified metrics) is buried below weaker proof (generic logos, partner badges, certification icons)
- L0 proof registry shows a range of proof strengths but the site doesn't differentiate between them visually or positionally

**Typical test:** Reorder proof sections on key pages to lead with the strongest evidence first. Structure: quantified outcomes at top, then named customer testimonials, then logos, then certifications/badges. Apply consistent visual treatment that signals proof hierarchy (larger format for stronger proof, smaller for weaker).

**Causal mechanism:** Not all proof is created equal. A case study showing "340% ROI in 6 months" is categorically stronger than a logo wall. But when both are displayed at the same visual weight and the logo wall appears first, the visitor's trust evaluation anchors on the weaker signal. Leading with the strongest proof sets a high trust anchor. Subsequent weaker proof then reinforces rather than dilutes. The hierarchy matches the visitor's need: "show me your best evidence first."

**ICE baseline:** Impact 3 | Confidence 4 | Ease 4
**Modifiers:**
- Impact +1 if the page is homepage or pricing page (highest-stakes trust evaluation)
- Confidence +1 if L0 proof registry has 3+ "verified" proof points with clear strength differentiation
- Ease +1 if change is primarily reordering existing elements (no new content)
- Impact -1 if the page already leads with strongest proof (reordering provides minimal lift)

**Common mistakes:**
- Removing weaker proof entirely instead of repositioning it (quantity of proof still matters, just not as much as quality)
- Treating all logos as equal (a Fortune 500 logo is stronger proof than an unknown startup logo)

**Sequencing notes:** Low effort, high learning value. Run early. Results inform how to position proof in all future experiments (headline tests, form context, case study placement).

---

## Category: Content/Resource

### CR-01: Competitive Comparison Page

**Category:** Content/Resource
**Applies when:**
- Competitive landscape identifies 3+ direct competitors
- No comparison or "vs." page exists on the company's site
- White spaces or unique differentiators are identified that could be highlighted in a comparison format
- Competitors have comparison pages that include the target company (defensive motivation)

**Typical test:** Create a comparison page showing the target company vs. top 2-3 competitors on key evaluation criteria. Lead with dimensions where the company wins. Include honest "where they're stronger" sections (builds credibility). Link from relevant service pages and consider paid search targeting "[Competitor] alternative" keywords.

**Causal mechanism:** B2B buyers actively compare vendors. If the company doesn't provide a comparison, buyers build their own from competitor sites and review platforms, where the company has no control over framing. A comparison page created by the company controls the evaluation criteria: it anchors the comparison on dimensions where the company is strongest. Honest inclusion of competitor advantages paradoxically builds trust (the company is confident enough to show the full picture).

**ICE baseline:** Impact 4 | Confidence 3 | Ease 2
**Modifiers:**
- Impact +1 if "[Company] vs [Competitor]" search volume exists or competitors already have comparison pages
- Confidence +1 if competitive landscape provides clear, verifiable differentiators for the comparison
- Ease -1 if comparison requires ongoing maintenance as competitors change
- Confidence -1 if differentiators are mostly "claimed" without verified proof

**Common mistakes:**
- Making the comparison page obviously biased (green checks for us, red X's for them on every dimension)
- Including competitors who aren't actual alternatives for the same buyer (creates false competitive frame)
- Not updating the page when competitors ship new features or change pricing

**Sequencing notes:** Higher effort (new page creation). Run after positioning fundamentals (HM-01, HM-02) establish the value prop direction. The comparison page should extend proven messaging, not test new positioning.

---

### CR-02: ROI Evidence Integration

**Category:** Content/Resource
**Applies when:**
- L0 proof registry has verified quantified outcomes (revenue impact, time saved, efficiency gains) not displayed on high-traffic pages
- Quantified ROI is identified as a top proof gap in positioning scorecard
- Competitors lead with ROI claims and the target company has evidence but doesn't surface it

**Typical test:** Two variants with different effort levels. Variant A (high ease): Add an evidence strip to high-traffic pages showing 3-4 quantified outcomes in a scannable format (metric + context, e.g., "340% ROI in 6 months - [Customer Name]"). Variant B (low ease): Build an interactive ROI calculator that uses company benchmarks to project value for the visitor's specific situation.

**Causal mechanism:** B2B purchase decisions involve financial justification. The champion needs ammunition to present ROI to decision-makers. If ROI evidence exists but isn't surfaced prominently, the champion has to dig for it or request it from sales. Surfacing quantified outcomes on high-traffic pages serves two purposes: it provides the champion with shareable proof, and it signals to early evaluators that the company can quantify its value (which many competitors can't or won't do).

**ICE baseline (Variant A):** Impact 4 | Confidence 3 | Ease 4
**ICE baseline (Variant B):** Impact 4 | Confidence 3 | Ease 2
**Modifiers:**
- Impact +1 if ROI evidence is available but completely absent from the current site
- Confidence +1 if proof points include named customers (not anonymized)
- Ease -1 for Variant B if calculator requires custom engineering
- Confidence -1 if ROI metrics are from a single customer (not generalizable)

**Common mistakes:**
- Displaying ROI numbers without customer context (unattributed numbers feel fabricated)
- ROI calculator that produces implausibly high numbers (destroys credibility)
- Using averages across very different customer segments (enterprise ROI shown to SMB visitors)

**Sequencing notes:** Variant A (evidence strip) can run early and in parallel with copy experiments. Variant B (calculator) is a Strategic Bet: higher effort, higher payoff. Start with Variant A to validate that ROI evidence resonates before investing in the calculator.

---

### CR-03: Assessment / Diagnostic Tool

**Category:** Content/Resource
**Applies when:**
- Company serves multiple segments with different needs and no self-service qualification mechanism exists
- 2+ personas identified with distinct entry points and evaluation criteria
- Site lacks interactive content that helps visitors self-identify their situation before engaging sales

**Typical test:** Build a short diagnostic (5-7 questions) that helps visitors identify their situation, maturity level, or fit. Output a personalized recommendation: which service/product tier fits, what outcomes to expect, suggested next step. Gate the detailed results behind email capture.

**Causal mechanism:** Visitors who don't know which product or service fits their situation face a classification problem before they face an evaluation problem. They need to figure out "what do I need?" before "is this company the right choice?" A diagnostic tool solves the classification problem, positioning the company as an expert guide. The email gate on detailed results converts the visitor at a moment of peak engagement (they've invested effort and want their answer). The diagnostic data also enriches the sales team's understanding of the lead.

**ICE baseline:** Impact 3 | Confidence 2 | Ease 2
**Modifiers:**
- Impact +1 if the company serves 3+ distinct segments with different product/service fit
- Confidence +1 if audience-messaging has well-defined personas with distinct challenges
- Ease -1 if diagnostic requires custom development (no quiz/assessment tool in stack)
- Ease +1 if the company already uses a quiz or assessment platform

**Common mistakes:**
- Making the diagnostic too long (>10 questions creates abandonment)
- Results that are too generic to feel personalized (the whole point is specificity)
- Not using diagnostic responses to inform sales follow-up (wasted data)

**Sequencing notes:** High effort, exploration-tier. Run after simpler experiments validate messaging direction. The diagnostic content should reflect proven positioning, not untested messaging.

---

## Category: Trust/Credibility

### TC-01: Team Credibility Surface

**Category:** Trust/Credibility
**Applies when:**
- Talent quality or team expertise is claimed as a differentiator in L0 but the team page is generic, missing, or lacks credentials
- Competitive landscape shows competitors with stronger team pages (detailed bios, credentials, thought leadership links)
- The company sells expertise-dependent services (consulting, professional services, implementation) where buyer confidence in the team matters

**Typical test:** Upgrade team page or create team credibility sections on service pages. Include specific credentials (years of experience, certifications, notable prior work), thought leadership links, and specialization areas. Test full team page redesign vs. team credibility strip on service pages.

**Causal mechanism:** For services companies, the team IS the product. Buyers are purchasing the judgment and expertise of the people who will work on their account. A generic team page ("Meet our passionate team") provides zero signal about capability. Specific credentials (ex-Google, 15 years in fintech, published researcher) activate authority bias: the buyer infers capability from verifiable expertise markers. The stronger the credentials displayed, the lower the perceived risk of engagement.

**ICE baseline:** Impact 3 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +1 if the company sells high-ticket services where team quality is the primary differentiator
- Confidence +1 if L0 explicitly lists team credentials or expertise claims
- Ease +1 if team information exists internally and just needs to be surfaced on the site
- Ease -1 if team members need to be photographed, interviewed, or profiled from scratch

**Common mistakes:**
- Using stock photos or AI-generated headshots (immediately destroys trust if detected)
- Listing credentials without connecting them to client value (impressive resume that doesn't explain how it helps the buyer)

**Sequencing notes:** Independent of homepage messaging experiments. Can run in parallel on team/about pages. Pairs with PS-03 (About Page Proof Hierarchy) for a combined about page restructure.

---

### TC-02: Objection Preemption Page

**Category:** Trust/Credibility
**Applies when:**
- Competitive landscape identifies a structural objection or "when we lose" scenario (e.g., "too expensive," "too small," "no enterprise features") with no rebuttal content on the site
- Audience-messaging identifies recurring objections in the decision process
- Company's FAQ or objection handling is buried, generic, or missing from the main navigation flow

**Typical test:** Create dedicated content addressing the top 1-2 structural objections. This could be a standalone page ("Is [Company] right for you?"), an FAQ section on the pricing page addressing cost objections, or a "How we compare" section addressing capability objections. Test placement on high-intent pages where the objection is most likely to block conversion.

**Causal mechanism:** Unanswered objections don't disappear; they become reasons to choose a competitor. When a buyer encounters a structural objection ("this seems expensive for what it is") and finds no counter-narrative on the site, they either leave or carry the objection into the sales process where it's harder to overcome. Proactive objection preemption reframes the concern before it solidifies: "Yes, our price is higher because [specific value justification]." This is loss aversion in reverse: showing what the buyer loses by choosing the cheaper option.

**ICE baseline:** Impact 4 | Confidence 3 | Ease 3
**Modifiers:**
- Impact +1 if the objection is identified as the primary "when we lose" reason in competitive landscape
- Confidence +1 if the company has specific evidence or case studies that directly address the objection
- Ease +1 if the content can be added to an existing page (FAQ section, pricing page sidebar) rather than a new page
- Confidence -1 if the objection rebuttal relies on claims without verified proof

**Common mistakes:**
- Addressing objections defensively ("we're not expensive!") instead of reframing ("here's why the investment pays for itself")
- Creating an objection page that inadvertently introduces concerns the visitor hadn't considered
- Addressing too many objections at once (dilutes the rebuttal strength for each)

**Sequencing notes:** Run after competitive analysis is strong enough to identify the real objections. Pairs with PZ-01 (Pricing Transparency) if the primary objection is pricing-related. Content from this experiment can inform sales enablement materials.

---

## Extending This Library

New patterns can be added following the schema above. Each pattern must have:
1. At least one trigger condition that can be evaluated from context files
2. A causal mechanism grounded in behavioral science, UX principles, or established CRO methodology
3. ICE baselines and at least 2 modifiers
4. At least 2 common mistakes
5. Sequencing notes

Patterns without all five components are drafts and should not be matched during opportunity detection.
