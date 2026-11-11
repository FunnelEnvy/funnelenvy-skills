# Experiment Patterns Library

Version: 2.0.0
Last updated: 2026-11-11
Pattern count: 32
Categories: 10

This module is the prompt library for the hypothesis-generator lenses. The surface, persona-and-journey and competitive-and-proof lenses read it while they look for candidates. Each pattern names a testable opportunity type, the conditions that make it fit, a default test, the causal reasoning, ICE baselines and modifiers.

## How Lenses Use This Library

- **Full match:** every `Applies when` condition holds in the loaded context. Emit a card with `pattern: true` and the pattern's `Key` as `mechanism_key`.
- **Partial match:** at least one condition holds and at least one cannot be confirmed. Emit the card anyway, with `pattern: true`, the pattern's `Key`, and the annotation `partial match: <missing condition>`. A partial match is a card, never a discard.
- **No match:** a concrete signal that fits no pattern still becomes a card. The lens coins a kebab-case `mechanism_key` and sets `pattern: false`.
- **Scoring:** `phases/score.md` starts a pattern card at its ICE baseline and applies its modifiers. Modifiers apply only when their condition can be confirmed from context.
- **Internal labels:** pattern IDs, keys and category names never appear in a deliverable.

## Pattern Schema

- **Key:** the `mechanism_key` every lens uses for this pattern, so cards from different lenses merge.
- **Applies when:** conditions checked against context files.
- **Typical test:** the default experiment, adapted to the context.
- **Mechanism:** the behavioral or UX principle. A starting point, not text to copy.
- **ICE:** baseline Impact, Confidence and Ease, then modifiers.
- **Mistakes:** what to avoid when building the card and the write-up.
- **Sequencing:** ordering notes for the `Sequencing` method section.
- **Calibration:** observed results, where recorded. One case study is one data point.

---

## Headline/Messaging

### HM-01: Value Prop Clarity Test

**Key:** `value-prop-clarity`
**Applies when:**
- Scorecard rates Clarity as Needs Work or Missing
- Homepage headline uses jargon, category language or feature-first framing
- The strongest L0 value prop is absent from what the homepage says

**Typical test:** Replace the feature or category headline with an outcome headline adapted from the primary value theme in audience-messaging.
**Mechanism:** Buyers decide in a few seconds whether a page is relevant. Category language makes them translate features into personal value. Outcome language lets them self-qualify at once.
**ICE:** I3 C4 E5. C+1 if audience-messaging gives a homepage channel adaptation. C-1 if the current headline copy is not in context. I+1 if Clarity is Missing. I+1 if the page is the top landing page by sessions.
**Mistakes:** Testing two vague headlines against each other. Changing the headline without aligning the subhead. Outcome claims no proof point supports.
**Sequencing:** Run early. Its result informs every downstream copy test.

### HM-02: Specificity Injection

**Key:** `specificity-injection`
**Applies when:**
- Scorecard rates Proof as Needs Work or Missing
- Claims appear without quantified evidence nearby ("trusted by hundreds")
- Verified or supported L0 proof points are missing from the page that makes the related claim

**Typical test:** Add a specific metric, customer name or timeframe beside the primary claim. Replace vague social proof with concrete numbers.
**Mechanism:** Specificity signals confidence in the claim. A round, vague claim invites skepticism. A named, numbered claim invites evaluation instead.
**ICE:** I3 C4 E5. I+1 if verified proof (named customer plus metric) is not displayed. C-1 if proof is only claimed strength. I+1 on pricing or demo pages.
**Mistakes:** Proof that does not match the claim beside it. Logos from the wrong segment. Impressive numbers that miss the buyer's concern.
**Sequencing:** Pairs with HM-01. Run after headline clarity so the proof supports the right message.

---

## Form Optimization

### FO-01: Form Field Reduction

**Key:** `form-field-reduction`
**Applies when:**
- A lead form has 5 or more fields
- No progressive profiling is in place
- The form serves a mid-funnel action (download, webinar, newsletter)

