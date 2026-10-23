# Phase 3 -- Cross-Cutting Checklist

This is the reusable core of the skill. Run every check below against the roadmap, across all items (checks are cross-cutting: they catch patterns a per-item skeptic cannot see). Each check emits **either** a cited finding **or** an affirmative "clean" pass. A silent skip is not allowed: if a check cannot be evaluated because a source is missing, that is a finding ("cannot assess -- source absent"), not a pass.

Checks are ordered so that the most structurally material ones (guardrail readability, threshold computability) come first, matching how the reference pass ranked findings.

## Two evaluation modes per check

Since v1.9.x, `hypothesis-generator` stamps per-item `validation_gates` verdicts (six tactical, three strategic). Where a check overlaps a gate the generator already runs, this skill is a **gate-verdict audit**: read the recorded verdict and verify it against the cited sources, catching gates that passed wrongly or ran against stale context. Where no gate covers the dimension, run a **full re-derivation** using the Phase 2 skeptic outputs and the sources. If the roadmap carries no `validation_gates` records, every check is a full re-derivation.

The per-check `Mode` line below states the default for current-generator output. When the generator grows a new covering gate, re-classify that check from re-derivation to gate-audit (do not re-verify what a trustworthy gate already covers; verify the gate instead).

## Altitude

Each check gives a **Tactical form** and, where the tactical form assumes an A/B test with an MDE and a denominator, a **Strategic analog** for the non-A/B strategic lane (holdouts, pre/post, directional reads). Apply the form that matches the item's altitude.

## Measurement Foundation exemption (OQ4)

Unscored `## Measurement Foundation` entries in the strategic roadmap are instrumentation prerequisites, not experiments. They are **exempt** from CC2 (threshold) and CC6 (impact) checks. They get exactly one check: **CC-MF** below.

---

## CC1 -- Guardrail readability

- **Tests:** is every named guardrail metric actually measurable in the current instrumentation state described by the source performance profile? A guardrail that resolves to a dead event binding, an unscopeable segment, or a metric that does not fire today silently reads clean while a real regression goes invisible.
- **Tactical form:** check each item's guardrail against the profile's documented instrumentation state.
- **Strategic analog:** the guardrail is often a business metric; check it against the profile's business-metric instrumentation state and any documented attribution gaps.
- **Owned here.** `experiment-measurement-audit` (downstream, per-experiment) checks guardrail *definition* only, not readability against instrumentation. When a guardrail is not readable today, the finding requires an interim qualitative guardrail to be named.
- **Mode:** partial gate overlap (metric-instrumentation gate). Audit the gate verdict where present; re-derive readability specifically, since the gate checks instrumentation existence, not guardrail-scoped readability.

## CC2 -- Threshold / stopping-rule computability

