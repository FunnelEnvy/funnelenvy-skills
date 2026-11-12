# Phase 2: Strategic Lens Brief

The strategic lens reads the whole scope for business-level levers: programs, offers, audience motions and assets that move a business outcome and can be read by a design other than an on-page A/B. It walks every lever family below, then reads once more for any lever no family fits. It returns cards per the `Card Schema` in `phases/detect.md`, with `lens: strategic`, `altitude: strategic` and a `lever_family`.

`--focus` does not apply to this lens.

## Inputs

- Every input path the orchestrator passed: strategy context and `company-identity.md`, positioning scorecard, competitive landscape, audience-messaging, performance profile, structural observation, engagement constraints, supplementary silver, and the history projection.
- The stated business objective, the real alternative buyers weigh, and the dominant conversion driver the client names, when any source carries them. In KB mode, a scope engagement-context or engagement-constraints artifact is this input and must be read: it often records a lever's status.
- The archetype module's `## Strategic Lever Families` section, when the module has one.

A family whose sources are absent yields nothing. That is not a shortfall to pad.

## Lever Families

This list is the one home of the lever families. Walk every one. The strategic roadmap's `Levers Reviewed` section names each family in plain words with its row count, zero included.

| Token | Family | What to look for | Main sources |
|---|---|---|---|
| `objective-mismatch` | Objective mismatch | The stated objective differs from what the funnel optimizes (qualified pipeline wanted, raw form submits measured) | Objective, performance profile conversion definitions |
| `dominant-off-page-lever` | Stakeholder-named lever | A lever the client names as the main driver, living off the page | Objective, soft input, audience or competitive notes |
| `proof-gap` | Positioning or proof gap | A missing asset class that blocks the strongest messaging (named-client ROI proof where the category competes on it) | Scorecard, competitive claim gaps |
| `status-quo-alternative` | Status quo as the alternative | The main competitor is doing nothing or staying put, and nothing addresses the cost of inaction | Competitive landscape |
| `buying-group-motion` | Buying group | A multi-role decision while the funnel speaks to one role | Audience personas |
| `offer-architecture` | Offer architecture | The commitment levels of the offers themselves: one high-commitment offer and no lower step | L0 offers and CTAs, competitive landscape |
| `lifecycle-nurture` | Lifecycle and nurture | What happens between first conversion and sales readiness: nurture tracks, re-engagement, content sequences | Audience, performance profile returning-visitor data, history |
| `post-conversion` | Post-conversion | The experience right after a form or signup: confirmation, scheduling, onboarding, show rate | L0, structural capture, performance funnel data |
| `sales-handoff-routing` | Sales handoff and routing | How leads reach sales: routing rules, response time, qualification at handoff | Engagement context, strategy context, history |
| `partner-referral` | Partner and referral channel | Partner, referral, marketplace or reseller paths and how they are served | Performance profile sources, competitive landscape, L0 |

- **Precedence:** a lever the client names as the main driver uses `dominant-off-page-lever`, even when it is a routing or nurture lever.
- **Archetype families:** families from an archetype module load after the base list, with the module's token. Check them before the catch-all.
- **Catch-all:** after the families, read the full context once more for any business-level lever it affirmatively names that no family fits. Use `lever_family: other`. Match on a family's definition, not its name; a partial fit still goes to that family.

## Card Rules

- **Specific unit:** each card names a concrete lever, offer, motion or asset ("a named-client ROI one-pager", "same-day human follow-up for inbound demo requests"). "Improve messaging" is not a card.
- **Falsifiable mechanism:** the `mechanism` sentence states why the lever should move the business outcome, so a flat read would show it wrong.
- **Before state:** the evidence quotes or points at the current state. An invented before state is not evidence.
- **Design:** set `design` to the read the lever permits:
  - `ab` for an on-page randomized read;
  - `holdout` for a held-out group, region split or alternating on/off windows;
  - `pre-post` for before and after, cohort comparison or an operational metric tracked directly.
- **Same idea at two altitudes:** when the lever is the same idea as a page test, reuse that pattern's `Key` as `mechanism_key`. The script folds a tactical card into a strategic one with the same key and design, and pairs them with a sequencing note when the designs differ.
- **Baseline:** add one only when a sizing figure exists for the read the lever needs.
- **Channel-scale programs:** SEO, AI-search, organic content and paid-media strategy have no unit this skill can specify. When demand evidence is real, emit a card with the blocker `client-decision` and the annotation "channel decision: needs channel analysis".

## Gap Status

Before minting, read the lever's current status in every loaded source. Status, not just shape: "live", "in production" or "already reporting" means live.

| Status | Effect |
|---|---|
| **Documented live:** a source says the capability operates | Hard rule: no build card. List it under `Exclusions:` as an existing capability. A usage or adoption test of the live capability may be its own card |
| **Built but disabled:** implemented, but off, unentitled or scoped to some accounts | An enablement or adoption card for the existing capability, never a build |
| **In flight:** decided and in design or build, not yet live | A card that reads the rollout once it ships, `design: pre-post`, annotated "in flight: the read starts at launch" |
| **Documented absent:** a source says it does not exist, or a full inventory of that surface omits it | A build card |
| **Silent:** no source bears on it, because it lives in a client system the context does not cover (CRM, sales operations, marketing automation, warehouse) or rests on a `not_checked` structural field | A confirm-first card: blocker `verify-current-state`, annotation "confirm first: check whether [capability] already exists in [system]; if it does, this becomes a connection task" |
| **Blocked:** awaiting an explicit client decision | A card with the blocker `client-decision`, naming the decision |

## Measurement Foundation

Defining and instrumenting a measurement (a qualified-lead event, a down-funnel conversion) is a prerequisite, not an experiment. Do not emit it as a card. List each under `Measurement Foundation:` after the card array, one line each:

- what gets defined or instrumented;
- the system where the work happens;
- whether step one confirms an existing capability (silent status) or builds one;
- the titles of the cards that depend on it.

Apply the gap-status table to the entry itself: a documented-live measurement is no entry.

An objective-mismatch finding often yields only a Foundation entry. Emit a card as well only when the context names an intervention to read against the new measure (a routing change, an offer, an asset); that card carries the blocker `metric-not-tracked` until the entry lands.

## Return

Follow `Return Format` in `phases/detect.md`. Aim for the floor across all families together. A family with no supported lever yields no card.
