# Copy-Craft Reference

Version: 1.0.0
Last updated: 2026-07-05
Scope: headline/H1, hero subhead, CTA button copy, CTA microcopy, form labels and error/privacy microcopy

Purpose: writing rules the hypothesis generator applies when producing proposed variant copy (construct.md Step 3 before/after and Step 3b multi-variation). This module governs HOW the words are written; it does not change experiment strategy, bundling, or scoring. Rules are evidence-graded.

---

## Evidence-quality preamble

The strong ground here is comprehension and usability mechanism evidence: users scan rather than read, easier-to-process claims are judged more credible, marking form fields cuts form failure, and lower reading level correlates with higher landing-page conversion. Almost none of it is B2B-website-conversion-specific. The strong findings are audience-general cognitive and usability mechanisms; the one directly-B2B signal (Wynter) measures message comprehension and preference, not conversion. Frame every rule as comprehension-optimization backed by mechanism, not as a guaranteed conversion outcome.

Encode direction and mechanism, never folklore lift percentages. The specific "+90% CTA", "specific CTA beats Submit by 30-40%", "benefit headlines 2-3x CTR" numbers in CRO blogs are unreplicated or non-citable; they do not go into generated copy or rationale.

Strength tags on each rule:
- **strong** -- controlled experiment(s), meta-analysis, or large-N eye-tracking/usability.
- **moderate** -- single-vendor controlled test, simulated-environment experiment, or large correlational dataset.
- **heuristic** -- expert opinion, single unreplicated case study, or blog claim with no traceable primary source. Do not phrase a heuristic as a law.

---

## Rules by element

### Headlines / H1s

1. **Optimize for comprehension before persuasion.** The reader must understand what this is and who it is for within one scan. [H-1, H-2, S-2] -- moderate.
2. **Write so the headline plus first line alone convey the core value.** Assume ~75-80% of the body goes unread. [H-2] -- strong.
3. **Lead the headline and each line with the load-bearing word.** Front-load specifics; users fixate on line beginnings and the top of the page. [H-2] -- strong.
6. **Do not sacrifice clarity for cleverness.** A plain specific statement beats a witty vague one. [H-1, H-4, S-2] -- moderate.
8. **Lead with the outcome or benefit, not the raw feature.** State the result the buyer gets. Treat magnitude claims as unproven. [H-7] -- heuristic (direction only).
11. **Test headline structure (question / statement / how-to / numbered) per case; no structure reliably wins.** Within any structure, choose the more specific version. [H-6, H-5] -- heuristic.

### Subheads

7. **Make the subhead concretize the headline's promise.** It is the second-most-read element, so spend it on specifics, not restatement. [S-1, H-2] -- moderate.

### CTA copy

12. **Write CTA labels that state what happens on click** ("Get my pricing", "Request a demo"), never generic ("Submit"). [C-1] -- moderate (direction via GoodUI repeatability).
13. **Match CTA verb commitment to buyer stage.** Low-commitment verbs for cold traffic ("See how it works"), high-commitment for ready buyers ("Talk to sales"). Mismatch raises anxiety. [C-4, C-3] -- heuristic.
14. **Place friction- and anxiety-reducing microcopy adjacent to the CTA** ("No credit card needed", "2-minute setup", "We won't share your email"). [C-3] -- moderate (principle) / heuristic (magnitude).
15. **Treat CTA pronoun ("my" vs "your") as a test idea, not a rule.** The famous first-person result is a single unreplicated case study. Propose it only as something worth testing, never as an asserted best practice. [C-2, folklore list] -- heuristic (explicitly de-rated).

### Form microcopy

16. **Mark required fields (asterisk) AND label optional fields "(optional)" beside the label.** Ambiguity causes roughly 1 in 3 users to miss a required field. Put the marker next to the label, not in placeholder text. [F-1] -- strong.
17. **Place form labels above the field; never use placeholder text as the only label.** [F-2] -- strong.
18. **Cut every form field that is not required to act on the lead; label each field you keep in plain terms.** Over-fielding is the norm and it costs conversion. [F-3] -- strong.
19. **Write inline, specific, plain-language validation errors** ("Enter a work email address") instead of generic ones ("Invalid input"). [F-4] -- strong.

---

## Cross-cutting rules

4. **Prefer concrete, quantified claims over abstract ones when a verified number exists.** Concrete, fluent claims are processed as more credible and true. Guardrail: use a specific number only when it is verifiable against the L0 proof registry per construct.md Step 4b. [H-5] -- strong (mechanism).
5. **Target roughly a 7th-grade reading level; cut 3+-syllable words.** Lower reading level correlates with materially higher conversion across industries. [H-3] -- moderate-strong (correlational).
9. **Purge buzzwords and empty category jargon** ("cutting-edge", "AI-powered", "disruptive", "best-in-class"). They read as noise to B2B buyers and lower perceived credibility. [S-2, jargon sources] -- heuristic-moderate.
10. **Keep genuinely useful domain terms your ICP already uses.** The rule is anti-buzzword, not anti-vocabulary. Match the buyer's actual language. [S-2] -- heuristic.
20. **Any claim ("2x faster", "cut costs 30%") must be specific AND verifiable.** Specificity only helps credibility if the reader believes it; fabricated precision backfires. Verification routes through construct.md Step 4b (proof-integrity): a specific number that fails that check is genericized or dropped, not shipped. [H-5, folklore list] -- strong (fluency mechanism) with the Step 4b guardrail.
21. **Do not encode conversion-lift percentages as promises.** State direction and mechanism; the specific magnitudes in CRO folklore are non-citable. This is a meta-rule about this module itself: generated copy and rationale never claim a numeric lift. [folklore list] -- strong.
22. **Prefer one clear primary message per view over stacking multiple offers.** Reducing competing messages reduced friction and drove large lifts in controlled tests. [H-1] -- moderate (B2C-sourced principle).

