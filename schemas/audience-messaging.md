> **Reference only.** The authoritative schema is inline in the corresponding phase file under `skills/positioning-framework/phases/`.
> If this file and the phase file disagree, the phase file wins.

---

# Audience & Messaging Schema (Layer 1)

<!-- v1.1: Added Money Quotes, per-insight confidence (H/M/L), frequency x intensity ranking, trigger events in persona grid, segment-before-synthesize discipline -->

**Version:** 1.1.0
**Output path:** `.claude/context/audience-messaging.md`
**Produced by:** `positioning-framework`
**Consumed by:** website-audit, ad copy, email sequences, copy briefs, content strategy, social content
**Replaces:** `audience-personas.md` + `messaging-framework.md` + `brand-voice.md` (merged pre-release; `brand-voice.md` is now also a standalone L1 file produced by the voice-inference skill; when it exists with confidence >= 3, this file defers to it for voice sections)

---

## Purpose

WHO the company talks to (personas), WHAT it says (messaging), and HOW it says it (voice). This single file replaces three separate L1 files by merging them into a logical flow: Personas -> Messaging -> Voice. Every content-producing skill reads this file.

**Boundary rule:** L0 (`company-identity.md`) has target segments, anti-personas, glossary, constraints, and the proof point registry as facts. This file has the analytical and creative layer: persona profiles, messaging hierarchy, value themes, voice profile, and language bank. L0 defines the company. This file defines how the company communicates.

---

## Schema Definition

### YAML Frontmatter

```yaml
---
schema: audience-messaging
schema_version: "1.1"
generated_by: positioning-framework
depth: standard                          # "quick" | "standard" | "deep"
last_updated: 2026-02-16
last_updated_by: positioning-framework
confidence: 3                            # 1-5, lowest section confidence within this file
company: "Company Name"

# Messaging summary
positioning_statement: "[Category] for [Persona] that [Big Unlock] by [Mechanism]."

# Persona summary
persona_count: 3
personas:
  - role: "CFO"
    segment: "PE-backed mid-market"
    primary_challenge: "transaction delays"
    tier: proven                             # proven | intended | speculative
  - role: "COO"
    segment: "high-growth"
    primary_challenge: "scaling operations"
    tier: proven
  - role: "CHRO"
    segment: "in transition"
    primary_challenge: "talent retention during change"
    tier: intended

# Value themes summary
value_theme_count: 3
value_themes:
  - name: "Theme name"
    proof_strength: strong               # strong | moderate | weak
  - name: "Theme name"
    proof_strength: moderate
  - name: "Theme name"
    proof_strength: weak

# Voice summary
tone: "professional, authoritative, direct"    # 3-5 adjectives from Voice Profile
person: "first plural"                          # "first plural" | "third person" | "mixed"
complexity: "accessible"                        # "jargon-heavy" | "accessible" | "mixed"
voice_consistency: "moderate"                   # high | moderate | low - see Voice Consistency Rating definition in messaging.md
voice_source: null                               # null if voice derived in-house, "brand-voice.md" if deferred to voice-inference skill

# Content counts
customer_language_count: 5                      # entries in Customer Language section
banned_terms_count: 3                           # entries in Banned Terms section
money_quote_count: 0                            # number of money quotes across all themes
trigger_events_per_persona: false               # true if trigger events populated for each persona

---
```

**Field notes:**
- `positioning_statement`: The one-liner from Section 7 (Positioning Statement). Must pass the competitor test.
- `personas`: Summary of each persona. Downstream skills check this to know which personas exist without reading the full body.
- `primary_challenge`: One-line version of core problem. Used for quick persona matching.
- `tier`: Persona evidence level. `proven` (buyer evidence exists), `intended` (website targets this role, no buyer evidence), `speculative` (client-requested only). Determines what depth fields can be populated.
- `value_themes`: Summary with proof strength. Downstream skills check before reading full body.
- `tone`: Derived from content analysis, not aspirational.
- `voice_consistency`: Categorical rating of cross-channel consistency. Valid values: `high` | `moderate` | `low`. Rating criteria defined in messaging.md Voice Consistency Rating section. `low` = significant inconsistency (a finding that should surface in the scorecard).

