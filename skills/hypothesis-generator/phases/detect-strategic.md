# Phase 2c: Strategic-Lever Detection

## Purpose

Read strategy, objective, audience, and competitive context for **business-level levers**, not page elements, and mint first-class strategic-lane opportunities that carry a measurement design. Where Phase 2 matches page-element patterns and Phase 2b catches novel page-element signals, this phase looks one altitude up: programs, offers, audience motions, and assets that move a business outcome and can be measured by a design beyond on-page A/B.

This phase runs after Phase 2b. It is **default-on and context-gated**: it fires only when the loaded context affirmatively names a business-level lever. With no qualifying lever in the loaded context, it emits nothing and is byte-inert (no padding, no new sections, no altitude change to the roadmap). Most candidate levers are expected to fail the quality gate, exactly as in Phase 2b. The gate prevents the lane from becoming a strategic-sounding dumping ground.

The lever families below are generic to B2B CRO. They derive entirely from inputs the skill already loads. No client-specific lever is hard-coded.

## Required Inputs

- Full bodies of all loaded context files (carried forward from Phase 1): `company-identity.md` (L0), `positioning-scorecard.md`, `competitive-landscape.md`, `audience-messaging.md`, and `performance-profile.md` when present
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

State, as with Phase 2b, that most candidate levers are expected to fail this gate. A surviving lever is a genuine business-altitude experiment with a measurable design, not an aspiration.

---

## Lever Families (inline checklist)

Evaluate the loaded context against each of the six generic B2B lever families below. Each family is a lens, not a quota: a run may surface several from one family and none from another, or nothing at all. For each candidate, capture the one-line definition fit, the context source it derives from, and a mechanism sketch, then run it through the Quality Gate above.

1. **Objective mismatch.** The stated business objective differs from what the page funnel actually optimizes (e.g., the objective is qualified-lead rate or pipeline quality, but the funnel optimizes raw form submits). Source: the stated objective plus `performance-profile.md` conversion definitions. Generic example: the brief names "qualified pipeline" as the goal while the only instrumented conversion is an ungated contact-form submit, so the optimized metric and the business goal diverge; the lever is to define and instrument a qualified-lead event and measure interventions against it.

2. **Stakeholder-named dominant off-page lever.** A lever the client or stakeholders explicitly name as the dominant driver, living off the page (speed-to-lead, lead routing, follow-up cadence). Source: the stated objective, the optional soft field, or `audience-messaging.md` / competitive notes. Generic example: the prospecting team names same-day follow-up as the single biggest determinant of conversion, yet inbound routing currently replies in two-plus days; the lever is a routing/cadence change measured by speed-to-lead and downstream qualified-meeting rate.

3. **Biggest positioning / proof gap.** A missing asset class blocking the highest-leverage messaging (e.g., named-client proof or ROI evidence absent while the category competes on it). Source: `positioning-scorecard.md` (Needs Work / Missing dimensions) plus `competitive-landscape.md` (claim gaps). Generic example: the scorecard rates Proof as Missing and competitors lead with quantified customer outcomes; the lever is to stand up a named-client ROI asset and measure its effect on qualified-demo rate.

4. **Real alternative / status quo.** The dominant competitor is "do nothing" or "stay on the incumbent," and the messaging never addresses cost-of-inaction or displacement. Source: `competitive-landscape.md` (the status-quo / no-decision alternative). Generic example: deals stall at "we will revisit next year" rather than going to a named competitor; the lever is a status-quo-displacement framing (cost-of-inaction) measured by stage-progression or stall rate.

5. **Buying-group / multi-stakeholder motion.** The decision involves a buying group, not a single visitor, and the funnel speaks to one role. Source: `audience-messaging.md` personas (multiple decision roles). Generic example: personas list an economic buyer, a technical evaluator, and an end user, but the page addresses only the end user; the lever is a buying-group orchestration motion (role-specific content paths or a shareable business-case asset) measured by multi-threaded-opportunity rate.

6. **Offer architecture.** The commitment level of the offers themselves, not the copy of one CTA (an offer ladder, alternative commitment tiers). Source: L0 offers / CTAs plus `competitive-landscape.md`. Generic example: the only offer is a high-commitment "Request a demo" while solution-aware visitors have no lower-commitment entry; the lever is to introduce a lower-commitment offer tier and measure its effect on qualified-pipeline contribution, not just clicks.

---

## Process

### Step 1: Lever Triage

Walk the six lever families against the loaded context. For each candidate lever:

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
  lever_family: [one of: objective-mismatch | dominant-off-page-lever | proof-gap | status-quo-alternative | buying-group-motion | offer-architecture]
  trigger_signal: [the specific signal from context]
  signal_source: [which context file and section]
  measurement_design: [candidate design from the enum: randomized_ab | holdout | pre_post | cohort | geo_split | switchback | operational_metric -- this is a CANDIDATE; construct.md Step 4c finalizes it]
  ice_baseline: 3/3/3
  confidence_penalty: -1
  notes: [quality gate evaluation summary, causal mechanism sketch, stand-up dependency]
```

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
2. **Same idea BUT different measurement altitude:** both stand. They are complementary, not duplicate: the page-element A/B stays in the tactical opportunity list and renders in the tactical roadmap; the strategic measurement renders in the strategic deliverable. A page-element A/B and a strategic holdout on the same idea are genuinely different experiments that teach different things.
3. **No overlap:** the strategic opportunity passes alone to the strategic path.

This carries forward the Phase 2b dedup logic (detect-contextual.md Step 3) in substance; the only change is framing, from "merge into one list" to "reconcile across two deliverables" by measurement altitude.

## Optional Soft Input

An optional soft field may strengthen detection when present: the business objective, the real alternative / status quo, or the dominant lever named by the client. It follows the same tri-state, penalty-free contract as the skill's other optional inputs (engagement-constraints, structural observation):

- **Present:** strengthens detection (sharpens lever families 1, 2, and 4 in particular).
- **Absent:** neither penalizes nor caps anything; the lever families still derive from the standard context files. Absence is the common case.
- It never flips the skill's mode and is never a mode-resolution requirement.

Mapping:

- **Legacy mode:** an optional field in `.claude/context/` (e.g., a stated business objective / real alternative / dominant lever note).
- **KB mode:** maps to the relevant silver artifact / objective field for the scope.

## Graceful Degradation

| Condition | Impact |
|-----------|--------|
| No qualifying business-level lever in context | Emit nothing. Behavior is byte-identical to pre-change output: no strategic hypotheses, no padding, no new sections. |
| A lever family's source context file is absent | That family degrades independently and emits nothing. Other families still evaluate. No penalty. |
| Optional soft field absent | Lever families derive from the standard context files. No penalty, no cap, no mode change. |

**Output to the strategic path:** Strategic opportunities do NOT join the tactical opportunity list. They flow to the strategic construction and scoring path: strategic-lane construction in `phases/construct.md` (Experiment Scope Rule unit allowance, Step 4c measurement design, Step 5b non-A/B feasibility branch), then strategic-lane scoring and tiering in `phases/score.md` (non-A/B feasibility judgment, separate strategic scoring/tiering, within-tier asset/ops clustering), then render into the separate strategic deliverable defined in `SKILL.md` > `Strategic Roadmap Output Format`. The tactical roadmap is built entirely from the Phase 2 / 2b opportunity list and is untouched by this phase. Detection ordering across phases stays 2 then 2b then 2c then 3.
