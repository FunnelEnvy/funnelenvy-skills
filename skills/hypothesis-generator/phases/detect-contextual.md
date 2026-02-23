# Phase 2b: Context-Derived Opportunity Detection

## Purpose

Evaluate unmatched signals from Phase 2 for novel testable experiments not covered by any pattern. The pattern library is a floor, not a ceiling. Signals that don't match a predefined pattern may still represent strong experiment opportunities when they point to specific, testable conditions.

## Required Inputs

- Unmatched signal list from Phase 2, Step 6
- Full body of all loaded context files (carried forward from Phase 1)

## Quality Gate

Every context-derived opportunity MUST pass ALL six criteria. If any criterion fails, the signal is discarded. No exceptions.

1. **Specific observable signal.** The opportunity points to a concrete condition in a named context file section. "Messaging could be stronger" fails. "Homepage subhead uses feature language while audience-messaging recommends outcome-first framing for the CTO persona" passes.

2. **Named page and element.** The experiment targets a specific page and a specific element on that page. "A landing page" fails. "Pricing page, tier comparison table" passes.

3. **Falsifiable causal mechanism.** The hypothesis includes a behavioral or UX principle that explains why the change should work. The mechanism must be falsifiable: you can imagine a negative result that disproves it. "This will improve conversions" fails. "Reframing the tier names around outcomes instead of feature counts reduces decision complexity for multi-stakeholder buyers evaluating pricing" passes.

4. **Before state documented.** The current state is either directly quoted from context or clearly inferable from a specific context file section. Invented or assumed "before" states fail.

5. **Genuine uncertainty.** The outcome of the experiment is not predetermined. If the change is so obviously correct that no reasonable person would argue against it, it's a "just do it" fix, not a hypothesis. Flag it in "What's Not Here" instead.

6. **Not a pattern gap.** The signal shouldn't match a pattern that was skipped because of missing data. That's a data gap, handled by Prerequisites (Phase 3, Change 3). Check: could this signal have triggered a pattern if more data were available? If yes, route to Prerequisites instead.

---

## Process

### Step 1: Signal Triage

Review each unmatched signal from Phase 2, Step 6. For each signal:

1. Evaluate against all six quality gate criteria
2. If any criterion fails, discard with a brief note on which criterion failed
3. If all criteria pass, advance to Step 2

Expected: most unmatched signals will fail the quality gate. This is by design. The gate prevents the phase from becoming a dumping ground for weak observations.

### Step 2: Opportunity Construction

For each signal that passes the quality gate, build an opportunity record:

```
Opportunity:
  pattern: context-derived
  type: "context-derived"
  category: [best-fit from existing categories, or "cross-cutting" if none fits]
  trigger_signal: [the specific signal from context]
  signal_source: [which context file and section]
  trigger_strength: full
  ice_baseline: 3/3/3
  confidence_penalty: -1
  notes: [quality gate evaluation summary, causal mechanism sketch]
```

Key differences from pattern-matched opportunities:
- `pattern` field is always "context-derived"
- `type` field is set to "context-derived" (used by scoring phase)
- `ice_baseline` starts at 3/3/3 (neutral midpoint) instead of a pattern baseline
- `confidence_penalty` of -1 is applied during scoring (no pattern precedent = lower structural certainty)

### Step 3: Dedup Against Phase 2

Before passing to Phase 3 (Hypothesis Construction):

1. For each context-derived opportunity, check if Phase 2 already produced an opportunity targeting the same page + mechanism combination
2. If overlap exists, merge the context-derived signal into the existing opportunity's notes (enriches the pattern-matched hypothesis rather than creating a duplicate)
3. If no overlap, pass as a new opportunity

**Output to Phase 3:** Context-derived opportunities are appended to the Phase 2 opportunity list. They flow through the same construction and scoring pipeline with the adjustments noted in `phases/construct.md` and `phases/score.md`.
