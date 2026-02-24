# Phase: Messaging, Personas & Voice

**Covers:** Persona messaging grids, value themes, messaging hierarchy, brand voice, language bank, switching dynamics, objection handling, and channel adaptations.

**Produces:** `.claude/context/audience-messaging.md` (merged output replacing audience-personas.md + messaging-framework.md + brand-voice.md)

**Reads:** Company identity (L0), competitive landscape (L1) for competitive context

---

## Shared Agent Rules

**Shared agent rules** (Proof Point Protocol, Content Integrity Check, Confidence Rules) are in `agent-header.md`. Read that file first.

---

## Required Inputs

Before starting messaging analysis, verify these preconditions:

1. `.claude/context/company-identity.md` exists with confidence >= 3
2. `.claude/context/competitive-landscape.md` exists
3. Competitive landscape frontmatter `competitors_analyzed` >= 1
4. L0 body sections populated:
   - Target Segments
   - Stated Differentiators
   - Proof Point Registry (at least 1 proof point)
5. `.claude/context/_research-extractions.md` exists (OPTIONAL but strongly recommended)
   - Run the Extractions Validation check:
     1. **Frontmatter check:** File has valid YAML frontmatter with `schema: research-extractions` and `total_pages` field.
        - If frontmatter exists and is valid: use the Index table for selective reads.
        - If frontmatter is missing: scan for `## N. [Page Type]` headers to discover available entries.
        - If file is entirely absent or empty: treat as absent.
     2. **Entry body spot-check:** For each entry you want to read, verify the corresponding `## N. [Page Type]` section exists. If missing: skip, note in research log.
   - If valid: read the Index table. Then read entries for: Homepage, About, Case Study, and Review Site page types. Use the raw content for voice derivation, problem framing analysis, and emotional language patterns.
   - If absent or invalid: proceed with L0 and L1 data only (current behavior). Note in completion summary: "No research extractions available. Voice profile and language bank derived from structured L0 data only. Confidence capped at 3 for voice-dependent sections."

If any precondition fails:
- STOP. Report to orchestrator with specific missing precondition.
- If only competitive-landscape.md is missing/empty, messaging CAN proceed with reduced scope: skip Switching Dynamics (Four Forces) and Competitor Voice Comparison sections. Flag these as `[SKIPPED - NO COMPETITIVE DATA]`.

**Note:** This agent does not perform web fetches. All source data comes from L0 (company-identity.md) and L1 (competitive-landscape.md). If `.claude/context/_fetch-registry.md` exists, you may consult it to understand extraction quality of upstream data but do not fetch URLs yourself.

---

## Raw Content Consumption

When `_research-extractions.md` is available, use it for these specific purposes:

### Voice Profile Derivation
Read Homepage, About, and Case Study page entries. Analyze the raw copy directly for tone (formal/casual, technical/accessible), person (1st/3rd), jargon density, and voice patterns.

Use 3-5 verbatim copy samples from the Key Content Sections as voice examples in the Voice Profile. Attribute each sample to its source page.

### Language Bank Population
Read Review Site extractions for verbatim customer language. Read Case Study extractions for "before" state language and outcome descriptions. These feed the Customer Language column of the Language Bank.

### Problem Framing for Switching Dynamics
Read Homepage and Case Study page entries for problem-framing patterns (fear, aspiration, urgency, rational). "Push" forces should use the company's actual problem language, not paraphrased versions from L0.

### Objection Surface Mining
Read FAQ and Pricing page entries for objection preemption patterns. These are direct inputs to the Objection Handling table.

---

## Depth Behavior

Read the DEPTH parameter from the task prompt.

### standard
- Persona messaging for top 2-3 segments from L0
- Value themes derived from L0 differentiators + competitive gaps
- Standard switching dynamics analysis
- Output length: 2,000-3,500 words

### deep
- Persona messaging for all segments from L0
- Extended value theme analysis with evidence mapping
- Deep switching dynamics with Four Forces framework
- Channel-specific messaging adaptations
- Output length: 3,500-5,000 words

### quick
- This agent should NOT be launched at quick depth.
- If launched anyway: produce a stub audience-messaging.md with confidence: 1 and a single section noting "Quick depth does not include messaging analysis. Run at standard or deep depth."

