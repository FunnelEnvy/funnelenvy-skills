# Phase 5: Write-Ups

This phase writes the full write-up for every row with `write_up: true`. The label layout is `Output Format` (tactical) or `Strategic Roadmap Output Format` (strategic) in `SKILL.md`. This file says how to fill each label. Rows without a write-up render as backlog rows and need nothing here.

## Inputs

- The ranked row, with its sizing object, blockers, `blocker_reasons`, annotations and `validation_gates`.
- The loaded context the row's evidence points to.
- `modules/experiment-patterns.md` for the row's pattern, `modules/copy-craft.md` for any proposed copy, and `modules/hypothesis-interactions.md` for bundles.
- The history projection, for the deployed-state and displacement reads below.

## Ground Rules

- **Numbers:** every sized figure comes from the row's sizing object. Never recompute samples, weeks or effects, and never invent a point estimate.
- **Keep the row:** a write-up never removes, suppresses or demotes its row. Counter-evidence goes in `**Notes:**`.
- **Unit:** the unit of testing is the hypothesis, not the variable. Elements that serve one idea change together in one variant.
- **Grounded:** proposed changes trace to the pattern library or the messaging analysis. Concrete enough that a developer or copywriter needs no follow-up question.
- **Proportionate claims:** one prior result is a prior signal, not a pattern. A principle without experiment data is a principle, not proof.

## Before Writing

Check these for every tactical write-up:

- **Mobile bounce:** before blaming rendering, check mobile's channel mix. When one channel is over 60% of mobile traffic and bounces high on desktop too, the problem is that channel's message, not the device.
- **Path selection bias:** a dedicated page that converts better may just draw higher-intent visitors. State whether the mechanism is a better page or a more motivated visitor.
- **Completion versus conversion:** completion rate is submits over form starts; conversion rate is submits over page visitors. State both and which one the test targets.

## Tactical Labels

### Key, Page, Mechanism

- `**Key:**` the row key, on its own line.
- `**Page:**` the row's surfaces. When the structural capture shows a sitewide form or CTA and the test changes it, name the full instance set ("the global demo-request form, all instances").
- `**Mechanism:**` the row's `mechanism_key` with hyphens as spaces, and nothing else.

### What to Test, Change Type, Proposed Change

- `**What to test:**` the concrete change in one sentence.
- `**Change type:**` one or more of `insert`, `replace-copy`, `modify`, `remove`, `reorder`, primary first. List a second type only when the variant really performs it.
- `**Proposed change:**` what the variant looks like. For copy, add `> **Before:**` and `> **After:**` pairs. Write all proposed copy (headline, subhead, CTA label, CTA microcopy, form labels and errors) against `modules/copy-craft.md`.
- **Variations:** for headline, hero, positioning and value-proposition tests, give two or three variations instead. Each anchors to a different element of the positioning (a verified differentiator, the strongest verified number, the buyer outcome, the positioning statement, an exclusive asset), uses one proof point, and keeps headline, subhead and CTA consistent. Add a third only when a distinct angle exists. Close with `> **Recommended:**` and a one-sentence reason.
- **Protected elements:** terms that L0 or brand voice marks as legally, regulatorily or brand-required:
  - *Legal or regulatory:* no variation may change the term. If the test is about changing it, add the `client-decision` reason "legal review before testing".
  - *Brand:* when a variation removes the term, add one that keeps it, and note "client confirmation recommended before testing a variation that drops [term]".

### Current State and Baseline

- **Deployed state first:** when the history shows a shipped treatment live on the surface, that treatment is the control. Never describe a build a prior test replaced. When the capture still shows the old build, trust the history on what is live and the capture on how it renders, and note "verify the live page before launch". A treatment live only for named accounts limits the claim to them.
- **Copy:** quote exact copy from context. When it is not available, describe what is known. Never fabricate it.
- **Structure:** cite the structural capture when it covers the page (field counts, CTA labels, element presence). Otherwise say the state is inferred. Zero conversions on a page may mean no mechanism or an untracked one; say so rather than assert absence.
- `**Baseline:**` sessions/mo and conversion rate from the sizing object's echoed figures. Omit when the row is not sized.

### Why This Should Work

Write the causal chain in two or three sentences: the observation, the behavioral or UX principle, the predicted behavior change, and the metric it shows up in. Start from the pattern's mechanism and adapt it. The prediction must be falsifiable.

### Target Metric, Guardrail, Audience

- `**Target metric:**` the most direct behavioral measure of the idea. Never a vanity metric (raw page views, unqualified time on page).
- **Displacement surfaces:** when the history shows an on-page metric moving against a downstream business metric on this surface, or a page of the same type, the downstream metric is primary and the on-page one a leading indicator. When the downstream metric is not tracked there, keep the on-page metric as primary, make the downstream metric the guardrail with the guardrail-first decision rule, and note the instrumentation needed.
- `**Guardrail metric:**` required for a proxy primary (a click-through, a navigation rate). Name the business metric the proxy should predict, its non-inferiority margin from the `Decision Posture`, and the decision rule: additive (proxy wins and guardrail holds) or guardrail-first (guardrail wins whatever the proxy does). When the change may filter out wrong-fit traffic, say a proxy drop alone is not a loss.
- `**Audience:**` the persona or segment. Pre-register a segment as the primary read when the persuadable audience is a diluted minority: Direct over 75% of the surface's sessions, bounce over 60%, new visitors over 80% for a familiarity-dependent mechanism, or a mechanism that only affects a sub-audience. These figures do not apply on a refused window. A segment the platform cannot isolate carries the `design-change` reason from validation.

