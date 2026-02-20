# Company Identity (L0) Construction Phase

Instructions for building `company-identity.md` from research findings. This file contains everything needed to produce the L0 context file: section routing from the framework, construction guidance, and the full schema inlined at the bottom.

---

## Depth Behavior

Read the DEPTH parameter from the task prompt.

### quick
- Minimal research: homepage + about page + 1-2 key pages only
- 4-7 web fetches budget (per research.md Depth Budget)
- Populate core sections only: Company Overview, Services & Capabilities, Target Segments
- Sections without sufficient data: mark `[NEEDS CLIENT INPUT]`
- Target confidence: 2-3
- Output length: 800-1,200 words

### standard
- Full research across website, review sites, social presence
- 15-20 web fetches budget
- All L0 sections populated
- Target confidence: 3-4
- Output length: 1,500-2,500 words

### deep
- Exhaustive research: all standard sources plus job postings, press releases, SEC filings, Wayback Machine, podcast mentions
- 25-35 web fetches budget
- All L0 sections populated with multiple corroborating sources
- Target confidence: 4-5
- Output length: 2,500-3,500 words

These are targets, not hard limits. Prefer concise, evidence-dense output over padding. If a section has thin data, make it shorter, not fluffier.

---

## Stale Content Detection

When prior work exists, compare freshly fetched content against existing L0 before extending it.

Check these fields specifically:
- Homepage H1 / hero copy (if different, company may have repositioned)
- Pricing model (if changed, downstream analysis may be invalid)
- Primary category / service description
- Target market language

If ANY of these differ materially from existing L0:
1. Flag the conflict
2. Decrease confidence on affected sections (per agent-header.md Confidence Rules)
3. Present both versions to the user at checkpoint
4. Do not auto-resolve. Let the user confirm which is current.

---

## Confidence Re-evaluation (extension only)

When extending an existing `company-identity.md`, you MUST re-evaluate section confidence scores against your new evidence. Follow the "When Extending a File" procedure in `agent-header.md`.

**L0 depth targets for reference:**

| Depth | Target Confidence | Raise To |
|-------|------------------|----------|
| quick | 2-3 | Up to 3 if new evidence fills gaps |
| standard | 3-4 | Up to 4 if all REQUIRED fields have sourced data |
| deep | 4-5 | Up to 5 only with multi-source corroboration |

Do not skip this step. Confidence scores that stay frozen at their initial values during extension are a known failure mode.

---

## Graceful Degradation

If you cannot complete all sections (insufficient research data, context limits):

1. **Prioritize REQUIRED sections** (Company Overview, Services, Service Exclusions, Target Segments, Anti-Personas, Stated Differentiators, Proof Point Registry, Constraints). Write these first.
2. **Always write output to disk.** Partial L0 on disk is better than no L0. Downstream agents need something to read.
3. **Mark incomplete sections with `[INCOMPLETE - reason]`.** E.g., `[INCOMPLETE - pricing page was JS-rendered, no pricing data extracted]`.
4. **Set confidence accordingly.** Missing REQUIRED sections = confidence 1. All REQUIRED present but thin = confidence 2.

---

## L0 Purity Constraint (mandatory)

company-identity.md is a Layer 0 file. It contains ONLY verifiable facts about the company. Enforce these rules in every section you write:

**Prohibited language patterns (never write these in L0):**
- Comparative statements: "compared to," "unlike competitors," "better than," "more than peers," "stronger than," "leads the market," "outperforms"
- Evaluative judgments: "impressive," "weak," "best-in-class," "industry-leading," "unique" (unless quoting the company's own copy, attributed)
- Analytical conclusions: "this suggests," "this indicates," "this positions them," "this means"
- Relative claims: "larger than," "faster than," "more experienced than" (comparisons require a referent that belongs in L1)

**What belongs in L0:** Names, dates, locations, URLs, product lists, pricing tiers, team size, stated claims (attributed to source), customer names, certifications, funding amounts, revenue figures, NPS scores, direct quotes from company materials.

**What belongs in L1 (not here):** Competitive comparisons, market positioning analysis, gap assessments, strength/weakness evaluations, "what this means" interpretations.

If you observe something comparative during research, capture it as an HTML comment: `<!-- competitive note: [observation] -->`. Do not surface it in the file body. Agent 2 (competitive.md) will handle comparative analysis in L1.

This constraint applies at ALL depth levels including deep. More research depth means more facts, not more analysis.

---

## Section Routing: Framework to L0

The following framework sections route into `company-identity.md`. Each subsection below explains what to extract and how to adapt it for L0.

### Company Overview
<!-- Output: company-identity.md > Company Overview -->

**Source:** Research findings (website extraction, LinkedIn, about page) + the One-Line Positioning Statement (see below in this file)

Synthesize into 2-4 factual sentences. Strip marketing language. Write for someone who has never heard of the company.

Template:
```
[Company name] is a [category] serving [target market]. [Key fact about scale/scope].
[One sentence on what makes them notable, if anything obvious].
```

The One-Line Positioning Statement (constructed below) informs the framing but should NOT be pasted verbatim here. Company Overview is factual description, not marketing copy.

### Services & Capabilities
<!-- Output: company-identity.md > Services & Capabilities -->

**Source:** Research Tier 0/1 (website extraction, config files)

List what the company actually offers. Group into logical categories if more than 6 items. Include technology partnerships if relevant.

### Service Exclusions
<!-- Output: company-identity.md > Service Exclusions -->

**Source:** Pre-Flight intake (Additional Context > service boundaries) + research

What the company explicitly does NOT do. **MUST be populated**, even if "None identified." This was the #1 gap in early autonomous runs. Without it, downstream skills accidentally position into services the company can't deliver.

Format each as: `**[Excluded service]**: [Why]`

### Glossary
<!-- Output: company-identity.md > Glossary -->

**Source:** Research findings (website terminology, product naming) + Pre-Flight intake language constraints

Capture:
- Product/service names and correct formatting
- Industry-specific terms the company uses
- Words or phrases to AVOID (compliance, legal, brand, competitive reasons)
- Internal vs. external naming differences
- Category language gaps: how customers describe the space vs. how the company does

**Pre-Flight intake wiring:** If the intake payload includes language constraints, map them here. "Must use" terms go to the Correct Usage column. "Must avoid" terms go to the Incorrect/Avoid column. These are authoritative -- they take priority over research-discovered patterns.

**Why this matters early:** Wrong terminology undermines everything downstream. A financial firm that says "audit services" when they don't audit has a compliance problem.

Format as a table:

| Term | Correct Usage | Incorrect / Avoid |
|------|--------------|-------------------|
| [Term] | [How to use it] | [What not to say] |

### Target Segments
<!-- Output: company-identity.md > Target Segments -->

**Source:** Research findings (website "Who We Serve" pages, case study patterns, pricing page audience signals)

Expand the frontmatter `target_market` with behavioral detail:
- Industry/vertical
- Size (revenue range, headcount range)
- Maturity stage
- Geographic focus
- Buying triggers (what event starts the search)

Format as a table:

| Segment | Description | Buying Condition |
|---------|-------------|-----------------|
| [Name]  | [Who they are] | [What's happening when they buy] |

Segments are behavioral, not firmographic. "PE-backed" is a segment. "100-500 employees" is a firmographic that goes in `company_size` frontmatter.

### Anti-Personas
<!-- Output: company-identity.md > Anti-Personas -->

**Source:** Research findings (pricing page exclusions, "not for you" sections, case study patterns showing which customers succeed vs. don't, service exclusion signals)

Be specific. "Startups" is too vague. "Pre-revenue startups with no finance team and a $5K budget" is useful. Every row should point to a better alternative.

Format:

| Anti-Persona | Why Not Us | Better Served By |
|-------------|-----------|-----------------|
| [Who]       | [Reason]  | [Alternative]    |

For each anti-persona, think in terms of:
- "We DON'T help..." -> Anti-Persona column
- "NOT solved by us because..." -> Why Not Us column
- "Better served by..." -> Better Served By column

### Stated Differentiators
<!-- Output: company-identity.md > Stated Differentiators -->

**Source:** Research findings (website claims, "why us" pages, feature comparison pages - company column ONLY)

List what the company claims. Do NOT include competitor comparison columns (those go to `competitive-landscape.md`). Each differentiator must reference proof point IDs.

For each claimed attribute, assess:
- Is this verifiable or just an opinion?
- Could a competitor claim this tomorrow? (Note it, but still include. Uniqueness analysis happens in L1.)
- What evidence exists?

Format:

| # | Differentiator | Claim | Proof Point IDs |
|---|---------------|-------|-----------------|
| 1 | [Short name]  | [The specific claim] | P1, P2 |

### Pricing Model
<!-- Output: company-identity.md > Pricing Model -->

**Source:** Research findings (pricing page, NOT competitor pricing columns)

Document the model, not dollar amounts:
- **Model**: Hourly / Project-based / Retainer / Subscription / Outcome-based / Hybrid
- **Relative positioning**: Budget / Mid-market / Premium / Ultra-premium
- **Notes**: Any relevant context

Mark `[NEEDS CONFIRMATION]` if inferred from positioning language. "Premium without the premium" implies mid-tier pricing. "Enterprise-grade" implies premium. "Accessible" or "right-sized" implies value.

### Constraints
<!-- Output: company-identity.md > Constraints -->

**Source:** Pre-Flight intake language constraints + research findings (website disclaimers, compliance pages, brand guidelines)

Two categories:
- **Regulatory**: Legal restrictions on claims. Include restricted terms and governing body reference.
- **Brand**: Self-imposed restrictions. Include restricted terms and why it matters.

**Pre-Flight intake wiring:** If the intake payload includes "must avoid" terms with regulatory or legal reasons, they map to the Regulatory category. "Must avoid" terms with brand or competitive reasons map to the Brand category. These are authoritative and must appear here even if not corroborated by research.

**MUST be populated.** Even if "No regulatory constraints identified."

### Buying Triggers
<!-- Output: company-identity.md > Buying Triggers -->

**Source:** Research findings (review site complaints, case study triggers, "How it works" pages)

Acute events that create urgency. Different from persona pain points (chronic). Examples: contract renewal, failed project, leadership change, growth milestone.

Format: `- [Trigger event]: [Why it creates urgency]`

### Retired Positioning
<!-- Output: company-identity.md > Retired Positioning -->

**Source:** Pre-Flight intake (Additional Context > retired messaging) + research

Past value props, taglines, or campaigns the company moved away from. Hard constraint: downstream skills must not re-propose retired messaging.

Format:

| What | When Used | Why Retired |
|------|-----------|------------|
| "[Past tagline]" | [Timeframe] | [Why stopped] |

**MUST be populated.** Even if "None identified" or user didn't answer.

### Category Gap
<!-- Output: company-identity.md > Category Gap -->

**Source:** Research findings (website category language, search behavior analysis, Google Trends if available)

Document the gap between the company's self-described category and how buyers actually search:

- **Company says**: "[Their self-described category]"
- **Buyers search for**: "[Terms buyers actually use]"
- **Gap**: [Description of the mismatch]

Validate category terms against search behavior. If the company uses a term nobody searches for, the framing is wrong regardless of how good it sounds. Use Google Trends data (Tier 2, 1I) to validate if available.

### One-Line Positioning Statement
<!-- Output: company-identity.md > Company Overview (adapted) -->

**Source:** Synthesis of all research findings above

Structure: `[Category] for [Persona] that [Big Unlock] by [Mechanism].`

Rules:
- Must pass the competitor test: could a competitor use this exact sentence? If yes, too generic.
- Must include a verifiable or specific element (not just adjectives).
- The mechanism should be what makes you different, not what you do.

This informs the Company Overview framing and anchors the audience-messaging.md positioning statement.

---

## Copy Verification (standard and deep only)

**NOTE: Copy verification is handled by the orchestrator (SKILL.md step 6.5), not by this agent.** The orchestrator reads the Homepage Messaging section of company-identity.md after Agent 1 completes and presents it to the user for verification. This agent's job is to extract copy accurately and tag it with source attribution.

**Source attribution values to apply during extraction:**
- `website-extracted`: WebFetch returned this content directly (default for all extracted copy)
- `meta-derived`: Pulled from meta/og tags, not visible page content
- `not-extracted`: JS-rendered, content could not be obtained

The orchestrator may update these tags after user verification:
- `website-confirmed`: User confirmed the extraction matches what they see
- `user-confirmed`: User provided or corrected this content

---

## Homepage Messaging (L0 Section)

Add a dedicated section to `company-identity.md` that captures the homepage messaging with source attribution. This section is consumed by downstream agents for experiment baselines and messaging analysis.

**CRITICAL:** The H1 must come from the main content area of the page, NOT from navigation menus, mega-menu dropdowns, or header taglines. Follow the Website Content Extraction Rules in `research.md`. If unsure, cross-check against the page's `<title>` tag for semantic overlap.

```markdown
## Homepage Messaging

- H1: "[exact headline text from main content hero]" [source: website-confirmed]
- Additional H1s: "[if carousel/slider]" / "[second slide]" [source: website-extracted]
- Subhead: "[exact subhead text]" [source: website-confirmed]
- CTA: "[button text]" / "[button text]" [source: website-confirmed]
- Format: [Static / Carousel (N slides) / Video / etc.] [source: user-confirmed]
- Nav taglines (reference only): "[any positioning-sounding taglines found in navigation]"
```

**Source attribution values:**
- `website-extracted`: WebFetch returned this content directly
- `website-confirmed`: WebFetch extracted it AND user confirmed it matches
- `user-confirmed`: User provided or corrected this content
- `meta-derived`: Pulled from meta/og tags, not visible page content
- `not-extracted`: JS-rendered, content could not be obtained

Downstream agents and render-deliverables should treat `not-extracted` content as a gap, not as something to build on. Never quote `not-extracted` copy as a current baseline in experiments or recommendations.

---

## Proof Point Registry
<!-- Output: company-identity.md > Proof Point Registry -->

Consolidate every piece of evidence from research into a single tagged table. This is the single source of truth for proof. All L1 files reference proof points by ID from this registry.

### Strength Scoring

| Score | Criteria |
|-------|----------|
| 5 | Quantified outcome with third-party verification |
| 4 | Specific metric or named testimonial with role/company, or case study with measurable outcome |
| 3 | Credible but unquantified: logo wall, award, third-party research (general, not company-specific) |
| 2 | Self-reported without verification: team credentials, years of experience claims |
| 1 | Unattributed assertion ("we're the best at X") |

### Tag Taxonomy

Use consistently so downstream skills can query by tag.

**Core tags:** `retention`, `culture`, `talent`, `execution`, `cost`, `speed`, `quality`, `enterprise`, `credibility`, `client-voice`, `scale`, `innovation`, `specialization`

Add domain-specific tags as needed. Keep total tags per proof point to 2-4.

### Registry Format

```markdown
## Proof Point Registry

| ID | Type | Content | Source | Strength | Tags |
|----|------|---------|--------|----------|------|
| P1 | Metric | [Specific metric with numbers] | [URL or source] | [1-5] | [tags] |
| P2 | Testimonial | "[Exact quote]" - [Name, Title, Company] | [URL] | [1-5] | [tags] |
| P3 | Case study | [What happened, with quantified outcome] | [URL] | [1-5] | [tags] |
| P4 | Third-party | [Award, certification, ranking] | [URL] | [1-5] | [tags] |
| P5 | Logo | [Company names] | [URL] | [1-5] | [tags] |
```

**Type values:** Metric, Testimonial, Case study, Third-party, Institutional, Logo

If a value theme has no proof above strength 2, flag it as vulnerable. Competitors can make unproven claims too.

---

## Confidence Reconciliation (mandatory, final step)

Before writing `company-identity.md` to disk, execute this procedure. Do not skip it.

1. Scan every section in the file body that has a confidence score (e.g., `**Confidence:** 3`).
2. Collect all section-level confidence scores into a list.
3. Set frontmatter `confidence` to the MINIMUM value in that list.
4. If no sections have confidence scores, set frontmatter `confidence` to 2.

This is not optional. The schema rule is: file-level confidence equals the lowest section confidence. A file with one section at confidence 2 and all others at confidence 4 has file-level confidence 2.

Common mistake to avoid: setting frontmatter confidence based on your overall assessment of data quality. Frontmatter confidence is a mechanical calculation, not a judgment call.

---

## Inline Schema Reference

The full schema for `company-identity.md`. The agent producing L0 follows this schema exactly.

### YAML Frontmatter

```yaml
---
schema: company-identity
schema_version: "1.0.0"
generated_by: positioning-framework  # or "manual"
last_updated: 2026-02-14
last_updated_by: positioning-framework
confidence: 3  # 1-5, overall confidence in data accuracy

company:
  name: ""
  url: ""
  founded: ""          # Year
  hq: ""               # City, State or City, Country
  legal_entity: ""     # Optional. Full legal name if different from brand name

category:
  primary: ""          # The market category. Use buyer language, not internal jargon.
  also_known_as: []    # Other category terms buyers use to find companies like this

target_market:
  company_size: ""     # e.g., "Mid-market to upper-mid-market"
  revenue_range: ""    # e.g., "$50M-$5B"
  geo: ""              # e.g., "US national" or "North America"
  segments: []         # e.g., ["PE-backed", "high-growth", "in transition"]
  industries: []       # e.g., ["energy", "healthcare", "financial services"]
---
```

**Field notes:**
- `confidence`: Skills use this to decide whether to trust data or re-research. Below 3 = treat as draft.
- `category.primary`: What buyers search for, not what the company calls itself. If there's a gap, note it in Category Gap.
- `target_market.segments`: Behavioral segments, not firmographics. "PE-backed" is a segment. "100-500 employees" goes in `company_size`.

### Markdown Body Sections

Sections marked **REQUIRED** must be present for the file to be considered complete. Optional sections can be omitted if data isn't available.

#### 1. Company Overview (REQUIRED)

2-4 sentences. What this company does, for whom, and at what scale. No marketing language, just facts.

```markdown
## Company Overview

[Company name] is a [category] serving [target market]. [Key fact about scale/scope].
[One sentence on what makes them notable, if anything obvious].
```

#### 2. Services & Capabilities (REQUIRED)

```markdown
## Services & Capabilities

### Core Services
- [Service 1]: [One-line description]
- [Service 2]: [One-line description]

### Extended Services
- [Service 3]: [One-line description]

### Technology Partnerships
- [Partner 1], [Partner 2], [Partner 3]
```

#### 3. Service Exclusions (REQUIRED)

```markdown
## Service Exclusions

- **[Excluded service]**: [Why]
- **[Excluded service]**: [Why]
```

#### 4. Target Segments (REQUIRED)

```markdown
## Target Segments

| Segment | Description | Buying Condition |
|---------|-------------|-----------------|
| [Name]  | [Who they are] | [What's happening when they buy] |
```

#### 5. Anti-Personas (REQUIRED)

```markdown
## Anti-Personas

| Anti-Persona | Why Not Us | Better Served By |
|-------------|-----------|-----------------|
| [Who]       | [Reason]  | [Alternative]    |
```

#### 6. Stated Differentiators (REQUIRED)

```markdown
## Stated Differentiators

| # | Differentiator | Claim | Proof Point IDs |
|---|---------------|-------|-----------------|
| 1 | [Short name]  | [The specific claim] | P1, P2 |
```

#### 7. Proof Point Registry (REQUIRED)

```markdown
## Proof Point Registry

| ID | Type | Content | Source | Strength | Tags |
|----|------|---------|--------|----------|------|
| P1 | Metric | [Specific metric with numbers] | [URL or source] | [1-5] | [tags] |
| P2 | Testimonial | "[Exact quote]" - [Name, Title, Company] | [URL] | [1-5] | [tags] |
| P3 | Case study | [What happened, with quantified outcome if available] | [URL] | [1-5] | [tags] |
| P4 | Third-party | [Award, certification, ranking] | [URL] | [1-5] | [tags] |
| P5 | Institutional | [Board member, investor, partnership] | [URL] | [1-5] | [tags] |
```

**Tags:** Use the tag taxonomy from the Proof Point Registry construction section above. Core tags: `retention`, `culture`, `talent`, `execution`, `cost`, `speed`, `quality`, `enterprise`, `credibility`, `client-voice`, `scale`, `innovation`, `specialization`. Keep 2-4 tags per proof point.

**Type values:** Metric, Testimonial, Case study, Third-party, Institutional, Logo

#### 8. Company Stats (OPTIONAL)

```markdown
## Company Stats

| Stat | Value | As Of | Source |
|------|-------|-------|--------|
| Revenue | $149M | 2023 | PR Newswire |
| Headcount | 673 | 2024 | Website |
```

#### 9. Pricing Model (OPTIONAL)

```markdown
## Pricing Model

- **Model**: [Hourly / Project-based / Retainer / Subscription / Outcome-based / Hybrid]
- **Relative positioning**: [Budget / Mid-market / Premium / Ultra-premium]
- **Notes**: [Any relevant context]
```

#### 10. Constraints (REQUIRED)

```markdown
## Constraints

### Regulatory
- **[Constraint name]**: [What's restricted and why]
  - Restricted terms: [list]
  - Reference: [regulation, governing body, or compliance doc]

### Brand
- **[Constraint name]**: [What's restricted and why]
  - Restricted terms: [list]
  - Context: [why this matters to the brand]
```

#### 11. Glossary (OPTIONAL)

```markdown
## Glossary

| Term | Correct Usage | Incorrect / Avoid |
|------|--------------|-------------------|
| [Term] | [How to use it] | [What not to say] |
```

#### 12. Buying Triggers (OPTIONAL)

```markdown
## Buying Triggers

- [Trigger event]: [Why it creates urgency]
```

#### 13. Retired Positioning (OPTIONAL)

```markdown
## Retired Positioning

| What | When Used | Why Retired |
|------|-----------|------------|
| "[Past tagline or value prop]" | [Approximate timeframe] | [Why they stopped using it] |
```

#### 14. Category Gap (OPTIONAL)

```markdown
## Category Gap

- **Company says**: "[Their self-described category]"
- **Buyers search for**: "[Terms buyers actually use]"
- **Gap**: [Brief description of the mismatch]
```

### Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

A `company-identity.md` file is **complete** when:

- [ ] YAML frontmatter has all required fields (company, category, target_market)
- [ ] Company Overview is filled (2-4 sentences)
- [ ] Services & Capabilities lists at least core services
- [ ] Service Exclusions is present (even if "None identified")
- [ ] Target Segments has entries from verified sources (target: 2+; fewer is acceptable with gap marker)
- [ ] Anti-Personas has entries from verified sources (target: 1+; fewer is acceptable with gap marker)
- [ ] Stated Differentiators has entries with proof point references (target: 2+; fewer is acceptable with gap marker)
- [ ] Proof Point Registry has entries from verified sources (target: 5+; fewer is acceptable with gap marker)
- [ ] Constraints section is present (even if no regulatory constraints exist)
- [ ] `confidence` score is set and honest

A file missing REQUIRED sections should have `confidence: 1` and a note about what's missing.

### Versioning

When updating an existing `company-identity.md`:
- Bump `last_updated`
- Update `last_updated_by` to the extending skill name
- Add a changelog entry at the bottom
- If proof points are added/removed, re-check all `Proof Point IDs` references in Stated Differentiators
- If services change, check Service Exclusions still holds

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
| 2026-02-14 | Initial creation | positioning-framework |
```
