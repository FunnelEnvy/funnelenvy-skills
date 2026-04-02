# Phase 2: Copy Agent

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/conversion-playbook.md (structural rules, CTA strategy, ordering constraints), modules/section-taxonomy.md (section selection, variant definitions, ordering constraints), modules/lp-audit-taxonomy.md (construct mode: D1, D2, D3, D5, D7, D8, D10)
> **Input:** `.claude/deliverables/campaigns/<slug>/brief.md` (Phase 1 output) + positioning context files (selective)
> **Output:** `.claude/deliverables/campaigns/<slug>/copy.md`

---

## Required Inputs

- `brief.md` in the campaign directory -- HARD REQUIREMENT. If missing: `[PRECONDITION FAILED]: Run Phase 1 (brief) first.`
- `modules/conversion-playbook.md` -- Sections 1-4, 6 only; Section 5 is ordering principles
- `modules/section-taxonomy.md` -- section selection signals, variant definitions, ordering constraints

## Selective Context Loading

Read the brief's frontmatter first. Then load positioning context based on what the brief references:

**Always load (frontmatter first, body only when noted):**

- `.claude/context/company-identity.md` (frontmatter: proof point counts by tier, target_market)
- `.claude/context/audience-messaging.md` (frontmatter: persona_count, value_themes, voice attributes; body: objection inventory -- loaded only when evaluating objection distribution in Step 6)

**Load if brief references competitive framing:**

- `.claude/context/competitive-landscape.md` (frontmatter: claim_overlap_score, top_competitors, white_spaces)

**Load when present:**

- `.claude/context/brand-voice.md` (frontmatter: tone_dimensions, vocabulary_stats)
- `.claude/context/performance-profile.md` (frontmatter: device_split, traffic_adequacy)

Do NOT load full positioning files end-to-end. Extract only what's specified above. Context window discipline matters here.

## Graceful Degradation

If `audience-messaging.md` is unavailable, the brief should already contain all needed proof points, voice rules, and persona messaging (extracted during Phase 1 or provided by the human). Use what's in the brief. If the brief also lacks this data, flag `[GAP]` markers and generate the best copy possible with what's available.

When a signal field is unavailable (context file missing), treat the signal as unmet. Contextual sections requiring that signal are excluded unless they have a default-include rule (e.g., Pricing Preview). Missing context files are graceful degradation, not failure.

---

## Workflow

### Step 1: Read Brief

Read the full `brief.md`. Extract:
- `traffic_awareness_stage`
- `traffic_source`
- `offer_type`
- `form_strategy` (fields, type, enrichment_tool)
- `post_submit`
- `target_persona`
- `target_keywords`
- `proof_points_count`
- `gaps`
- CTA button text (for consistency across all placements)
- Page pillars (pain/fix pairs)
- Headline strategy preference
- Proof points with placement instructions
- Testimonial selection
- Objection handling questions
- Language guidance (banned terms, required disclaimers)

### Step 2: Read L0/L1 Frontmatter

For each available context file, extract the signal fields listed in the Selective Context Loading section above. Note which files are present and which are missing.

Cross-reference proof points in the brief against the full proof library (from `company-identity.md` or `audience-messaging.md`) to ensure nothing was lost or misquoted during brief building.

### Step 3: Section Selection

Read `modules/section-taxonomy.md`. For each of the 14 section types, evaluate the selection signal against extracted fields:

- **Required sections** (Hero, Primary CTA, Final CTA, Footer): always included
- **Contextual sections**: include only when selection signal is met
- When a signal field is unavailable (context file missing), treat the signal as unmet (section excluded unless it has a "default include" rule like Pricing Preview)

Build the section manifest as a list of `{type, variant}` pairs.

**Taxonomy compliance rule:** Every section in the manifest must map to one of the 14 section types defined in the taxonomy. Do not invent custom section types (e.g., "Trust Metrics Bar," "Value Recap Strip"). If content doesn't fit an existing type, either place it within the closest matching section (as a design note or sub-element) or flag it as a gap for taxonomy update. Each section type appears at most once in the manifest (required sections appear exactly once).

