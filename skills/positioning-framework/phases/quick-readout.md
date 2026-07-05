# Quick Depth Readout (orchestrator-inline)

Read by the ORCHESTRATOR (not a spawned agent) when depth=quick, after Agent 1 completes.
SKILL.md > `Quick Depth Inline Health Check` defines when this runs and which dimensions are
assessable; this file carries the output templates, writing rules, and the quick-depth context
file spec. Verbatim extraction from SKILL.md (v1.1.2) -- no content change.

## Quick Depth Health Check Template

The orchestrator produces a single output containing two parts: a terminal summary and a lightweight context file.

**Terminal output (shown to user):**

```markdown
# Quick Positioning Readout: [Company Name]

**URL:** [url]
**Category:** [what shelf this sits on in the buyer's mind]
**Date:** [YYYY-MM-DD]

---

## 1. What They Say (Current Positioning)

[2-3 sentences summarizing how the company positions itself. Use their exact H1 and key claims. Note the category they claim vs. the category buyers actually use.]

**H1:** "[exact headline]"
**Claimed category:** [what they call themselves]
**Buyer's category:** [what buyers actually search for]
**Gap:** [mismatch between the two, if any]

**What users actually say:** [Pull 2-3 testimonial snippets from homepage or pricing page. Note whether testimonials reinforce or contradict the H1 positioning. If users praise X but the H1 claims Y, flag the disconnect.]

---

## 2. Competitive Context

[Who are the top 3 competitors and how do they position? One line each. Then: does this company show up when buyers search? Is it on review sites? Is it in listicles?]

| Competitor | Their H1/Positioning | Key Differentiator |
|-----------|---------------------|-------------------|
| | | |
| | | |
| | | |

**Discoverability:** [Found in search? On Clutch/G2? In "best X" lists? Be blunt.]

---

## 3. What's Actually Different (Top 3 Value Themes)

**Before writing this section, cross-reference the features page against the homepage claims. Look for:**
- Capabilities listed on the features page that the homepage doesn't lead with. Under-marketed features are often the strongest differentiators.
- Capabilities present on the features page that do NOT appear on any competitor's feature list. These outrank shared capabilities, even if the company buries them.
- Pricing tier gates. Features locked to higher tiers signal what the company considers premium value, which is often the real differentiator.

If you find a product capability that no listed competitor offers, it ranks above any narrative-level differentiator ("built by experts," "decade of experience") regardless of how prominently the company markets it.

| # | Differentiator | Proof | Strength |
|---|---------------|-------|----------|
| 1 | | | Strong / Moderate / Weak |
| 2 | | | Strong / Moderate / Weak |
| 3 | | | Strong / Moderate / Weak |

---

## 4. Positioning Health Check

| Dimension | Rating | Signal |
|-----------|--------|--------|
| Clarity | Strong / Needs Work / Missing | [one phrase] |
| Differentiation | Strong / Needs Work / Missing | [one phrase] |
| Proof | Strong / Needs Work / Missing | [one phrase] |
| Specificity | Strong / Needs Work / Missing | [one phrase] |
| Consistency | Strong / Needs Work / Missing | [one phrase] |
| Category Fit | Strong / Needs Work / Missing | [one phrase] |

**Overall: X Strong, Y Needs Work, Z Missing**

---

## 5. Top 3 Fixes (What to Do First)

[Three specific, actionable recommendations ranked by impact. Not generic advice. Tied to what you found in the research.]

1. **[Fix name]** - [What's wrong] -> [What to do] -> [Expected impact]
2. **[Fix name]** - [What's wrong] -> [What to do] -> [Expected impact]
3. **[Fix name]** - [What's wrong] -> [What to do] -> [Expected impact]

---

*Quick readout by positioning-framework --depth quick. For the full framework with battle cards, copy briefs, persona messaging, and structured data layer, run: /positioning-framework <url> --depth standard*
```

## Quick Depth Tips

- If the company has public pricing, that's a goldmine. Pricing structure reveals positioning more than any About page.
- The gap between "claimed category" and "buyer's category" is often the #1 finding. If nobody searches for the category term the company uses, that's the headline.
- When rating Proof, check for third-party validation (review sites, rankings, press). Self-published testimonials are weaker than independent reviews.
- The most useful output from a quick readout is often "here's what you're NOT saying that you should be." Whitespace identification in 3 sentences.

## Quick Depth Quality Rules

1. **Be opinionated.** This is not a research report. It's an assessment. Say what's good, what's bad, and what to fix. Don't hedge with "could potentially consider."
2. **No filler.** Every sentence must contain information. Delete any sentence that says "it's important to" or "in today's competitive landscape" or anything that could apply to any company.
3. **Proof hierarchy is strict.** Named customer + specific metric = Strong. Named customer + general praise = Moderate. Unattributed aggregate claim = Weak. If every value theme scores "Weak," say so.
4. **The health check must be honest.** Most companies land at Needs Work on most dimensions. Strong requires genuine evidence. Missing means effectively absent. If everything is Strong, something is wrong.
5. **Fixes must be specific.** "Improve your messaging" is not a fix. "Replace homepage H1 'We help businesses grow' with '[Specific category] for [specific audience] that [specific outcome]'" is a fix.
6. **Distinguish product reality from marketing reality.** If the features page shows capabilities the homepage doesn't lead with, note the gap explicitly. The scorecard should assess what the company markets, but the differentiator section should assess what the product actually does. A product with unique capabilities that are poorly marketed is a different diagnosis than a product with nothing unique. One needs better marketing; the other needs a better product.
7. **Never recommend building what already exists.** Before recommending "build X feature," verify the feature doesn't already exist on the features page, docs, or integrations list. If a capability exists but is poorly marketed, the fix is "surface X" not "build X."

## Quick Depth Context Files

At quick depth, produce two context files:

**1. `company-identity.md`** - Produced by Agent 1 as normal, but with `depth: "quick"` and confidence capped at 3.

**2. `positioning-scorecard.md`** - Minimal version with `depth: "quick"`:

```yaml
---
schema: positioning-scorecard
schema_version: "2.0"
generated_by: positioning-framework
depth: quick
last_updated: YYYY-MM-DD
last_updated_by: positioning-framework
confidence: 2  # max 3 at quick depth
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

## Quick Reference

[Abbreviated quick reference - positioning statement, top 3 differentiators, top 3 fixes]

## Positioning Health Check

[6-dimension table from the terminal output with Rating + Signal columns]
```

No messaging gap analysis section. No section confidence table. The full health check is produced at standard/deep depth.
