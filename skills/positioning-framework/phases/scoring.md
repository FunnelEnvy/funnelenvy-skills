# Phase: Scoring & Quality Checks

This phase reads all prior context (company identity, competitive landscape, audience messaging) and produces the positioning scorecard and runs final quality verification.

---

## Shared Agent Rules

**Shared agent rules** (Content Integrity Check, Confidence Rules) are in `agent-header.md`. Read that file first.

---

## Required Inputs

Before starting scoring, verify these preconditions:

1. `.claude/context/company-identity.md` exists with confidence >= 3
2. `.claude/context/competitive-landscape.md` exists
3. `.claude/context/audience-messaging.md` exists

If company-identity.md is missing or confidence < 3: STOP. Cannot score.

If competitive-landscape.md OR audience-messaging.md is missing:
- Proceed with available data only.
- For any dimension that depends on missing data, rate as `[INSUFFICIENT DATA]` instead of Strong/Needs Work/Missing.
- Note in health check summary: "X dimensions could not be fully assessed due to missing {competitive|messaging} analysis."

Dimensions and their data dependencies:

| Dimension | Requires L0 | Requires Competitive | Requires Messaging |
|-----------|-------------|---------------------|--------------------|
| Clarity | Yes | No | No |
| Differentiation | Yes | Yes | No |
| Proof | Yes | No | No |
| Specificity | Yes | No | Yes |
| Consistency | Yes | No | Yes |
| Category Fit | Yes | Yes | No |

---

## Depth Behavior

Read the DEPTH parameter from the task prompt.

### standard
- Score all 6 dimensions
- Full health check written to positioning-scorecard.md
- Output length: 800-1,200 words

### deep
- Score all 6 dimensions with extended evidence citations
- Additional "Positioning Gaps" analysis section
- Full health check written to positioning-scorecard.md
- Output length: 800-1,200 words

### quick
- This agent should NOT be launched at quick depth. The orchestrator produces an inline health check instead (see Quick Depth Behavior below).
- If launched anyway: produce a stub positioning-scorecard.md with confidence: 1 and a single section noting "Quick depth uses inline health check. Run at standard or deep depth for full scoring."

---

## Graceful Degradation

If input context files are incomplete or have low confidence:

1. **Always produce positioning-scorecard.md.** Even with incomplete inputs, the health check and gap analysis are valuable. Rate dimensions based on what's available.
2. **Note input gaps in Section Confidence.** If competitive-landscape.md is missing sections, note "Competitive Landscape: confidence limited by incomplete competitor profiles" in the Section Confidence table.
3. **Do not inflate ratings to compensate for missing data.** Missing input = lower confidence in the rating, not a default "Needs Work." If you genuinely can't assess a dimension, rate it based on available evidence and note the limiting factor.
4. **Always write output to disk.** Partial scorecard on disk is better than none.

---

## Output Length Targets
- Quick: 400-600 words (inline health check)
- Standard: 800-1,200 words
- Deep: 800-1,200 words

These are targets, not hard limits. Prefer concise, evidence-dense output over padding. If a section has thin data, make it shorter, not fluffier.

---

## Standard and Deep Depth Behavior

Everything below this line applies to standard and deep depth only. At quick depth, the orchestrator produces the inline health check above and does not spawn Agent 4.

---

## Section Confidence Scores

Rate every section of the positioning framework on a 1-5 confidence scale. Downstream skills check these before consuming a section. Low-confidence sections produce DRAFT content, not final content.

| Section | Confidence (1-5) | Limiting Factor | How to Improve |
|---------|-----------------|-----------------|----------------|
| Glossary | | | |
| Buyer Alternatives | | | |
| Competitive Landscape | | | |
| Stated Differentiators | | | |
| Value Themes | | | |
| Personas | | | |
| Market Category | | | |
| Seasonal | | | |
| Switching Dynamics | | | |
| Objections | | | |

