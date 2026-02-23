> **Reference only.** The authoritative schema is inline in the corresponding phase file under `skills/positioning-framework/phases/`.
> If this file and the phase file disagree, the phase file wins.

---

# Competitive Landscape Schema (Layer 1)

**Version:** 1.0.0
**Output path:** `.claude/context/competitive-landscape.md`
**Produced by:** `positioning-framework`
**Consumed by:** website-audit, copy briefs, sales enablement, content strategy, hypothesis roadmap, most downstream skills
**Replaces:** `market-landscape.md` + `competitor-profiles.md` (merged pre-release)

---

## Purpose

Combined competitive and market context in a single file. Contains market framing, buyer alternatives, JTBD taxonomy, per-competitor deep dives with inline battle card data, pricing comparison, claim overlap analysis, and white space identification.

This replaces the prior two-file split where `market-landscape.md` held market-level data and `competitor-profiles.md` held per-competitor data. The old split created redundancy: market-landscape's "Competitive Overview" summary tables duplicated competitor-profiles' JTBD Taxonomy. The merged structure has ONE competitive hierarchy (the JTBD Taxonomy) with no summary-vs-detail duplication.

**Boundary rule:** Everything about the competitive landscape goes here: market framing, buyer alternatives, competitor analysis, claim overlap, white space. Company identity facts (services, differentiators, proof points, pricing model) live in `company-identity.md` (L0). Persona messaging, voice, and positioning strategy live in other L1 files.

---

## Schema Definition

### YAML Frontmatter

```yaml
---
schema: competitive-landscape
schema_version: "1.0"
generated_by: positioning-framework  # skill that first created this file
depth: standard                      # "quick" | "standard" | "deep"
last_updated: 2026-02-16
last_updated_by: positioning-framework  # skill that last modified this file
confidence: 3                        # 1-5, lowest section confidence within this file
company: "Company Name"

# Market-level summary
category: "B2B conversion optimization"
category_buyer_term: "CRO agency"       # what buyers actually search for

# Competitive summary
competitors_analyzed: 3
top_competitors:
  - name: "Competitor A"
    positioning: "their H1 or core claim"
    threat_level: high                   # high | medium | low | emerging
  - name: "Competitor B"
    positioning: "their claim"
    threat_level: medium
  - name: "Competitor C"
    positioning: "their claim"
    threat_level: medium
competitor_names:
  - "Competitor A"
  - "Competitor B"
  - "Competitor C"
white_spaces:
  - "unclaimed territory 1"
  - "unclaimed territory 2"
overlap_zones:
  - "claim made by 2+ competitors"
claim_overlap_score: 0.72               # non-unique claims / total claims (0-1)
---
```

**Field notes:**
- `depth`: "quick" = surface level. "standard" = enough for messaging. "deep" = extended competitive analysis (Tier 2/3 sources).
- `claim_overlap_score`: Number of non-unique claims / total claims in the Claim Overlap Map. Higher = more generic positioning.
- `top_competitors`: Only the top 3 in frontmatter. Full list in body and in `competitor_names`.
- `category_buyer_term`: What buyers search for, not what the company calls itself. If these differ, the Category Gap section in `company-identity.md` documents the mismatch.
- `competitor_names`: Full list of all competitors with profiles in the body. Downstream skills check this to see who's covered.

**Downstream consumption pattern:** Read frontmatter first. If `top_competitors`, `white_spaces`, and `claim_overlap_score` are sufficient, stop there. Only read the body when you need JTBD detail, per-competitor profiles, or battle card data.

---

### Markdown Body Sections

#### 1. Market Overview (REQUIRED)

Category framing and buyer context. 2-3 sentences for someone unfamiliar with the space.

```markdown
## Market Overview

[Category] is the market for [what buyers are trying to do]. Buyers typically search for "[buyer terms]". [Company] positions as [how they frame themselves] within this space.
```

**Used by:** Website audit (category alignment), content strategy (keyword framing), ad copy (search terms).

---

#### 2. Buyer Alternatives (REQUIRED)

How buyers solve the problem without hiring any vendor. This is often the real competition.

```markdown
## Buyer Alternatives

| Alternative Behavior | Why They Do It | What It Costs Them | When They Outgrow It | Source |
|---------------------|---------------|-------------------|---------------------|--------|
| | | | | |
```

Write in buyer language, not analyst language. At least 3 alternatives. Each alternative must cite at least one source, or be marked `[INFERRED]`.

**Used by:** Messaging framework (push/pull dynamics), copy briefs (problem-aware content), ad copy (objection handling).

---

#### 3. JTBD Taxonomy (REQUIRED)

Competitors categorized by relationship to the customer's Job To Be Done. This is the single competitive hierarchy for the file. All three tiers required with real competitor names.