**Typical test:** Cut to 3 or 4 essential fields. Capture the rest through enrichment or follow-up.
**Mechanism:** Each field raises perceived effort and prompts a cost-benefit check. For mid-funnel offers the content rarely justifies 7 or more fields.
**ICE:** I4 C4 E4. C-2 if the form is a high-intent action where qualification matters. I+1 if mobile is over 40% of visits. E-1 for an embedded third-party form. Smaller effect when the form already has 4 or 5 fields.
**Mistakes:** Removing fields sales uses without enrichment in place. Treating all fields as equal: phone and email carry very different friction.
**Sequencing:** Choose FO-01 or FO-02 for a given form, not both.

### FO-02: Multi-Step Form Conversion

**Key:** `multi-step-form`
**Applies when:**
- A single-page form has 5 or more fields
- The form is high-intent (demo, consultation, trial), so cutting fields would cost qualification
- Progressive disclosure could defer qualification to later steps

**Typical test:** Split into 2 or 3 steps: lowest-friction fields first, qualification next, scheduling last. Show progress.
**Mechanism:** Commitment and consistency. Finishing step 1 makes finishing the rest more likely, and the visitor faces two fields instead of a wall of seven.
**ICE:** I4 C4 E3. E-2 for an embedded third-party form with limited flow control. C+1 if abandonment data exists. I+1 if completion is measurably low. C+1 if a conversational variant is feasible.
**Mistakes:** The highest-friction question in step 1. No step-level abandonment tracking. Four or more steps for seven fields. Dropdowns where buttons would do.
**Sequencing:** See FO-01.

### FO-03: Form Context Reinforcement

**Key:** `form-context-reinforcement`
**Applies when:**
- The form has no value reinforcement around it
- No reminder of what the visitor gets, no trust signal near submit, no expectation of what happens next

**Typical test:** Add a "what you'll get" summary, a relevant proof point, privacy reassurance and the next step beside the form.
**Mechanism:** At submit the visitor re-asks "is this worth my information?" Reinforcement at the point of action answers it.
**ICE:** I3 C4 E5. I+2 for a high-commitment form. I-1 for a light content download. C+1 if verified proof is available.
**Mistakes:** Generic trust badges that miss the real objection. New claims that clash with the page's value prop. Omitting what happens next.
**Sequencing:** Combines well with FO-01 or FO-02.

### FO-04: Form Field Micro-Copy Optimization

**Key:** `form-microcopy`
**Applies when:**
- Field labels are generic or ambiguous, with no helper text or examples
- Performance data shows form abandonment or low completion

**Typical test:** Clarify labels, add example placeholder values and short helper text. Field count and order stay the same.
**Mechanism:** Each ambiguous label is a small decision. Examples remove the interpretation step, and the saving compounds across fields.
**ICE:** I3 C4 E5. E+1 if marketing owns the form builder. I+1 for a deep-funnel form. C+1 if abandonment localizes to specific fields. C-1 if labels are already clear. I+1 if the form targets new visitors.
**Mistakes:** Placeholder text with no persistent label. Over-explaining simple fields.
**Sequencing:** Hours of work. Run before or alongside structural form changes; results show which fields to cut.
**Calibration:** One deep-funnel site gained 7.3% referred leads from a label and placeholder change; a second section gained 19% (directional).

---

## Navigation/UX Flow

### NX-01: Navigation Intent Mismatch

**Key:** `persona-navigation`
**Applies when:**
- Audience-messaging defines 2 or more personas with distinct challenges
- Navigation is feature-only, with no persona or use-case paths
- Scorecard rates Specificity as Needs Work

