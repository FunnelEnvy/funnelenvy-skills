> **Reference only.** The authoritative schema is inline in the corresponding phase file under `skills/positioning-framework/phases/`.
> If this file and the phase file disagree, the phase file wins.

---

# Positioning Scorecard Schema (Layer 1)

**Version:** 1.0.0
**Output path:** `.claude/context/positioning-scorecard.md`
**Produced by:** `positioning-framework`
**Consumed by:** website-audit, hypothesis roadmap, positioning-framework (Mode 3 audit); also serves as the quick-reference summary for sales, content writers, and new hires

---

## Purpose

Categorical assessment of positioning quality plus a scannable quick-reference summary. The quick reference, health check, messaging gap analysis, and per-section confidence scores. This is the "how good is the positioning" file that tells downstream skills where the gaps are and what needs fixing, and gives humans a 5-minute positioning overview.

**Boundary rule:** This file assesses the positioning. It does not define it (that's `audience-messaging.md`) or implement it (that's L2 deliverables like copy briefs).

---

## Schema Definition

### YAML Frontmatter

```yaml
---
schema: positioning-scorecard
schema_version: "2.0"
generated_by: positioning-framework
depth: standard
last_updated: 2026-02-17
last_updated_by: positioning-framework
confidence: 3
company: "Company Name"

# Structured summary (downstream skills can use frontmatter for quick decisions)
ratings:
  clarity: "needs_work"          # strong | needs_work | missing
  differentiation: "strong"
  proof: "missing"
  specificity: "needs_work"
  consistency: "needs_work"
  category_fit: "strong"
strong_count: 2
needs_work_count: 3
missing_count: 1
top_gap: "proof"                 # dimension name
top_opportunity: "clarity"       # dimension name
---
```

**Field notes:**
- `ratings`: Each dimension rated as `strong`, `needs_work`, or `missing`. No numerical scores.
- `strong_count`, `needs_work_count`, `missing_count`: Category tallies. Replace `overall_score`.
- `top_gap`: Dimension name of the single most impactful weakness.
- `top_opportunity`: Dimension name of the single most impactful opportunity.

---

### Markdown Body Sections

#### 0. Quick Reference (REQUIRED)

A scannable snapshot of the full positioning framework. This is what someone reads in 5 minutes to understand the company's positioning without digesting the full analysis. Sales reps keep this open during calls, content writers scan it before drafting, new hires read it on day one.

This section absorbs the former standalone quick-reference deliverable.

```markdown
## Quick Reference

# [Company Name] - Positioning Quick Reference

**One-liner:** [positioning statement from audience-messaging.md > Positioning Statement]
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

This is NOT a replacement for the full framework. It is a derived summary.

**Used by:** Sales teams (during calls), content writers (before drafting), new hires (onboarding), anyone who needs the 5-minute version.

---

#### 1. Positioning Health Check (REQUIRED)

```markdown
## Positioning Health Check

| Dimension | Rating | Key Finding |
|-----------|--------|-------------|
| **Clarity** | Strong / Needs Work / Missing | [specific evidence for rating] |
| **Differentiation** | Strong / Needs Work / Missing | [specific evidence for rating] |
| **Proof** | Strong / Needs Work / Missing | [specific evidence for rating] |
| **Specificity** | Strong / Needs Work / Missing | [specific evidence for rating] |
| **Consistency** | Strong / Needs Work / Missing | [specific evidence for rating] |
| **Category Fit** | Strong / Needs Work / Missing | [specific evidence for rating] |

**Overall: X Strong, Y Needs Work, Z Missing**

### Top Gap
[1-2 sentences on the single most critical weakness.]

### Top Opportunity
[1-2 sentences on the single most impactful opportunity.]
```

Ratings must be honest. Most companies land at Needs Work on most dimensions. Strong requires genuine evidence. Missing means the dimension is effectively absent. If a run produces all-Strong, the agent is broken.

The Key Finding column is required. One sentence of specific evidence for why that rating. This prevents ratings from becoming as meaningless as numerical scores.

**Used by:** Website audit (prioritizes fixes by Missing/Needs Work dimensions), hypothesis roadmap (experiments target Missing and Needs Work dimensions).

---

#### 2. Messaging Gap Analysis (REQUIRED)

For every line of hero copy and primary claims on the website:

```markdown
## Messaging Gap Analysis

| Copy Element | Source Page | Generic? | Evidence? | Recommendation |
|-------------|------------|----------|-----------|----------------|
| "[exact copy]" | Homepage H1 | Yes/No | Yes/No | [What to change] |
| "[exact copy]" | About page headline | Yes/No | Yes/No | [What to change] |
```

Generic = a competitor could paste this on their site. No evidence = assertion without proof.

**Used by:** Copy briefs (rewrite priorities), website audit (specific issues).

---

#### 3. Section Confidence Scores (REQUIRED)

Per-section confidence ratings for the entire positioning framework. Downstream skills check this before consuming sections.

```markdown
## Section Confidence

| Section | Confidence (1-5) | Limiting Factor | How to Improve |
|---------|-----------------|-----------------|----------------|
| Glossary | 4 | Need to confirm banned terms with client | Client review |
| Buyer Alternatives | 3 | Inferred from industry knowledge | Interview actual buyers |
| Competitive Landscape | 3 | Researched top 3 of 8 | Expand to full set |
| Value Themes | 4 | Strong proof for top 2, weak for bottom 2 | Source case studies |
| Personas | 2 | Inferred from website, not validated | Interview sales team |
| Market Category | 3 | Search validation done, no volume data | Add SEMrush/Ahrefs |
| Switching Dynamics | 3 | Inferred from reviews | Interview recent switchers |
| Objections | 3 | Pulled from reviews and FAQ | Need sales team input |
```

**Rule:** Sections scoring 1-2 produce DRAFT content. Sections scoring 4-5 produce final content.

**Used by:** Every downstream skill. This is the "can I trust this data" reference.

---

## Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

- [ ] YAML frontmatter has all required fields including ratings (per-dimension), strong/needs_work/missing counts, top_gap, top_opportunity
- [ ] Quick Reference section present with all subsections populated (one-liner, personas, differentiators, competitive positioning, proof points, health summary, objections, voice)
- [ ] Positioning Health Check has honest ratings (not all Strong) with specific Key Finding per dimension
- [ ] Messaging Gap Analysis covers at least homepage H1 and 2-3 other primary claims
- [ ] Section Confidence populated for every section of the positioning framework
- [ ] `confidence` value equals the lowest section confidence within this file

---

## Versioning Rules

- Update `last_updated` and `last_updated_by` when modifying
- Preserve `generated_by` as the original producing skill
- Ratings can change in any direction on re-assessment (unlike other L1 files where confidence only rises)
- Section Confidence can be updated by any skill that has new data affecting confidence
- Mark changes: `<!-- re-scored by [skill-name] [date] -->`

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
| 2026-02-17 | Replaced 1-5 numerical scores with categorical ratings (Strong / Needs Work / Missing). Renamed Positioning Scorecard to Positioning Health Check. | positioning-framework |
| 2026-02-16 | Added Quick Reference as section 0 (absorbed standalone deliverable) | positioning-framework |
```