**Rule:** Sections scoring 1-2 produce content marked DRAFT. Sections scoring 4-5 produce final copy.

---

## Positioning Health Check (6 Dimensions)

Rate each dimension as **Strong**, **Needs Work**, or **Missing**. Each rating requires a specific Key Finding with evidence. Most companies land at Needs Work on most dimensions. Strong requires genuine evidence. Missing means the dimension is effectively absent. If a run produces all-Strong, the agent is broken.

### Rating Definitions

| Rating | Definition | What to Look For |
|--------|-----------|------------------|
| **Strong** | Positioning on this dimension is specific, differentiated, and backed by named evidence. No major gaps. | Specific claims + proof points with IDs + consistency across channels |
| **Needs Work** | Positioning exists but is generic, unproven, or inconsistent across channels. Improvable. | Vague language, self-asserted claims, mixed messaging between pages |
| **Missing** | No meaningful positioning on this dimension. Absent or so generic it's indistinguishable from competitors. | Dimension not addressed anywhere, or only addressed with filler copy |

### Dimension Calibration

| Dimension | Strong | Needs Work | Missing |
|-----------|--------|------------|---------|
| **Clarity** | Buyer understands value prop in one page scroll. Category, audience, and outcome named explicitly. | Value prop exists but requires 2+ pages to piece together. Jargon or abstraction obscures meaning. | Homepage could belong to any company in the category. No specificity. |
| **Differentiation** | Claims territory competitors don't occupy. Can name what's different without referencing competitors. | Differentiators stated but overlap with 2+ competitors' claims. "Better" not "different." | No differentiators beyond table-stakes features. Interchangeable with competitors. |
| **Proof** | 2+ named customers with specific metrics. Third-party validation (awards, analyst mentions, reviews). | Named customers exist but no metrics. Or metrics exist but no attribution. Logo wall without stories. | No named customers, no case studies, no external validation. All claims self-asserted. |
| **Specificity** | Names concrete segments, use cases, outcomes, and numbers. "We help X do Y, resulting in Z." | References outcomes but in general terms. "Increase revenue" not "reduce CAC by 30% for mid-market SaaS." | Pure abstraction. "Unlock potential." "Drive growth." No concrete anything. |
| **Consistency** | Same core narrative across homepage, about, LinkedIn, ads, sales collateral. Voice and claims aligned. | Core message exists but varies across channels. LinkedIn says one thing, homepage says another. | No coherent narrative. Each channel tells a different story or contradicts others. |
| **Category Fit** | Company appears where buyers search. Category term matches buyer vocabulary. SEO and positioning aligned. | Category claimed but buyers use different terms. Or right terms but poor visibility. | Company doesn't show up in the category buyers search. Misaligned or invisible. |

### Health Check Output Format

```markdown
## Positioning Health Check

| Dimension | Rating | Key Finding |
|-----------|--------|-------------|
| Clarity | Needs Work | Value prop requires reading homepage + about page to piece together. H1 is aspirational, not descriptive. |
| Differentiation | Strong | "Only platform that combines X with Y" is specific and not claimed by analyzed competitors. |
| Proof | Missing | No named customers anywhere on site. Three self-asserted claims with no attribution. |
| Specificity | Needs Work | Names target segment (mid-market SaaS) but outcomes are generic ("grow faster"). |
| Consistency | Needs Work | LinkedIn emphasizes enterprise features; homepage targets startups. Mixed signals. |
| Category Fit | Strong | Ranks for "[category] software" terms. Buyer vocabulary matches company vocabulary. |

**Overall: 2 Strong, 3 Needs Work, 1 Missing**

### Top Gap
Proof. Zero named customers or quantified outcomes. Every differentiator is self-asserted.

### Top Opportunity
Clarity. The differentiators exist (Differentiation is Strong) but the homepage doesn't surface them. Rewriting the H1 and first scroll is high-impact, low-effort.
```

---

## Messaging Gap Analysis

For every line of hero copy and primary claims on the website:

| Copy Element | Source Page | Generic? | Evidence? | Recommendation |
|-------------|------------|----------|-----------|----------------|
| "[exact copy]" | Homepage H1 | Yes/No | Yes/No | [What to change] |

- **Generic** = a competitor could paste this on their site and it still makes sense. Flag it.
- **No evidence** = assertion without a specific number, name, or verifiable fact.

Every company has at least 2-3 generic claims. If the analysis finds zero, it's not honest.

**Note:** Competitive White Space analysis lives in `competitive.md`, not here.

---

## Output

### positioning-scorecard.md

Output to `.claude/context/positioning-scorecard.md`. Follow the inline schema below.

Contains:
- Quick Reference summary (section 0, REQUIRED)
- Positioning Health Check with 6 dimensions (from health check above)
- Messaging Gap Analysis (from analysis above)
- Section Confidence Scores (from confidence ratings above)

The YAML frontmatter `ratings`, category counts, `top_gap`, and `top_opportunity` fields must match the body content.

### Competitive Battle Cards

Battle cards are INLINED in `competitive-landscape.md` as per-competitor profile sections. They are not produced as separate files by this phase. The competitive phase handles this.

**Note:** This phase does NOT produce deliverables (copy briefs, experiment hypotheses, etc.). Human-readable deliverables are produced by the render-default-deliverables skill (L2), which consumes the context files this phase produces.

## Quality Checks

### Cross-File Integrity Verification

After producing the scorecard, perform these content-level quality checks across all context files:

- [ ] Battle cards include "when we lose" sections (check competitive-landscape.md)
- [ ] No system internals leak into output files (grep for file paths, function names, debug markers)
- [ ] Proof IDs referenced in messaging are defined in company-identity.md
- [ ] Source attribution tags are present on all factual claims

If any check fails, note it in the scorecard's health check section. Do not silently pass.

Split into two groups: checks Agent 4 performs by reading context files, and checks the orchestrator performs after all agents complete.

### Agent 4 Checks (verify by reading context files)

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