### Read Model and Read Threshold

- `**Read model:**` follow the `Output Format` line for the row's read model. A/B, directional and scripted pre/post lines carry the sample per arm, the weeks or window, the achievable effect, and the traffic and rate the sizing object echoes.
- `**Expected effect and read threshold:**`
  - *A/B and directional:* state the six parts `Output Format` lists. For a proxy read with no baseline rate, state them against an absolute threshold set before launch, or declare the first run baseline-setting.
  - *Pre/post and holdout by design:* state a pre-registered read criterion. Say the window is set before launch and name its basis: the sales cycle, or the volume needed to reach a stated count. The script sizes no window for these designs, so never print a week count.
  - *Scripted pre/post:* an A/B design the script moved to pre/post for low conversions carries a sizing object. Quote its conversions per arm over the full window as the reason a split test cannot read, then state the criterion as above.
  - *Directional result:* do not ship and do not extend; queue a fresh confirmation test of the same mechanism, sized on the posture effect.

### Evidence and Scores

- `**Evidence:**` the row's evidence pointers, in plain words: what was observed, where.
- `**Scores:**` from the row's `ice`, in the exact `Output Format` shape, then one sentence per score.

### Bundled Elements

Count the elements the variant changes: headline, subhead, CTA copy, CTA destination, hero visual, layout, proof elements, form. With more than one, add `**Bundled elements:**` with the list, what the test will teach and what it will not isolate.

- The element that carries the thesis must be the dominant change. If it is not, restructure or rename the test to the thesis the dominant change tests.
- A thesis element most visitors never see makes a flat result unreadable: pre-register the segment that sees it, move it into view, or note the limit.
- A bundle whose loss cannot name one failure mode is several tests. Say so in `**Notes:**` and recommend the sequence.

### Win, Loss, Notes, Readiness

- `**What a win proves:**` what a positive result validates about positioning, messaging or audience. For variations, what it means if the recommended one wins and if another does.
- `**What a loss teaches:**` what a negative result reveals and where to go next. For a bundle, say a loss does not isolate the element. For a proxy read, cover a proxy win with a flat guardrail.
- `**Notes:**` the row's annotations in plain words: a partial fit and what is missing, counter-evidence, a running experiment named in plain words, an engagement constraint, unregistered proof, a comparative claim. Name any roadmap section in plain words, never in a code span. Omit when none.
- `**Readiness:**` under every tier except `Ready Now`: one line from the row's `blocker_reasons`.

## Strategic Labels

- `**Key:**`, `**Mechanism:**`, `**Evidence:**`, `**Scores:**`, `**What a win proves:**`, `**What a loss teaches:**`, `**Notes:**` and `**Readiness:**` follow the tactical rules.
- `**Lever:**` the row's surfaces: the named program, offer, motion or asset.
- `**What to stand up:**` what gets built, published, routed or changed. Bundle the parts that serve one idea (the asset, where it lives and the copy that frames it); a second idea is a second row.
- `**Measurement:**` the design in plain words (a regional holdout, a before-and-after window, a cohort comparison, a tracked operational metric), and its limits: what it cannot isolate, such as seasonality, contamination or mix shift. When a randomized read is available now and a qualified-layer read only after a Foundation entry lands, describe the second read as a later enrichment.
- `**Read model:**` as the tactical line, from the sizing object.
- `**Business metric:**` the outcome and its direction, distinct from a page micro-conversion.
- `**Why this should work:**` the causal chain in two or three sentences.
- `**Requires:**` the prerequisites, or "none". A confirm-first row opens with the existence check, as `Strategic Roadmap Output Format` shows. A Foundation entry the row depends on is named here.
- `**Read condition and window:**` what counts as a read, and the basis that sets the window before launch, per `Read Model and Read Threshold`. When a disqualified baseline cannot be avoided, say the comparison window is directional only. When a page test shares the mechanism, one neutral line on keeping the windows apart.

## Inconclusive Guidance

For each write-up, give the `If Tests Are Inconclusive` method section one short block:

- **Check first:** the most informative segment split (paid versus organic, device, new versus returning, the source that tracks the persona).
- **Leading indicator:** the micro-conversion that should move even if the main metric does not, and what to test next if it moves alone.
- **If flat:** for a well-supported row, the bolder version of the same idea. For a weakly supported one, move on.
- **If directional:** a fresh confirmation test of the same mechanism, never a ship.
- **After a win on volatile traffic:** when over 30% of the page's traffic comes from one volatile source, a 30-day before-and-after check after launch.