---

## Graceful Degradation

If you cannot complete all sections (insufficient input data, context limits):

1. **Prioritize in this order:** Persona Messaging Grid, Value Themes, Messaging Hierarchy, Voice Profile, Language Bank. These are the highest-value outputs. Switching Dynamics, Seasonal Relevance, and Channel Adaptations are lower priority.
2. **Always write output to disk.** Partial audience-messaging.md is better than none. Agent 4 needs something to read.
3. **Mark incomplete sections with `[INCOMPLETE - reason]`.** E.g., `[INCOMPLETE - no review data available for Language Bank customer language entries]`.
4. **Set confidence accordingly.** Missing persona data = confidence 2. No customer language from real sources = confidence 2.

---

## Output Length Targets
- Quick: N/A (skipped at quick depth)
- Standard: 2,000-3,500 words
- Deep: 3,500-5,000 words

These are targets, not hard limits. Prefer concise, evidence-dense output over padding. If a section has thin data, make it shorter, not fluffier.

---

## Value Themes with Proof

Attributes are what you have. Value is what the customer gets. Every value theme needs evidence.

| Value Theme | Supporting Capabilities | Proof Type | Specific Evidence | Proof Point IDs |
|------------|----------------------|-----------|-------------------|-----------------|
| [Theme] | [Capabilities] | Metric / Testimonial / Case study / Certification | [specific data] | P1, P2 |

**Proof hierarchy (strongest to weakest):**
1. Specific metrics with attribution (e.g., "reduced close time by 40% for [Client]")
2. Named customer testimonials with role and company
3. Customer count or logo wall
4. Industry certifications or awards
5. Team credentials (e.g., "Big 4 alumni")
6. Anecdotal claims with no attribution (weakest, flag these)

### Value Theme Proof Assessment

For each value theme, assess proof status:

**Proven** (safe to lead with):
- Level 1-2 proof (specific metrics with attribution, named testimonials)
- Claim has been validated by someone outside the company
- Frontmatter mapping: `proof_strength: strong`

**Claimed** (use with caveats):
- Level 3-5 proof (customer count, certifications, credentials)
- OR: structural capability exists but no customer has confirmed the specific value claim
- Downstream: can headline this theme but must pair with a proof point. Cannot use as the primary differentiator without stronger evidence.
- Frontmatter mapping: `proof_strength: moderate`

**Aspirational** (do not lead with):
- Level 6 proof only (anecdotal, no attribution)
- OR: capability exists on paper but no evidence of customer adoption
- Downstream: body copy only. Never headline. Flag for proof development.
- Frontmatter mapping: `proof_strength: weak`

Write the assessment in the Value Themes table's "Proof Type" column as: "[Level] ([assessment])" -- e.g., "Metric (Proven)" or "Structural (Claimed)".

---

## Quantified Value & Cost of Alternatives

For each buyer alternative (from competitive-landscape.md > Buyer Alternatives), estimate the economic impact:

| Alternative | Cost to Buyer | Switching Cost to Your Solution | Quantified ROI (if evidence exists) |
|-------------|--------------|-------------------------------|-------------------------------------|
| Internal workaround | | | |
| Freelancer/contractor patchwork | | | |
| Cheaper/simpler tool | | | |
| Status quo / do nothing | | | |

**Where to find ROI data:** Case studies with measurable outcomes (strongest), testimonials referencing specific improvements, industry benchmarks, press releases announcing partnership results.

If no quantified ROI evidence exists, flag it explicitly: "No quantified ROI evidence found. For a company selling to [financially-oriented buyer], this is the #1 proof gap to close."

When no quantified ROI exists, produce a **ROI Data Collection Brief** as an appendix to audience-messaging.md. This turns a gap callout into an action item the client can execute immediately.

```markdown
### ROI Data Collection Brief

No quantified client ROI evidence was found in public sources. The following questions, sent to 3-5 past clients, would close this gap:

1. [Metric-specific question, e.g., "What was your month-end close time before and after engagement?"]
2. [Metric-specific question, e.g., "How many hours per week did your team spend on [task] before vs after?"]
3. [Cost question, e.g., "What were you spending on [alternative] before switching?"]
4. [Timeline question, e.g., "How long did [process] take before vs after?"]
5. [Outcome question, e.g., "What revenue/pipeline impact can you attribute to [deliverable]?"]

**Suggested format for client responses:** "[Metric] went from [X] to [Y] over [timeframe]."
**Minimum viable proof:** One named client with one before/after metric.
```