### Step 3.5: Brand Component Matching (conditional)

Glob `.claude/context/` (and any client-specific context directories referenced in the brief) for:
- A file with `brand-design-system` in the filename or with `schema: brand-design-system` in frontmatter
- A companion `.html` file with `brand-components` in the filename (e.g., `brand-components.html`)

**If neither file is found:** Skip this step entirely. Proceed to Step 4. The pipeline runs with the generic section catalog. No component constraints apply.

**If a brand design system file is found:** Read its component inventory (YAML `components:` block). For each section in the manifest from Step 3, match it to an available brand component:

1. **Semantic matching.** Read component names, capabilities, and constraints from the YAML inventory. Infer which taxonomy sections each component can serve based on component semantics -- not explicit mapping fields. For example, a component named `hero` or `hero--split` with capabilities like "full-width, dark overlay, headline + subheadline" maps to Hero section types.

2. **Record match quality** per section:
   - **Exact:** One component directly serves this section type and variant
   - **Composition:** Two or more components combine to serve this section (e.g., hero-split + form-container for Hero with inline form)
   - **Close fit:** A component serves the section type but not the exact variant (e.g., a generic content section serving a specific narrative variant)
   - **Variant degradation:** No component serves the requested variant; degrade to the closest available variant that a component supports
   - **No match:** No component serves this section type at all

3. **Handle degradations and gaps:**
   - **Variant degradation:** Switch to the closest variant that has component support. Log in degradation list.
   - **No match (non-required section):** Remove the section from the manifest. Log as degradation with `level: section_removed`.
   - **No match (required section: Hero, Primary CTA, Final CTA, Footer):** Keep the section. Flag that the design agent will need to build it from scratch using design tokens only (no component snippet available). Log as degradation with `level: missing_component`.

4. **Extract and enforce component constraints.** For each matched component, read constraint fields from the YAML inventory (e.g., `max_items`, `max_chars`, character limits per sub-element). These constraints apply during Step 7 (Write Copy). Record constraints in memory for application during copy writing.

**Output annotations.** When writing each section in Step 7, include an HTML comment at the top of each section recording the brand component match:

```markdown
## Problem Framing: pain-cards
<!-- BRAND COMPONENT: spg-card-grid--3 + spg-card | MATCH: exact | CONSTRAINTS: max 4 cards, body max ~150 chars per card -->
```

For compositions:
```markdown
## Hero: pain-lead with Primary CTA: inline-form
<!-- BRAND COMPONENT: spg-hero--split + spg-form-container | MATCH: composition | CONSTRAINTS: headline max 80 chars, form max 5 fields -->
```

If no brand component exists for a section (missing_component level):
```markdown
## Mid-Page CTA: sticky-bar
<!-- BRAND COMPONENT: none (design agent builds from tokens) | MATCH: none -->
```

**Constraint enforcement during Step 7.** When writing copy for sections with component constraints:
- Respect character limits per element (headline, body, card excerpt, etc.)
- Respect item count limits (max cards, max stats, max logos)
- If a constraint would force cutting substantive content, note the trade-off in the section's HTML comment but still respect the constraint. The brand component's physical layout is not negotiable.

**Degradation logging.** After completing all section matching, add a `component_degradations` block to the frontmatter written in Step 8:

```yaml
component_degradations:
  - section: <section-type>
    original_variant: <original-variant-slug>
    resolved_variant: <resolved-variant-slug>
    component: <component-class-name>
    reason: "<why the degradation occurred>"
    level: variant_degradation | section_removed | missing_component
component_degradation_count: <int, total degradation entries>
brand_design_system: <filename of the brand design system file read>
brand_components_html: <filename of the brand components HTML file detected>
```

If no degradations occurred, still include the fields:
```yaml
component_degradations: []
component_degradation_count: 0
brand_design_system: <filename>
brand_components_html: <filename>
```

