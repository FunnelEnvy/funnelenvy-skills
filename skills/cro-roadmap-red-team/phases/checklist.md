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
- **Strategic analog:** flag any non-A/B design (holdout, pre/post, directional read) with no pre-registered read criterion. A directional read with no declared bar is as empty as "beats the MDE."
- **Foundation:** exempt.
- **Mode:** gate-verdict audit where the tactical threshold gate is present; re-derive the strategic analog (verify the read criterion is actually pre-registered and computable).

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

- **Tests:** does any item re-test something a settled prior experiment already resolved? When the KB (or the roadmap's cited experiment-history input) records a prior outcome, flag items that re-run a settled question or contradict a prior directional result without acknowledging it.
- **Tactical + strategic:** check each item against any available experiment-history evidence; if no history source resolved, record "no experiment history available to check" (a scoped clean note, not a silent pass).
- **Mode:** full re-derivation.

## CC11 -- Premise-gap-still-open (strategic)

- **Tests (strategic items only):** independently verify each lever's premise gap is actually OPEN against current state, rather than accepting the roadmap's framing. This directly targets the documented strategic-lane defect: a lever minted for a capability that is already live in production because the generator read an artifact's shape, not its current status. Read current status across all resolved sources; distinguish documented-live (the gap is closed -- the lever is stale) from documented-absent (genuinely open) from context-silent (unknown -- the lever should be confirm-first, not a committed build).
- **Mode:** gate-verdict audit where the criterion-7 tri-state gate is present (verify the recorded documented-live / documented-absent / context-silent verdict against current-state evidence); full re-derivation otherwise.

## CC-MF -- Measurement Foundation integrity (strategic)

- **Tests (Foundation entries only):** is each unscored `## Measurement Foundation` entry a genuine instrumentation prerequisite, or is it a scored intervention smuggled in as unscored to dodge the scoring gates? A Foundation entry that proposes a user-facing change with an expected conversion effect is misfiled.
- **Mode:** full re-derivation.

---

## Completeness step (non-skippable)

After running CC1-CC11 and CC-MF, ask explicitly: **what structural flaw is present in this roadmap that none of the named checks caught?** The checklist is a floor, not a ceiling -- it was induced from prior passes and will miss flaw classes those passes did not exhibit. Record any additional structural finding here as `CC-EXTRA` with a cited basis. If none, state "no additional structural flaw found" affirmatively.

## Output of this phase (held in-session)

Per check: verdict (finding or clean), the cited basis, and which items it touches. Findings are materiality-ranked (most structurally material first) for the critique's cross-cutting section and feed the Phase 4 self-critique grading (a self-critique "deflects" when it waves away a check finding that applies to its item).