Tailor every question to the company's specific services and buyer personas. No generic questions.

---

## Persona Messaging Grid

Build one row per primary persona.

| Persona + Team | Tier | Their Daily Reality | Top 3 Challenges | What Changes With Your Solution | Value They'd Pitch to Their Boss |
|---------------|------|--------------------|-----------------|---------------------------------|--------------------------------|

**Depth requirements per persona:**
- Role and who reports to them
- What they're measured on (their KPIs)
- What tools/systems they live in daily
- What they've tried before and why it failed
- How they'd describe the problem to a peer (verbatim language, not marketing language)
- What would make them a champion internally for buying your solution

### Persona Tiers

**Proven Persona** (confidence 3-5): At least ONE of these exists:
- Named testimonial from someone in this role
- Case study featuring this buyer type
- Review or forum post from this role mentioning the company
Full narrative allowed. All depth fields populated.

**Intended Persona** (confidence 2): Company website targets this role (dedicated page, service line, or segment mention) but no direct buyer evidence exists.
- Grid row: populate Role, Reporting Structure, KPIs, Top 3 Challenges (inferrable from job postings and industry knowledge)
- Grid row: DO NOT populate "Their Daily Reality" narrative, "Value They'd Pitch to Their Boss" quote, or emotional state. These require real buyer evidence. Write: "[NEEDS CLIENT INPUT -- no buyer evidence for this role]"
- Depth fields: populate only what's discoverable (role, KPIs, tools). Mark all others as [NEEDS CLIENT INPUT].

**Speculative Persona** (confidence 1): Neither website targeting nor buyer evidence. Only include if client explicitly requested it.
- Grid row: single row with role name and "[CLIENT-REQUESTED -- no public evidence this is a buyer]"
- No depth fields. No narrative.

Never write confident narrative for a persona you're guessing at. A half-empty row with honest gaps is more valuable than a plausible-sounding fabrication that downstream skills treat as fact.

**Persona validation rules:**
- Every audience segment with a dedicated page on the company's website MUST have a persona row or an explicit exclusion note
- Every major service line maps to at least one persona
- Proven personas from case study quotes. Intended personas from website navigation/service pages. Speculative personas only from client request. Tag each persona's tier in the grid.
- Never silently drop a persona. If excluded, note why.

---

## Seasonal & Trend Relevance

| Quarter | Relevant Services/Products | Why Urgent Now | Messaging Angle | Content Opportunity |
|---------|--------------------------|---------------|-----------------|-------------------|
| Q1 | | | | |
| Q2 | | | | |
| Q3 | | | | |
| Q4 | | | | |

**Ongoing trends** (not seasonal but currently relevant): Regulatory changes, technology shifts, market conditions, competitor moves.

### When Seasonality is Weak

If the company's services have no strong quarterly variation:

1. Write: "No strong seasonal patterns detected. Demand is event-driven rather than calendar-driven."
2. Replace the quarterly table with an **Event-Driven Triggers** table:

   | Trigger Event | Relevant Services | Messaging Angle | Content Opportunity |
   |--------------|-------------------|-----------------|-------------------|
   | [e.g., "Series B close"] | | | |
   | [e.g., "New VP of Marketing hire"] | | | |

3. Still populate the Ongoing Trends section. Trends are always relevant.

The quarterly table is required only when genuine seasonal patterns exist. Filling four rows with marginal distinctions is worse than an honest "event-driven" assessment.

---

## Switching Dynamics (Four Forces)

| Force | Description | Implications for Messaging |
|-------|-------------|---------------------------|
| **Push** (away from status quo) | What frustrations drive them to look? | Amplify in problem-aware content |
| **Pull** (toward your solution) | What specifically attracts them to you? | Lead with in solution-aware content |
| **Habit** (keeping them stuck) | What makes switching feel hard? | Address as objections |
| **Anxiety** (fear of switching) | What could go wrong if they switch? | Reduce with guarantees, proof, process clarity |