---

## Do-not-encode list (folklore)

These are documented so the skill actively avoids them. Do not restate any of these as a rule or a promised percentage in generated copy or rationale.

1. **First-person CTA pronoun (+90%).** One 2013 Unbounce/Aagaard case study, one page. No independent published replication located. Invented ranges ("10-40%") cite nothing. Do not encode as a rule. At most: "pronoun framing is worth testing; effect unproven and page-specific."
2. **"Specific CTA beats 'Submit' by 30-40%" / "benefit verb +121%".** Exact percentages from blogs with no primary test. Direction (descriptive > generic) has GoodUI repeatability support; numbers non-citable. Encode direction only.
3. **Button color case studies ("red beat green +21%").** Survivorship-bias folklore, context/contrast-dependent, not a law. Keep out of a copy module.
4. **Benefit-headline magnitudes ("2-3x CTR", "23-35% better").** AdEspresso 37K-ad dataset is real but Facebook ad copy, cited secondhand; ecommerce percentages blog-invented. Direction defensible as heuristic; numbers not B2B-web evidence.
5. **Single-company anecdotes as laws (Highrise "+30% headline", Basecamp signup, "$100M Bing headline").** One company, one context, often whole-page-redesign confounds. Illustrations, not rules.
6. **"Clarity trumps persuasion = 200%" applied to B2B.** Real MECLABS tests but B2C banking, whole-message rewrites, not isolated headline swaps. Encode the principle, never the number, never imply a B2B headline result.
7. **Optimal word/character-count "rules" for headlines.** No robust cross-context evidence for a magic length. Unbounce's word-count finding is page-level, industry-varying (SaaS 250-725 words), not a headline character limit.

---

## Source appendix

Tiered source list, for contributor orientation.

Strong / primary:
- NNG, F-Shaped Pattern of Reading: https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
- NNG, Text Scanning Patterns (Eyetracking): https://www.nngroup.com/articles/text-scanning-patterns-eyetracking/
- Baymard, Mark Both Required and Optional Fields: https://baymard.com/blog/required-optional-form-fields
- Baymard, Field Label UX (Labels Above Field): https://baymard.com/blog/mobile-form-usability-label-position
- Baymard, Checkout Usability: https://baymard.com/research/checkout-usability
- Baymard, Form Design Best Practices: https://baymard.com/learn/form-design
- Oxford / Communication Theory, Perceived Convincingness Model (processing fluency, r approx .26): https://academic.oup.com/ct/article/32/4/488/6718085
- Frontiers, Narratives Are Persuasive Because They Are Easier to Understand: https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2021.719615/full

Moderate / case-study and controlled-single-vendor:
- Unbounce Conversion Benchmark Report 2024: https://unbounce.com/conversion-benchmark-report/
- Unbounce CBR 2024 (PR summary): https://www.prnewswire.com/news-releases/unbounces-2024-conversion-benchmark-report-proves-that-attention-spans-are-declining-and-so-are-conversion-rates-302239407.html
- MarketingExperiments, Clarity Trumped Persuasion: https://marketingexperiments.com/copywriting/web-messaging-clarity-conversion
- MarketingExperiments, Clarity Trumps Persuasion (hub): https://marketingexperiments.com/value-proposition/clarity-trumps-persuasion
- MECLABS, Conversion Heuristic: https://meclabs.com/research/discovery/wharton-customer-first-science
- MarketingExperiments, Quick Lift Ideas (headline/subhead): https://marketingexperiments.com/conversion-marketing/quick-lift-headines
- CXL, Value Proposition Study (eye-tracking; summary-sourced): https://cxl.com/research-study/value-proposition-study/
- Wynter, Message Testing guide: https://wynter.com/post/message-testing
- Wynter, B2B Message Testing: https://wynter.com/products/message-testing
- GoodUI, patterns and evidence (repeatability): https://goodui.org/ ; https://www.goodui.org/evidence/test014
- GoodUI, Pattern #15 Bulleted Reassurances: https://goodui.org/patterns/15/

Weak-heuristic / folklore (documented, not relied on):
- Unbounce, CTA Buttons That Convert (restates first-person case study): https://unbounce.com/conversion-rate-optimization/cta-buttons-that-convert/
- ClickZ, Me vs. You pronouns: https://clickz.com/me-vs-you-how-pronouns-affect-click-conversion-rates/32596/
- conversion.studio, Feature vs Benefit (cites AdEspresso 37K ads): https://conversion.studio/blog/feature-vs-benefit
- Copyhackers, Asking Questions in Your Copy: https://copyhackers.com/2015/09/asking-questions/
- BDOW!/Sumo, Headline Formulas: https://bdow.com/stories/headline-formulas/
- Radix Communications, Does jargon kill B2B copy: https://radix-communications.com/does-jargon-kill-b2b-copy-or-does-it-bring-it-to-life/
