<!-- Agent-consumable section taxonomy. Trimmed from section-taxonomy-v03.md.
     Source design doc has full research rationale and evidence basis.
     This file is the shared reference for copy (Phase 2) and QA (Phase 4). -->

# Landing Page Section Taxonomy

Composable section library for the landing-page-generator skill. The copy agent selects and sequences sections based on campaign brief metadata and L0/L1 context signals. The design agent renders them using `templates/section-catalog.html`. copy.md IS the section manifest. If a section isn't in copy.md, it doesn't appear on the page.

## Section Taxonomy

### REQUIRED SECTIONS

These appear on every page. Variant selection is signal-driven.

#### 1. Hero

The first content block. Headline, supporting text, primary CTA. Sets the conversion frame for the entire page.

| Variant | Selection Signal | Structure |
|---|---|---|
| `pain-lead` | `traffic_awareness_stage` = unaware OR problem_aware | Lead with the problem. Headline names the pain. Subheadline bridges to solution. CTA is low-commitment ("See How" / "Learn More"). |
| `keyword-match` | `traffic_source` = paid_search AND `traffic_awareness_stage` = solution_aware. Also for competitive campaigns where `target_keywords` contain competitor name, "vs", or "alternative". | Headline echoes search intent (mirrors `target_keywords`). For competitive queries, headline positions against the category leader. Subheadline differentiates. CTA matches offer type directly. |
| `proof-lead` | proof_points verified >= 2 AND (`traffic_source` = retargeting OR `traffic_awareness_stage` = product_aware OR most_aware) | Lead with strongest quantified result. Headline is the metric. Subheadline contextualizes. CTA is direct (book/start/get). |

**Default:** `pain-lead` (safest when signals are ambiguous).

**Note on product-aware/most-aware traffic:** These audiences need less copy, not more. Hero should be tight: headline + proof or headline + offer. Do not add a pain-acknowledgment line for most-aware visitors. For product-aware, a single sentence of pain context in the subheadline is acceptable but not a dedicated problem section below.

#### 2. Primary CTA

The main conversion action. Can be inline form, modal trigger button, or multi-step flow depending on form strategy.

| Variant | Selection Signal | Structure |
|---|---|---|
| `inline-form` | `form_strategy.type` = inline AND `form_strategy.fields` <= 4 | Form fields visible on page, embedded in hero or immediately below. Reduces friction for short forms. |
| `modal-trigger` | `form_strategy.type` = modal OR `form_strategy.fields` > 4 | Button triggers lightbox overlay. Keeps hero clean when form is complex. |
| `multi-step` | `form_strategy.type` = multi_step | Step 1 visible (1-2 fields), remaining steps revealed progressively. For high-field-count forms that need to feel simple. |

**Note:** Primary CTA placement is defined by which hero variant is used. The CTA lives inside or immediately adjacent to the hero. This section defines the CTA mechanism, not a standalone page block.

#### 3. Final CTA

Closing conversion block. Appears as the last content section before footer. Reinforces the offer after the page has built its case.

| Variant | Selection Signal | Structure |
|---|---|---|
| `mirror` | Default | Repeats hero headline (or shortened version) + same CTA. Visual contrast from hero (dark background if hero is light, or vice versa). |
| `urgency` | `offer_type` = content AND asset is time-sensitive, OR brief contains deadline/scarcity signal | Adds urgency element (limited availability, deadline, cohort size). Same CTA mechanism. |
| `summary` | page has 6+ sections above | Brief recap of key value props (3-4 bullet max) + CTA. Helps visitors who scrolled through a long page remember why they should act. |

**Default:** `mirror`.

#### 4. Footer

Minimal. Logo, legal links, no navigation that competes with CTA.

**No variants.** Every LP footer is the same: logo, copyright, privacy link, terms link. No social links, no sitemap, no blog links.

### CONTEXTUAL SECTIONS

Included when selection signals are met. Listed in rough default ordering (see Ordering Constraints for the actual rules).

#### 5. Social Proof Bar

Visual credibility signal. Usually appears high on the page.

**Selection signal:** Customer logos or metrics recognizable to the target audience. "Recognizable" means the target persona would know the brand on sight. Two Fortune 500 logos beat five unknown logos.

