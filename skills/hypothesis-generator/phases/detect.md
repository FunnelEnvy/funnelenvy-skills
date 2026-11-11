# Phase 2: Lens Briefs

This file holds the card schema every lens writes to, and the briefs for four of the five lenses: surface, persona and journey, history, and competitive and proof. The strategic lens brief is in `phases/detect-strategic.md`. Each lens subagent receives its own brief, the `Card Schema` section below, and the resolved input paths. It reads the files itself.

## Card Schema

A card is one candidate opportunity: a surface, a lever, a mechanism and an evidence pointer. Each lens returns a JSON array of cards. The consolidation script (`scripts/consolidate_backlog.py`) validates every card and stops on the first invalid one, naming its index and field.

### Fields

| Field | Type | Required | Rule |
|---|---|---|---|
| `lens` | string | yes | Your lens: `surface`, `persona-journey`, `history`, `strategic` or `competitive-proof` |
| `altitude` | string | yes | `tactical` (a page element) or `strategic` (a program, offer, motion or asset) |
| `title` | string | yes | Short plain-words name of the test |
| `surfaces` | array of strings | yes | At least one. Tactical: a page path such as `/pricing`. Strategic: the named program, offer, motion or asset |
| `mechanism_key` | string | yes | Kebab-case slug, such as `form-field-reduction`. Use the pattern's `Key` when a pattern applies; coin one otherwise. See `Shared Rules` for when a key takes an element suffix |
| `mechanism` | string | yes | One plain sentence: why the change should move behavior |
| `evidence` | array of strings | yes | At least one non-empty pointer: source file and section, in plain words, with the observed fact |
| `lever_family` | string | strategic only | A kebab-case token from the family list in `phases/detect-strategic.md`, or `other` |
| `design` | string | no | `ab` (default), `holdout` or `pre-post` |
| `arms` | integer | no | Default 2; at least 2. Control plus variants |
| `baseline` | object | no | See `Baseline` below |
| `blockers` | array of strings | no | Only these values: `metric-not-tracked`, `no-baseline`, `verify-current-state`, `design-change`, `client-decision` |
| `annotations` | array of strings | no | Plain-words notes the reader needs: partial match, counter-evidence, a running experiment, an engagement constraint |
| `pattern` | boolean | no | `true` when the card came from a prompt-library pattern |
| `history_items` | array of strings | no | Ledger ids such as `I3` or `P2` (history lens) |
| `spec_items` | array of strings | no | Spec checklist ids this card answers |

The script ignores any other field. A `history_items` or `spec_items` id must be copied exactly as given.

### Baseline

Add `baseline` only when a real figure exists. Never invent one.

**Baseline table:** the orchestrator resolves one baseline per surface in Phase 1 and passes the table to every lens. Copy a listed surface's baseline verbatim. Resolve one with the rules below only for a surface the table lacks.

| Key | Content |
|---|---|
| `monthly_sessions` | Traffic for the target surface, per 30 days. Take, first match wins: (1) the delivered sample a history record reports for this surface, converted to 30 days, when its window counts under the measurement boundary; (2) the page's sessions in the performance profile, normalized to 30 days. For a pre-registered segment, use the segment's traffic, not the page's |
| `rate` | The primary metric's conversion rate, 0 to 1. For a proxy primary, the proxy's rate |
| `window_start` | `YYYY-MM-DD`: first day of the window the figures came from. Required whenever a measurement boundary governs: the script refuses a null start then. Use null only when the source states no dates |
| `source` | Plain words: which file and table the figures came from |

The script sizes every card from this object and the `Decision Posture` in `SKILL.md`. Do not compute samples, weeks or effects yourself.

### Shared Rules

- **Inputs:** read every input path you were given. In KB mode that includes every silver in the scope, supplementary silver included, and any cross-scope artifact reached through a declared `depends_on` edge. Read no other scope.
- **Floor:** aim for at least the floor you were given (default 10 cards). It is a target. If the evidence supports fewer, return fewer. Never pad, split one idea into several cards, or repeat a card.
- **One floor on candidacy:** every card carries an evidence pointer. Nothing else keeps a card out. Do not drop a card for low traffic, a missing metric, a running experiment, contrary advice or a partial fit. Record those facts as `blockers` or `annotations`.
- **One idea per card:** elements that serve one testable idea belong on one card (a headline, subhead and CTA rewritten together). Two independent ideas are two cards. The cross-surface bundling rule in `modules/hypothesis-interactions.md` decides multi-surface cases.
- **Merging is automatic:** cards with the same `altitude`, the same `mechanism_key` and an overlapping surface merge in the script, and only one title survives. Reuse a pattern `Key` exactly only for the same change on that surface, so your card merges with other lenses' cards. A different element or claim under the same pattern gets `<pattern-key>-<element>`, such as `proof-placement-pricing-table`. Use a distinct key too when the test design differs.
- **Hard rule, identical forms:** do not emit a form-swap test between two forms with the same fields and structure. Report the discard (see `Return Format`).
- **Plain words:** titles, mechanisms, evidence and annotations are written for a client reader. No file names inside annotations, no pattern IDs, no field names.

