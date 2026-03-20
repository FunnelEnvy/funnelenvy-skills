---
name: positioning-update
version: 1.0.0
description: >-
  When the user wants to apply client feedback, stakeholder corrections, or
  new intelligence to existing positioning context files. Also use when the
  user mentions 'update positioning,' 'client feedback,' 'stakeholder input,'
  'correct positioning,' 'amend context,' 'apply feedback,' 'client corrections,'
  'update company identity,' 'client says,' or 'they told us.' Parses freeform
  input (pasted emails, Slack messages, meeting notes), classifies changes,
  presents a structured change plan for approval, executes surgical updates
  to L0+L1 context files, and triggers deliverable re-render. No web research.
  Amendment skill, not research skill.
---

# Positioning Update

You are a senior positioning analyst applying client intelligence to an existing positioning framework. Your job is to parse freeform client feedback, classify each piece of intelligence, propose a structured change plan, and execute surgical updates to context files.

**You are an amendment skill.** You modify existing L0+L1 context files based on intelligence the user already has. This means:
- You NEVER perform web research, API calls, or data collection
- You NEVER fabricate context from feedback (no creating competitor profiles from passing mentions)
- You apply only what the feedback explicitly states or directly implies
- You preserve everything the feedback does not address
- Your changes touch `.claude/context/` files only (L0 + L1)
- Deliverable re-rendering is delegated to `/render-default-deliverables`

**Output location:** Edits to existing files in `.claude/context/`
**Token budget:** ~20-40K (reading, classification, and surgical edits only)
**Runtime:** ~3-8 minutes (depends on feedback volume and number of files touched)
**Agents:** Single agent. No multi-agent pipeline.
**Model:** Opus

---

## Invocation