| Variant | Selection Signal | Structure |
|---|---|---|
| `logo-row` | 4+ audience-recognizable logos available | Horizontal row of customer/partner logos. Grayscale or muted. No text. Must not visually compete with adjacent CTA. |
| `stat-bar` | verified proof_points >= 3 AND recognizable logos unavailable | 3-4 key metrics in a horizontal bar (e.g., "500+ customers", "99.9% uptime", "$2B managed"). Numbers over logos when logos are weak. |
| `endorsement-bar` | Notable industry analyst, publication, or award mentioned in L0 | "Featured in..." or "Recognized by..." with publication/award logos. |

**Omit when:** Available logos are not recognizable to the target audience AND fewer than 3 verified proof points AND no notable endorsements. No social proof is better than weak social proof. Do NOT pad with unknown logos to hit a count threshold.

**One section, one variant.** Social Proof Bar is a single section slot. Select one variant. Do not split into two separate sections (e.g., a stat bar AND a logo row). If both logos and metrics are strong, prefer `logo-row` and surface key metrics in the hero trust line (as part of the Hero section) or in a Quantified Proof Block lower on the page. The `stat-bar` variant signal explicitly requires "recognizable logos unavailable" -- if logos are available, `stat-bar` does not qualify.

**Segment match caveat:** Do not show Fortune 500 logos to an SMB audience. Match logo tier to target segment.

#### 6. Problem Framing

Articulates the pain the audience is experiencing. Builds urgency before introducing the solution.

**Selection signal:** `traffic_awareness_stage` = unaware OR problem_aware. Also include when audience-messaging.md surfaces a primary challenge that is complex or multi-faceted.

| Variant | Selection Signal | Structure |
|---|---|---|
| `pain-cards` | Primary challenge has 3+ distinct symptoms or consequences | 3-card grid. Each card names a symptom and its business impact. Visual icons optional. |
| `narrative` | Primary challenge is a single coherent story (process breakdown, status quo failure) | Short paragraph or 2-3 sentences describing the current state. More editorial, less modular. |
| `contrast` | Strong before/after data available (from proof points or performance profile) | Two-column: "Without [solution]" vs. "With [solution]". Left column is the problem, right column is the outcome. |

**Omit when:** `traffic_awareness_stage` = product_aware OR most_aware. These audiences already know the problem. A dedicated problem section wastes page real estate and can feel condescending.

**Important distinction:** Omitting the problem *section* does not mean omitting all pain acknowledgment. For product-aware traffic, a brief pain reference in the hero subheadline ("Tired of X? [Product] does Y.") is fine. The rule is: no standalone problem section for Stage 4-5, but a sentence of empathy in the hero is acceptable.

#### 7. Solution Overview

Explains what the product/service does and how it addresses the problem. Bridges from pain to proof.

**Selection signal:** `traffic_awareness_stage` != most_aware. Almost always included. The variant determines depth.

| Variant | Selection Signal | Structure |
|---|---|---|
| `feature-grid` | `target_persona` is technical buyer OR `target_keywords` contain product/feature terms | 3-4 feature cards with names, short descriptions, optional icons. Emphasizes capabilities. |
| `outcome-grid` | `target_persona` is executive/business buyer | 3-4 outcome cards framed as results, not features. "Reduce X by Y%" not "Automated X engine." |
| `process-steps` | Service is complex, multi-step, or unfamiliar (consulting, advisory, implementation) | 3-4 numbered steps showing the engagement or product workflow. Demystifies the "how." |

**Omit when:** `traffic_awareness_stage` = most_aware AND offer_type = demo.

#### 8. Quantified Proof Block

Hard evidence. Specific metrics tied to named customers.

**Selection signal:** proof_points with tier = verified >= 1. At least one named customer with a specific, quantified outcome.

| Variant | Selection Signal | Structure |
|---|---|---|
| `single-stat` | 1 standout verified proof point significantly stronger than others | Large stat (e.g., "347% increase in pipeline") + 1-2 sentence context + customer attribution. Visual emphasis on the number. |
| `stat-trio` | 3+ verified proof points of comparable strength | Three stats side by side, each with customer name and metric. No deep narrative, just impact density. |
| `mini-case` | 1 verified proof point with enough narrative context for a story | Stat + 3-4 sentence narrative: who the customer is, what they were doing before, what changed, the result. Not a full case study, but more context than a bare stat. |

**Omit when:** No verified proof points exist. Do NOT use claimed or company-asserted metrics here.

#### 9. Testimonial Block

Qualitative social proof. Customer voice, not company voice.

**Selection signal:** proof_points with tier = supported >= 1 (named customer with praise but no hard metric). Also include when verified proof exists but you want emotional/relational proof alongside the quantified block.

