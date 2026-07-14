# Prose-Craft Reference

Version: 1.0.0
Last updated: 2026-07-14
Scope: renderer- and generator-authored prose. The humanizer pass over agent-authored narrative slots and generated deliverable prose. NOT client-page variant copy (that is `copy-craft.md`).

Purpose: humanizer / anti-AI-writing rules applied as a rewrite and authoring discipline over agent-authored prose. Four consumers: (1) render-program-site, the Phase 4 humanizer pass over PROSE slots; (2) hypothesis-generator, roadmap prose discipline; (3) landing-page-generator, copy and design prose discipline; (4) cro-roadmap-red-team, critique prose discipline. This module governs HOW prose reads, not what is claimed. It never changes a claim, a score, or a recommendation.

Provenance: the enrichment signs (11 and up) draw on the StrategyU strategy-writing catalog (Minto Pyramid Principle, Zelazny, Carmen Simon), rewritten here in FunnelEnvy voice.

---

This is a self-contained reference. It does not depend on a device-level `humanizer` skill, which is not a declarable plugin dependency. Passages quoted verbatim from source markdown are already deliverable-grade and are exempt: the pass targets only agent-authored prose, never a verbatim quote pulled from an input file.

## How to Apply

Read each authored passage. For each sign below, check whether the passage exhibits it. Rewrite to remove the sign while preserving meaning. When in doubt, prefer the plainer phrasing. Introduce no new claims; only rephrase what the agent already wrote.

## Signs to Detect and Fix

The first ten signs are the core humanizer list. The remaining signs (11 and up) are the StrategyU enrichment.

1. **Inflated symbolism / significance.** Phrases that assign grand importance ("stands as a testament," "plays a vital role," "underscores the importance," "a beacon of"). Replace with the concrete fact.

2. **Promotional language.** Marketing puffery presented as fact ("cutting-edge," "seamless," "robust," "world-class," "best-in-class," "revolutionary," "game-changing"). State what the thing does, not how impressive it is.

3. **Superficial -ing analyses.** Trailing participial clauses that gesture at analysis without adding content ("..., highlighting the need for," "..., reflecting a broader trend," "..., emphasizing its role in"). Cut the clause or convert it to a concrete statement.

4. **Vague attributions.** Unsourced hedged claims ("industry experts agree," "studies show," "it is widely believed," "many argue"). Either name the source or drop the claim.

5. **Em-dash overuse.** Em dashes used as a catch-all connector. This repo bans em dashes entirely: use commas, colons, semicolons, or parentheses instead. Sweep for the character and remove it.

6. **Rule of three.** Reflexive three-item lists where two or one would do ("fast, reliable, and scalable"; "clear, concise, and compelling"). Use the items that carry real meaning; drop the filler third.

7. **AI vocabulary.** Words that cluster in AI output: "delve," "leverage" (as a verb), "tapestry," "realm," "landscape" (figurative), "navigate" (figurative), "foster," "underscore," "pivotal," "crucial," "boasts," "showcasing," "elevate," "harness," "unlock," "intricate," "multifaceted." Replace with plain equivalents.

8. **Negative parallelisms.** "It is not just X, it is Y" / "not only X but also Y" constructions used for rhetorical lift rather than content. Rewrite as a direct statement.

9. **Excessive conjunctive phrases.** Overuse of "moreover," "furthermore," "additionally," "in addition," "consequently," "thus," "therefore" to glue sentences. Cut most of them; let sentences stand on their own.

10. **Hedging clusters.** "Potentially," "it seems," "perhaps," "arguably," "in many ways," "to some extent" stacked together. State the claim or qualify it once, precisely.

11. **Lazy descriptors that dodge the insight.** Filler adjectives that sound analytical but carry no content ("significant," "important," "key," "notable," "considerable," "substantial") standing in for the actual finding. Name the specific thing that is significant and why, or cut the word. "A significant drop in demo signups" becomes "demo signups fell 40% after the form change."

12. **Copula avoidance.** Bending a sentence to avoid a plain "is/are," usually by promoting a weak verb ("serves as," "functions as," "represents," "constitutes," "acts as"). Use the direct copula. "The hero serves as the primary conversion driver" becomes "the hero is the primary conversion driver."

13. **Synonym cycling.** Rotating through synonyms for the same thing across a passage to avoid repeating a word ("the experiment," then "the test," then "the trial," then "the initiative" for one A/B test). Pick the correct term and repeat it. Consistent naming is clarity, not monotony.

14. **Nominalization.** Burying the action in a noun built from a verb ("the implementation of," "the utilization of," "the optimization of," "a reduction in," "the provision of"). Use the verb. "The implementation of the new CTA drove an increase in clicks" becomes "the new CTA drove more clicks."

15. **Fake-precision hedging.** Inventing a precise-sounding number or degree with no basis in the evidence ("roughly 30% of users," "the vast majority," "nearly all," "about 3x" when no source establishes the figure). Distinct from hedging clusters (sign 10): the problem here is manufactured precision, not stacked qualifiers. Cite the real figure or state the direction without a fabricated magnitude.

16. **Awkward verb-noun pairings.** Verbs yoked to nouns they do not naturally take, a tell of generated phrasing ("drive alignment," "deliver clarity," "enable visibility," "unlock efficiencies," "achieve simplicity"). Use a concrete verb and object. "This drives alignment across the funnel" becomes "this makes the funnel steps consistent."

17. **Anthropomorphized data.** Giving data intent or agency ("the data suggests," "the data wants," "the numbers tell us," "the metrics reveal," "the evidence argues"). Data does not suggest or want anything; a person reads it. Attribute the reading to the analysis or state the fact directly. "The data tells us bounce is high" becomes "bounce rate on the pricing page is 68%."

18. **Staccato noun-phrase lists.** Strings of terse noun phrases used as if they were sentences ("Higher conversion. Faster load. Clearer copy."). Distinct from rule of three (sign 6): the tell here is the fragment cadence, not the count. Write full sentences that connect the phrases and state the relationship between them.

19. **Structural tells.** Whole-passage patterns that read as generated: symmetrical paragraphs (every section the same length and shape), transitions that announce themselves ("Let us now turn to," "It is worth noting that," "With that in mind"), and compliment-before-critique framing ("While the roadmap is strong, ..."). Vary structure to fit the content, cut self-announcing transitions, and state the critique directly without a softening preamble.

## Conflict rule

Where a StrategyU rule and a repo convention conflict, the repo-stricter rule wins. Canonical example: the repo bans em dashes entirely, so StrategyU's allowance of one em dash per section does NOT apply. Sweep for the character and remove it (sign 5).

## Output Standard

Authored prose reads like a senior strategist wrote it: direct, specific, evidence-anchored, no filler. It persuades by being concrete, not by sounding impressive.