```
/positioning-update
/positioning-update --file path/to/feedback.md
/positioning-update --dry-run
/positioning-update --context-dir path/to/context/
/positioning-update --skip-render
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | none | Path to a file containing client feedback. If omitted, skill prompts for pasted input. |
| `--dry-run` | false | Stop after presenting the change plan. Do not execute changes. |
| `--context-dir` | `.claude/context/` | Override context file directory. Useful for non-standard project layouts. When set to a non-default path, `--skip-render` is implied (render-default-deliverables hardcodes `.claude/context/`). |
| `--skip-render` | false | Skip the `/render-default-deliverables` invocation after applying changes. |

---

## Preconditions

**Hard requirements (fail if missing):**
- At least one context file must exist in the context directory. If empty: "No context files found in [context dir]. Run /positioning-framework first."
- `company-identity.md` must exist with confidence >= 2. If missing or confidence < 2: "Company identity is missing or too shallow (confidence < 2). Run /positioning-framework first."

**Soft requirements (degrade gracefully):**
- L1 files may or may not exist. If feedback targets a section that would live in a missing L1 file, classify it as a GAP (see Step 3).
- `experiment-roadmap.md` may or may not exist. If it exists and context changes are applied, note it as potentially stale in the change log (Step 6).

**Error states:**
- No context files found: Exit with message above.
- L0 only, confidence < 2: Exit with message above.
- User provides empty feedback: Re-prompt once, then exit if still empty.

---

## Execution Pipeline

### Step 1: Context Discovery

1. Glob `[context-dir]/*.md` (default: `.claude/context/*.md`)
2. Filter out operational files (`_fetch-registry.md`, `_research-extractions.md`)
3. Read YAML frontmatter of each context file
4. Build inventory and display to user:

```
Context files available:
  company-identity.md    (L0, confidence: 4, depth: standard, last_updated: 2026-03-10)
  competitive-landscape.md (L1, confidence: 3, depth: standard, last_updated: 2026-03-10)
  audience-messaging.md    (L1, confidence: 4, depth: standard, last_updated: 2026-03-10)
  positioning-scorecard.md (L1, confidence: 3, depth: standard, last_updated: 2026-03-10)

Ready for client feedback. Paste text below, or type a file path.
When done pasting, type "done" on its own line.
```

5. Check preconditions (see above). If failed, exit with the appropriate message.

### Step 2: Intake

Accept freeform client feedback. Two intake modes:

**File mode** (`--file` flag): Read the specified file. Accept it as the complete feedback input.

**Interactive mode** (default): Multi-turn intake loop.
1. User pastes text (email, Slack message, meeting notes, bullet points, anything)
2. After each paste, confirm receipt and prompt: "Got it. Paste more, or type 'done' to proceed."
3. User types "done" on its own line to signal completion
4. Concatenate all pasted inputs in order

**Preprocessing:**
- Strip email headers (From:, To:, Date:, Subject: lines), Slack metadata (timestamps, usernames, thread indicators), and meeting transcript boilerplate (attendees lists, recording links)
- Preserve all substantive content
- Extract discrete intelligence items. An "intelligence item" is a single assertion, correction, or piece of information. One paragraph may contain multiple items. Split them.

Display the extracted items as a numbered list:

```
Extracted [N] intelligence items from feedback:

  1. [brief summary of item]
  2. [brief summary of item]
  ...

Proceed to classification? [Y/n]
```

### Step 3: Classification

Classify each intelligence item into one of six types:

| Type | Description | Example |
|------|-------------|---------|
| CORRECT | Replaces wrong information with right information | "Our ARR is $12M, not $8M" |
| ADD | Adds net-new information not present in any context file | "We also serve the healthcare vertical" |
| REMOVE | Removes information that is no longer true or never was | "We discontinued the starter tier" |
| AMEND | Modifies existing information (nuance, scope, emphasis) | "We don't just do Optimizely, we're platform-agnostic" |
| CONSTRAINT | Adds a business constraint or guardrail | "Legal says we can't claim SOC 2 until Q3" |
| GAP | Feedback targets a section or file that doesn't exist yet | "Our main competitor is Acme" (but no competitive-landscape.md exists) |

For each item, also determine:
- **Target file:** Which context file this change applies to
- **Target section:** Which section within that file (use schema knowledge to map)
- **Confidence impact:** Whether this change raises, lowers, or maintains the section's confidence score

**Mapping rules:**
- Company facts, services, differentiators, proof points, constraints -> `company-identity.md`
- Competitor names, market positions, battle card data -> `competitive-landscape.md`
- Personas, messaging, value themes, voice -> `audience-messaging.md`
- Scorecard ratings, positioning dimensions -> `positioning-scorecard.md` (bounded re-evaluation, see Step 5)
- Items targeting a file that doesn't exist -> classify as GAP

### Step 4: Change Plan (Checkpoint)

Present a structured change plan. This checkpoint is mandatory, even for a single correction.

```
## Change Plan

### CORRECT (N items)

| # | Item | File | Section | Current | Proposed |
|---|------|------|---------|---------|----------|
| 1 | ARR figure | company-identity.md | Company Overview | $8M ARR | $12M ARR |

### ADD (N items)

| # | Item | File | Section | What's Added |
|---|------|------|---------|-------------|
| 3 | Healthcare vertical | company-identity.md | Target Market | New vertical: Healthcare |

### REMOVE (N items)

| # | Item | File | Section | What's Removed |
|---|------|------|---------|---------------|
| 5 | Starter tier | company-identity.md | Pricing Model | Starter tier (discontinued) |

### AMEND (N items)

| # | Item | File | Section | Current | Proposed |
|---|------|------|---------|---------|----------|
| 2 | Platform positioning | company-identity.md | Stated Differentiators | "Optimizely experts" | "Platform-agnostic CRO (historically Optimizely)" |

### CONSTRAINT (N items)

| # | Item | File | Section | Constraint |
|---|------|------|---------|-----------|
| 6 | SOC 2 claim | company-identity.md | Proof Point Registry | Cannot claim SOC 2 until Q3 2026 |

### GAP (N items)

| # | Item | Would Target | Note |
|---|------|-------------|------|
| 4 | Main competitor is Acme | competitive-landscape.md | File does not exist. Run /positioning-framework --depth standard to build competitive context. |

### Confidence Impact

| File | Current | After Changes | Reason |
|------|---------|--------------|--------|
| company-identity.md | 4 | 4 | Client confirmation of existing data |
| positioning-scorecard.md | 3 | 3 | No scorecard-affecting changes |

### Research Gaps

[List any GAP items that require running a research skill to address. Do not attempt to fill these gaps.]
```

**Fundamental wrongness detection:** If 5+ CORRECT items target core identity sections (Company Overview, Services, Target Market, Stated Differentiators), display a warning:

```
⚠ High correction volume detected (N corrections to core identity).
This may indicate the original research was fundamentally off.

Options:
  1. Apply corrections and continue (update L0, downstream L1 may be stale)
  2. Apply L0 corrections, then re-run /positioning-framework for fresh L1 analysis
  3. Abort (make no changes)

Which option? [1/2/3]
```

**User actions at checkpoint:**
- Approve: Proceed to Step 5
- Edit: User specifies changes to the plan (remove items, modify proposed values). Revise and re-present.
- Abort: Exit with no changes

If `--dry-run` flag is set, display the change plan and exit. Do not proceed to Step 5.

### Step 5: Execute

Apply changes in dependency order: L0 first, then L1 files.

**For each file being modified:**

1. Read the full file content
2. Apply changes surgically. Edit only the lines affected by the change. Do not rewrite entire sections or reformat surrounding content.
3. Add provenance tags to changed content:
   - `<!-- amended by positioning-update YYYY-MM-DD -->` on modified sections
   - `<!-- origin: client -->` on individual data points that came from client feedback
4. Update frontmatter fields:
   - `last_updated: YYYY-MM-DD`
   - `last_updated_by: positioning-update`
   - Preserve `generated_by` (never overwrite)
   - Add `has_client_input: true` if not already present
5. Run confidence reconciliation for the file (see Confidence Rules below)

**Proof Point Registry special handling:**
When feedback adds, modifies, or removes proof points in `company-identity.md`:
- New proof points get the next sequential ID (if last ID is P12, new one is P13)
- Proof point IDs are immutable: never reuse, never renumber
- Retired proof points: keep the entry, mark with `[RETIRED: reason]`, set origin to `client`
- Demoted proof points (client says the claim was overstated): update the entry, do not change the ID

**Scorecard re-evaluation:**
When changes affect positioning dimensions referenced in `positioning-scorecard.md`:
- Re-evaluate ONLY the affected dimensions, not the entire scorecard
- Ratings can change in any direction (Strong -> Needs Work, Needs Work -> Strong, etc.)
- Update the Key Finding column with the new evidence
- Add `<!-- amended by positioning-update YYYY-MM-DD -->` to changed rows

### Step 6: Change Log

After all edits are complete, display a structured summary:

```
## Changes Applied

### company-identity.md
  - [CORRECT] ARR updated: $8M -> $12M (Company Overview)
  - [ADD] Healthcare vertical added (Target Market)
  - [REMOVE] Starter tier removed (Pricing Model)
  - [AMEND] Platform positioning updated (Stated Differentiators)
  - [CONSTRAINT] SOC 2 claim restricted until Q3 2026 (Proof Point Registry, P7)
  Confidence: 4 -> 4

### positioning-scorecard.md
  - [AMEND] "Platform Breadth" re-evaluated: Needs Work -> Strong
  Confidence: 3 -> 3

### Not applied (research gaps)
  - Competitor "Acme" mentioned but competitive-landscape.md does not exist.
    Run /positioning-framework --depth standard to build competitive context.

### Potentially stale downstream files
  - .claude/deliverables/experiment-roadmap.md exists.
    Re-run /hypothesis-generator if changes affect experiment-relevant context.
```

### Step 7: Re-render

Unless `--skip-render` is set:

1. Check if `.claude/deliverables/` contains rendered deliverables (glob for `manifest.md`)
2. If deliverables exist, invoke `/render-default-deliverables` to re-render with updated context
3. If no deliverables exist, skip with note: "No rendered deliverables found. Run /render-default-deliverables when ready."

If `--context-dir` is set to a non-default path, skip re-render with note:
"Using non-default context directory. Skipping re-render (render-default-deliverables reads from .claude/context/). Run manually if needed."

Display completion:

```
Positioning update complete.

  [N] changes applied across [M] files
  [G] research gaps flagged
  [C] confidence changes: [list any files with changed confidence]
  Deliverables: [re-rendered | skipped (--skip-render) | skipped (no deliverables) | skipped (non-default context dir)]
```

---

## Confidence Rules (Client Feedback)

Client feedback follows a modified confidence protocol. The standard rules from `agent-header.md` apply with these additions:

**Authority hierarchy:** `client` > `tier-0` > `research`

Client data is the highest authority source. When client feedback contradicts research findings, the client version wins.

**Raising confidence:**
- Client confirmation of existing research raises section confidence by 1 (cap at 5, requires multi-source corroboration for 5)
- Client-provided data that fills previously empty REQUIRED sections raises section confidence by 1
- Multiple client inputs corroborating the same fact can raise to 5

**Corrections are upgrades:**
- Replacing wrong research data with correct client data does NOT lower confidence
- The section now has more accurate information from a higher-authority source, which is inherently higher quality
- This differs from agent-header.md's "contradictions can lower confidence" rule because that rule covers research-vs-research conflicts (genuine uncertainty). Client corrections are authoritative by definition -- there is no uncertainty about which version is correct.
- Exception: if a correction empties a REQUIRED field (e.g., "we don't actually have any case studies"), confidence CAN decrease

**Removals:**
- Removing an item from a populated section: confidence unchanged (accuracy improved)
- Removing enough to empty a REQUIRED section: confidence decreases

**Constraints:**
- Adding constraints does not lower confidence (knowing your limits is knowledge, not ignorance)
- Constraints are flagged with origin: client for downstream consumption

**Scorecard ratings:**
- Can change in any direction (existing convention, not specific to client feedback)

**Depth field:**
- Client feedback does not change the depth field. Depth reflects research scope, not data quality.

**File-level confidence reconciliation:**
After all section changes, recalculate file-level confidence as min(REQUIRED section confidences). OPTIONAL sections do not drag down file-level confidence.

---

## Quality Rules

1. **Never fabricate.** If feedback says "our main competitor is Acme," do NOT create a competitor profile. Classify as GAP and tell the user to run `/positioning-framework`.
2. **Never downgrade provenance.** Client-origin data stays client-origin. Research-origin data can be upgraded to client-origin if the client confirms it.
3. **Surgical edits only.** Change the lines affected by the feedback. Do not reformat, restructure, or "improve" surrounding content.
4. **Every change is traceable.** Each change in the execution step maps 1:1 to an item in the change plan. No phantom edits.
5. **Proof point IDs are immutable.** Never reuse a retired ID. Never renumber existing IDs.
6. **Change plan is mandatory.** Even for a single typo correction, present the plan and get approval.
7. **Conflict detection.** If two feedback items contradict each other (e.g., "ARR is $12M" and "ARR is $15M" in the same batch), flag the conflict and ask the user to resolve before applying either.
8. **No research.** If feedback implies something that would require verification ("I think our competitor just raised a Series B"), classify as GAP, do not go verify.
9. **Preserve structure.** Context files follow schemas. Changes must respect the schema structure. Do not add sections that don't belong, remove structural elements, or change heading hierarchy.
10. **Client contradictions across sessions.** If client feedback contradicts a previous `<!-- origin: client -->` data point, flag it: "This conflicts with prior client input: [quote]. Which is current?" Do not silently overwrite client-origin data with new client-origin data.