### Prompt Library

The surface, persona-and-journey and competitive-and-proof lenses read `modules/experiment-patterns.md` and any archetype module they were given. Follow that module's `How Lenses Use This Library`:

- A full match is a card with `pattern: true` and the pattern's `Key`.
- A partial match is a card with the annotation `partial match: <missing condition>`.
- Check archetype patterns before base patterns. When both fit the same page and mechanism, use the archetype `Key`.
- With `--focus`, work only the named categories.

### Contrarian Check

Before returning, check each tactical card against `modules/contrarian-triggers.md` and apply its action: reframe the test, or add the counter-evidence or verify-first annotation. Then run its `Context Grounding Check`. A trigger never removes a card.

### Engagement Constraints

When an engagement-constraints input is present, read it for what it implies for each card. Carry the implication, never the raw entry:

- **Release calendar:** a committed release that touches the card's surface during the read: annotate "read out fully before the [month] release, or start after it". A planned `measurement_regime_boundaries` entry dated after the run date reads the same way for every surface.
- **Approval bandwidth:** annotate the concurrency limit the input implies, for example "two or three concurrent tests at most".
- **Internal testers or delivery risk:** annotate the launch check, for example a tester exclusion or a blocked delivery domain.
- **Blocking constraint:** when the input says the client has not approved work on this surface or lever, add the blocker `client-decision` and say what is needed.

### Testing Method

Every tactical lens sets `design` from the engagement's testing method. Resolve it the same way in every lens, first match wins:

1. The engagement-constraints input states `testing_method`. Values other than `ab`, `pre_post`, `cohort` or `operational` fall to `ab`.
2. The experiment-history projection: classify each in-scope record's design as A/B or not. Leave out records with no control group and unrecognized values. More than half non-A/B means a non-A/B method.
3. Otherwise `ab`.

Under a non-A/B method, give every tactical card `design: pre-post`. Under `ab`, leave `design` unset.

### Return Format

Return one JSON array of cards. Two kinds of item are not cards; list them after the array, under these headings, only when any exist:

- `Exclusions:` one line each, `<item>: <grounds>`, for a hard-rule discard (a form swap between identical forms, a lever documented as already live) or a history item outside the requested focus.
- `Measurement Foundation:` strategic lens only; see `phases/detect-strategic.md`.

When you return fewer cards than the floor, end with one line: `Shortfall: <n> of <floor>; <why the evidence supports no more>`.

---

## Surface Lens

**Job:** walk the site surface by surface and find what is testable on each page.

**Inputs:** the performance profile, the structural observation (live structure) or live capture, `company-identity.md`, the positioning scorecard, and the prompt library.

**Work:**

1. List the surfaces: every page the profile reports with traffic, every captured page, and every page L0 names. Include the homepage and the top conversion page.
2. For each surface, read its copy, proof, forms, CTAs, navigation and layout against the prompt library.
3. Run the performance triggers and structural triggers below.
4. Emit a card per testable idea, with a `baseline` when the profile or a history record gives one.

### Performance Triggers

Fire only when the performance profile is present. "Sessions/mo" means sessions in the profile's range, normalized to 30 days.

