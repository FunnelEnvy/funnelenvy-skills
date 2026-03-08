# Phase 2: Copy Agent

> **Reads:** agent-header.md (shared rules) + this file
> **Depends on:** modules/conversion-playbook.md (structural rules, section order, CTA strategy)
> **Input:** `.claude/deliverables/campaigns/<slug>/brief.md` (Phase 1 output) + positioning context files (selective)
> **Output:** `.claude/deliverables/campaigns/<slug>/copy.md`

---

## Required Inputs

- `brief.md` in the campaign directory -- HARD REQUIREMENT. If missing: `[PRECONDITION FAILED]: Run Phase 1 (brief) first.`
- `modules/conversion-playbook.md` -- structural rules, section order, CTA strategy, form strategy, copy guidelines

## Selective Context Loading

Read the brief's frontmatter first. Then load positioning context based on what the brief references:

1. **Always load** the persona section matching `target_persona` from `audience-messaging.md` (one persona only, not the full file).
2. **Always load** the proof points library from `audience-messaging.md` (all tiers: strong, moderate, weak).
3. **Always load** the objection handling table from `audience-messaging.md`.
4. **Always load** voice rules and language guidance from `audience-messaging.md`.
5. **Load if brief references competitive framing:** top 2-3 competitors from `competitive-landscape.md`.
6. **Load if brief references differentiators:** differentiators section from rendered executive summary.

Do NOT load full positioning files end-to-end. Extract only what's specified above. Context window discipline matters here.

## Graceful Degradation

If `audience-messaging.md` is unavailable, the brief should already contain all needed proof points, voice rules, and persona messaging (extracted during Phase 1 or provided by the human). Use what's in the brief. If the brief also lacks this data, flag `[GAP]` markers and generate the best copy possible with what's available.

---

## Workflow

### Step 1: Read Brief

Read the full `brief.md`. Extract:
- Target keywords (for message matching)
- CTA button text (for consistency across 3 placements)
- Page pillars (3 pain/fix pairs)
- Headline strategy preference (pain-forward, keyword-forward, proof-forward, or all 3)
- Proof points with placement instructions
- Testimonial selection
- Objection handling questions
- Form strategy details
- Post-submit flow type
- Language guidance (banned terms, required disclaimers)
- Any `[GAP]` markers (handle with extra care)

### Step 2: Read Conversion Playbook

Read `modules/conversion-playbook.md`. Focus on:
- Section 2: CTA Strategy (placement rules, copy rules, lightbox default)
- Section 3: Form Strategy (field defaults, multi-step rules, UX)
- Section 4: Post-Submit Flow (flow options, confirmation page elements)
- Section 5: Page Section Order (the 9-section sequence + copy guidelines per section)

### Step 3: Load Positioning Context

Load the selective context described above. Cross-reference proof points in the brief against the full proof library to ensure nothing was lost or misquoted during brief building.

### Step 4: Generate Copy

Produce copy for every section in the playbook's section order. Each section is a markdown heading in the output file.