Messaging that only does Push + Pull without addressing Habit + Anxiety will generate interest but not conversion.

### Switching Dynamics Evidence

Each force must cite its source:

- **Push (away from status quo):** Source from reviews, forum complaints, case study "before" states, job posting pain signals
- **Pull (toward solution):** Source from testimonials, case study outcomes, product page claims with proof
- **Habit (keeps them in status quo):** Source from competitor lock-in signals, integration depth, forum discussions about switching costs
- **Anxiety (fear of switching):** Source from objections in reviews, FAQ pages, comparison page disclaimers

If a force has no supporting evidence from available sources, write: `[Force]: No public evidence found. [NEEDS CLIENT INPUT - likely sources: sales team, customer interviews]`

Do not write confident psychological narratives without evidence. "Buyers feel anxiety about migration complexity" requires a source. Without one, it's fabrication.

### Switching Dynamics by Depth

**Standard depth:**
- Four Forces table with evidence column (current behavior above)
- One "Implications for Messaging" per force
- Sources: L0 buying triggers, competitive buyer scenarios, testimonials

**Deep depth (all of standard PLUS):**
- Per-persona force assessment: which forces hit hardest for each persona? A CFO's "anxiety" (fear of switching) differs from a PE partner's.

  | Force | [Persona 1] Impact | [Persona 2] Impact | [Persona 3] Impact |
  |-------|-------------------|-------------------|-------------------|
  | Push  | [specific] | [specific] | [specific] |
  | Pull  | [specific] | [specific] | [specific] |
  | Habit | [specific] | [specific] | [specific] |
  | Anxiety | [specific] | [specific] | [specific] |

- Force intensity: rate each force as Strong / Moderate / Weak based on evidence volume and source quality. A "Push" force sourced from 5 reviews and 3 Reddit threads is Strong. One sourced from a single FAQ page inference is Weak.

---

## Objection Handling

| Objection | Why They Think This | Response | Proof Point |
|-----------|--------------------|-----------| ------------|

Pull objections from: sales team feedback, negative reviews, competitor comparison pages, FAQ pages, Reddit/forum discussions.

### Objection Categories

Check each category. If no objection is found for a category, write "[No public evidence]" -- don't skip the category.

1. **Structural:** "You're not a [type of firm]" / "You're too small/large"
   Source: competitive positioning gaps, regulatory constraints
2. **Competitive:** "Why not [Competitor]?" / "Our existing firm does this"
   Source: competitive-landscape battle cards, buyer scenarios
3. **Proof:** "Can you show results?" / "Who else have you done this for?"
   Source: proof point gaps, value theme vulnerability flags
4. **Process:** "How does this work?" / "What's the engagement model?"
   Source: FAQ pages, pricing page language, competitive comparison pages
5. **Risk:** "What if it doesn't work?" / "What's the switching cost?"
   Source: switching dynamics (Anxiety force), review complaints

At standard depth: populate at least 3 categories.
At deep depth: populate all 5 categories.

---

## Value Prop Summary

Force the positioning into a single row per persona. If you can't fill this cleanly, the framework has gaps.

| We help... (Persona) | Struggling with... (Problem) | Solved by... (Solution) | So they can... (Benefit) |
|----------------------|-----------------------------|-----------------------|-------------------------|

Each row must be distinct. If two personas have identical rows, the persona split is wrong.

---

## Anti-Value Prop

| We DON'T help... (Anti-Persona) | Struggling with... (Anti-Problem) | NOT solved by us because... | Better served by... |
|--------------------------------|----------------------------------|---------------------------|-------------------|

Be specific. "Startups" is too vague. "Pre-revenue startups with no finance team and a $5K budget" is useful.

---

## Language Bank

Structured vocabulary reference that ALL downstream skills must respect. **Pre-Flight intake language constraints are authoritative.** Where intake constraints conflict with research-discovered patterns (e.g., intake says "avoid 'consulting'" but the website uses it), the intake constraint wins. Note the conflict in the relevant entry.