| Condition | Card |
|---|---|
| Page over 500 paid sessions/mo and bounce over 45% | Paid landing message mismatch |
| Page CVR under half the site average and over 200 sessions/mo | Conversion friction on a high-traffic page |
| Site-level mobile bounce over 10pp above desktop, or mobile CVR under half of desktop, with mobile at least 20% of sessions | Mobile friction, targeted at the top mobile entry pages; state the gap as site-level |
| Landing page bounce over 55% and a top-5 entry point | First-impression failure |
| Top conversion page with no other card targeting it | Untested high-value page |
| One channel bounces at twice another on the same page, or the profile lists a bounce mismatch by source | Channel-specific message mismatch |
| A form event fires but page conversion is under 5% | Form friction |
| Returning-to-new conversion ratio marks the site familiarity-dependent | First-visit failure or nurture gap |
| Primary CVR trend down over 0.5pp, or bounce trend up over 5pp | Worsening metric; find what changed |
| Page failure mode is shallow engagement | Messaging mismatch, not layout |
| Page failure mode is deep engagement | Funnel friction: CTA, pricing or trust |
| A page group converts under a quarter of the top group | Structural content-to-conversion gap |
| A pre-sized opportunity marked large | That opportunity |
| Over 200 paid sessions/mo to a page with no paid variant | Paid landing page (NX-04) |
| Element data on a page over 500 sessions/mo shows primary CTA clicks under 3% | CTA visibility or clarity (EE-01) |
| One element gets over 5 times the clicks of the next on the same page | CTA hierarchy dominance |
| Sequential items where later ones get under 20% of the first | Hidden content (EE-02) |
| A large non-search, non-self-referral source of unverified intent | Segmentation card, or a `client-decision` blocker asking whether it belongs in the denominator |
| A sister-property referral with an elevated quick-back rate | Cross-property handoff pathing |

**Rules:**
- Device data is site-level in every producer. Never condition a card on a per-page device split.
- Bot or synthetic-monitoring traffic documented on a surface: correct the sessions figure before using it, and annotate "traffic excludes an estimated [share] of automated monitoring".
- Under a governing measurement boundary, the trend triggers fire only when both profile windows count. Other triggers may fire on a refused window, but give the card its true `window_start`, so the script refuses to size it.
- When the source's intent is unknown, prefer a question for the client over a card about an unknown population.

### Profile Schema Equivalence

The trigger conditions use ga4-audit field names. The skill accepts a stamped `schema_version` from `"2.0"` to `"2.3"`, or no stamp. ga4-audit stamps `"2.3"` and aa-audit `"2.1"`; profiles are interchangeable at a stamp for every field the stamp guarantees.

- With a stamp, the version gates which triggers are eligible. A trigger still fires only when its data is present.
- Without a stamp, a trigger fires when the profile carries equivalent content:

| Field condition | Equivalent content |
|---|---|
| Pre-sized opportunities with impact | A sized opportunity table with impact buckets |
| CVR and bounce trend deltas | Period-over-period trend tables |
| Page sessions and bounce conditions | A page-level traffic and bounce table |
| Data gaps | Documented data-gap or measurement notes |
| Site-level device gap | A site-level device breakdown |

- Data with no equivalent (element interactions, page groups, failure modes, new versus returning) leaves its triggers silent. Judge equivalence per trigger, not per profile.

### Structural Triggers

Fire only when the structural observation is present. Fields are tri-state (`present`, `absent`, `not_checked`); a missing field is `not_checked`, which neither fires nor suppresses.

| Condition | Patterns |
|---|---|
| Form with 5 or more fields or many required fields | FO-01, FO-02 |
| Form with no proof or reassurance near it | FO-03; FO-04 partial unless labels were captured |
| High CTA count, or a generic or high-commitment primary label | NX-02, EE-03 |
| Login present but below the fold or low in navigation | NX-07 (partial without return-rate data) |
| Sequential UI with several items | EE-02 targeting; firing needs element drop-off data |
| Named-client proof absent or low proof count on an evaluation page | HM-02, SP-01, SP-02, SP-03 |
| Team credibility absent where expertise is claimed | TC-01 |
| Objection content absent on a decision page | TC-02 |
| Chat widget or overlay over the primary CTA | NX-06 |
| Navigation not persona-segmented while 2 or more personas are defined | NX-01, PS-03 |
| Comparison, ROI tool or pricing page absent | CR-01, CR-02 or CR-03, PZ-01: confirms the structural condition only; the competitive or positioning condition still decides |
| Service-page copy skeleton reads generically against claimed differentiators | PS-04 |

**Rules:**
- Structure supplies targets and current state. Performance data supplies firing counts for engagement patterns. Do not fire the same pattern twice on one page from both.
- A page block status other than clean, a low page confidence or a viewport divergence makes signals from that page a partial match.
- **Broken mobile render:** this rule is its one home. When `mobile_render_clean: false` on a page, the surface lens sets the blocker `design-change` on each of its cards for that page and annotates the defect: fix it and re-measure before reading any device-targeted test (the counter-evidence is CTR-14 in `modules/contrarian-triggers.md`).
- Personalization needs cross-session data and exit paths need behavioral data; a single capture cannot fire them.