```markdown
## JTBD Taxonomy

### Direct Competitors
Same JTBD, same type of solution.

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |
|-----------|------------------|---------------------|--------------------------|--------------------------|

### Secondary Competitors
Same JTBD, different type of solution.

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |

### Indirect Competitors
Different JTBD, conflicting solution that prevents adoption.

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |
```

**Used by:** Battle card generation (tier context), positioning framework, sales enablement, copy briefs.

---

#### 4. Per-Competitor Profiles (REQUIRED)

One subsection per Major and Emerging competitor. Minor competitors get a row in the JTBD Taxonomy table only (no profile). Battle card data is INLINED here, not produced as separate deliverables.

```markdown
## Competitor Profiles

### [Competitor Name]

**Size:** [Major/Emerging] | [headcount, funding, key scale metrics]
**Tier:** [Direct/Secondary/Indirect]

**Positioning:**
- H1: "[exact headline]"
- Category claim: [what shelf they put themselves on]
- Primary differentiator: [their #1 claim]

**Proof & Social Proof:**
- [Logos, testimonials, case study count, named customers]

**Pricing Model:**
- [Model, tiers, relative positioning. Mark [NEEDS CONFIRMATION] if inferred]

**Tone/Voice:**
- [Formal/casual, technical/accessible, personality notes]

**Recent Strategic Signals:**
- [New content, hires, acquisitions, repositioning. From Tier 2/3 sources if available]

**Specific Competitive Tactic:**
- [One concrete example: a specific page, form, pricing trick, dark pattern, or sales behavior. URL if available]

**Battle Card:**
- **Strengths:** [What they're genuinely good at]
- **Weaknesses:** [Where they fall short for your target customer]
- **When we win:** [Scenarios, customer types, or use cases where you beat them]
- **When we lose:** [When they're the better choice. If empty, the analysis isn't honest.]
- **Killer question:** [A question that exposes their weakness without trash-talking]
- **Proof to deploy:** [P_ IDs from L0's Proof Point Registry]

**Confidence:** [1-5 for this competitor's data quality]
```

**Used by:** Sales enablement (battle card data is inline), copy briefs (competitive context), positioning framework.

---

#### 5. Competitive Attributes Matrix (REQUIRED)

Company attributes mapped against competitor types. Company attributes sourced from L0's Stated Differentiators.

```markdown
## Competitive Attributes Matrix

| Category | Target Company | vs. Direct | vs. Secondary | vs. Indirect |
|----------|---------------|-----------|--------------|-------------|
| Capabilities | | | | |
| Service model | | | | |
| Pricing/structure | | | | |
| Expertise/credentials | | | | |
| Customer experience | | | | |
```

For each claimed attribute: Is it verifiable? Could a competitor claim it tomorrow? What evidence exists (reference P_ IDs from L0)?

**Used by:** Battle cards (win/lose scenarios), messaging framework (proof mapping).

---

#### 6. Competitive Pricing (REQUIRED)

```markdown
## Competitive Pricing

| Dimension | Target Company | Competitor A | Competitor B | Competitor C |
|-----------|---------------|-------------|-------------|-------------|
| Pricing model | | | | |
| Relative positioning | | | | |
| Engagement model | | | | |
| Minimum engagement | | | | |
| Contract structure | | | | |
```

Target company pricing pulled from L0's Pricing Model. Do not re-research.

**Revenue estimation discipline:** Only estimate competitor revenue when you have concrete signals (public funding rounds, published revenue figures, Growjo/ZoomInfo data, SEC filings). Otherwise write "Unknown." Unfounded estimates undermine credibility.

**Used by:** Battle cards (pricing objection handling), sales enablement.

---

#### 7. Claim Overlap Map (REQUIRED)

Which company claims are unique vs. shared with competitors.

```markdown
## Claim Overlap Map

| Claim | Us | Comp A | Comp B | Comp C | Unique? | Use As |
|-------|-----|--------|--------|--------|---------|--------|
| [claim] | x | x | x | - | NO | Qualifier (body copy) |
| [claim] | x | - | - | - | YES | Headline / lead |
```

**Rules:**
- Company claims sourced from L0's Stated Differentiators.
- Mark as unique ONLY if no competitor makes a substantially similar claim.
- `PARTIAL` is a valid value in the Unique? column: use when a claim overlaps on surface promise but differs on mechanism, audience, or proof. Format: `PARTIAL ([surface claim] overlaps; differs on [mechanism/audience/proof])`.
- Campaign taglines are NOT claims. Only durable positioning statements.
- Downstream skills: never lead with a claim marked "NO" in the Unique column. Those are table stakes. Lead with "YES" claims only. PARTIAL claims can lead IF the differentiating mechanism is made explicit.

**Used by:** Copy briefs (headline selection), messaging framework (hierarchy), website audit (claim validation).

---

#### 8. Competitive White Space (REQUIRED)

Unclaimed positioning territory based on the full competitive analysis.