**Origin-aware rules:** When reading L0's Glossary and Constraints sections, check the `Origin` column or tag. `client`-origin glossary terms and constraints are **mandatory** -- if the client says "never use 'disruptor,'" that is a hard rule regardless of what the website says. `client`-origin terms go directly into Banned Terms or the relevant Language Bank subsection **without validation**. `research`-origin glossary terms are **recommendations** -- you can override them with justification if messaging analysis suggests a different approach (e.g., the website avoids a term but reviews show customers use it heavily).

### Customer Language Sourcing Priority

1. **_research-extractions.md review site entries:** Read entries tagged as "Review Site" or "Reddit" page types. Extract verbatim buyer phrases describing the problem, solution, or switching experience.
2. **L0 Proof Point Registry:** Each proof point with a customer quote provides verbatim language. Extract the phrases buyers use to describe value, not just the attribution.
3. **Competitive landscape buyer scenarios and objections:** The objection language in competitive-landscape.md reflects how buyers talk about the category. Extract phrasing patterns.
4. **L0 Homepage Messaging (testimonials):** Last resort. These are curated by the company and represent the language the company WANTS buyers to use, not necessarily the language buyers actually use.

### When Customer Language is Thin

If fewer than 3 entries come from sources 1-3 (non-curated):

- Flag explicitly: "Customer language derived primarily from company-curated testimonials. Real buyer language likely differs. **Confidence: 2.**"
- Add a "Customer Language Collection Brief" appendix (following the ROI Data Collection Brief pattern):

  **Customer Language Collection Brief**

  No unmoderated customer language was found in public sources. To populate the language bank with real buyer phrases:

  1. Search G2/Capterra for "[company] reviews" -- extract how reviewers describe the problem they were solving and why they chose this company
  2. Search Reddit for "[category]" recommendation threads -- how do buyers describe the need?
  3. Ask 3-5 recent clients: "How would you describe what we do to a peer who's never heard of us?"

  Target: 5+ verbatim phrases from non-curated sources.

### Customer Language (use in headlines, ads, email subjects)
Captured from reviews, forums, testimonials, and Reddit. These are the words buyers actually use.
- "[exact phrase]" - Source: [G2 review / Reddit thread / testimonial]

### Company Language (use in body copy, about pages)
How the company describes itself. May differ from customer language.
- "[exact phrase]" - Source: [homepage / about page / LinkedIn]

### Competitor-Owned Terms (AVOID in differentiating copy)
Phrases a competitor has claimed. Using these positions you as a follower.
- "[term]" - Owned by: [Competitor]

### Banned Terms (NEVER use)
Words/phrases off-limits for legal, compliance, brand, or strategic reasons. **Populate from L0 Constraints section.** Any terms marked "must avoid" in the Pre-Flight intake or L0 Glossary (Incorrect/Avoid column) MUST appear here with reason.
- "[term]" - Reason: [why]

### Category Terms (use in SEO, paid search, category-level copy)
Validated search terms buyers actually use to find solutions in this space.
- "[term]" - Search validation: [Google Trends / search results quality]

---

## Brand Voice & Tone

Derived from research, not self-reported. Analyze tone patterns across all content collected in Phase 1. Document how the company actually sounds, flag inconsistencies, compare against competitor voice.

### Voice Profile
- **Tone:** [formal / conversational / technical / casual / authoritative]
- **Person:** [first person "we" / third person / mixed]
- **Complexity:** [jargon-heavy / accessible / mixed]
- **Personality:** [3-5 adjectives derived from content analysis, not aspirational]
- **Emotion:** [reserved / empathetic / urgent / confident]

### Channel Consistency Audit

| Channel | Observed Tone | Matches Core Voice? | Notes |
|---------|--------------|--------------------| ------|
| Homepage | | Yes / No / Partial | |
| About page | | Yes / No / Partial | |
| Case studies | | Yes / No / Partial | |
| LinkedIn posts | | Yes / No / Partial | |
| Careers page | | Yes / No / Partial | |
| Glassdoor reviews | | N/A | [Internal vs. external voice] |

Inconsistency is a finding. A company that sounds warm on the homepage but robotic in case studies has a voice problem.

### Voice Consistency Rating
**high** (consistent voice):
- Same person (we/they) across all channels
- Tone adjectives would be the same if you described any channel independently
- Vocabulary is consistent (no channel uses jargon while another uses plain language)
- 0-1 channels marked "Partial" in the Channel Consistency Audit