---

## Persona and Journey Lens

**Job:** follow each persona from arrival to conversion and find where the journey breaks.

**Inputs:** audience-messaging, brand voice when present, `company-identity.md`, the competitive landscape (alternatives buyers weigh), the performance profile's channel, source and new-versus-returning data, and the prompt library.

**Work:**

1. For each persona: how it arrives (channel, source, entry page), what it must learn to act, where it converts, and what it is told along the way.
2. Look for breaks:
   - *Arrival:* ad or channel promise against the landing page.
   - *Relevance:* a page that speaks to a different persona or awareness stage.
   - *Path:* navigation that makes the persona filter features.
   - *Ask:* a CTA or offer too large for the stage.
   - *Committee:* a buying group the funnel addresses as one person.
   - *Return:* returning visitors treated as new.
3. Match against the prompt library, especially the Personalization and Navigation categories, NX-04, NX-07, EE-03 and HM-01.
4. A concrete signal no pattern fits is still a card (`pattern: false`). Name the signal type in the evidence: something expected is missing, two sources contradict, an asset is unused, or the site structure works against the persona.

Persona cards are usually tactical. A card about the buying motion itself, not a page, belongs to the strategic lens; leave it.

---

## History Lens

**Job:** turn the experiment history into continuations. Every lead, high and medium follow-up in scope becomes a card.

**Inputs:** the history projection path (or the orchestrator's numbered item list), the full-entry budget left, the insight records it lists, and (when bound) the producer index and its insight records.

**Work:**

1. Read the projection, then the sections and full entries it points to, inside the entry budget.
2. Take each in-scope follow-up: typed items keep their ids (`I1`, `I2` and so on) and their stated priority. On the producer index path, use the ids the orchestrator numbered in index order. A prose next test gets the next `P` id and a priority from this rubric:
   - A gold insight guide's designated lead experiment with no typed item: `recommended_lead`.
   - The next step a record names as its primary follow-up, or the first next test its final learning names: `high`.
   - Secondary or exploratory next tests: `medium`.
3. Mint one card for each lead, high or medium item, with its id in `history_items`. Low items mint nothing; they count as considered. A typed item with an unrecognized priority mints when it reads as a lead or primary follow-up.
4. Mint regardless of the parent outcome (winner, loser, directional or flat) and of the item's type.
5. Add the annotation `history: <type> after a <outcome> result`, where type is rollout, iteration, follow-up, discriminating test or new hypothesis, and outcome is winning, losing, directional win, directional loss or flat. Scoring reads it.
6. When a record states its delivered sample or its own detectable-effect floor for the surface, carry it into `baseline` and the evidence.

**Surfaces:**
- A page path maps as written; a locale or path variant maps to its page.
- An audience, segment or element instead of a page maps to the parent record's page, or sitewide when that is absent.
- An off-site channel (email, paid ads, in-app) still mints. Name the channel as the surface and annotate "off-site channel". A lifecycle or nurture follow-up is strategic, with `lever_family: lifecycle-nurture`.

**Same mechanism or a new test:** same surface plus same change is one test: reuse the parent's `mechanism_key` so the script merges it. Same surface plus a different design is a separate card with its own key: an isolation arm, an intent split, a dosage variant, a re-run with down-funnel tracking, or a rollout to a new surface.

**Focus:** with `--focus`, an item outside the named categories mints nothing. List it under `Exclusions:` with the grounds "outside the requested focus".

---

## Competitive and Proof Lens

**Job:** find where the company's claims, proof and objection handling fall short of what buyers compare.

**Inputs:** the competitive landscape, the L0 proof registry, the positioning scorecard, audience-messaging objections, and the prompt library.

**Work:**

1. Map claim overlap: which differentiators are crowded and which are white space.
2. Compare proof: competitor proof strength, verified registry proof missing from the pages where the claim is made, and proof of different strengths mixed together.
3. List structural objections and loss reasons with no rebuttal on the site.
4. Compare pricing transparency and evaluation aids (comparison pages, ROI evidence, diagnostics).
5. Match against the Social Proof, Content/Resource, Trust/Credibility and Pricing categories, plus HM-02, PS-03 and PS-04.

**Proof integrity:** a card whose test would show a number must point at a registry entry that carries it, at the same scope. A number that is only on the live page, or claimed strength only, gets the annotation "proof not registered: confirm before it ships". A card that names competitors gets "comparative claim: legal review before launch".

A missing proof asset or business-case motion that needs a program, not a page change, belongs to the strategic lens.