> **Confidence rule:** File-level confidence in frontmatter MUST equal the minimum of all section-level confidence scores in the body. This is a mechanical calculation, not a judgment.

**Downstream consumption pattern:** Read frontmatter first. If the structured summary has sufficient data for your needs (persona list, positioning statement, voice tone), use it. Read the full body only when you need the analytical narrative, specific proof points, or language bank entries.

---

### Markdown Body Sections

---

## PART 1: PERSONAS (WHO)

---

#### 1. Persona Messaging Grid (REQUIRED)

One row per primary persona. Each row must be distinct. If two personas have identical rows, the persona split is wrong.

```markdown
## Persona Messaging Grid

| Persona + Team | Tier | Their Daily Reality | Top 3 Challenges | What Changes With Your Solution | Value They'd Pitch to Their Boss |
|---------------|------|--------------------|-----------------|---------------------------------|--------------------------------|
| [Role, Team] | [tier] | [What their day looks like] | 1. [Challenge] 2. [Challenge] 3. [Challenge] | [Specific outcome] | [How they'd sell it internally] |
```

**Depth per persona:**
- Role and who reports to them
- What they're measured on (their KPIs)
- What tools/systems they live in daily
- What they've tried before and why it failed
- How they'd describe the problem to a peer (verbatim, not marketing language)
- What would make them a champion internally

**Trigger Events** (required per persona):
- [trigger] -- [frequency band: widespread | moderate | isolated]
Source: L0 Buying Triggers, VOC Extractions Lens 3, Switching Dynamics Push forces.

**Persona validation rules:**
- Every audience segment with a dedicated page on the company's website MUST have a persona row or an explicit exclusion note
- Every major service line maps to at least one persona
- Proven personas from case study quotes. Intended personas from website navigation/service pages. Speculative personas only from client request. Tag each persona's tier in the grid.

**Used by:** Every content skill. This is the "who am I writing for" reference.

---

#### 2. Cost of Alternatives (REQUIRED)