```markdown
## Competitive White Space

1. **[Territory name]** [Ready/Credible/Aspirational] - [Why it's unclaimed and why it matters to buyers]
2. **[Territory name]** [Credible] - [...]
```

At least 1 white space identified. Include where the market is over-indexed (everyone claims the same thing).

Addressability ratings: **Ready** = L0 shows existing capability + proof (cite P_ IDs). **Credible** = existing capability, no proof yet (default). **Aspirational** = no existing capability.

**Used by:** Hypothesis roadmap (experiment opportunities), messaging framework (differentiation), content strategy (thought leadership angles).

---

#### 9. Market Over-Indexing (OPTIONAL)

Where the market is saturated on one message, creating differentiation-by-absence opportunities.

```markdown
## Market Over-Indexing

- **"[Overused claim]"** - [Who claims it and why it's now table stakes]
```

**Used by:** Copy briefs (what NOT to lead with), brand voice (tone differentiation).

---

#### 10. Buyer Scenarios & Objections (REQUIRED)

Buyer scenarios that map to competitive win/lose dynamics, and common objections from the market.

```markdown
## Buyer Scenarios

| Buyer Scenario | Trigger | What They Need | Where They Look First |
|---------------|---------|---------------|----------------------|

## Common Objections

| Objection | Source | Existing Rebuttal | Rebuttal Strength |
|-----------|--------|-------------------|-------------------|
```

**Used by:** Battle cards ("When We Win/Lose" maps to scenarios), objection handling in copy.

---

#### 11. Competitor Confidence Ratings (REQUIRED)

```markdown
## Competitor Confidence Ratings

| Competitor | Confidence | Validation Sources | Notes |
|-----------|-----------|-------------------|-------|
```

**Used by:** Skills deciding whether to trust competitor data or re-research.

---

#### 12. Founder/Leadership Intelligence (OPTIONAL)

Key leadership insights from podcast appearances, interviews, earnings calls.

```markdown
## Founder Intelligence

### [Name] ([Competitor])
- [Key strategic insights from interviews, podcasts, earnings calls]
```

**Used by:** Battle cards (strategic context), sales prep.

---

## Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

A competitive-landscape.md file is considered **complete** when:

- [ ] YAML frontmatter has all required fields (schema, schema_version, generated_by, depth, last_updated, last_updated_by, confidence, company, category, category_buyer_term, top_competitors, competitors_analyzed, competitor_names, white_spaces, overlap_zones, claim_overlap_score)
- [ ] Market Overview defines the market in buyer language
- [ ] Buyer Alternatives has entries from verified sources (target: 3+ non-vendor alternatives in buyer language; fewer is acceptable with gap marker)
- [ ] JTBD Taxonomy covers all three tiers with real competitor names
- [ ] Per-Competitor Profiles exist for every Major and Emerging competitor
- [ ] Each profile includes verbatim H1, category claim, at least one specific competitive tactic, and inline battle card data (strengths, weaknesses, when-we-win, when-we-lose, killer question, proof to deploy)
- [ ] Battle card "when we lose" is populated for every profiled competitor (empty = dishonest analysis)
- [ ] Competitive Attributes Matrix maps L0 differentiators against competitor types with P_ evidence references
- [ ] Competitive Pricing section populated (or flagged with confidence impact)
- [ ] Claim Overlap Map covers claims from L0's Stated Differentiators (target: 5+; fewer is acceptable with gap marker)
- [ ] No campaign taglines in the Claim Overlap Map
- [ ] Competitive White Space identifies unclaimed territory (target: 1+; mark `[NONE FOUND - no buyer signals available]` if none identified from available data)
- [ ] Buyer Scenarios has entries from verified sources (target: 3+; fewer is acceptable with gap marker)
- [ ] Competitor Confidence Ratings populated for every profiled competitor
- [ ] `confidence` value equals the lowest section confidence within this file
- [ ] Post-Research Questionnaire included (3-5 questions at standard, 5-10 at deep) with specific, research-informed questions

---

## Versioning Rules

When a skill extends this file (e.g., a deep-depth run extending standard-depth analysis):

- Update `last_updated` and `last_updated_by` to the extending skill
- Preserve `generated_by` as the original producing skill
- Can only RAISE confidence scores, never lower them
- Preserve existing competitor profiles; do not overwrite unless the extending skill has strictly better data
- Append new competitor profiles for net-new competitors
- Extend the Claim Overlap Map with additional competitor columns or new claims
- Add to White Space and Buyer Scenarios; do not overwrite existing entries
- Mark extended sections with `<!-- extended by [skill-name] [date] -->` comments
- Update `competitors_analyzed`, `competitor_names`, and `top_competitors` in frontmatter

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
| 2026-02-16 | Initial creation | positioning-framework |
| 2026-02-18 | Extended to 8 competitors, deeper white space | positioning-framework (deep) |
```
