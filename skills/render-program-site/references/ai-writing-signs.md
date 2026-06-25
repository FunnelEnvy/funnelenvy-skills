# AI Writing Signs (Humanizer Reference)

Lean, portable embed of the signs of AI-generated writing. The render-program-site skill applies these rules in a final pass over agent-authored spoke prose (the `<!--PROSE-->` slot contents: lever, move, hypothesis, per-relationship commentary, score narrative) before the site is finalized. Passages quoted verbatim from the source roadmap markdown are already deliverable-grade and are exempt; this pass targets only prose the curation pass authors.

This is a self-contained reference so the skill does not depend on the device-level `humanizer` skill, which is not a declarable plugin dependency.

## How to Apply

Read each renderer-authored passage. For each sign below, check whether the passage exhibits it. Rewrite to remove the sign while preserving meaning. When in doubt, prefer the plainer phrasing. Do not introduce new claims; only rephrase what the renderer already wrote.

## Signs to Detect and Fix

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

## Output Standard

Renderer-authored prose should read like a senior strategist wrote it: direct, specific, evidence-anchored, no filler. The pitch persuades by being concrete, not by sounding impressive.