**moderate** (recognizable but drifting):
- Person shifts on 1-2 channels (e.g., homepage "we" but case studies "they")
- Tone adjectives differ by channel (homepage is warm, service pages are corporate)
- 2-3 channels marked "Partial" in the Channel Consistency Audit
- OR: core branded pages (homepage, about) are consistent but capability/service pages read like different writers

**low** (no consistent voice):
- Person shifts across 3+ channels
- No common tone adjectives across channels
- 4+ channels marked "Partial" or "No" in the Channel Consistency Audit
- OR: branded pages contradict each other (homepage casual, about page formal)

The rating is derived from the Channel Consistency Audit table, not from overall impression. Count the "Partial" and "No" entries.

### Competitor Voice Comparison

| Company | Tone | Differentiating? |
|---------|------|-----------------|
| [Target company] | [tone summary] | - |
| [Competitor A] | [tone summary] | [Distinct or interchangeable?] |

If every company sounds the same, that IS the finding. Flag voice white space.

### Do / Don't Examples

| Do (on-brand) | Source | Don't (off-brand or generic) | Source |
|---------------|--------|------------------------------|--------|
| "[actual sentence]" | [page] | "[actual sentence]" | [page] |

Real examples from the company's content. Not invented.

### Brand Narrative Tensions

Identify cases where the company's marketing campaigns, brand messaging, or public statements contradict the website positioning or category language. These tensions are strategic opportunities if resolved, or credibility risks if ignored.

| Tension | Where It Appears | Intentional Provocation or Accidental? | Recommended Resolution |
|---------|-----------------|---------------------------------------|----------------------|
| [e.g., Campaign says "Consulting is Dead" but website says "consulting firm"] | [Campaign page vs title tag] | [Intentional brand provocation] | [Keep campaign for differentiation, maintain category terms in SEO-critical locations] |

If no tensions found, write "No brand narrative tensions detected." Don't skip the section.

### Voice Rules for Downstream Skills

Actionable constraints for content production:
- [e.g., "Always use first person plural. Never third person."]
- [e.g., "No exclamation marks. Confidence comes from specificity, not punctuation."]
- [e.g., "Avoid superlatives unless backed by a proof point."]
At least 3 actionable rules.

---

## Messaging Hierarchy

The bridge between positioning analysis and actual copy production. Structured so downstream skills can grab the right message for the right context.

### Primary Message (1 sentence)
[One-line positioning statement from company-identity.md > One-Line Positioning Statement]

### Supporting Messages (pick 2-3 per asset)
1. [Message] (PROOF: P1, P2)
2. [Message] (PROOF: P3)
3. [Message] (PROOF: P4, P5)

### Per-Persona Lead Messages
- [Persona 1]: "[Their version of the primary message]"
- [Persona 2]: "[Their version]"

### Objection-Response Pairs (for sales pages, FAQ, retargeting)
- "[Objection]" -> "[Response]" (PROOF: P_)

Every message references proof point IDs. No unsupported claims in the hierarchy.

---

## Channel Adaptations

**Every channel adaptation must be derived from the messaging hierarchy above. Do not invent new copy, taglines, or claims. Adapt existing messages to channel constraints. If the messaging hierarchy doesn't contain enough material for a channel, write `[INSUFFICIENT SOURCE MATERIAL]` instead of generating new content.**

Same core message, adapted per channel constraints.

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

---

## Output Routing

All sections above merge into a single context file: `.claude/context/audience-messaging.md`

**What goes where in audience-messaging.md:**

| This phase section | Maps to audience-messaging.md section |
|---|---|
| Persona Messaging Grid | Personas > Persona Messaging Grid |
| Quantified Value & Cost of Alternatives | Personas > Cost of Alternatives |
| Switching Dynamics | Personas > Switching Dynamics |
| Objection Handling | Personas > Objection Handling |
| Value Prop Summary | Personas > Value Prop Summary |
| Anti-Value Prop | Personas > Anti-Value Prop |
| Value Themes with Proof | Messaging > Value Themes |
| Messaging Hierarchy | Messaging > Messaging Hierarchy |
| Seasonal & Trend Relevance | Messaging > Seasonal Relevance |
| Channel Adaptations | Messaging > Channel Adaptations |
| Voice Profile | Voice > Voice Profile |
| Channel Consistency Audit | Voice > Channel Consistency Audit |
| Competitor Voice Comparison | Voice > Competitor Voice Comparison |
| Language Bank (all subsections) | Voice > Language Bank |
| Do/Don't Examples | Voice > Do/Don't Examples |
| Voice Rules | Voice > Voice Rules |