If no brand files were detected (Step 3.5 was skipped), omit all four fields entirely.

### Step 4: Variant Selection

For each included section, determine the specific variant using the variant selection signal from the taxonomy:

- Evaluate variant signals in table order (first match wins)
- If no variant signal matches, use the stated default variant
- If no default is stated, use the first variant in the table

### Step 5: Ordering

Arrange selected sections following the ordering constraints from `modules/conversion-playbook.md` Section 5:

- Validate all 10 hard rules. If any hard rule would be violated by the current ordering, reorder to comply. If compliance is impossible with the selected sections (which should not happen with the taxonomy's rules), STOP and flag the conflict.
- Apply soft rules as defaults. Deviate only with explicit rationale noted in a code comment in the output.
- If no signal-driven reason to reorder, use the default sequence from the taxonomy.

### Step 6: Objection Distribution

Read `audience-messaging.md` objection inventory (body, not just frontmatter). For each objection:

1. Identify which section it naturally attaches to (pricing objection -> Pricing Preview, complexity concern -> Solution Overview, security worry -> Trust Signals, etc.)
2. Assign as inline: weave into that section's copy (**Pattern A**)
3. Any objection that does not naturally attach to a specific section -> route to Objection Handling section (**Pattern B**)
4. If no residual objections need Pattern B AND an Objection Handling section was included, remove it from the manifest
5. If residual objections exist AND no Objection Handling section was included, add one
6. Mark each inline objection assignment with an HTML comment: `<!-- Inline objection: addresses "[objection text]" from audience-messaging.md -->`

### Step 7: Write Copy

**Pre-step: Bad Alternative Exercise (conversion-playbook.md Rule 2)**

Before writing any section, run the Bad Alternative Exercise using `company-identity.md` differentiators and category:

1. Name the specific bad alternative the target persona resorts to without this product
2. Name how this product is specifically better
3. Convert step 2 into an action statement

Write the exercise output before proceeding. This is the raw material for headline variants and the value prop thread that runs through the page.

**Section-by-section copy generation:**

For each section in manifest order:

- Write the section heading as `## [Section Name]: [variant-slug]` (e.g., `## Hero: pain-lead`)
- Write copy content following the variant's structural guidelines from the taxonomy
- Embed inline objection handling where assigned (Pattern A), marked with HTML comments
- Reference proof points by ID (P1, P2, etc.), not inline evidence
- Separate sections with `---` horizontal rules

**Hero section specifics:**

Generate three headline variants using the Bad Alternative Exercise output, strongest proof point, and #1 buying objection:

1. Pull the strongest proof point from `company-identity.md` Proof Point Registry. Prefer `verified` tier (named customer + specific metric). Fall back to `supported` if no verified proof exists. Note the proof point ID (e.g., P3) for traceability. If no proof points exist at verified or supported tier, note this gap and skip the proof-led headline variant.

2. Identify the #1 buying objection from `audience-messaging.md` target persona's `primary_challenge`. Common B2B objections: implementation time, integration complexity, requires technical skills, cost, requires organizational buy-in.

3. Generate three headline variants:
   - **Headline A (Pain-led):** Built from the Bad Alternative Exercise. Names the specific bad alternative and how the product eliminates it.
   - **Headline B (Proof-led):** Leads with the strongest verified proof point as a bold claim. Skip this variant if only `claimed` tier proof exists.
   - **Headline C (Objection-led):** Leads with the product benefit while preemptively handling the #1 buying objection.

   Each variant must pass the Specificity Litmus Test (conversion-playbook.md Rule 1): replace the company name with a competitor's. If the headline still works, rewrite it.

4. Generate hook line for each variant (1 sentence, `[OPTIONAL]` marker):
   - If headline is pain-led (A): hook adds the bold claim
   - If headline is proof-led (B): hook adds objection handling
   - If headline is objection-led (C): hook adds the bold claim

5. Mark which option is recommended and why.

- Subheadline: 1 sentence explaining HOW the company delivers the outcome.
- CTA button text: exactly as specified in the brief. Same text every time it appears.
- Social proof line: "Trusted by [X] companies" or similar, using a metric from the brief.
- If the brief has a `[GAP]` on ad copy, write headlines that message-match the target keywords directly.

**CTA Text Generation**

Apply conversion-playbook.md Rule 6 (CTA Narrative Continuation).

Generate CTA text that continues the recommended headline's narrative. The CTA is the actionable next step to fulfilling the headline's claim.

Run the litmus test: read the CTA in isolation. If it makes sense without the headline, it's too generic. Rewrite.

Generate one primary CTA and one alternate. Both must use the same narrative thread.

Form submission buttons (lightbox or inline) use direct, action-specific text ("Book My Demo," "Download the Guide") and do not need to follow the narrative rule.

**Lightbox Form Copy**

- Form headline (e.g., "Book Your 15-Minute Strategy Call")
- Form subheadline (e.g., "No commitment. See how we can help.")
- Field labels per the brief's form strategy
- Submit button text: echoes the CTA value, not "Submit"
- Micro-copy below submit: sets expectation for what happens next

**Post-Submit Flow Copy**

Based on the brief's post-submit type (calendar, asset, or thank-you):

- Confirmation headline
- What to expect next (1-2 sentences, specific)
- "Add to Calendar" text if applicable
- Link to one relevant piece of content (case study or guide) as nurture

### Step 8: Write Frontmatter

Write to `.claude/deliverables/campaigns/<slug>/copy.md` with frontmatter:

```yaml
---
schema: campaign-copy
schema_version: "2.0"
client: <company-name>
campaign: <campaign-slug>
sections:
  - type: <section-type>
    variant: <variant-slug>
  # ... one entry per section, in page order
section_count: <int>
objections_distributed_inline: <int, Pattern A count>
objections_in_faq_block: <int, Pattern B count, 0 if no FAQ section>
hero_variant: <slug, redundant with sections[0].variant but explicit for quick reference>
headline_approach: <matches hero variant: pain-lead | keyword-match | proof-lead>
recommended_headline: <A | B | C>
cta_text: <exact CTA text used across all CTA instances>
sections_with_proof: <int, count of sections containing proof point references>
proof_points_used: <P1, P3, P7, etc.>
gaps_carried_forward:
  - <any unresolved gaps from brief>
word_count: <int>
# Brand component fields (present only when brand design system detected in Step 3.5)
component_degradations:       # [] if no degradations, omit block if no brand files
  - section: str
    original_variant: str
    resolved_variant: str
    component: str
    reason: str
    level: str                # variant_degradation | section_removed | missing_component
component_degradation_count: int  # 0 if no degradations, omit if no brand files
brand_design_system: str      # filename, omit if no brand files
brand_components_html: str    # filename, omit if no brand files
generated_by: "landing-page-generator/copy v2.0"
last_updated: <ISO-8601>
---
```

### Step 9: Confirm

Present to the human:
- Which headline option is recommended and why
- Which testimonial was used
- Any gaps worked around
- Any sections where proof is weak
- Section manifest summary (types and variants selected)
- "Run `/landing-page-generator <company> <slug> --stage design` when ready for Phase 3."

---

## Construct-Mode Taxonomy Dimensions

Read `modules/lp-audit-taxonomy.md` Construct Mode section (table at bottom) plus the full dimension text for D1, D2, D5, D7, D8, and D10. These dimensions contain best-practice constraints that apply during copy generation, not just during QA. Specifically:

| Dimension | Construct-mode constraint |
|-----------|--------------------------|
| D1: Awareness-Stage Alignment | Set headline approach based on the brief's `traffic_awareness_stage`. Product-aware traffic gets proof-led or pain-led copy. Problem-aware gets problem agitation. Match CTA commitment level to awareness stage. |
| D2: Value Proposition Clarity | H1 must pass the caveman test and specificity audit. Subheader covers exactly one of: what the product is, or how the headline claim is achievable. No vague claims ("save time," "grow revenue") without specifics. |
| D3: Message Match | If ad copy is available in the brief, the H1 must echo the ad's core phrase. If unavailable, flag as `[GAP]` and optimize for target keyword match instead. |
| D5: Social Proof Strategy | Place proof by specificity gradient: ATF gets aggregate numbers/logos, mid-page gets named testimonials, bottom gets detailed metrics. At least 2 distinct proof types. Align strongest proof to the primary buying objection. |
| D7: Persuasion Psychology | Apply loss framing in at least one section (what they risk by not acting). Pre-empt top 2-3 objections before the FAQ. Include risk reversal language near the CTA if applicable ("no obligation," "cancel anytime"). Consider a micro-commitment path if the primary CTA is high-commitment. |
| D8: Copy Quality | Write at 7th-9th grade level. Follow the Rule of One (one persona, one big idea, one promise, one offer). Subheadings must tell a coherent story when read independently. No corporate speak, hedging language, or passive voice. |
| D10: Competitive Differentiation | Lead with white-space claims (where competitors are weak or absent). Avoid overlap-zone claims unless uniquely provable. If competitive-landscape.md shows high claim_overlap_score, the copy must work harder on differentiation. |

These are generation constraints, not a post-hoc checklist. Apply them as you write each section.

---

## Self-Check Checklist

Before writing the file, verify:

- [ ] Every section in the manifest maps to one of the 14 taxonomy section types (no invented types)
- [ ] No section type appears more than once in the manifest
- [ ] Every headline message-matches target keywords from the brief
- [ ] Every section in frontmatter `sections` array has a matching `## SectionName: variant` heading in body
- [ ] Proof points appear in at least 4 selected sections where applicable
- [ ] All CTA instances use identical text (hard rule #10)
- [ ] Ordering satisfies all 10 hard rules from conversion-playbook.md Section 5
- [ ] Every objection from audience-messaging.md is either inline (Pattern A with HTML comment) or in Objection Handling section (Pattern B) or noted as out-of-scope
- [ ] Zero banned terms from language guidance
- [ ] Required disclaimers present in footer section
- [ ] At least one named testimonial with full attribution (if proof exists)
- [ ] All headlines under 10 words
- [ ] Copy at 7th grade reading level or below (simple sentences, short paragraphs, no jargon unless it's buyer vocabulary)
- [ ] No competing secondary CTAs (one action, repeated)
- [ ] `[GAP]` markers preserved from brief and handled appropriately
- [ ] If brand design system detected: every section has a `<!-- BRAND COMPONENT: ... -->` HTML comment
- [ ] If brand design system detected: component constraints are respected in copy (char limits, item counts)
- [ ] If brand design system detected: all degradations logged in frontmatter with valid rationale
- [ ] If no brand files: no brand component comments or frontmatter fields present

If any check fails, fix it before writing. If it can't be fixed (e.g., no named testimonial exists), preserve the `[GAP]` marker.

---

## Copy Quality Standards

**Reading level:** 5th-7th grade. Short sentences. Active voice. No compound-complex structures.

**Proof density:** Every section should include at least one proof point where applicable. Hero, Problem Framing, Quantified Proof, and Objection Handling sections must have proof. Other sections may have proof but are not required.

**Specificity Litmus Test:** Numbers beat adjectives. "96% reduction" beats "dramatic improvement." "4 weeks" beats "fast turnaround." "NPS 93" beats "industry-leading satisfaction."

**Banned vague patterns:** "Transform," "Revolutionize," "Unlock," "Empower," "Streamline," "Next-generation," "World-class," "Cutting-edge," "Best-in-class." These are filler, not positioning.

**Voice consistency:** All copy follows the brand voice from the context files. Check against the "Sounds Like / Doesn't Sound Like" table if available.

**Scannability:** Paid traffic visitors are scanners. Use short paragraphs (2-3 sentences max per card/section). Front-load the most important information.
