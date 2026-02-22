# Phase: Opportunity Detection

## Required Inputs

- Full body of `company-identity.md` (L0)
- Full body of all available L1 context files
- `modules/experiment-patterns.md` (loaded by orchestrator)
- Any `modules/evidence-*.md` files (optional, loaded by orchestrator if present)

## Depth Behavior

This phase does not vary by depth. All available context is scanned regardless of how it was produced.

## Graceful Degradation

| Missing Context | Impact |
|----------------|--------|
| positioning-scorecard.md | Skip scorecard-triggered patterns. Use gap inference from L0 + other L1 instead. |
| competitive-landscape.md | Skip competitive-pressure patterns (pricing transparency, differentiator crowding). |
| audience-messaging.md | Skip persona-dependent patterns (segment hero, industry proof, nav intent mismatch). |
| All L1 files | Detect from L0 only. Limited to patterns triggered by website copy, proof points, and structural signals. |

---

## Detection Process

### Step 1: Extract Testable Signals

Scan each context file for specific, concrete signals that indicate a testable opportunity. A signal is NOT a vague observation ("messaging could be better"). A signal is a specific, observable condition ("homepage headline uses category language 'Revenue Intelligence Platform' instead of outcome language").

**Signal sources by context file:**

**From company-identity.md (L0):**
- Homepage headline and subhead copy (exact text)
- Stated differentiators vs. proof points supporting them
- Target segments and personas listed
- Pricing model presence or absence
- Proof point registry: count, strength distribution, which pages they appear on
- Website structure: which pages exist, what's missing
- Form fields observed during research
- CTA language observed

**From positioning-scorecard.md (L1):**
- Dimensions rated "Needs Work" or "Missing" (direct triggers)
- Gap analysis narrative (specific observations about what's weak and why)
- Top gap and top opportunity fields from frontmatter

**From competitive-landscape.md (L1):**
- Claim overlap map: which differentiators are crowded vs. unique
- White spaces: positioning territories no competitor has claimed
- Competitor pricing transparency vs. target company
- Competitor proof strength vs. target company

**From audience-messaging.md (L1):**
- Persona definitions: how many, how distinct
- Channel adaptations: recommended messaging per page/touchpoint
- Voice profile: current tone vs. recommended tone
- Banned terms list: language currently used that should be avoided
- Message hierarchy: primary, secondary, tertiary messages and where they should appear

### Step 2: Match Signals Against Patterns

For each signal extracted in Step 1, check against the trigger conditions ("Applies when") in `modules/experiment-patterns.md`.

**Matching rules:**
- A signal can trigger multiple patterns. This is expected and correct.
- A pattern can be triggered by signals from multiple context files. Use the strongest signal.
- If a pattern's trigger condition partially matches (e.g., "form has 5+ fields" and you found a form but can't confirm field count), create the opportunity but flag it as "trigger partially confirmed."
- If `--focus` flag was set, only evaluate patterns in the specified categories.

### Step 3: Evidence Augmentation

If any `modules/evidence-*.md` files were loaded, apply their contents now:

- Additional trigger conditions from evidence modules are checked against context signals
- Scoring calibration data is attached to matching opportunities (passed to Phase 4)
- Evidence modules may introduce patterns not in the base library. Process identically.

If no evidence modules exist, skip this step entirely. The skill functions normally without them.

### Step 4: Build Opportunity List

For each pattern match, produce an opportunity record:

```
Opportunity:
  pattern: [pattern ID and name]
  category: [headline | form | navigation | personalization | layout | pricing]
  trigger_signal: [the specific signal from context that matched]
  signal_source: [which context file and section]
  trigger_strength: [full | partial]
  ice_baseline: [I/C/E from pattern definition]
  calibration_data: [from evidence modules, if any]
  notes: [anything relevant to downstream phases]
```

These records are internal only. Never written to disk, never appear in deliverables.

### Step 5: Preliminary Filtering

Remove opportunities where:
- Trigger is "partial" AND no other signal supports the same pattern
- Pattern category was excluded by `--focus` flag
- Same page + mechanism combination appears twice (keep stronger trigger)

Do NOT filter based on ICE scores. That happens in Phase 4.

**Output to Phase 3:** Complete opportunity list, typically 15-25 items. If fewer than 8, note this for the orchestrator's completion summary.