| Variant | Selection Signal | Structure |
|---|---|---|
| `single-quote` | 1 strong testimonial, clear and specific | Large quote, customer name, title, company. Optional headshot placeholder. |
| `quote-pair` | 2 testimonials from different personas or segments | Two quotes side by side. Useful when page targets multiple roles or when showing breadth of satisfaction. |
| `video-testimonial` | Video testimonial URL available in L0 or brief | Embedded video thumbnail with play button + pull quote below. |

**Omit when:** No supported or verified proof points with quotable language exist. Do NOT fabricate testimonial language.

#### 10. Comparison Table

Direct competitive positioning. Shows why this solution wins against alternatives.

**Selection signal:** `target_keywords` contain competitor name, "vs", "alternative", "compare", OR `traffic_source` = paid_search with competitive intent.

| Variant | Selection Signal | Structure |
|---|---|---|
| `vs-table` | 1 primary competitor (threat_level = high) | Two-column comparison: "Us vs. Them." Feature/capability rows with check/x or descriptive cells. Name the competitor explicitly only if brief allows it. Use factual comparisons only; avoid disparaging language. |
| `category-table` | 2+ competitors OR positioning against a category | Multi-column table or "Why [Company]?" grid showing differentiation across the category, not against one rival. |
| `differentiator-list` | `white_spaces` from competitive-landscape.md has 3+ entries | Not a table. A vertical list of "Only with [Company]" differentiators. Each one names a capability competitors lack. Drawn directly from white_spaces. |

**Omit when:** No competitive keywords in brief AND campaign is not targeting competitive search intent.

#### 11. Objection Handling

Preempts objections and answers questions that block conversion.

**Two patterns (not mutually exclusive):**

**Pattern A: Distributed inline objections (preferred).** Objection-handling copy woven into the sections where the objection naturally arises. More effective than consolidated FAQ because it handles doubt at the point of friction.

**Pattern B: Consolidated FAQ block.** For objections that don't map to a specific content section, or when objection count is high enough to warrant a browsable format.

**Selection signal for Pattern B:** audience-messaging.md objection inventory contains 4+ objections that don't naturally attach to other sections. Also include when `offer_type` = consultation (high commitment = more pre-decision questions) or when the product/service is novel.

**Variants (Pattern B only):**

| Variant | Selection Signal | Structure |
|---|---|---|
| `accordion` | 4+ objections/questions | Expandable accordion. Each item: question as trigger, answer as expandable content. Keep as a content section, not near the form. |
| `inline-list` | 2-3 objections only | No accordion needed. Simple Q&A pairs displayed vertically. Less visual overhead. |

**Omit Pattern B when:** All substantive objections can be addressed inline within other sections AND form is simple (3 or fewer fields) AND offer is low-commitment.

**Planting doubts caveat:** Source FAQ content from actual customer objections (sales calls, Wynter tests, audience-messaging.md). Do NOT generate hypothetical concerns -- they can introduce objections the visitor hadn't considered.

**Copy agent responsibility:** Identify which objections from audience-messaging.md are best addressed inline (Pattern A) vs. standalone FAQ block (Pattern B). The section heading `## Objection Handling: accordion` or `## Objection Handling: inline-list` signals Pattern B. Pattern A objections are embedded in other section copy with no separate heading.

#### 12. Mid-Page CTA

A conversion reminder placed mid-scroll. Prevents long pages from losing ready-to-convert visitors.

**Selection signal:** Page contains a proof section (Quantified Proof, Testimonial, or Comparison) with additional content sections below it. Trigger is narrative position (after the first major proof block), not a fixed section count.

**Critical distinction:** Multiple placements of the *same* CTA improve conversion. Multiple *competing* CTAs (different goals) decrease it.

| Variant | Selection Signal | Structure |
|---|---|---|
| `simple-bar` | Default | Centered text + button on a visually differentiated background. Repeats primary CTA text exactly. |
| `value-recap` | Page is proof-heavy (2+ proof sections above this point) | One sentence summarizing the case so far + CTA button. "Ready to see results like these?" |
| `sticky-bar` | `device_split.mobile_pct` > 40% OR page has 8+ sections | Floating CTA bar that remains visible during scroll. Especially effective on mobile where scrolling back to the hero is high-friction. |

**Omit when:** Page has 4 or fewer total sections.

#### 13. Trust / Security Signals