- **Tests:** does every stopping rule have a computable threshold? A rule like "ship if it beats the test's MDE at full sample" is circular when the metric is variant-instrumented and has no baseline rate to compute an MDE from.
- **Tactical form:** flag any stopping rule that references an MDE or lift the metric has no baseline rate for. Require a pre-registered absolute threshold, or an explicit statement that the first run is baseline-setting, not ship/kill.
- **Posture audit (tactical):** audit every tier label, Test Feasibility line, and read window against the decision posture the roadmap itself declares, never against remembered values or the generator's own files. The roadmap declares it in How to Read: the rendered "Decision posture" line (confidence and sidedness, power, relative MDE, directional band) and the Quick Win ceiling the tier definitions state. Against a declared posture, each of these is a finding: a Quick Win whose estimated duration exceeds the declared ceiling; a feasibility line sized at a different MDE, confidence, or power than the declared posture, unless it surfaces a record's or profile's own stated detectable-effect floor for that surface and names that source (an unsourced non-posture MDE stays a finding); a feasibility line that does not name the traffic figure it was sized on. Only when the roadmap renders no "Decision posture" line (output from a generator before 1.18) audit tier labels and feasibility durations against the old fixed reference instead: 95% two-sided confidence, 80% power, a 15% relative MDE, a Quick Win ceiling of 6 weeks, and Infeasible beyond 26 weeks. A declared posture looser than that reference is not a finding: the roadmap states its bar, so the reader knows what a result means. Four things stay findings under any posture: a missing threshold part (next bullet); a second look at a running test, or an extension of one; a directional result shipped or credited as a win; and a test sized on a prior result's point estimate instead of the declared MDE.
- **Six-part read threshold (tactical):** a stopping rule passes CC2 under any declared posture, or under the fallback reference, if and only if it states all six parts: (1) the metric it reads; (2) the significance level, two-sided; (3) the MDE and the sample per arm the test is sized for; (4) a single pre-registered read point; (5) the directional action, meaning what happens when the lift points the predicted way but misses significance; and (6) the guardrail's margin together with the guardrail's own detectable drop at that sample. An explicit "no guardrail" clause with its reason also meets part 6, but only when the primary is a direct lead metric with no downstream metric to protect; whenever the primary is a proxy, or the item names a guardrail, the margin and its detectable drop are required. A missing part is a finding however strict or loose the posture. A one-sided primary read fails part 2; a one-sided harm stop on the guardrail, declared before launch, does not. A first run declared baseline-setting is not a ship/kill rule and is exempt until its baseline exists.
- **Strategic analog:** flag any non-A/B design (holdout, pre/post, directional read) with no pre-registered read criterion. A directional read with no declared bar is as empty as "beats the MDE."
- **Foundation:** exempt.
- **Mode:** gate-verdict audit where the tactical threshold gate is present; re-derive the strategic analog (verify the read criterion is actually pre-registered and computable). The posture audit and the six-part rule are always full re-derivation: a passing gate verdict says a threshold exists, not that it is complete or matches the declared posture.

## CC3 -- Headline-metric hygiene

- **Tests:** are the load-bearing numbers corrected for the caveats the source profile ITSELF documents (bot share, synthetic/monitoring traffic, non-addressable traffic)? A headline number used to size an opportunity without applying a caveat the source already flags is a finding.
- **Tactical + strategic:** same test; check every number the roadmap leans on for sizing or framing against the profile's own documented caveats.
- **Mode:** full re-derivation (no gate covers caveat application).

## CC4 -- Delivery and representativity bias

- **Tests:** does the variant actually reach the population the hypothesis targets, and does the read get biased toward a non-target segment? This is an interpretation threat, not only a launch gate: a "win" concentrated in a non-target segment can point opposite to intent.
- **Tactical form:** check documented delivery/exposure constraints against the item's target population.
- **Strategic analog:** check whether the lever's intervention reaches the buyer/account population it targets, given documented reach constraints.
- **Mode:** full re-derivation.

## CC5 -- Observation provenance

- **Tests:** are "current state" facts from production, or from test/fixture/staging data? Merchandising, pricing, and content claims are the highest risk. A hypothesis built on a pattern observed only in a test account, or absent on the one production surface observed, inherits this caveat.
- **Tactical + strategic:** check the provenance of every current-state fact the item relies on, using the source capture's own frontmatter/provenance notes.
- **Mode:** full re-derivation.

## CC6 -- Impact vs addressable