The positioning statement is referenced from `company-identity.md` (L0) and repeated as the anchor in the Messaging section.

---

## Confidence Re-evaluation (extension only)

When extending an existing `audience-messaging.md`, you MUST re-evaluate section confidence scores against your new evidence. Follow the "When Extending a File" procedure in `agent-header.md`.

**Messaging depth targets for reference:**

| Depth | Target Confidence | Raise To |
|-------|------------------|----------|
| standard | 3-4 | Up to 4 if personas have sourced data and voice is audited |
| deep | 4-5 | Up to 5 only with customer language from multiple real sources |

Do not skip this step. Confidence scores that stay frozen at their initial values during extension are a known failure mode.

---

## Confidence Reconciliation (mandatory, final step)

Before writing `audience-messaging.md` to disk, execute this procedure. Do not skip it.

1. Scan every section in the file body that has a confidence score (e.g., `**Confidence:** 3`).
2. Collect all section-level confidence scores into a list.
3. Set frontmatter `confidence` to the MINIMUM value in that list.
4. If no sections have confidence scores, set frontmatter `confidence` to 2.

This is not optional. The schema rule is: file-level confidence equals the lowest section confidence. A file with one section at confidence 2 and all others at confidence 4 has file-level confidence 2.

Common mistake to avoid: setting frontmatter confidence based on your overall assessment of data quality. Frontmatter confidence is a mechanical calculation, not a judgment call.

---

## Inline Schema: audience-messaging.md

### YAML Frontmatter

```yaml
---
schema: audience-messaging
schema_version: "1.0"
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
tone: "professional, authoritative, direct"
person: "first plural"                    # "first plural" | "third person" | "mixed"
complexity: "accessible"                  # "jargon-heavy" | "accessible" | "mixed"
voice_consistency: "moderate"             # high | moderate | low - see Voice Consistency Rating definition above

# Content counts
customer_language_count: 5
banned_terms_count: 3

---
```

### Markdown Body Structure