Economic impact of buyer alternatives (from competitive-landscape.md's Buyer Alternatives).

```markdown
## Cost of Alternatives

| Alternative | Cost to Buyer | Switching Cost to Your Solution | Quantified ROI (if evidence exists) |
|-------------|--------------|-------------------------------|-------------------------------------|
```

If no quantified ROI evidence exists, flag it: "No quantified ROI evidence found. For a company selling to [financially-oriented buyer], this is the #1 proof gap to close."

**Used by:** Copy briefs (ROI arguments), ad copy (cost comparison), sales enablement.

---

#### 3. Switching Dynamics (REQUIRED)

Four Forces analysis of what drives and prevents switching.

```markdown
## Switching Dynamics

| Force | Description | Implications for Messaging |
|-------|-------------|---------------------------|
| **Push** (away from status quo) | [Frustrations driving them to look] | Amplify in problem-aware content |
| **Pull** (toward your solution) | [What attracts them to you] | Lead with in solution-aware content |
| **Habit** (keeping them stuck) | [What makes switching feel hard] | Address as objections |
| **Anxiety** (fear of switching) | [What could go wrong] | Reduce with guarantees, proof, process clarity |
```

Messaging that only does Push + Pull without addressing Habit + Anxiety will generate interest but not conversion.

**Used by:** Messaging framework (funnel stage mapping), ad copy (push/pull messaging), objection handling.

---

#### 4. Objection Handling (REQUIRED)

```markdown
## Objection Handling

| Objection | Why They Think This | Response | Proof Point |
|-----------|--------------------|-----------| ------------|
```

Sources: sales team feedback, negative reviews, competitor comparison pages, FAQ pages, Reddit/forum discussions.

**Used by:** Copy briefs (objection preemption), sales enablement, FAQ content, messaging hierarchy (objection-response pairs).

---

#### 5. Value Prop Summary (REQUIRED)

One row per primary persona. Forces the positioning into a single sentence per buyer.

```markdown
## Value Prop Summary

| We help... (Persona) | Struggling with... (Problem) | Solved by... (Solution) | So they can... (Benefit) |
|----------------------|-----------------------------|-----------------------|-------------------------|
```

Each row must be distinct. Identical rows = bad persona segmentation.

**Used by:** Ad copy (headline generation), email subjects, sales one-liners.

---

#### 6. Anti-Value Prop (OPTIONAL)

Who the company does NOT help. Merged from L0's Anti-Personas with analytical depth.

```markdown
## Anti-Value Prop

| We DON'T help... (Anti-Persona) | Struggling with... (Anti-Problem) | NOT solved by us because... | Better served by... |
|--------------------------------|----------------------------------|---------------------------|-------------------|
```

Be specific. Every anti-persona row should point to an alternative that actually serves them better.

**Used by:** Ad targeting (exclusion), content strategy (what not to write about).

---

## PART 2: MESSAGING (WHAT)

---

#### 7. Positioning Statement (REQUIRED)

The anchor for all messaging.

```markdown
## Positioning Statement

[Category] for [Persona] that [Big Unlock] by [Mechanism].
```

Must include a verifiable or specific element. Must pass the competitor test (no competitor could use the same sentence).

**Used by:** Every content skill. This is the North Star message.

---

#### 8. Value Themes with Proof (REQUIRED)

Attributes are what you have. Value is what the customer gets.

```markdown
## Value Themes

| Value Theme | Supporting Capabilities | Proof Type | Specific Evidence | Proof Point IDs |
|------------|----------------------|-----------|-------------------|-----------------|
| [Theme]    | [Capabilities]       | Metric    | [specific data]   | P1, P2          |
```

Every value theme needs evidence. Themes without Level 1-3 proof are flagged as vulnerable.

Each theme includes `[HIGH]`/`[MEDIUM]`/`[LOW]` confidence tags and frequency x intensity bands (widespread/moderate/isolated x HIGH/MEDIUM/LOW).

**Proof hierarchy:**
1. Specific metrics with attribution
2. Named customer testimonials with role and company
3. Customer count or logo wall
4. Industry certifications or awards
5. Team credentials
6. Anecdotal claims with no attribution (weakest)

**Used by:** Copy briefs (which themes to use per page), ad copy (headline themes), email sequences (nurture themes).

---

#### 9. Messaging Hierarchy (REQUIRED)

Structured so downstream skills can grab the right message for the right context.

```markdown
## Messaging Hierarchy

### Primary Message (1 sentence)
[Positioning statement]

### Supporting Messages (pick 2-3 per asset)
1. [Message] (PROOF: P1, P2)
2. [Message] (PROOF: P3)
3. [Message] (PROOF: P4, P5)

### Per-Persona Lead Messages
- [Persona 1]: "[Their version of the primary message]"
- [Persona 2]: "[Their version]"

### Objection-Response Pairs (for sales pages, FAQ, retargeting)
- "[Objection]" -> "[Response]" (PROOF: P_)
```

Every message references proof point IDs. No unsupported claims.

**Used by:** Copy briefs (message selection), email sequences (per-email message), ad copy (per-ad message).

---

#### 10. Seasonal Relevance (REQUIRED)

```markdown
## Seasonal Relevance

| Quarter | Relevant Services/Products | Why Urgent Now | Messaging Angle | Content Opportunity |
|---------|--------------------------|---------------|-----------------|-------------------|
| Q1 | | | | |
| Q2 | | | | |
| Q3 | | | | |
| Q4 | | | | |

### Ongoing Trends
- [Regulatory changes, technology shifts, market conditions, competitor moves]
```

**Used by:** Content strategy (editorial calendar), ad copy (seasonal campaigns), email sequences (timely triggers).

---

#### 11. Channel Adaptations (REQUIRED)

Same message adapted per channel constraints.

```markdown
## Channel Adaptations

| Channel | Constraint | Primary Message Adaptation | Proof to Include |
|---------|-----------|---------------------------|-----------------|
| Homepage H1 | 6-12 words | [adaptation] | None (subhead carries proof) |
| Homepage subhead | 15-25 words | [adaptation] | P1 or P2 (strongest metric) |
| LinkedIn ad (single image) | Primary text: 150 chars above fold (600 max). Headline: 70 chars. | [adaptation] | One stat |
| Google Search (RSA) | 3 headlines x 30 chars each + 2 descriptions x 90 chars each | [adaptation] | H1: brand/category. H2: differentiator. H3: proof or CTA. |
| Meta ad (Facebook/Instagram) | Primary text: 125 chars above fold. Headline: 40 chars. | [adaptation] | None (visual-first) |
| Email subject line | 40-50 chars | [adaptation] | None |
| Sales one-liner | 15 seconds spoken (~30-40 words) | [adaptation] | One proof point |
| Conference intro | 30 seconds spoken (~75 words) | [adaptation] | Name-drop + metric |
| Case study headline | 8-15 words | [adaptation] | Format: "[Client type] + [outcome] + [timeframe or metric]" |
| Webinar/event title | 8-12 words | [adaptation] | Promise a specific takeaway |
```

**Used by:** Every channel-specific content skill.

---

## PART 3: VOICE (HOW)

---

#### 12. Voice Profile (REQUIRED)

```markdown
## Voice Profile

- **Tone:** [formal / conversational / technical / casual / authoritative - based on observed patterns]
- **Person:** [first person "we" / third person / mixed]
- **Complexity:** [jargon-heavy / accessible / mixed - note if it shifts by page]
- **Personality:** [3-5 adjectives derived from content analysis, not aspirational]
- **Emotion:** [reserved / empathetic / urgent / confident - default emotional register]
```

Derived from observed patterns across website, LinkedIn, case studies, careers page. NOT aspirational.

**Used by:** Every content skill as the voice baseline.

---

#### 13. Channel Consistency Audit (REQUIRED)

```markdown
## Channel Consistency Audit

| Channel | Observed Tone | Matches Core Voice? | Notes |
|---------|--------------|--------------------| ------|
| Homepage | | Yes / No / Partial | |
| About page | | Yes / No / Partial | |
| Case studies | | Yes / No / Partial | |
| LinkedIn posts | | Yes / No / Partial | |
| Careers page | | Yes / No / Partial | |
| Glassdoor reviews | | N/A | [Internal vs. external voice comparison] |
```

Inconsistency is a finding. At least 4 channels audited.

**Used by:** Website audit (voice consistency check), brand strategy.

---

#### 14. Competitor Voice Comparison (REQUIRED)

```markdown
## Competitor Voice Comparison

| Company | Tone | Differentiating? |
|---------|------|-----------------|
| [Target company] | [tone summary] | - |
| [Competitor A] | [tone summary] | [Distinct or interchangeable?] |
```

If every company sounds the same, that IS the finding. Flag voice white space.

**Used by:** Copy briefs (voice differentiation), brand strategy.

---

#### 15. Language Bank (REQUIRED)

```markdown
## Language Bank

### Customer Language (use in headlines, ads, email subjects)
- "[exact phrase]" - Source: [G2 review / Reddit / testimonial]

### Company Language (use in body copy, about pages)
- "[exact phrase]" - Source: [homepage / about / LinkedIn]

### Competitor-Owned Terms (AVOID in differentiating copy)
- "[term]" - Owned by: [Competitor]

### Banned Terms (NEVER use)
- "[term]" - Reason: [why]

### Category Terms (use in SEO, paid search, category-level copy)
- "[term]" - Search validation: [Google Trends / search quality]
```

Customer Language: target 5+ entries from actual reviews/forums. If fewer than 5 genuine entries exist in available sources, include what's found and mark `[N/5 found - insufficient public data]`. Never invent entries to hit the target. Banned Terms must be populated.

**Money Quotes** (sub-section):
Per value theme, 2-3 verbatim quotes directly usable in copy/ads/landing pages. Format: `"[quote]" -- [source type, date, segment]`. When public VOC insufficient: `[NO PUBLIC VOC - Interview Data Needed]` with hypothesized quotes labeled `[HYPOTHESIZED - NOT VERIFIED]`.

**Used by:** Every content skill reads this before writing anything. Primary input for copywriting, email, and ad copy skills.

---

#### 16. Do/Don't Examples (REQUIRED)

```markdown
## Do / Don't Examples

| Do (on-brand) | Source | Don't (off-brand or generic) | Source |
|---------------|--------|------------------------------|--------|
| "[actual sentence]" | [page] | "[actual sentence]" | [page] |
```

Real examples from the company's content. Not invented.

**Used by:** Copy briefs (voice calibration), content review.

---

#### 17. Brand Narrative Tensions (OPTIONAL)

<!-- Not currently consumed downstream. Added for schema completeness. Potential future consumers: scoring.md (positioning health check), website-audit. -->

Cases where the company's marketing campaigns, brand messaging, or public statements contradict the website positioning or category language. These tensions are strategic opportunities if resolved, or credibility risks if ignored.

```markdown
## Brand Narrative Tensions

| Tension | Where It Appears | Intentional Provocation or Accidental? | Recommended Resolution |
|---------|-----------------|---------------------------------------|----------------------|
| [e.g., Campaign says "Consulting is Dead" but website says "consulting firm"] | [Campaign page vs title tag] | [Intentional brand provocation] | [Keep campaign for differentiation, maintain category terms in SEO-critical locations] |
```

If no tensions found, write: "No brand narrative tensions detected." Do not skip the section.

**Used by:** No current downstream consumer. Produced by messaging.md Agent 3 as part of voice analysis. Intended future consumers: scoring.md (credibility risk flag), website-audit hypothesis roadmap.

---

#### 18. Voice Rules for Downstream Skills (REQUIRED)

```markdown
## Voice Rules

Actionable constraints for content production:
- [e.g., "Always use first person plural. Never third person."]
- [e.g., "Technical terms are fine for practitioner personas. Simplify for executive personas."]
- [e.g., "No exclamation marks. Confidence comes from specificity, not punctuation."]
- [e.g., "Avoid superlatives unless backed by a proof point."]
```

At least 3 actionable rules.

**Used by:** Every content skill as hard constraints.

---

## Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

**Personas:**
- [ ] YAML frontmatter has all required fields including persona summary
- [ ] Persona Messaging Grid has entries from verified sources (target: 2+ distinct personas; fewer is acceptable with gap marker)
- [ ] Every major service line maps to at least one persona
- [ ] Cost of Alternatives has entries from verified sources (target: 3+ alternatives with economic impact; fewer is acceptable with gap marker)
- [ ] Switching Dynamics covers all four forces
- [ ] Objection Handling has entries from verified sources (target: 3+ objections with sources; fewer is acceptable with gap marker)
- [ ] Value Prop Summary has distinct rows per persona

**Messaging:**
- [ ] Positioning statement present and passes competitor test
- [ ] Value themes with proof present (target: 3+; every theme has Level 1-3 evidence or is flagged as vulnerable; fewer is acceptable with gap marker)
- [ ] Messaging hierarchy references proof point IDs (no unsupported claims)
- [ ] Per-persona lead messages present for each persona in the grid
- [ ] Seasonal relevance covers at least current and next quarter
- [ ] Channel adaptations cover at minimum: homepage H1, LinkedIn ad, Google Search RSA, email subject, sales one-liner, case study headline

**Voice:**
- [ ] Voice Profile derived from observed content, not aspirational
- [ ] Channel Consistency Audit covers channels found (target: 4+; fewer is acceptable with gap marker)
- [ ] Competitor Voice Comparison includes competitors found (target: 2+; fewer is acceptable with gap marker)
- [ ] Language Bank Customer Language has entries from real sources (target: 5+; fewer is acceptable with gap marker)
- [ ] Language Bank Banned Terms is populated
- [ ] Do/Don't Examples use actual sentences from company content
- [ ] Voice Rules has actionable constraints (target: 3+; fewer is acceptable with gap marker)

**VOC Integration:**
- [ ] Money Quotes section present with at least one theme covered
- [ ] Per-insight confidence tags present on value themes and pain points
- [ ] Trigger Events populated per persona
- [ ] Frequency x intensity bands used in Value Themes ordering

**General:**
- [ ] `confidence` value equals the lowest section confidence within this file
- [ ] All proof point ID references (P1, P2, etc.) resolve to entries in company-identity.md's Proof Point Registry

---

## Versioning Rules

- Update `last_updated` and `last_updated_by` when modifying
- Preserve `generated_by` as the original producing skill
- Can only RAISE confidence scores, never lower them
- When adding personas, do not remove existing ones without explicit justification
- Language Bank entries are additive; do not remove existing entries without justification
- Mark extensions: `<!-- extended by [skill-name] [date] -->`

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
```
