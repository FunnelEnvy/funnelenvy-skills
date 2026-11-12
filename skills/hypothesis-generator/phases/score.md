# Phase 4: Scoring, Ranking and the History Ledger

This phase scores every row, runs `rank`, closes the history ledger and accounts for dropped prior write-ups. ICE orders rows within a readiness tier. There are no thresholds, quotas or caps: a low score sorts a row down its tier, never out of the roadmap.

## Step 1: Score Every Row

Read `modules/ice-scoring.md` first. Give each row `ice: {i, c, e}`, integers 1 to 5, after the checks in `phases/validate.md`.

1. **Start:** a row whose `mechanism_key` is a pattern `Key` in `modules/experiment-patterns.md` or the archetype module, alone or with an element suffix, starts at that pattern's baseline. Any other row starts at 3/3/3.
2. **Pattern modifiers:** apply each one whose condition the context confirms.
3. **Context adjustments:**
   - *Confidence:* exact current copy versus an inferred current state; copy from audience-messaging versus adapted from L0; a direct versus proxy primary (see `Guarded proxy` in the `Decision Posture`); page traffic and conversion data present; a failure mode that matches or contradicts the mechanism; the row's `validation_gates`, read as evidence.
   - *Impact:* homepage; the scorecard's top gap; page traffic, bounce and conversion against the site; a large pre-sized opportunity; a worsening trend on the target metric; a page no context file mentions.
   - *Ease:* copy-only; structural change; personalization infrastructure; third-party embedded elements.
4. **History rows:** read the row's `history:` annotation.

   | Type | Parent result | Confidence | Ease |
   |---|---|---|---|
   | Rollout | Winning | +1, validated mechanism | +1, proven variant |
   | Discriminating test | Any | +1, designed to read cleanly | 0 |
   | Follow-up, confirm and extend | Directional win | +1 | 0 |
   | Follow-up | Winning, re-applying the mechanism | 0 to +1 | 0 |
   | Iteration, follow-up or new hypothesis | Any other | 0 | 0 |

   A rollout whose parent did not win scores as a follow-up. A directional loss reads as a loss.
5. **Clamp** each score to 1-5.

**Figures:**
- A refused window under `Measurement-Regime Boundary` feeds no modifier: skip every adjustment that reads a figure or classification from it. A trend adjustment also needs both windows to count.
- Documented bot or monitoring traffic: score on the corrected figure.
- Under a non-A/B testing method, low page traffic does not lower Impact; reach still raises it.

**Strategic rows:** score with the strategic guidance in `modules/ice-scoring.md`. A confirm-first row and a `lever_family: other` row each carry extra uncertainty in Confidence.

## Step 2: Rank

Write the scored rows to a temp file and run `rank` as `Phase 4: Check, Score and Rank` in `SKILL.md` shows:

```
$PY <skill-dir>/scripts/consolidate_backlog.py rank --rows <scored rows> --write-ups <N> \
    [--history-items <ids>] [--excluded-history <ids>]
```

- `--history-items`: every lead or high ledger id, plus each typed item with an unrecognized priority that the history lens minted. On the producer index path these are the `I` ids the orchestrator numbered in Phase 1. The script reports every listed id that no row carries and no exclusion covers as unaccounted.
- `--excluded-history`: the ids a lens listed under `Exclusions:`, each with its grounds, standing engagement exclusions included.

The output gives each row `readiness`, `rank` and `write_up`, plus `history_ledger` and `history_unaccounted`.

## Step 3: Close the History Ledger

Skip when no history source is bound.

1. **Hard rule:** the roadmap is not written while `history_unaccounted` is non-empty. For each unaccounted id, mint the missing card and re-run from consolidation, or add it to `--excluded-history` with grounds and re-run `rank`. Never drop an id silently.
2. Give each lead or high id one status from `history_ledger`, first match wins:

   | Status | When |
   |---|---|
   | `not_advanced` | The ledger says `excluded`; its grounds go to `## Exclusions` |
   | `strategic` | The carrying row is strategic |
   | `folded` | The carrying row has a live-program annotation |
   | `adopted` | The carrying row's title came from the history card |
   | `merged` | Any other carrying row |

3. Medium and low items close as considered, unless a row carries them (then `adopted` or `merged`).
4. Feed the render:
   - `### Experiment Program Continuity` names, for each lead or high item, the write-up number or backlog key that carries it, or its `Exclusions` entry.
   - The completion message's history line counts each status, with 0 unaccounted.
5. **Partial coverage:** when the projection reported COVERAGE PARTIAL or a WARNING, or the bounded-read fallback ran, the ledger covers only what was read. The completion message says "coverage partial" and names what was not read.

## Step 4: Account for Dropped Prior Write-Ups

Skip when no prior roadmap was passed to `consolidate`.

1. A key in `dropped_prior_keys` is a dropped prior write-up when its prior roadmap carries it on a `**Key:**` line. A dropped prior backlog row needs no entry: the backlog is regenerated from current context each run, and the completion message lists the key.
2. Give each dropped prior write-up one outcome:
   - *Restored:* add a card with the prior title, so the title pass carries its key, and re-run from consolidation.
   - *Excluded:* one `## Exclusions` line in its own altitude's roadmap, naming the prior item by title, with its grounds: merged into a named row, superseded by a named row, or no longer supported and why.
3. **Hard rule:** no roadmap is written while any dropped prior write-up has neither outcome. Never drop one silently.
4. A prior strategic roadmap the run leaves untouched (`Re-render Behavior` > `No strategic rows` in `SKILL.md`) loses nothing, so its write-ups need no outcome.
5. The completion message counts each outcome, with 0 unaccounted.

## Step 5: Sequencing

Write the `### Sequencing` method section. It explains order; it never changes `rank`.

1. **Engagement constraints:** release timing, the concurrency limit and approval limits from the rows' annotations come first. State the reasoning, not the raw constraint.
2. **Dependencies:**
   - *Interactions:* multiplicative pairs from `modules/hypothesis-interactions.md`.
   - *Stand-ups:* a strategic row's prerequisites, and Measurement Foundation entries before the rows that need them.
   - *Live program:* one test per surface at a time, naming the running experiment.
   - *Shared mechanism:* a page test and a strategic read that share a mechanism keep their read windows apart.
3. **Barrier order on one page:** relevance, then clarity, then anxiety, then distraction, then urgency. A test on an earlier barrier runs before a later one on the same page.
4. **Tiebreaks:** continuations of winning tests first, then pages closer to conversion (checkout, pricing, demo, product, homepage, category, content).
5. **Low-traffic pages:** when three or more rows share a page under 500 sessions/mo, only one runs at a time; name the order.