```markdown
# Audience & Messaging: [Company Name]

---

## Personas

### Persona Messaging Grid

| Persona + Team | Tier | Their Daily Reality | Top 3 Challenges | What Changes With Your Solution | Value They'd Pitch to Their Boss |
|---------------|------|--------------------|-----------------|---------------------------------|--------------------------------|
| [Role, Team] | [tier] | [What their day looks like] | 1. [Challenge] 2. [Challenge] 3. [Challenge] | [Specific outcome] | [How they'd sell it internally] |

[Depth per persona: role, reports-to, KPIs, tools, prior attempts, peer language, champion criteria]

### Cost of Alternatives

| Alternative | Cost to Buyer | Switching Cost to Your Solution | Quantified ROI (if evidence exists) |
|-------------|--------------|-------------------------------|-------------------------------------|

### Switching Dynamics

| Force | Description | Implications for Messaging |
|-------|-------------|---------------------------|
| **Push** (away from status quo) | | Amplify in problem-aware content |
| **Pull** (toward your solution) | | Lead with in solution-aware content |
| **Habit** (keeping them stuck) | | Address as objections |
| **Anxiety** (fear of switching) | | Reduce with guarantees, proof, process clarity |

### Objection Handling

| Objection | Why They Think This | Response | Proof Point |
|-----------|--------------------|-----------| ------------|

### Value Prop Summary

| We help... (Persona) | Struggling with... (Problem) | Solved by... (Solution) | So they can... (Benefit) |
|----------------------|-----------------------------|-----------------------|-------------------------|

### Anti-Value Prop

| We DON'T help... (Anti-Persona) | Struggling with... (Anti-Problem) | NOT solved by us because... | Better served by... |
|--------------------------------|----------------------------------|---------------------------|-------------------|

---

## Messaging

### Positioning Statement

[Category] for [Persona] that [Big Unlock] by [Mechanism].

### Value Themes

| Value Theme | Supporting Capabilities | Proof Type | Specific Evidence | Proof Point IDs |
|------------|----------------------|-----------|-------------------|-----------------|

### Messaging Hierarchy

#### Primary Message (1 sentence)
[Positioning statement]

#### Supporting Messages (pick 2-3 per asset)
1. [Message] (PROOF: P1, P2)

#### Per-Persona Lead Messages
- [Persona]: "[Their version]"

#### Objection-Response Pairs
- "[Objection]" -> "[Response]" (PROOF: P_)

### Seasonal Relevance

| Quarter | Relevant Services/Products | Why Urgent Now | Messaging Angle | Content Opportunity |
|---------|--------------------------|---------------|-----------------|-------------------|

#### Ongoing Trends
- [Regulatory, technology, market, competitor trends]

### Channel Adaptations

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

---

## Voice

### Voice Profile

- **Tone:** [observed, not aspirational]
- **Person:** [first/third/mixed]
- **Complexity:** [jargon-heavy / accessible / mixed]
- **Personality:** [3-5 adjectives from content analysis]
- **Emotion:** [reserved / empathetic / urgent / confident]

### Channel Consistency Audit

| Channel | Observed Tone | Matches Core Voice? | Notes |
|---------|--------------|--------------------| ------|

### Competitor Voice Comparison

| Company | Tone | Differentiating? |
|---------|------|-----------------|

### Language Bank

#### Customer Language (use in headlines, ads, email subjects)
- "[exact phrase]" - Source: [source]

#### Company Language (use in body copy, about pages)
- "[exact phrase]" - Source: [source]

#### Competitor-Owned Terms (AVOID in differentiating copy)
- "[term]" - Owned by: [Competitor]

#### Banned Terms (NEVER use)
- "[term]" - Reason: [why]

#### Category Terms (use in SEO, paid search, category-level copy)
- "[term]" - Search validation: [source]

### Do / Don't Examples

| Do (on-brand) | Source | Don't (off-brand or generic) | Source |
|---------------|--------|------------------------------|--------|

### Voice Rules

Actionable constraints for content production:
- [rule 1]
- [rule 2]
- [rule 3+]
```

### Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

**Personas:**
- [ ] Persona Messaging Grid has entries from verified sources (target: 2+ distinct personas; fewer is acceptable with gap marker)
- [ ] Every major service line maps to at least one persona
- [ ] Cost of Alternatives has entries from verified sources (target: 3+ alternatives with economic impact; fewer is acceptable with gap marker)
- [ ] Switching Dynamics covers all four forces
- [ ] Objection Handling has entries from verified sources (target: 3+ objections with sources; fewer is acceptable with gap marker)
- [ ] Value Prop Summary has distinct rows per persona

**Messaging:**
- [ ] Positioning statement present and passes competitor test
- [ ] Value themes with proof present (target: 3+; every theme has Level 1-3 evidence or is flagged; fewer is acceptable with gap marker)
- [ ] Messaging hierarchy references proof point IDs (no unsupported claims)
- [ ] Per-persona lead messages present for each persona
- [ ] Seasonal relevance covers at least current and next quarter
- [ ] Channel adaptations cover at minimum: homepage H1, LinkedIn ad, Google Search RSA, email subject, sales one-liner, case study headline

**Voice:**
- [ ] Voice Profile derived from observed content, not aspirational
- [ ] Channel Consistency Audit covers channels found (target: 4+; fewer is acceptable with gap marker)
- [ ] Competitor Voice Comparison includes competitors found (target: 2+; fewer is acceptable with gap marker)
- [ ] Customer Language has entries from real sources (target: 5+; fewer is acceptable with gap marker)
- [ ] Banned Terms is populated
- [ ] Do/Don't Examples use actual sentences from company content
- [ ] Voice Rules has actionable constraints (target: 3+; fewer is acceptable with gap marker)

**General:**
- [ ] YAML frontmatter has all required fields
- [ ] `confidence` value equals the lowest section confidence within this file

### Versioning Rules

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