**Typical test:** Add "For [Role]" or "By Use Case" paths beside or in place of feature navigation.
**Mechanism:** Role paths are a relevance shortcut. Each persona stops filtering features to find its own problem.
**ICE:** I4 C3 E2. C+1 if navigation pages bounce high. E-1 if the CMS limits navigation changes. I+1 for 3 or more personas. C+1 if competitors use persona navigation.
**Mistakes:** Persona pages that are filtered feature lists. Five or more persona entries. Labels visitors do not identify with.
**Sequencing:** Long build. A win turns each persona page into its own testing surface.

### NX-02: CTA Clarity and Hierarchy

**Key:** `cta-clarity-hierarchy`
**Applies when:**
- Several CTAs compete at similar visual weight
- The primary CTA is vague ("Learn More", "Contact Us")
- Scorecard rates Clarity as Needs Work

**Typical test:** One specific primary CTA ("Book a 15-min Demo"); secondary CTAs demoted visually.
**Mechanism:** More equal choices slow the decision (Hick's Law). Specific language also sets expectations about the commitment.
**ICE:** I3 C4 E4. I+1 for 3 or more equal CTAs. C+1 if a testing platform is already on the page. I+1 if the CTA is the primary conversion.
**Mistakes:** A specific CTA that leads to a generic form. Leaving not-ready visitors no path. Insider jargon in the label.
**Sequencing:** After a headline test on the same page, so CTA copy follows the winning message.

### NX-03: Exit Path Optimization

**Key:** `secondary-exit-path`
**Applies when:**
- A high-traffic page loses many visitors
- There is no secondary path for visitors not ready for the primary CTA
- A lower-commitment offer exists or could exist

**Typical test:** Add a lower-commitment secondary CTA for visitors who scroll past the primary or show exit intent.
**Mechanism:** A consolation offer moves interested but unready visitors into nurture instead of losing them.
**ICE:** I3 C3 E3. I+2 if traffic is high and primary conversion is under 1%. E+1 if exit-intent tooling exists. C+1 if the offer already exists.
**Mistakes:** A secondary offer better than the primary. Aggressive exit popups. An offer unrelated to the page.
**Sequencing:** After primary CTA tests.

### NX-04: Paid Landing Page Optimization

**Key:** `paid-landing-match`
**Applies when:**
- Over 200 paid sessions a month reach the page
- Paid bounce exceeds organic bounce on the same page
- The page has full site navigation and no dedicated paid variant exists

**Typical test:** For paid visitors only: headline and visual aligned to the ad, navigation reduced to one conversion path, hero that echoes the ad's promise.
**Mechanism:** The ad sets an expectation. A mismatched headline breaks it on arrival, and full navigation offers exits before the value lands. Visual and verbal continuity confirms the visitor is in the right place.
**ICE:** I4 C3 E3. I+1 if paid spend on the page exceeds $5K a month. C+2 if the paid-organic bounce gap exceeds 10pp. E+1 if the platform targets by traffic source. E-1 if several campaigns with different messages share the page. C+1 if message match and navigation reduction are tested together. I+1 if the ad creative has mirrorable visual elements.
**Mistakes:** Parroting the ad instead of keeping its promise. Removing navigation for organic visitors too. Treating message match as copy only.
**Sequencing:** Needs traffic-source targeting. Without it the card carries the blocker `design-change`.
**Calibration:** One streaming service gained 45% subscriptions, rising to 65%, from a combined hero shrink, countdown and ad parity change. The lift belongs to the combination.

### NX-05: Value-Before-Commitment Sequencing

**Key:** `value-before-commitment`
**Applies when:**
- The primary CTA asks for commitment before showing value
- The product can be previewed (interactive demo, sample output, sandbox)
- Competitors offer self-serve evaluation

**Typical test:** Put a value preview before or in place of the gate.
**Mechanism:** Commitment before value creates an asymmetry buyers resist. Value first lowers perceived risk, and the endowment effect makes the later ask feel smaller.
**ICE:** I5 C3 E2. I+1 if competitors offer self-serve evaluation. C+1 if a demo environment exists. E+2 if an interactive demo tool is in use. E-2 if the asset must be built. C-1 if unguided evaluation could confuse buyers.
**Mistakes:** A marketing video passed off as a preview. Gating the preview behind a form. A generic sandbox with no guided use case.
**Sequencing:** Hard to reverse. Validate messaging first.

### NX-06: Comparison-Mode Intervention

**Key:** `session-depth-offer`
**Applies when:**
- A meaningful segment views 5 or more pages per session
- No comparison or evaluation content surfaces during browsing
- Only time-based or exit-intent popups exist, or none

**Typical test:** A session-depth offer (comparison guide, ROI calculator, "still evaluating?" prompt) that fires after the fifth page view, matched to the pages seen.
**Mechanism:** Page count tracks evaluation intent. An offer fitted to comparison behavior meets that state; time-based triggers interrupt browsers and miss evaluators alike.
**ICE:** I3 C3 E3. I+2 if that segment exceeds 15% of sessions. C+1 if the asset exists. E+1 if overlay tooling exists. C+1 if the segment visits pricing. C-1 if depth comes from blog reading.
**Mistakes:** A 3-page threshold. A newsletter offer for a deep evaluator. One offer regardless of pages visited.
**Sequencing:** Independent of page-level tests and of NX-03.

### NX-07: Return Visitor Intent Optimization

**Key:** `login-prominence`
**Applies when:**
- Returning visitors exceed 30% of acquisition-page traffic
- Returning visitors behave differently from new visitors on those pages
- Login is buried, icon-only or absent there

**Typical test:** A clearly labeled login path ("Log In" text, a returning-visitor banner, or a conditional account entry) that leaves the new-visitor flow intact.
**Mechanism:** Existing users hunting for login inflate bounce and sometimes leave. Prominent login costs new visitors nothing. Auto-redirecting returning users past marketing pages tends to backfire, because they lose upgrade messaging.
**ICE:** I4 C4 E5. I+1 if returning visitors exceed 40%. I+1 for freemium or trial products. C+1 if returning visitors bounce much higher. E-1 if conditional display needs new infrastructure. C-1 if the account offers little value.
**Mistakes:** Auto-redirecting past the marketing site. Assuming the pattern transfers when the account has little value. Counting logins instead of downstream value.
**Sequencing:** Low effort and a distinct segment, so it can run beside new-visitor tests with targeting.
**Calibration:** An apparel retailer gained 4.1% orders and 5.3% revenue per visitor from an icon-to-"Log In" change. The same change failed on a site whose account held only order history.

---

## Personalization

### PE-01: Segment-Based Hero Personalization

**Key:** `segment-hero-personalization`
**Applies when:**
- Audience-messaging defines 2 or more personas with distinct value props
- Every visitor sees the same hero
- Scorecard rates Specificity as Needs Work or Missing

**Typical test:** Persona-matched hero copy served by UTM, referral source, reverse IP or self-selection.
**Mechanism:** Relevance drives conversion. Matching the opening message to the visitor's frame closes the gap between "this page exists" and "this page is for me."
**ICE:** I5 C3 E2. C+2 if segments are identifiable from existing UTMs or campaigns. E+2 with native audience targeting. E-2 with no personalization infrastructure. C-1 if personas overlap.
**Mistakes:** A personalized headline over a generic page. Too little traffic per segment. Trusting reverse IP as exact.
**Sequencing:** After headline and CTA tests. Personalize proven messaging only.

### PE-02: Industry/Vertical Social Proof Matching

**Key:** `industry-proof-matching`
**Applies when:**
- Customers span several industries in the L0 registry
- Social proof shows the same to every visitor
- At least 3 proof points exist per target vertical

**Typical test:** Match displayed proof to the visitor's industry signal.
**Mechanism:** "Companies like mine use this" lowers perceived risk more than "companies use this."
**ICE:** I4 C3 E2. C+1 for 3 or more case studies per vertical. E+2 with dynamic content blocks. C-1 for claimed-only proof. I-1 for a single-vertical business.
**Mistakes:** Personalizing with 1 or 2 customers per vertical. Matching industry but not company size.
**Sequencing:** Extend PE-01's system rather than build a second one.

---

## Page Structure/Layout

### PS-01: Above-the-Fold Hierarchy Reset

**Key:** `above-fold-hierarchy`
**Applies when:**
- The page leads with features, screenshots or heavy navigation instead of a value prop and one CTA
- Scorecard rates Clarity as Needs Work or Missing
- The first screen does not say what the company does and why it matters

**Typical test:** Outcome headline, a how subhead, one primary CTA and a trust signal above the fold; details below.
**Mechanism:** The visitor first asks "is this for me?" Hierarchy should follow that sequence: relevance, then capability, then proof.
**ICE:** I4 C3 E3. I+1 if bounce exceeds 60%. E-2 for a template-locked page. C+1 if audience-messaging gives a message hierarchy.
**Mistakes:** Vague aspiration in place of features. Removing every product cue. An empty-feeling first screen on desktop.
**Sequencing:** Run HM-01 first, then restructure around the winning message.

### PS-02: Long-Form vs. Short-Form Page Test

**Key:** `page-length-architecture`
**Applies when:**
- A key page is very long or too thin for a complex decision
- The page serves both exploring and ready-to-act visitors

**Typical test:** Long page: condense with progressive disclosure. Short page: add proof, objection handling and implementation detail below the fold.
**Mechanism:** Short pages under-serve the champion who must sell internally; long pages lose the convinced buyer looking for the CTA.
**ICE:** I3 C3 E2. C+1 with scroll-depth data. I+1 for mixed-intent traffic. E-1 if new content is needed.
**Mistakes:** Treating length as the variable when architecture is. Cutting content without knowing its job. No scroll or section tracking.
**Sequencing:** After copy and CTA tests.

### PS-03: About Page Proof Hierarchy

**Key:** `about-page-proof`
**Applies when:**
- The About page leads with mission or values instead of capability proof
- Credentials and quality claims sit low on the page
- Scorecard rates Proof as Needs Work and the strongest proof points appear late

**Typical test:** Lead with quantified outcomes, named customers, credentials and recognition; move mission and values below.
**Mechanism:** About-page visitors are judging whether the company can deliver. Proof answers that; mission answers a question they are not asking yet.
**ICE:** I3 C3 E3. I+1 if the page is top-5 by visits. C+1 if 3 or more verified proof points are absent from it. E+1 if it is reordering only. C-1 if the current layout cannot be confirmed.
**Mistakes:** Deleting mission entirely. Leading with bare logos.
**Sequencing:** Independent of homepage tests. Pairs with SP-03 on the same page.

### PS-04: Service Page Differentiation Injection

**Key:** `service-differentiation`
**Applies when:**
- Service or product pages describe capabilities without differentiation
- Competitive context shows claim overlap in those areas
- The copy could belong to any competitor

**Typical test:** Add differentiation blocks (method, comparison points, service-specific proof) where the page now describes generic capability.
**Mechanism:** Comparison-mode buyers read near-identical service pages. A specific differentiator breaks the pattern and gives them something to remember.
**ICE:** I3 C3 E4. I+1 for high claim overlap. C+1 if audience-messaging gives service-specific adaptations. C-1 for claimed-only differentiators. I-1 if service traffic is low relative to the homepage.
**Mistakes:** Differentiating on a commodity feature. Process detail buyers do not weigh at this stage.
**Sequencing:** Extend the winning homepage message into service pages.

---

## Pricing

### PZ-01: Pricing Transparency Test

**Key:** `pricing-transparency`
**Applies when:**
- Competitors publish pricing and the company does not, or the reverse
- Pricing is "contact us" or no pricing page exists
- Scorecard shows a Specificity gap on pricing or evaluation

**Typical test:** Add a pricing indicator (starting-at price, range, tier comparison or full pricing). Create the page if none exists.
**Mechanism:** Buyers self-serve evaluation. Hidden pricing blocks fit assessment; published pricing anchors expectations and filters unqualified leads.
**ICE:** I4 C2 E3. C+2 if competitors publish and the company loses on ease of evaluation. I-1 for highly variable deal sizes. E-1 if publishing needs internal alignment. C+1 for clear packages. C+1 for savings framing that applies the Rule of 100 (percentages under $100, absolutes over).
**Mistakes:** Numbers without value anchoring. Tiers without who-it-is-for. Skipping ranges or starting-at as a middle option.
**Sequencing:** Usually needs a business decision first; the card carries the blocker `client-decision` when context shows that.

---

## Social Proof

### SP-01: Testimonial Format Optimization

**Key:** `testimonial-format`
**Applies when:**
- Testimonials appear as text-only blocks without attribution
- Testimonial content is generic rather than outcome-specific
- Testimonials do not match the page's persona or use case

**Typical test:** Full attribution (name, title, company, photo), outcome pull quotes and persona-page matching.
**Mechanism:** Testimonials work through identification. Without role and company context the reader cannot judge "is this person like me?"
**ICE:** I3 C4 E4. I+1 on pricing or demo pages. C+1 for named testimonials with metrics. E-1 if content must be collected. C-1 if the current format cannot be confirmed.
**Mistakes:** Stock photos. Off-segment testimonials.
**Sequencing:** Independent; can run beside headline or CTA tests in other sections.

### SP-02: Case Study Structure Test

**Key:** `case-study-structure`
**Applies when:**
- Case studies lack before/after metrics, a timeline or a challenge/solution structure
- Case studies are buried, not surfaced on high-traffic pages
- Verified registry outcomes are not yet case studies

**Typical test:** A: restructure case studies into challenge, approach and quantified results. B: surface one-line case summaries on high-traffic pages as proof strips.
**Mechanism:** Case studies serve champions who need detail and scanners who need a signal. Generic ones serve neither.
**ICE:** I3 C3 E3. I+1 for named enterprise customers. C+1 with before/after metrics. E-1 if rewriting is needed. E+1 if surfacing existing data.
**Mistakes:** Vague results. Subjects that do not match the persona.
**Sequencing:** Pairs with CR-02. Strengthen the content before testing strips.

### SP-03: Proof Hierarchy Restructure

**Key:** `proof-hierarchy`
**Applies when:**
- Proof of different strengths is mixed together on key pages
- The strongest proof sits below weaker proof
- The site does not distinguish proof strength visually

**Typical test:** Order proof strongest first: quantified outcomes, named testimonials, logos, then badges. Scale visual weight to strength.
**Mechanism:** The first proof seen sets the trust anchor. A strong anchor lets weaker proof reinforce rather than dilute.
**ICE:** I3 C4 E4. I+1 on homepage or pricing. C+1 for 3 or more verified proof points of clearly different strength. E+1 if it is reordering only. I-1 if the page already leads with its best proof.
**Mistakes:** Deleting weaker proof. Treating all logos as equal.
**Sequencing:** Run early; it informs proof placement everywhere.

---

## Content/Resource

### CR-01: Competitive Comparison Page

**Key:** `comparison-page`
**Applies when:**
- Competitive context names 3 or more direct competitors
- No comparison or "vs." page exists
- Differentiators or white space suit a comparison format
- Competitors' comparison pages include the company

**Typical test:** A comparison page against the top 2 or 3 competitors on key criteria, leading with winning dimensions and honest about where others are stronger.
**Mechanism:** Buyers compare anyway. A company-made comparison sets the criteria, and candor about competitor strengths builds trust.
**ICE:** I4 C3 E2. I+1 if comparison search demand exists or competitors run comparison pages. C+1 for verifiable differentiators. E-1 for ongoing maintenance. C-1 for claimed-only differentiators.
**Mistakes:** Obvious bias. Competitors that are not real alternatives. Letting the page go stale.
**Sequencing:** After positioning fundamentals settle the value prop.

### CR-02: ROI Evidence Integration

**Key:** `roi-evidence`
**Applies when:**
- Verified quantified outcomes exist but are absent from high-traffic pages
- Scorecard names quantified ROI as a top proof gap
- Competitors lead with ROI claims the company could match

**Typical test:** A (low effort): an evidence strip of 3 or 4 attributed outcomes. B (high effort): an ROI calculator built on company benchmarks.
**Mechanism:** Champions need financial justification. Surfaced outcomes give them shareable proof and signal that the company can quantify its value.
**ICE:** A: I4 C3 E4. B: I4 C3 E2. I+1 if ROI evidence is wholly absent from the site. C+1 for named customers. E-1 for B if it needs custom engineering. C-1 for single-customer metrics.
**Mistakes:** Unattributed numbers. Implausible calculator outputs. Averages across unlike segments.
**Sequencing:** Run A first. Build B only after A shows ROI evidence resonates.

### CR-03: Assessment / Diagnostic Tool

**Key:** `diagnostic-tool`
**Applies when:**
- Several segments with different needs and no self-qualification path
- 2 or more personas with distinct entry points
- No interactive content helps visitors identify their situation

**Typical test:** A 5 to 7 question diagnostic that recommends a fit and next step, with detailed results behind email capture.
**Mechanism:** Visitors must classify their need before they can evaluate a vendor. A diagnostic solves classification, positions the company as a guide, and converts at peak engagement.
**ICE:** I3 C2 E2. I+1 for 3 or more segments. C+1 for well-defined personas. E-1 for custom development. E+1 if a quiz platform exists.
**Mistakes:** More than 10 questions. Generic results. Diagnostic answers unused by sales.
**Sequencing:** High effort. Build on validated messaging.

### CR-04: Content Page Conversion Injection

**Key:** `content-conversion-injection`
**Applies when:**
- High-traffic content or SEO pages have no conversion path beyond navigation
- They rank and draw sessions but carry no CTA or form
- The topic sits next to a monetizable offer

**Typical test:** A contextual conversion element below the fold: a topic-matched widget, inline CTA or banner to a related solution.
**Mechanism:** Content readers have latent need next to a purchase. The page does the persuading; the element offers the next step instead of a dead end.
**ICE:** I3 C3 E4. I+1 for a top-10 organic page. I+1 if the topic maps to a revenue offer. C+1 if injection was validated elsewhere on the site. E+1 if a reusable component exists. E-1 if the CMS blocks per-page widgets. C-1 for low-intent readers.
**Mistakes:** A hard sell on an educational post. Ignoring cannibalization of lower-value engagement. One widget for every topic.
**Sequencing:** Independent surface. Validate on the top page, then replicate.
**Calibration:** A travel content site gained 3% site-wide purchases from a below-fold widget while clicks to other content fell.

---

## Trust/Credibility

### TC-01: Team Credibility Surface

**Key:** `team-credibility`
**Applies when:**
- Team expertise is a claimed L0 differentiator but the team page is generic or missing
- Competitors show stronger team pages
- The company sells expertise-dependent services

**Typical test:** A team page upgrade or team-credibility strips on service pages: credentials, prior work, specialization.
**Mechanism:** In services the team is the product. Verifiable expertise markers lower perceived engagement risk.
**ICE:** I3 C3 E3. I+1 for high-ticket services where the team is the differentiator. C+1 if L0 lists credentials. E+1 if the material exists internally. E-1 if profiles must be produced.
**Mistakes:** Stock or generated headshots. Credentials not tied to client value.
**Sequencing:** Pairs with PS-03.

### TC-02: Objection Preemption Page

**Key:** `objection-preemption`
**Applies when:**
- Competitive context names a structural objection or loss reason with no rebuttal on the site
- Audience-messaging names recurring objections
- FAQ or objection content is buried, generic or missing

**Typical test:** Content for the top 1 or 2 objections: a fit page, a pricing FAQ or a "how we compare" section, placed where the objection blocks conversion.
**Mechanism:** Unanswered objections become reasons to choose a competitor. Preemption reframes the concern before it sets.
**ICE:** I4 C3 E3. I+1 if it is the primary loss reason. C+1 with direct evidence against the objection. E+1 if it fits an existing page. C-1 for unverified rebuttals.
**Mistakes:** Defensive tone. Raising objections visitors did not have. Too many objections at once.
**Sequencing:** Pairs with PZ-01 when the objection is price.

---

## Element Engagement

### EE-01: CTA Click-Through Optimization

**Key:** `cta-click-through`
**Applies when:**
- Element data shows primary CTA click rate under 3% on a page with over 500 sessions a month
- The page has a clear conversion action
- CTA copy, placement or weight looks insufficient

**Typical test:** Change CTA copy, size, contrast or placement, or add a sticky CTA.
**Mechanism:** A low click rate on a well-read page means the persuasion arc is not reaching action: mismatch with the content, low salience, or too large an ask.
**ICE:** I4 C4 E5. C+1 if a secondary CTA out-clicks the primary. I+1 on a top-5 landing page. I-1 if the click rate already exceeds 5%. C+1 for a deep-engagement failure mode on the page.
**Mistakes:** Color alone. Copy changes without aligned context. Adding CTAs. Ignoring device differences.
**Sequencing:** Fix the headline first, then the CTA.

### EE-02: Element Engagement Drop-off

**Key:** `sequential-content-dropoff`
**Applies when:**
- Element data shows later carousel, tab or accordion items under 20% of the first item's interactions
- The hidden items carry distinct value
- The page has over 300 sessions a month

**Typical test:** Surface the high-value items: a static grid, reordered tabs, previews, or fewer and better items.
**Mechanism:** Each click to reveal the next item filters out visitors. Valuable content behind that wall goes unseen.
**ICE:** I3 C3 E3. I+1 if hidden items hold proof. I+1 on pricing or product pages. C+1 if item 2 gets under 10% of item 1. E-1 for a major layout change. E+1 for reordering only.
**Mistakes:** A wall of text in place of structure. Flattening content that is genuinely optional. Assuming the most-viewed item converts best.
**Sequencing:** After EE-01 on the same page. Pairs with PS-01 when the carousel sits above the fold.

### EE-03: CTA Commitment Language Calibration

**Key:** `cta-commitment-level`
**Applies when:**
- The primary CTA asks for high commitment ("Subscribe", "Buy Now", "Request Demo") from visitors not yet product-aware
- Audience-messaging places the persona at problem-aware or solution-aware
- Click rate is low despite strong engagement

**Typical test:** Lower-commitment CTA language matched to the dominant awareness stage, tested along a spectrum ("Subscribe", "Start Free Trial", "View Demo", "See How It Works").
**Mechanism:** CTA language signals the size of the ask. A premature large ask triggers loss aversion; a smaller one lets the product do the selling. This differs from NX-02: a clear, single CTA can still ask for too much.
**ICE:** I4 C4 E5. I+1 for purchase language on non-purchase traffic. I+1 for B2B SaaS. C+1 if traffic sources confirm low awareness. C-1 for bottom-funnel traffic. E-1 if the post-click flow must change.
**Mistakes:** Going vague ("Learn More"). One commitment level for mixed traffic. Changing the button but not the copy around it.
**Sequencing:** After NX-02 establishes one clear CTA.
**Calibration:** SaaS tests moved CTA clicks 68% ("Subscribe" to "Free Trial") and 249% ("Subscribe" to "View Demo"). Clicks are a proxy; downstream effects vary.

---

## Extending This Library

A new pattern needs a `Key`, at least one condition a lens can check in context, a mechanism grounded in behavioral science or UX practice, ICE baselines with at least two modifiers, at least two mistakes, and a sequencing note. Lenses do not use a pattern that lacks any of these.
