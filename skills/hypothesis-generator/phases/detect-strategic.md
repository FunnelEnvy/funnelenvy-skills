# Phase 2c: Strategic-Lever Detection

## Purpose

Read strategy, objective, audience, and competitive context for **business-level levers**, not page elements, and mint first-class strategic-lane opportunities that carry a measurement design. Where Phase 2 matches page-element patterns and Phase 2b catches novel page-element signals, this phase looks one altitude up: programs, offers, audience motions, and assets that move a business outcome and can be measured by a design beyond on-page A/B.

This phase runs after Phase 2b. It is **default-on and context-gated**: it fires only when the loaded context affirmatively names a business-level lever. With no qualifying lever in the loaded context, it emits nothing and is byte-inert (no padding, no new sections, no altitude change to the roadmap). Most candidate levers are expected to fail the quality gate, exactly as in Phase 2b. The gate prevents the lane from becoming a strategic-sounding dumping ground.

The lever families below are generic to B2B CRO. They derive entirely from inputs the skill already loads. No client-specific lever is hard-coded.

## Required Inputs

- Full bodies of all loaded context files (carried forward from Phase 1): `company-identity.md` (L0), `positioning-scorecard.md`, `competitive-landscape.md`, `audience-messaging.md`, and `performance-profile.md` when present
- The structural observation artifact when present (KB mode only; `silver-structural-observation`), including its `not_checked` fields for criterion 7's context-is-silent state
- The stated business objective when available (from the brief, the spec, or context)
- The optional soft field per the `Optional Soft Input` section below

**No input is required.** Each lever family derives from one or more of the inputs above and degrades independently when its source is absent. Absence is penalty-free: a missing source simply means that lever family emits nothing. The phase never stops, caps confidence, or flips mode on a missing input.

## Quality Gate

Every strategic-lever opportunity MUST pass ALL criteria below. If any criterion fails, the candidate is discarded (a lever family that resolves only to a vague "messaging could be stronger" fails on specificity). This gate is modeled on the Phase 2b gate, with the page-and-element criterion relaxed and the rest carried forward in intent.

1. **Specific observable signal.** The opportunity points to a concrete condition named in a context file section. "The positioning could be sharper" fails. "positioning-scorecard rates Proof as Missing; competitive-landscape shows two competitors leading with named-client ROI evidence the company lacks" passes.

2. **Named intervention unit (RELAXED).** The opportunity names a specific intervention unit that is a **named lever, offer, audience-motion, or asset OR a page element**. Page-and-element specificity is no longer required, but specificity still is. "A landing page" fails. "Improve messaging" fails. "Introduce a named-client ROI proof asset" passes; "shift lead routing to same-day human follow-up for inbound demo requests" passes; "add a lower-commitment offer tier (a guided assessment) beside the demo request" passes.

3. **Falsifiable causal mechanism.** The hypothesis includes a behavioral, economic, or buying-process principle that explains why the change should move the business outcome, and a negative result must be imaginable. "This will improve pipeline" fails. "A named-client ROI asset reduces perceived risk for the economic buyer in a multi-stakeholder evaluation, which should raise the qualified-demo rate; if qualified-demo rate is flat after the asset is live, the risk-reduction mechanism is wrong" passes.