Addresses privacy, compliance, or security concerns that could block form submission.

**Selection signal:** `form_strategy.fields` > 4 OR form collects sensitive data (phone, company revenue, employee count). Also include when `target_market.industries` includes regulated verticals (finance, healthcare, government, education).

| Variant | Selection Signal | Structure |
|---|---|---|
| `badge-row` | Compliance certifications exist (SOC 2, GDPR, HIPAA, ISO) | 2-3 certification badges/icons near the form. Maximum 3 badges. Unfamiliar badges decrease trust vs. no badge. 6+ seals create skepticism. |
| `reassurance-text` | No formal certifications but privacy is a concern | Short text block: "Your data is secure. We never share your information." + privacy link. Placed near or below the form. |

**Omit when:** Form is email-only capture AND industry is not regulated. For simple email capture, over-signaling security can remind visitors of risks they hadn't considered. If included for email-only forms, limit to a single line of reassurance text, never badges.

**Placement rule:** Trust signals must be visually proximate to the form fields. A badge in the footer doesn't help a form in the hero.

#### 14. Pricing Preview

Gives pricing context before the conversion ask. Research strongly favors transparency over gating.

**Selection signal: DEFAULT INCLUDE.** Include pricing information on most B2B SaaS landing pages. Non-transparent pricing pages have higher form submission rates, BUT transparent pricing pages generate more pipeline.

**Variants:**

| Variant | Selection Signal | Structure |
|---|---|---|
| `tier-cards` | 2-3 pricing tiers available from company-identity.md | Standard pricing card layout (tier name, price, features, CTA per tier). |
| `starting-at` | Single starting price or price range available | "Starting at $X/mo" with brief feature summary + "Get a custom quote" CTA. Minimum viable transparency. |
| `model-explainer` | Pricing model is known but exact numbers vary (usage-based, per-seat, custom scoping) | Explain how pricing works (per seat, per transaction, tiered by usage) without exact numbers. |
| `roi-frame` | No public pricing AND genuinely custom enterprise deals with variable scope | Frame investment in terms of return. "Companies see an average of X% ROI." Pair with interactive ROI calculator when feasible. This is the fallback, not the default. |

**Omit when:** Genuinely custom enterprise deals where pricing depends on scope discovery AND the client's sales process explicitly requires a consultative pricing conversation. Even then, include at minimum a `model-explainer`.

## Ordering Constraints

These replace the fixed 10-section sequence in `conversion-playbook.md` Section 5. The design agent applies these as hard rules when rendering copy.md sections into HTML.

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

11. **Proof sections appear in the middle third of the page.** After problem/solution framing, before objection handling and final CTA. Build the case in the middle, handle objections at the bottom.
12. **Comparison Table appears after at least one proof section.** Show your own results before positioning against competitors. Proof first, then contrast.
13. **Objection Handling (Pattern B consolidated FAQ) appears in the bottom third.** It's a pre-conversion cleanup, not a storytelling device. Pattern A inline objections appear wherever the friction arises.
14. **Trust / Security Signals appear near the form.** Whether the form is inline in the hero or in a modal, trust signals should be visually proximate to the input fields.
15. **Mid-Page CTA goes after the first major proof block,** not at a fixed halfway point. Once the strongest evidence has been presented, offer the action.
16. **Pricing Preview precedes Final CTA but follows proof sections.** Show value, then show price, then ask for conversion.

### Default Section Sequence (when signals are ambiguous)

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

## Section Count Guidance

The governing principle is from MECLABS: **match page length to the visitor's perceived cost/risk and their current awareness level.** High-commitment decisions warrant longer pages. Low-risk actions warrant shorter pages. Section count is a consequence of this principle, not a target.

- **Short page (4-5 sections):** Hero + Primary CTA, one content/proof section, Final CTA, Footer. Appropriate for `traffic_awareness_stage` = most_aware with a low-friction offer (content download, free trial).
- **Standard page (6-8 sections):** Most campaigns land here. Covers problem/solution framing, proof, and CTA with room for one or two contextual sections.
- **Long page (9-12 sections):** Complex offers, unaware/problem-aware traffic, or high-commitment actions (enterprise demos with 5+ field forms).

If the copy agent finds itself selecting 12+ sections, it should prioritize: cut the weakest proof section or collapse Solution Overview into Problem Framing as a contrast variant. Beyond 12, audit each section for whether it adds conversion-relevant information the visitor doesn't already have.