**Cross-file consistency:**
- [ ] Proof point IDs are consistent across all files (every P_ reference resolves to an entry in company-identity.md's Proof Point Registry)
- [ ] Each context file's `confidence` value equals the lowest section confidence within that file
- [ ] One-line positioning statement passes the competitor test (could a competitor use this exact sentence?)
- [ ] Campaign content distinguished from positioning (no campaign taglines in differentiator lists or claim overlap map)

**company-identity.md completeness:**
- [ ] Service Exclusions section is populated (even if "None identified")
- [ ] Constraints > Regulatory is populated (even if "No constraints identified")
- [ ] Retired Positioning section is populated (even if "None identified")
- [ ] Proof Point Registry contains every piece of evidence, each with ID, type, content, source, strength, tags

**competitive-landscape.md completeness:**
- [ ] Competitive analysis covers all three JTBD tiers with real competitor names and data
- [ ] Battle cards include "when we lose" sections for every profiled competitor
- [ ] Competitive white space identifies unclaimed positioning territory (target: 1+; mark `[NONE FOUND]` if none identified from available data)
- [ ] Claim Overlap Map covers claims from L0 (target: top 5+; fewer is acceptable with gap marker)
- [ ] Buyer Alternatives captures entries from verified sources (target: 3+ non-vendor alternatives; fewer is acceptable with gap marker)

**audience-messaging.md completeness:**
- [ ] Every value theme has Level 1-3 proof (metric, testimonial, or case study). Flag any that don't.
- [ ] Every persona row has all columns filled with distinct content (not copy-pasted across personas)
- [ ] Every major service line maps to at least one persona. No orphan services.
- [ ] Value Prop Summary rows distinct per persona
- [ ] Language Bank has entries in Customer Language from actual reviews/forums (target: 5+; fewer is acceptable with gap marker)
- [ ] Language Bank Banned Terms section is populated
- [ ] Messaging Hierarchy references proof point IDs (no unsupported messages)
- [ ] Channel Adaptations cover at minimum: homepage H1, LinkedIn ad, email subject, sales one-liner
- [ ] Brand Voice profile derived from observed content, not aspirational self-description
- [ ] Brand Voice do/don't examples use actual sentences from company content
- [ ] Brand Voice rules include actionable constraints (target: 3+; fewer is acceptable with gap marker)
- [ ] Seasonal relevance covers at least current and next quarter

**positioning-scorecard.md (this agent's own output):**
- [ ] Positioning health check completed with honest ratings (not all Strong)
- [ ] Messaging gap analysis flags generic claims found (target: 2-3+; fewer is acceptable with gap marker)
- [ ] Section Confidence scores populated for every section (no section left unscored)
- [ ] If client provided a prior worksheet (Mode 4), reconciliation table present

### Frontmatter-Body Consistency Check

Before finalizing the health check, verify these fields match between frontmatter and body in each context file:

**audience-messaging.md:**
- `positioning_statement` in frontmatter matches the positioning statement in body section
- `personas[].name` in frontmatter matches persona names in Persona Messaging Grid
- `value_themes[].name` in frontmatter matches value theme names in Value Themes section

**competitive-landscape.md:**
- `top_competitors` in frontmatter matches the top 3 competitors identified in body profiles
- `white_spaces` in frontmatter matches White Space section

**company-identity.md:**
- `company.name` in frontmatter matches Company Overview
- `category.primary` in frontmatter matches category used throughout body

If any mismatch is found: flag it in the health check under the relevant dimension with a note: "Frontmatter-body inconsistency detected in [file]: [field]. Body content is authoritative." Do not silently resolve the inconsistency.

### Orchestrator Checks (verify after all agents complete)

These checks require context the orchestrator has but Agent 4 does not (research execution history, user interaction state, file system state). The orchestrator runs these after Agent 4 returns.

- [ ] All 4 context files exist in `.claude/context/` with valid YAML frontmatter
- [ ] Tier 0 (local project data) checked if running inside a codebase. If unavailable, noted in Section Confidence.
- [ ] Tier 1 sources (website, LinkedIn, reviews, competitors, category) all attempted
- [ ] Tier 2 sources (Reddit/forums, financial data, job postings, Google Trends) attempted for Mode 1
- [ ] Competitor list validated against at least 2 buyer-perspective sources
- [ ] Every persona with a dedicated website page is included or explicitly excluded with reasoning
- [ ] Regulatory/compliance constraints checked with client (or flagged as unknown)
- [ ] Pricing & engagement model documented (or flagged as unknown)
- [ ] Pre-Flight intake questions asked (or gaps documented)

---

## Inline Schema: positioning-scorecard.md

This is the schema for the positioning-scorecard.md context file. It includes the Quick Reference section (formerly a standalone deliverable) as section 0.

### YAML Frontmatter

```yaml
---
schema: positioning-scorecard
schema_version: "2.0"
generated_by: positioning-framework
depth: standard
last_updated: YYYY-MM-DD
last_updated_by: positioning-framework
confidence: 3
company: "Company Name"

ratings:
  clarity: "needs_work"
  differentiation: "strong"
  proof: "missing"
  specificity: "needs_work"
  consistency: "needs_work"
  category_fit: "strong"
strong_count: 2
needs_work_count: 3
missing_count: 1
top_gap: "proof"
top_opportunity: "clarity"
---
```

### Markdown Body

#### Section 0: Quick Reference (REQUIRED)

This is a scannable snapshot of the full framework. What someone reads in 5 minutes to understand positioning without the full analysis. Sales reps keep this open during calls. Content writers scan it before drafting. New hires read it on day one.

```markdown
## Quick Reference

# [Company Name] - Positioning Quick Reference

**One-liner:** [positioning statement from company-identity.md]
**Category:** [Market category]
**Primary persona:** [Who you're talking to]
**Primary differentiator:** [The one thing no competitor can claim]

### What We Do
[2-3 sentences. Product description, not marketing copy.]

### Who We Serve
[Company profile: industry, size, maturity. 2 sentences max.]

### Key Personas
| Persona | Core Problem | Our Value |
|---------|-------------|-----------|
| [Role] | [Their pain in their words] | [What changes] |

### Top 3 Differentiators
1. [Claim] - PROOF: [P_ reference]
2. [Claim] - PROOF: [P_ reference]
3. [Claim] - PROOF: [P_ reference]

### Competitive Positioning
| Competitor | Their Angle | Our Advantage |
|-----------|------------|---------------|
| [Name] | [Their pitch in 5 words] | [Why we win] |

### Proof Points (Top 5)
[The 5 highest-strength proof points from the registry, with IDs]

### Positioning Health: [X Strong, Y Needs Work, Z Missing]
**Biggest gap:** [1 sentence on the most critical issue]
**Biggest opportunity:** [1 sentence on the clearest white space]

### Objection Cheat Sheet
| They Say | We Say |
|----------|--------|
| "[objection]" | "[response]" |

### Voice in 5 Words
[The 5 personality adjectives from the Brand Voice profile]
```

#### Section 1: Positioning Health Check (REQUIRED)

```markdown
## Positioning Health Check

| Dimension | Rating | Key Finding |
|-----------|--------|-------------|
| **Clarity** | Strong / Needs Work / Missing | [specific evidence] |
| **Differentiation** | Strong / Needs Work / Missing | [specific evidence] |
| **Proof** | Strong / Needs Work / Missing | [specific evidence] |
| **Specificity** | Strong / Needs Work / Missing | [specific evidence] |
| **Consistency** | Strong / Needs Work / Missing | [specific evidence] |
| **Category Fit** | Strong / Needs Work / Missing | [specific evidence] |

**Overall: X Strong, Y Needs Work, Z Missing**

### Top Gap
[1-2 sentences on the single most critical weakness.]

### Top Opportunity
[1-2 sentences on the single most impactful opportunity.]
```

#### Section 2: Messaging Gap Analysis (REQUIRED)

```markdown
## Messaging Gap Analysis

| Copy Element | Source Page | Generic? | Evidence? | Recommendation |
|-------------|------------|----------|-----------|----------------|
| "[exact copy]" | Homepage H1 | Yes/No | Yes/No | [What to change] |
```

#### Section 3: Section Confidence Scores (REQUIRED)

```markdown
## Section Confidence

| Section | Confidence (1-5) | Limiting Factor | How to Improve |
|---------|-----------------|-----------------|----------------|
| Glossary | | | |
| Buyer Alternatives | | | |
| Competitive Landscape | | | |
| Value Themes | | | |
| Personas | | | |
| Market Category | | | |
| Switching Dynamics | | | |
| Objections | | | |
```

**Rule:** Sections scoring 1-2 produce DRAFT content. Sections scoring 4-5 produce final content.

### Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

- [ ] YAML frontmatter has all required fields including ratings (per-dimension), strong/needs_work/missing counts, top_gap, top_opportunity
- [ ] Quick Reference section present with all subsections populated
- [ ] Positioning Health Check has honest ratings (not all Strong) with specific Key Finding per dimension
- [ ] Messaging Gap Analysis covers at least homepage H1 and 2-3 other primary claims
- [ ] Section Confidence populated for every section of the positioning framework
- [ ] `confidence` value equals the lowest section confidence within this file

### Versioning Rules

- Update `last_updated` and `last_updated_by` when modifying
- Preserve `generated_by` as the original producing skill
- Ratings can change in any direction on re-assessment (unlike other L1 files where confidence only rises). See agent-header.md Confidence Rules for the full decrease policy, including contradictory evidence exceptions.
- Section Confidence can be updated by any skill that has new data
- Mark changes: `<!-- re-rated by [skill-name] [date] -->`