- **Tests:** does an Impact score conflate total surface traffic with the smaller, often unsized, addressable segment?
- **Tactical form:** flag any Impact resting on "highest-traffic surface" when the measurable effect is a micro-conversion on an unsized minority of that traffic.
- **Strategic analog:** flag any lever whose Impact rests on the whole program surface rather than a sized addressable population.
- **Foundation:** exempt.
- **Mode:** full re-derivation (the generator's Impact-anchor guard is a soft modifier, not a verdict gate).

## CC7 -- Bundle interpretability

- **Tests:** for any bundled item (multiple mechanisms or surfaces changed together), can a flat result name a single failure mode, or does the bundle collapse N independent mechanisms into one uninterpretable verdict?
- **Tactical + strategic:** check every multi-mechanism item; recommend split or sequence when a flat read would be uninterpretable.
- **Mode:** full re-derivation.

## CC8 -- Competing-mechanism check

- **Tests:** where multiple mechanisms could explain the same observed metric, is the item targeting the best-evidenced one? Uses the Phase 2 cold-derived mechanism (full-treatment items) vs the roadmap's chosen mechanism.
- **Tactical + strategic:** flag any item that targets a weaker-evidenced mechanism while a larger MEASURED signal points elsewhere.
- **Mode:** full re-derivation (this is exactly what the cold-derivation skeptic pass feeds).

## CC9 -- Claim-provenance floor

- **Tests:** is each item's load-bearing evidence verified, or is it hypothesized / vendor-asserted / unverified? An item resting on `[HYPOTHESIZED - NOT VERIFIED]` money quotes or a single unconfirmed observation should carry that as an explicit confidence ceiling, not an unmarked premise.
- **Tactical + strategic:** check the provenance tier of each item's key evidence against the source's own proof-status markings.
- **Mode:** full re-derivation.

## CC10 -- Contradicts prior result

- **Tests:** does any item re-test something a settled prior experiment already resolved? When the KB, the legacy experiment history, or the roadmap's cited experiment-history input records a prior outcome, flag items that re-run a settled question or contradict a prior directional result without acknowledging it.
- **Directional priors:** a prior the history labels directional, or one whose stated primary p falls in the roadmap's declared directional band with the lift in the predicted direction, must be acknowledged as directional at the declared posture. It earns a fresh confirmation test, never a rollout. An item that treats it as flat, or as a win (a rollout, or replication credit), is a finding. A prior is read at the plan it ran under: one that missed its own bar is not promoted to a win because it would clear the roadmap's posture today.
- **Unverified outcomes are not wins:** a prior outcome the history qualifies as unverified (for example, a bracketed qualifier saying the client's data team has not confirmed it) is not a settled win. An item that rolls it out or leans on it as replication-grade evidence is a finding; an item that aims in its leaning direction without that credit is not.
- **Tactical + strategic:** check each item against any available experiment-history evidence, in either mode. In legacy mode the source is `.claude/context/experiment-history.md` (when it declares `schema: experiment-history`) plus the `insight.md` experiment records, resolved and read per Phase 1. If no history source resolved, record "no experiment history available to check" (a scoped clean note, not a silent pass).
- **Mode:** full re-derivation.

## CC11 -- Premise-gap-still-open (strategic)

- **Tests (strategic items only):** independently verify each lever's premise gap is actually OPEN against current state, rather than accepting the roadmap's framing. This directly targets the documented strategic-lane defect: a lever minted for a capability that is already live in production because the generator read an artifact's shape, not its current status. Read current status across all resolved sources; distinguish documented-live (the gap is closed -- the lever is stale) from documented-absent (genuinely open) from context-silent (unknown -- the lever should be confirm-first, not a committed build).
- **Mode:** gate-verdict audit where the criterion-7 tri-state gate is present (verify the recorded documented-live / documented-absent / context-silent verdict against current-state evidence); full re-derivation otherwise.

## CC12 -- Deployed-state accuracy

- **Tests:** does each item's stated control describe what is **currently deployed** on the target surface, or a build a prior experiment or feature release has since replaced? Every other check in this list reads the roadmap's cited sources, which are knowledge-base artifacts. A claim faithful to those artifacts and false against the deployed product satisfies all of them. This check is the one that looks at the product.
- **Tactical form:** for each item, resolve the target surface's currently-shipped treatment and compare it against the item's `Current state` / `Before` block. Three failure shapes, all observed in the 2026-08-31 reference pass: a control describing a build a concluded experiment's winning variant replaced; a control whose own proposed change is already partly shipped, so the item is testing a variant against itself; and a surface described as untouched while a variant-less feature build is live on it.
- **Strategic analog:** the lever's premise-gap state. A lever proposed as a build for a capability already shipped to some population is the same failure at business altitude, and it is adjacent to but distinct from CC11: CC11 asks whether the gap is documented open, closed, or context-silent; CC12 asks whether the deployment record contradicts whatever the sources documented.
- **Boundary with CC5.** CC5 asks whether a current-state fact came from production or a fixture, a question about the **capture's origin**. CC12 asks whether a later deploy **superseded** that capture. A fact can be impeccably production-sourced and still describe a build retired since. Do not fold them: the evidence and the remedy differ.
- **Mode:** gate-verdict audit where the generator emitted a deployed-state annotation (verify the recorded shipped treatment against the deployment record); **full re-derivation otherwise**. The re-derivation path is not optional legacy handling: a roadmap generated before that annotation existed, or against a producer that surfaces experiment occupancy only, is exactly the case that produces falsified controls, and unlike the generator this skill may read the client's deployment record directly.
- **Occupancy is not deployed state.** A concluded experiment whose winning variant ships at full weight **frees its slot** and **becomes the control**. A source reporting only which experiment slots are occupied will report "nothing running here" for a surface whose control is a shipped variant. Never accept an occupancy signal as evidence a surface is unchanged.

## CC13 -- History-backlog coverage

- **Tests:** does the roadmap account for every recommendation the client's own experiment program already made? Build the backlog yourself from the history sources Phase 1 resolved, and derive every prose item's priority yourself from the record text, never from any generator output. A typed `next_experiments` item in an insight record carries its own priority; use it as written. Rate a prose next test by this rubric: an insight guide's designated lead experiment with no typed item is `recommended_lead`; a Next Steps follow-up the record names as primary, or, where the record has no Next Steps field, the next test its final Learning sentences name first, is `high`; a secondary or exploratory mention in Next Steps, the Learning, or a guide is `medium`. Every `recommended_lead` and `high` item must be accounted for in one of five ways: adopted as a hypothesis, merged into a named hypothesis, folded into a live experiment, routed to the strategic roadmap, or listed as considered and not advanced with its grounds. An item accounted for in none of these ways is a finding: the roadmap dropped a recommendation, and no reader can tell whether it was judged or missed. An item whose `surfaces` are empty, or name an audience, element, or off-site channel rather than a page, is still in the backlog; it belongs to its parent record's page or to the not-advanced list.
- **Tactical + strategic:** same test across both roadmaps. A strategic routing counts only when the strategic roadmap actually carries the lever; a merge counts only when the named hypothesis actually tests the item's mechanism.
- **Mode:** full re-derivation from the rendered `Experiment Program Continuity`, `Evidence From Completed Experiments`, and `What's Not Here` sections. The roadmap renders no experiment identifiers, so match each backlog item by surface and mechanism. Any coverage count the generator reports is a claim, not evidence: re-derive the backlog from the sources, never from the generator's history script or its ledger, so a parsing defect cannot pass both skills.
- **Boundary with CC10.** CC13 is about omission: a prior recommendation the roadmap never accounts for. CC10 is about contradiction: an item that re-runs a settled question or misreads a prior result. An item can pass one and fail the other; record each under its own check.
- **No history source:** record "no experiment history available to check backlog coverage" (a scoped clean note, not a silent pass). Medium and low items are never findings by omission: the roadmap may list them as considered without grounds, and may aggregate them when they are numerous.

## CC-MF -- Measurement Foundation integrity (strategic)

- **Tests (Foundation entries only):** is each unscored `## Measurement Foundation` entry a genuine instrumentation prerequisite, or is it a scored intervention smuggled in as unscored to dodge the scoring gates? A Foundation entry that proposes a user-facing change with an expected conversion effect is misfiled.
- **Mode:** full re-derivation.

---

## Completeness step (non-skippable)

After running CC1-CC13 and CC-MF, ask explicitly: **what structural flaw is present in this roadmap that none of the named checks caught?** The checklist is a floor, not a ceiling -- it was induced from prior passes and will miss flaw classes those passes did not exhibit. Record any additional structural finding here as `CC-EXTRA` with a cited basis. Note that deployed-state drift, which the 2026-08-31 reference pass recorded here, is now `CC12` and should not resurface as a `CC-EXTRA`. Likewise a Quick Win whose tier contradicts its own duration estimate, which the 2026-10-21 reference pass recorded here, is now part of `CC2`'s posture audit. A class that recurs has earned a named check, and this step exists for the ones that have not. If none, state "no additional structural flaw found" affirmatively.

## Output of this phase (held in-session)

Per check: verdict (finding or clean), the cited basis, and which items it touches. Findings are materiality-ranked (most structurally material first) for the critique's cross-cutting section and feed the Phase 4 self-critique grading (a self-critique "deflects" when it waves away a check finding that applies to its item).