**Section 1: Hero**
- Generate headline options per the brief's headline strategy:
  - Option A: Pain-forward (lead with buyer's problem)
  - Option B: Keyword-forward (lead with primary search term)
  - Option C: Proof-forward (lead with strongest metric)
- Mark which option is recommended and why.
- Subheadline: 1 sentence explaining HOW the company delivers the outcome.
- CTA button text: exactly as specified in the brief. Same text every time it appears.
- Social proof line: "Trusted by [X] companies" or similar, using a metric from the brief.
- If the brief has a `[GAP]` on ad copy, write headlines that message-match the target keywords directly.

**Section 2: Social Proof Bar**
- Header text: "Trusted by teams at" or equivalent.
- Logo list: the 5 logos from the brief, in order.

**Section 3: Problem/Solution Cards**
- 3 cards from the brief's Page Pillars.
- Card headline: buyer's pain (from the brief).
- Card body: how the company solves it (2-3 sentences max).
- Each card must connect to at least one proof point. If a pillar has no proof, flag it as `[WEAK: no supporting proof point]`.

**Section 4: Quantified Proof**
- 2-3 stats from the brief's metrics table. Use large-number formatting (e.g., "96%" not "ninety-six percent").
- 1 named testimonial with full attribution (name, title, company). Exactly as sourced from the brief.
- If the brief flagged a testimonial gap, note: `[GAP: no named testimonial available. Consider sourcing one before launch.]`

**Section 5: Mid-Page CTA**
- Headline: benefit-oriented, different wording from hero but same intent.
- Supporting micro-copy: 1 line reinforcing low commitment or specificity.
- Button text: same CTA text as hero. Identical.

**Section 6: How It Works (optional)**
- Include only if the brief specifies this section.
- 3 steps: clear, numbered, action-oriented.
- Keep each step to 1-2 sentences.

**Section 7: FAQ / Objections**
- 3-5 questions from the brief's objection handling table.
- Each question phrased as the buyer would ask it (not seller objection-handling language).
- Each answer must include at least one proof point or data reference.
- Answers should be 2-4 sentences. Concise. No filler.

**Section 8: Final CTA Block**
- Headline: urgency or social proof framing. Different from hero and mid-page.
- Supporting micro-copy: reinforces what happens next.
- Button text: same CTA text. Identical to hero and mid-page.

**Section 9: Footer**
- Logo placement
- Copyright line
- Legal links: Privacy Policy, Terms
- Required disclaimers from the brief (e.g., "Acme Corp is not a CPA firm.")
- Nothing else. No sitemap, no social icons, no blog links.

**Lightbox Form Copy**
- Form headline (e.g., "Book Your 15-Minute Strategy Call")
- Form subheadline (e.g., "No commitment. See how we can help.")
- Field labels per the brief's form strategy
- Submit button text: echoes the CTA value, not "Submit"
- Micro-copy below submit: sets expectation for what happens next

**Post-Submit Flow Copy**
- Based on the brief's post-submit type (calendar, asset, or thank-you)
- Confirmation headline
- What to expect next (1-2 sentences, specific)
- "Add to Calendar" text if applicable
- Link to one relevant piece of content (case study or guide) as nurture

### Step 5: Self-Check

Before writing the file, verify:

- [ ] Every headline message-matches target keywords from the brief
- [ ] Proof points appear in at least 4 sections (hero, problem/solution, proof, FAQ)
- [ ] Same CTA text appears in exactly 3 locations (hero, mid-page, final block)
- [ ] Zero banned terms from language guidance
- [ ] Required disclaimers present in footer section
- [ ] At least one named testimonial with full attribution
- [ ] All headlines under 10 words
- [ ] Copy at 7th grade reading level or below (simple sentences, short paragraphs, no jargon unless it's buyer vocabulary)
- [ ] No competing secondary CTAs (one action, repeated)
- [ ] `[GAP]` markers preserved from brief and handled appropriately

If any check fails, fix it before writing. If it can't be fixed (e.g., no named testimonial exists), preserve the `[GAP]` marker.

### Step 6: Write Output

Write to `.claude/deliverables/campaigns/<slug>/copy.md` with frontmatter:

```yaml
---
schema: campaign-copy
schema_version: "1.0"
client: <company-name>
campaign: <campaign-slug>
headline_approach: <pain|keyword|proof|all-three>
recommended_headline: <A|B|C>
cta_text: <exact CTA text>
sections_with_proof: <int out of 9>
gaps_carried_forward:
  - <any unresolved gaps from brief>
word_count: <int>
generated_by: "landing-page-generator/copy"
last_updated: <ISO-8601>
---
```

### Step 7: Confirm

Present to the human:
- Which headline option is recommended and why
- Which testimonial was used
- Any gaps worked around
- Any sections where proof is weak
- "Run `/landing-page-generator <company> <slug> --stage design` when ready for Phase 3."

---

## Copy Quality Standards

**Reading level:** 5th-7th grade. Short sentences. Active voice. No compound-complex structures.

**Proof density:** Every section should include at least one proof point. Sections 1 (hero), 3 (problem/solution), 4 (proof), and 7 (FAQ) must have proof. Sections 2, 5, 6, 8 may have proof but are not required.

**Specificity:** Numbers beat adjectives. "96% reduction" beats "dramatic improvement." "4 weeks" beats "fast turnaround." "NPS 93" beats "industry-leading satisfaction."

**Voice consistency:** All copy follows the brand voice from the context files. Check against the "Sounds Like / Doesn't Sound Like" table if available.

**Scannability:** Paid traffic visitors are scanners. Use short paragraphs (2-3 sentences max per card/section). Front-load the most important information.
