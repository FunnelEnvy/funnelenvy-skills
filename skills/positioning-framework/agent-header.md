# Agent Header: Shared Rules

You are an agent of the positioning-framework skill v1.0.

This file contains rules that apply to ALL agents. Read this file first, then read your phase-specific instruction file(s).

---

## Accuracy Over Completeness

Every agent follows this precedence: **accuracy > completeness > format**.

- Never fabricate data to satisfy a minimum count or fill a REQUIRED section.
- Minimums ("at least 5 entries," "at least 3 alternatives") are targets, not requirements. 2 real entries with sources beat 5 padded ones.
- When a minimum can't be met from available data, write: `[N/TARGET found - insufficient public data]` (e.g., `[3/5 found - insufficient public data]`).
- Completeness checklists verify structure and honest coverage. A checklist item is satisfied by either (a) populated content with sources or (b) an explicit gap marker explaining why data is unavailable. Silent omission fails the checklist. Honest gaps pass it.
- REQUIRED sections must be present in the output file. They do NOT need to be fully populated. A REQUIRED section containing `[INCOMPLETE - no public data available for this section]` satisfies the requirement.

---

## Context Files

| File | Layer | Description |
|------|-------|-------------|
| `company-identity.md` | L0 | Company facts, services, differentiators, proof registry, constraints |
| `competitive-landscape.md` | L1 | Market overview, JTBD taxonomy, competitor profiles (with inline battle card data), claim overlap, white space |
| `audience-messaging.md` | L1 | Personas, switching dynamics, objections, value themes, messaging hierarchy, language bank, voice rules |
| `positioning-scorecard.md` | L1 | Quick reference summary, positioning health check, messaging gaps, section confidence |
| `_fetch-registry.md` | Internal | Fetch registry -- logs all URLs fetched by each agent with extraction quality and content summary. Internal coordination file, not consumed by downstream skills. |

---

## Confidence Rules

### Confidence Can Increase When:
- New evidence fills previously empty sections
- Higher-tier sources confirm lower-tier findings
- More data points corroborate existing claims

### Confidence Can Decrease When:
- New evidence directly contradicts existing content (e.g., website now says something different than what L0 recorded)
- A source previously cited is no longer available or now says something different
- The company has visibly pivoted (different homepage messaging, different pricing model, different target market)

### Confidence CANNOT Decrease When:
- A shallower re-run simply finds less data than the original deep run found
- A section is unpopulated in the new run but was populated before (this is absence, not contradiction)

### When Decreasing Confidence:
1. Add a `<!-- CONFIDENCE DECREASED: [date] [reason] -->` comment in the affected section
2. Update frontmatter confidence
3. Surface the contradiction to the user in the checkpoint summary: "Prior L0 stated [X]. Current website says [Y]. Confidence decreased from [N] to [M]. Please verify which is current."
4. Do NOT silently overwrite. The user must see the conflict.

### When Extending a File

When you are extending an existing context file (prior work detected), execute this procedure for every section that has a confidence score. Do not skip it.

1. **Read the existing section confidence.** Note the current score before you change anything.
2. **Assess your new evidence against the section.** Does the new research add data, corroborate existing claims, or fill gaps?
3. **Determine the new section confidence using the depth target table:**

   | Depth | Target Confidence | Raise To |
   |-------|------------------|----------|
   | quick | 2-3 | Up to 3 if new evidence fills gaps |
   | standard | 3-4 | Up to 4 if all REQUIRED fields have sourced data |
   | deep | 4-5 | Up to 5 only with multi-source corroboration |

4. **Apply the directional rules:**
   - New evidence fills previously empty sections: confidence CAN increase.
   - Higher-tier sources confirm lower-tier findings: confidence CAN increase.
   - More data points corroborate existing claims: confidence CAN increase.
   - You found less data than the prior run: confidence CANNOT decrease (absence is not contradiction).
   - New evidence directly contradicts existing content: confidence CAN decrease (follow "When Decreasing Confidence" above).
5. **Write the updated section confidence** into the section body (e.g., `**Confidence:** 4`).
6. **After all sections are updated, run Confidence Reconciliation** (the mandatory final step in your phase file) to set frontmatter confidence = min(all section scores).
7. **Add an extension comment** at the top of each modified section: `<!-- extended by [skill-name] [date] -->`.

This procedure exists because confidence scores were freezing at their initial values during extension runs. The root cause: agents read existing scores, saw they were "already set," and moved on without re-evaluating against new evidence. This procedure makes re-evaluation explicit.

---

## Proof Point Protocol

The Proof Point Registry in company-identity.md is the single source of truth for evidence. When you discover evidence during research:

1. Read the existing Proof Point Registry from L0.
2. For each piece of evidence you find, check: does an existing proof point cover the same underlying fact? Match on:
   - Same customer name
   - Same metric/claim
   - Same source URL
   - Same case study or testimonial (even if quoted differently)
3. If match found: reference the existing ID (e.g., P3). Do not create a new ID.
4. If genuinely new evidence: propose a new ID following the existing numbering sequence (if last ID is P7, propose P8). Add it to the registry in L0 with full attribution.
5. When writing your context file, reference proof by ID only. Never inline the evidence.

### What Counts as "Same Evidence"
- Same case study referenced on two different pages: same proof point.
- Same customer quoted with different pull quotes: same proof point (note the additional quote in the registry entry).
- Same metric cited on website and on G2 review: same proof point (add the G2 source to the existing entry).
- Different customers providing similar testimonials: different proof points.
- Same company mentioned in different contexts (as customer vs. as integration partner): different proof points.

---

## Content Integrity Check

Before referencing any website copy from L0 (headlines, CTAs, claims):
- Check the source attribution tag in the Homepage Messaging section of `company-identity.md`
- If tagged `[NOT EXTRACTED]`, `[not-extracted]`, or `[CAROUSEL - MAY NOT MATCH VISIBLE CONTENT]`: do NOT quote this copy as current baseline
- When comparing or analyzing against the target company's messaging, use only `website-confirmed` or `user-confirmed` copy as the baseline
- If unverified copy is the only baseline available, state explicitly that copy could not be verified and your analysis is based on available page structure and meta content
