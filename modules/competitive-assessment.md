# Competitive Assessment Module

Shared analytical frameworks for assessing competitive claims, overlap, and differentiation. Used by any agent that evaluates how competitors position against a target company.

**Consumed by:** `phases/competitive.md` (Agent 2), future skills (Competitive Research Automator)
**Dependencies:** Requires L0 `company-identity.md` (Stated Differentiators section) as input. Does not fetch.

---

## 1. Claim Assessment Framework

Use this framework whenever assessing a competitor's positioning against the target company's stated differentiators.

For each differentiator from L0's Stated Differentiators section, evaluate every relevant competitor on three dimensions:

### Claim Status

Does the competitor explicitly assert this capability?

| Rating | Definition | Where to look |
|--------|-----------|---------------|
| YES | Appears on homepage, features/services page, or sales collateral | Primary site pages, pitch decks if available |
| PARTIAL | Implied but not explicitly stated (e.g., a case study shows the capability but it's not a headline claim) | Case studies, blog posts, job descriptions |
| NO | Not claimed anywhere in public materials | Confirmed after checking primary pages + review profiles |

### Proof Status

Does the competitor have evidence backing the claim?

| Rating | Definition | What qualifies |
|--------|-----------|----------------|
| PROVED | Specific metrics, named case studies, or third-party validation | "Reduced churn by 34% for [Named Client]", G2 badge, analyst report citation |
| CLAIMED | Asserted without supporting evidence | "We deliver best-in-class results" with no specifics |
| NONE | Not even claimed (Claim Status = NO) | N/A |

**Alignment with L0 Proof Point Protocol:** These ratings map directly to L0's evidence tiers (`verified` = PROVED, `supported` = PROVED or CLAIMED depending on specificity, `claimed` = CLAIMED). Use the same judgment standard.

### Replicability

Could the competitor credibly make this claim within 12 months?

| Rating | Definition | Examples |
|--------|-----------|----------|
| EASY | Hire a few people, add a page, adjust messaging | "Industry expertise" (any firm can hire from the industry) |
| HARD | Requires meaningful investment, track record accumulation, or organizational change | "10-year dataset of benchmarks" (can't shortcut time) |
| STRUCTURAL | Would require changing their business model, core technology, or fundamental go-to-market | "Integrated strategy + execution under one roof" for a pure advisory firm |

**The differentiation threshold:** Only attributes where the target company's competitors face STRUCTURAL replicability barriers qualify as true differentiators. Everything else is a temporary advantage at best.

### Output Format

Write each matrix cell as:

```
[Claim] | [Proof] | [Replicability] -- [one sentence summary]
```

Example:
```
YES | CLAIMED | STRUCTURAL -- Claims end-to-end PE value creation but no published case
studies with metrics; their audit-first model makes true operational execution a
structural shift.
```

---

## 2. Claim Similarity Assessment

Use this framework whenever determining whether two or more companies are making "the same" claim. This applies to the Claim Overlap Map and any cross-competitor comparison.

### Substantially Similar (mark as SHARED)

Two claims are substantially similar when a buyer hearing both would perceive them as interchangeable promises. The test: if you swapped the company names, would the claim still make sense without modification?

Examples of SHARED claims:
- "We focus on execution, not just strategy" vs. "We don't just advise, we implement" (same promise, different words)
- "Deep industry expertise in financial services" vs. "Specialized in financial services" (same scope, different emphasis)

### Not Substantially Similar (mark as UNIQUE)

Two claims are NOT substantially similar when they differ on at least one of:

- **Mechanism of delivery:** "AI-powered analytics" vs. "hands-on consultant teams" both promise "better insights" but via fundamentally different mechanisms
- **Target buyer:** "PE value creation for portfolio companies" vs. "mid-market growth advisory" both promise growth but for different buyers with different buying criteria
- **Scope of promise:** "Full P&L transformation" vs. "Sales process optimization" both improve revenue but at different altitudes

### Partial Overlap (mark as PARTIAL)

Use PARTIAL when claims share surface-level language but differ on mechanism, audience, or proof. This is the most common real-world case and the most important to get right.

Format for PARTIAL entries:

```
PARTIAL -- Overlaps on [surface claim] but differs on [mechanism/audience/proof].
```

Example:
```
PARTIAL -- Both claim "execution focus" but Accordion means data/analytics delivery
while Globex means human-centered organizational transformation. A buyer
choosing between them would not see these as the same service.
```

### Downstream Implications

- **SHARED** claims signal a differentiation problem. The target company cannot win on this claim alone.
- **PARTIAL** claims are usable as headlines IF the differentiating mechanism is made explicit in copy. Flag these as messaging opportunities, not problems.
- **UNIQUE** claims are the strongest positioning territory. Flag these for emphasis in deliverables.

### Origin-Aware Precedence

Origin-aware precedence rules are defined in `phases/competitive.md` Step 7 and take priority over this module's assessments.

---

## 3. Claim Overlap Score Calculation

After completing the overlap map, calculate:

```
claim_overlap_score = (SHARED count + 0.5 * PARTIAL count) / total claims mapped
```

- Score 0.0-0.3: Strong differentiation. Most claims are unique.
- Score 0.3-0.6: Moderate overlap. Messaging needs sharper positioning.
- Score 0.6-1.0: High overlap. Fundamental differentiation problem. Flag in scorecard.

The 0.5 weight for PARTIAL reflects that partial overlaps are exploitable with good messaging, unlike SHARED claims which require repositioning or proof escalation.

Write the score to frontmatter as `claim_overlap_score` (float, 2 decimal places).