4. **Before state documented.** The current state is directly quoted from context or clearly inferable from a specific context file section (the missing asset class, the current routing, the current offer ladder, the stated objective vs. the funnel's optimized metric). Invented or assumed before-states fail.

5. **Genuine uncertainty.** The outcome is not predetermined. A lever whose result no reasonable stakeholder would dispute is a "just do it" decision, not an experiment; flag it in "What's Not Here" instead of minting it here.

6. **Not a pattern gap.** The lever should not be a page-element pattern that was skipped only for missing data. If a richer data load would have triggered a Phase 2 pattern at the page-element altitude, route it to Prerequisites rather than minting a strategic lever.

7. **Gap is still open.** Assess the named intervention's current status against the loaded context, distinguishing three states:

   - **Documented live.** Any loaded artifact documents the capability, instrumentation, routing, asset, or measurement as implemented, live in production, shipped, or operating. The gap is closed: discard the lever and note it in "What's Not Here" as an existing capability. The only residual experiment a closed gap supports is a usage/adoption test of the existing capability, minted on its own merits, never as "stand up" the capability. **Built-but-disabled is this state, not documented-absent:** a capability documented as implemented but disabled, unentitled, or scoped to a subset of accounts/surfaces is documented-live with a documented-open ENABLEMENT gap. The permitted shape is the enablement/adoption experiment of the existing capability (with `absence_verified: true` on the enablement gap itself), never a "stand up" build; refinement work the context names (better logic, a supporting model) is that experiment's stand-up dependency, not grounds to reframe the lever as a build. Read the before-state (criterion 4) for *current status*, not just current shape: a documented "live" / "in production" / "already reporting" status lands here.
   - **Documented absent.** A loaded artifact affirmatively states the capability does not exist (a named data gap, a documented missing asset class, an explicitly absent instrumentation). The gap is open and evidenced: the lever may be minted as a build, subject to the remaining criteria. Comprehensive-inventory silence also lands here: when the loaded context comprehensively inventories a surface it does cover (the site's offer set, its conversion-event inventory) and the capability does not appear in that inventory, that absence is documented, not silence. The context-is-silent state below is reserved for systems the context was never positioned to observe.
   - **Context is silent.** No loaded artifact bears on the capability's status, AND either (a) the capability lives in a client-side system the loaded context does not cover (CRM, sales operations, marketing automation, data warehouse, internal reporting), OR (b) the capability's before-state rests on a structural-observation field recorded `not_checked` for a website surface -- a page or asset whose existence the capture did not check this run. Both are the same underlying state, distinct from documented-absent above: something the loaded context could have borne on but does not, rather than something it inventoried and found missing. Silence about a system the context was never positioned to observe, or about a surface the capture did not check, is NOT evidence of absence. The lever may still be minted, but ONLY in the confirm-first shape: the first sequenced step of the experiment is verifying whether the capability already exists, not building it, and the record carries `absence_verified: false` (see the opportunity-record addition below). A lever whose before-state rests on silence -- system-silence or not-checked-silence alike -- and that is minted as an unconditional build fails this criterion.

   The prior binary reading (documented-live fails, everything else passes) is superseded: silence and documented absence are no longer the same state.

   **Documented-in-flight is a distinct fourth state, named explicitly.** A client initiative documented as decided and already in Design/Build -- the decision is made, but the capability is not yet live -- is neither documented-live (nothing is operating yet) nor documented-absent (the gap is not open: a decision has already closed it). It discards via criterion 5 (Genuine uncertainty), not this criterion: the "should we build this" question is already settled, so there is no genuine uncertainty left to test. Name the discard for what it is in "What's Not Here": an in-flight initiative, distinct from criterion 7's documented-live "existing capability" note and from a build recommendation. The only residual experiment available once the initiative ships is reading the rollout (an adoption, usage, or performance read of the newly live capability), which may be minted on its own merits in a later run, exactly as the documented-live residual experiment is.

State, as with Phase 2b, that most candidate levers are expected to fail this gate. A surviving lever is a genuine business-altitude experiment with a measurable design, not an aspiration.

**Blocked-pending-decision routing.** A lever that passes all seven criteria but is documented as blocked pending an explicit client decision routes to the strategic "What's Not Here" as a decision-blocked item, carrying its demand evidence and the decision that unblocks it. It is re-evaluated on the next run and is never minted while blocked.

---

## Lever Families (inline checklist)

Evaluate the loaded context against each of the six generic B2B lever families below. Each family is a lens, not a quota: a run may surface several from one family and none from another, or nothing at all. For each candidate, capture the one-line definition fit, the context source it derives from, and a mechanism sketch, then run it through the Quality Gate above.

1. **Objective mismatch.** The stated business objective differs from what the page funnel actually optimizes (e.g., the objective is qualified-lead rate or pipeline quality, but the funnel optimizes raw form submits). Source: the stated objective plus `performance-profile.md` conversion definitions. An INFERRED objective (derived from the loaded strategy context plus the performance profile's own conversion definitions) suffices for this family's mismatch read when those conversion definitions make the mismatch observable without the inference doing the work; the elicited soft input (per `Optional Soft Input` below) is always preferred when present.

   **This family produces two distinct object types, never one conflated bet:**

   a. **A Measurement Foundation entry (unscored prerequisite).** Defining and instrumenting the qualified event is a stand-up, not an experiment: no reasonable stakeholder disputes its value, so it fails criterion 5 as a scored bet by construction. It routes to the strategic deliverable's Measurement Foundation section (see SKILL.md `Strategic Roadmap Output Format`), carrying what gets instrumented, which system does the work, and which scored experiments depend on it. It carries no ICE scores. Apply criterion 7's tri-state to the Foundation entry itself: documented-live discards it; silence about a client-side system gives it the confirm-first shape.

   b. **A scored strategic experiment (optional).** ONLY an intervention measured against the newly instrumented metric can be minted as a scored bet: a routing change, an offer change, an asset, a motion, read on the qualified outcome once the Foundation entry lands. Such a bet carries the Foundation entry as its stand-up dependency and sequences after it. If the context names no such intervention, family 1 emits the Foundation entry alone, and that is a complete, correct output.

   Generic example: the brief names "qualified pipeline" as the goal while the only instrumented conversion is an ungated contact-form submit. Family 1 emits (a) a Foundation entry to define and instrument the qualified-lead event, in confirm-first shape if the context is silent on whether the CRM already holds a usable qualified-lead view; and (b), only if the context names one, a scored intervention (e.g., a same-day follow-up routing change) measured against the new event. It never emits "instrument the event" as a scored experiment with an Impact score, because Impact anchors measure conversion effects, not value-of-information.

2. **Stakeholder-named dominant off-page lever.** A lever the client or stakeholders explicitly name as the dominant driver, living off the page (speed-to-lead, lead routing, follow-up cadence). Source: the stated objective, the optional soft field, or `audience-messaging.md` / competitive notes. Generic example: the prospecting team names same-day follow-up as the single biggest determinant of conversion, yet inbound routing currently replies in two-plus days; the lever is a routing/cadence change measured by speed-to-lead and downstream qualified-meeting rate.

3. **Biggest positioning / proof gap.** A missing asset class blocking the highest-leverage messaging (e.g., named-client proof or ROI evidence absent while the category competes on it). Source: `positioning-scorecard.md` (Needs Work / Missing dimensions) plus `competitive-landscape.md` (claim gaps). Generic example: the scorecard rates Proof as Missing and competitors lead with quantified customer outcomes; the lever is to stand up a named-client ROI asset and measure its effect on qualified-demo rate.

4. **Real alternative / status quo.** The dominant competitor is "do nothing" or "stay on the incumbent," and the messaging never addresses cost-of-inaction or displacement. Source: `competitive-landscape.md` (the status-quo / no-decision alternative). Generic example: deals stall at "we will revisit next year" rather than going to a named competitor; the lever is a status-quo-displacement framing (cost-of-inaction) measured by stage-progression or stall rate.

5. **Buying-group / multi-stakeholder motion.** The decision involves a buying group, not a single visitor, and the funnel speaks to one role. Source: `audience-messaging.md` personas (multiple decision roles). Generic example: personas list an economic buyer, a technical evaluator, and an end user, but the page addresses only the end user; the lever is a buying-group orchestration motion (role-specific content paths or a shareable business-case asset) measured by multi-threaded-opportunity rate.

6. **Offer architecture.** The commitment level of the offers themselves, not the copy of one CTA (an offer ladder, alternative commitment tiers). Source: L0 offers / CTAs plus `competitive-landscape.md`. Generic example: the only offer is a high-commitment "Request a demo" while solution-aware visitors have no lower-commitment entry; the lever is to introduce a lower-commitment offer tier and measure its effect on qualified-pipeline contribution, not just clicks.

### Archetype Family Extension

When Phase 1's archetype resolver (SKILL.md Phase 1 step 7) loaded an archetype pattern module that defines a `## Strategic Lever Families` section, those families load additively as families 7+ for this run: same quality gate, same opportunity-record shape (Step 2), with `lever_family` taking the module-defined token. Archetype families count as families for family precedence: they are checked before the Catch-All Leg, and a candidate matching one routes through it, never through the leg. This extension point is inert today: no archetype module defines strategic families, and a module without the section contributes nothing, penalty-free.

### Catch-All Leg (family-agnostic detection)

After walking the six families, perform one full-body read of the loaded context for any business-level lever (a program, offer, audience motion, asset, or operational motion that moves a business outcome) the context AFFIRMATIVELY names and that fits no family. The families are lenses, not the recall boundary: a lever is not disqualified for fitting none of them. This leg licenses what a generous read finds anyway, so detection does not depend on one run reading past the checklist while the next walks it literally.

- **Raised signal bar (the leg's only extra requirement).** A catch-all candidate must derive from signals in TWO independent loaded artifacts (e.g., a dormant capability named in the strategy context AND the commercial concentration that makes it valuable named in a performance or segmentation artifact). One artifact's mention is not enough: with no family template constraining the read, the two-artifact bar replaces the family's structural constraint. Independence is judged at the evidence-origin level: two artifacts restating the same underlying capture, quote, or figure (including an artifact echoing a claim from its own `depends_on` parent) are ONE signal, not two. The second signal need not name the lever again: the lever named once in one artifact plus independently derived evidence of its value in another (concentration, demand, or gap data) meets the bar, exactly as in the example above. Record both sources in `signal_source` as a list of artifact-and-section references.
- **Same gate, verbatim.** Every catch-all candidate runs the identical quality gate above, all seven criteria including criterion 7's tri-state. No relaxation anywhere.
- **Zero-survivor expectation.** The catch-all is expected to produce zero survivors on most runs. It is not a quota; a run whose six families already cover the context's levers correctly emits nothing here.
- **Anti-patterns.** "Strengthen the brand," "improve go-to-market," "invest in community," and any lever whose intervention unit or mechanism cannot be stated specifically fail criteria 1-3 exactly as family candidates do. Channel-scale programs the skill cannot specify from its loaded inputs (SEO, generative/AI-search optimization, organic content programs, paid-media strategy) are anti-patterns here regardless of signal support: their intervention unit requires channel analysis outside this skill's inputs, so they fail criterion 2 by construction; when the demand evidence is real, route them to "What's Not Here" as channel decisions rather than discarding silently. The leg must not become a strategic-sounding dumping ground.
- **Family precedence.** A candidate that matches a family routes through that family, never through this leg. Match on a family's DEFINITION sentence, not its name: a candidate that satisfies a family's definition routes there even when the fit is partial; a candidate that fails every family's definition is catch-all-eligible. A near-miss family never consumes-and-discards a candidate: it either matches, or the leg evaluates the candidate. The leg only ever ADDS candidates the families cannot see; it never re-routes or re-scores a family candidate.
- **Record shape.** Survivors mint the standard opportunity record (Step 2) with `lever_family: catch-all`, the same `ice_baseline: 3/3/3`, and the de-novo `confidence_penalty: -1` PLUS one additional -1 for family-less structural uncertainty (applied in `phases/score.md` Step 6b; both are soft modifiers, not a ceiling). Catch-all survivors flow through the identical construction, gate, scoring, and render path; in the rendered deliverable a catch-all experiment is indistinguishable from a family one.
- **Measurement-shaped finds.** A catch-all find whose intervention is itself instrumentation or measurement routes to the Measurement Foundation slot exactly as family 1a's stand-ups do: unscored, never an Impact-scored bet, folded into or listed beside the family-1 Foundation entries. The leg's scored-record shape applies only to non-measurement levers.

---

## Process

### Step 1: Lever Triage

Walk the six lever families, then the Catch-All Leg, against the loaded context. For each candidate lever:

1. Evaluate against all quality gate criteria.
2. If any criterion fails, discard with a brief note on which criterion failed (mechanism not falsifiable, unit not specific, before-state invented, etc.).
3. If all criteria pass, advance to Step 2.

Expected: most candidate levers fail the gate. This is by design. A context with no qualifying lever produces nothing here, and the roadmap is unchanged.

### Step 2: Opportunity Construction

For each lever that passes the quality gate, build an opportunity record:

```
Opportunity:
  pattern: strategic-lever
  type: "strategic"
  lane: "strategic"
  lever_family: [one of: objective-mismatch | dominant-off-page-lever | proof-gap | status-quo-alternative | buying-group-motion | offer-architecture | catch-all]
  trigger_signal: [the specific signal from context]
  signal_source: [which context file and section]
  measurement_design: [candidate design from the enum: randomized_ab | holdout | pre_post | cohort | geo_split | switchback | operational_metric -- this is a CANDIDATE; construct.md Step 4c finalizes it]
  ice_baseline: 3/3/3
  confidence_penalty: -1
  absence_verified: [true | false]   # true when a loaded artifact affirmatively documents the gap; false when the before-state rests on context silence about a client-side system
  confirm_first: [true | false]      # true when absence_verified is false; the experiment's first sequenced step is the existence check, not the build
  notes: [quality gate evaluation summary, causal mechanism sketch, stand-up dependency]
```

`absence_verified: false` forces `confirm_first: true`. A confirm-first record's stand-up dependency begins with the verification step, its rendered sequencing names the check as step one, and its Confidence carries the contingency (see `phases/score.md` Step 6b and `modules/ice-scoring.md`). Confirm-first is the ONLY shape available for silence-based levers; routing a standalone client question in place of minting is not an alternative here, because unminted questions do not survive into the deliverable.

Key differences from pattern-matched opportunities:

- `pattern` is always "strategic-lever" and `type` is "strategic".
- `lane: "strategic"` is the explicit lane tag. It is the routing discriminator: a record carrying it flows to the strategic construction, scoring, and render path (Step 3 and the `Output to Phase 3` section below), never onto the Phase 2 / 2b tactical opportunity list. The separate path keeps the tactical list strategic-record-free by construction, so the tag marks routing, not render placement.
- `measurement_design` is a candidate the phase proposes from the read; `construct.md` Step 4c selects and finalizes the design (and may refine it).
- `ice_baseline` starts at 3/3/3 (neutral midpoint), the same de-novo baseline as context-derived opportunities.
- `confidence_penalty` of -1 is applied during scoring (no pattern precedent = lower structural certainty), the same de-novo penalty as context-derived opportunities.

### Step 3: Cross-Deliverable Dedup Against the Tactical Opportunity List

Strategic opportunities do NOT merge into the Phase 2 / 2b tactical opportunity list. They flow to the separate strategic path. But because a strategic lever and a tactical page-element opportunity can target the same underlying idea, reconcile each strategic opportunity against the tactical opportunity list before it advances. This reconciliation spans the two deliverables (tactical roadmap and strategic roadmap); it does not collapse them into one list.

For each strategic opportunity, check whether a tactical opportunity already targets the same underlying idea via a page-element proxy:

1. **Same idea AND same measurement altitude:** the strategic record supersedes and absorbs the tactical one (merge the tactical detail into the strategic record's notes, and drop the tactical opportunity from the tactical list). This is the case where the page-element test and the strategic measurement are really the same experiment, so it belongs in one place: the strategic deliverable.
2. **Same idea BUT different measurement altitude:** both stand. They are complementary, not duplicate: the page-element A/B stays in the tactical opportunity list and renders in the tactical roadmap; the strategic measurement renders in the strategic deliverable. A page-element A/B and a strategic holdout on the same idea are genuinely different experiments that teach different things. Both records carry a scheduling-constraint annotation, and each deliverable renders it as ONE natural-language line: the strategic experiment's "Read condition and window" line states that the page-level test on the shared surface must not run overlapping the strategic read window (or must be accounted for in the read), and the tactical roadmap's Sequencing Rationale states the converse. The pair predicate is the conjunction: same underlying idea AND a shared read surface (a tactical test on the same idea but a disjoint surface is not a pair; a tactical test on the same surface but a different idea is not a pair). When more than one tactical test qualifies, the strategic line names each qualifying test (still one line, listing them), and each qualifying test's Sequencing Rationale carries its own converse. Register rules apply in full: the line is neutral and connective, never evaluative, and carries no internal tokens.
3. **No overlap:** the strategic opportunity passes alone to the strategic path.

This carries forward the Phase 2b dedup logic (detect-contextual.md Step 3) in substance; the only change is framing, from "merge into one list" to "reconcile across two deliverables" by measurement altitude. A regeneration-only strategic run (no tactical phases executed this run) performs this reconciliation against the on-disk tactical roadmap, read after detection completes. **A regeneration-only run never writes the tactical deliverable.** Its side of a case-2 scheduling line, and any case-1 drop, land on the tactical roadmap's next re-render; until then, note the pending tactical-side annotation (or drop) in the completion message so the operator knows the tactical deliverable lags. The strategic run renders only its own deliverable's line.

## Optional Soft Input

An optional soft field may strengthen detection when present: the business objective, the real alternative / status quo, or the dominant lever named by the client. It follows the same tri-state, penalty-free contract as the skill's other optional inputs (engagement-constraints, structural observation):

- **Present:** strengthens detection (sharpens lever families 1, 2, and 4 in particular).
- **Absent:** neither penalizes nor caps anything; the lever families still derive from the standard context files. Absence is the common case.
- It never flips the skill's mode and is never a mode-resolution requirement.

Mapping:

- **Legacy mode:** an optional field in `.claude/context/` (e.g., a stated business objective / real alternative / dominant lever note).
- **KB mode:** maps to the relevant silver artifact / objective field for the scope. When the bound KB defines an engagement-context / engagement-constraints reference artifact for the scope, that artifact IS the soft input and MUST be read when it exists: strategy-context artifacts that reference such a document for lever status make it load-bearing, and skipping it reproduces the already-solved-gap defect class (minting as a build a lever the engagement context documents as live or blocked).

**Active elicitation (interactive runs only).** When the run is INTERACTIVE and no soft input is present in any loaded source, ask the user ONE consolidated pre-flight question before Phase 2c detection, covering the three fields: the stated business objective; the dominant conversion driver as the client names it; and the real alternative buyers weigh. The question is asked at most once per run and never blocks a non-interactive run. Non-interactive or automated runs, and an unanswered question, proceed exactly as today, penalty-free: the absence semantics above are unchanged.

## Graceful Degradation

| Condition | Impact |
|-----------|--------|
| No qualifying business-level lever in context | Emit nothing. Behavior is byte-identical to pre-change output: no strategic hypotheses, no padding, no new sections. |
| A lever family's source context file is absent | That family degrades independently and emits nothing. Other families still evaluate. No penalty. |
| Optional soft field absent | Lever families derive from the standard context files. No penalty, no cap, no mode change. |
| A catch-all candidate has fewer than two independent bearing artifacts | The two-artifact signal bar is unmeetable for THAT candidate, not failed: the candidate is dropped penalty-free. Other catch-all candidates and family detection are unaffected. |

**Output to the strategic path:** Strategic opportunities do NOT join the tactical opportunity list. They flow to the strategic construction and scoring path: strategic-lane construction in `phases/construct.md` (Experiment Scope Rule unit allowance, Step 4c measurement design, Step 5b non-A/B feasibility branch), then strategic-lane scoring and tiering in `phases/score.md` (non-A/B feasibility judgment, separate strategic scoring/tiering, within-tier asset/ops clustering), then render into the separate strategic deliverable defined in `SKILL.md` > `Strategic Roadmap Output Format`. The tactical roadmap is built entirely from the Phase 2 / 2b opportunity list and is untouched by this phase. Detection ordering across phases stays 2 then 2b then 2c then 3.
