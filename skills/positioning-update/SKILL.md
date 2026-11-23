---
name: positioning-update
version: 1.1.0
updated: 2026-11-23
description: >-
  When the user wants to apply client feedback, corrections or new research
  to existing positioning context. Also use for 'update positioning,' 'apply
  feedback,' 'client feedback,' 'stakeholder input,' 'correct positioning,'
  'update company identity,' 'amend context,' 'client says,' 'they told us,'
  'refresh positioning,' or 'amend the knowledge base.' Amendment skill, not
  research. Amends L0+L1 context files or a bound knowledge base's positioning
  artifacts (--scope).
---

# Positioning Update

You are a senior positioning analyst applying new intelligence to an existing positioning framework. The input is client feedback or other source material, such as a research extraction. Your job is to parse it, classify each piece of intelligence, propose a structured change plan, and execute surgical updates to the positioning context.

**You are an amendment skill.** You modify existing L0+L1 positioning context based on intelligence the user already has. This means:
- You NEVER perform web research, API calls, or data collection
- You NEVER fabricate context from feedback (no creating competitor profiles from passing mentions)
- You apply only what the feedback explicitly states or directly implies
- You preserve everything the feedback does not address
- Your changes touch L0 + L1 context only: `.claude/context/` files in legacy mode, or the scope's company facts and silver positioning artifacts in KB mode (see `KB Mode (Dual-Mode Output)`)
- Deliverable re-rendering is delegated to `/render-default-deliverables`

**Output location:** Edits to existing files in `.claude/context/` (KB mode: edits to the scope's existing KB artifacts, see `KB Mode (Dual-Mode Output)`)
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
/positioning-update --provenance research --file path/to/extraction.md
/positioning-update --scope <slug> --file <path-to-capture-in-kb>
/positioning-update --no-kb
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | none | Path to a file containing the feedback or source material. If omitted, skill prompts for pasted input. In KB mode it is required and must be a bronze artifact inside the bound KB (see `KB Mode (Dual-Mode Output)` > `Input Source Check`). |
| `--dry-run` | false | Stop after presenting the change plan. Do not execute changes. |
| `--context-dir` | `.claude/context/` | Legacy mode only. Override the context file directory for non-standard project layouts. A non-default path implies `--skip-render`, because render-default-deliverables has no context-directory flag. In KB mode, warn and ignore it. |
| `--skip-render` | false | Skip the `/render-default-deliverables` invocation after applying changes. Applies in both modes. |
| `--provenance` | `client` | Where the input came from: `client` or `research`. Sets the origin comments, `has_client_input` and the confidence rules (see `Confidence Rules (Client Feedback)`). Applies in both modes. |
| `--scope` | (none) | KB mode only. Names the KB scope to amend. Required in KB mode; warn-and-ignore in legacy mode. See `KB Mode (Dual-Mode Output)`. |
| `--no-kb` | off | Force legacy `.claude/context/` I/O even when a KB binding is detected. See `KB Mode (Dual-Mode Output)`. |

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

**KB mode (supported).** When the working repo declares a CRO knowledge base binding, this skill amends the scope's KB artifacts instead of `.claude/context/` files. See `KB Mode (Dual-Mode Output)`. In KB mode the hard requirements are the scope's `bronze-company-facts` and `silver-strategy-context`, the lower of their two confidences at 2 or more, and a `--file` that names a bronze artifact inside the KB. Force a legacy run with `--no-kb`.

---

## KB Mode (Dual-Mode Output)

This skill runs in one of two I/O modes, resolved ONCE at startup (before Step 1) and held in-session. Only the read source, the write target and the hand-off change. Classification, the change plan, surgical edits, provenance comments and the confidence rules are identical in both modes.

- **Legacy mode** (default): read and amend `.claude/context/*.md`.
- **KB mode:** read and amend the scope's company facts and silver positioning artifacts in the bound KB.

This is a single-agent skill. Mode resolution produces in-session KB state (`kb_root`, `kb_type`, `scope` and the type-definition paths), and the steps below consult it.

### Mode Resolution Procedure

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy mode, and note in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy I/O."
3. Parse the KB root path and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/` and its `artifacts/` directory defines `bronze-company-facts` and `silver-strategy-context`, the L0 pair this skill amends. If any check fails: legacy mode, and report which check failed. Never write typed artifacts into a half-configured KB. The three L1 silver types (`silver-competitive-analysis`, `silver-audience-analysis`, `silver-positioning-scorecard`) are optional: an item aimed at a missing one is a GAP, as an item aimed at a missing L1 file is in legacy mode.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope.
5. Run the `Input Source Check` below.

There is deliberately no `--kb` force flag. A failed detection of the KB falls back to legacy loudly so a broken KB binding gets fixed instead of worked around.

**Flag notes:** `--scope` in legacy mode: warn and ignore. `--context-dir` in KB mode: warn and ignore, since it names a legacy directory.

### Type Definitions

The bound type definitions at `.claude/skills/{kb-type}/artifacts/{artifact-type}.md` decide which fields an amended artifact carries. A field counts as declared only when the type definition lists it in its own `field_definitions`. kb-start's universal template makes `depends_on` optional for every type, and that does not count. This skill never names a KB type skill or a client-specific path. It composes `governed_by` as `{kb-type}/{artifact-type}` at runtime.

### Input Source Check

In KB mode the input must already be a KB source, so every amended artifact can cite it.

- **Rule:** `--file` must resolve to a file inside `kb_root` whose frontmatter has `kb_layer: bronze`. Resolve the path from the working repo root, as in legacy mode.
- **Failure:** No `--file`, pasted input, a file outside `kb_root` or a file of another layer is a HARD STOP before Step 1. Tell the user to capture the input into the KB with `kb-capture` first, then re-run with `--file` naming the capture.
- **Scope:** The input need not carry the run's scope. A meeting or email capture often spans scopes. Scope isolation governs discovery, not this operator-named input.
- **Held value:** Hold the input's KB-root-relative path in session as `input_path`.

### Read-Side Mapping

In KB mode, Step 1 finds the scope's artifacts by type, not by path:

1. Glob `{kb_root}/**/*.md`.
2. Keep each file whose `governed_by` is `{kb_type}/` plus one of the five types in the table below, and whose `scope` matches. Scope isolation is absolute: an artifact from another scope is never read or amended.
3. Inventory each kept artifact's path, type, confidence and `updated`.

| Legacy context file | KB artifact type |
|---|---|
| `company-identity.md` | `bronze-company-facts` + `silver-strategy-context` |
| `competitive-landscape.md` | `silver-competitive-analysis` |
| `audience-messaging.md` | `silver-audience-analysis` |
| `positioning-scorecard.md` | `silver-positioning-scorecard` |

**L0 precondition:** Both L0 types must exist for the scope, and the lower of their two confidences must be 2 or more. Otherwise exit: "Company facts or strategy context for scope `{scope}` is missing or too shallow (confidence < 2). Run /positioning-framework <url> --scope {scope} first."

### Classification Mapping

In KB mode, Step 3's mapping rules target artifact types:

- **L0 items:** Route each to `bronze-company-facts` or `silver-strategy-context` by the section table in positioning-framework's `phases/company.md` > `KB Mode Output`. Facts such as the company overview, services, statistics, constraints, proof points and pricing go to the company facts. Target segments, differentiators, buying triggers and the category gap go to the strategy context.
- **L1 items:** Competitive items go to `silver-competitive-analysis`, audience and messaging items to `silver-audience-analysis`, and scorecard items to `silver-positioning-scorecard`.
- **GAP:** An item whose type has no artifact for the scope.

The change plan names each target by its path and type.

### Amendment

In KB mode, Step 5 applies every legacy rule: surgical edits, provenance comments, `last_updated_by: positioning-update`, preserved `generated_by` and the proof-point ID rules. KB artifacts also get:

- **Dates and version:** `updated` set to the run date, in place of the legacy `last_updated`. No separate `last_updated` field is written. A minor `version` bump.
- **Source edge:** When the artifact's type declares `depends_on`, add `input_path` to it if absent.
- **Source comment:** When the type does not declare `depends_on`, the amended comment names the input instead: `<!-- amended by positioning-update YYYY-MM-DD from {input_path} -->`.
- **`data_provenance`:** Only when the type declares it. `--provenance client` sets `client`. `--provenance research` leaves the value as it is, so a `client` artifact is never downgraded.

Which procedure writes depends on the session:

- **kb-start loaded:** When the session has kb-start loaded, as a managed KB repo requires, its `Artifact Write Routing` governs every amended write. Each write takes the `Update Path` and its `Universal Post-Write` cycle. This skill's surgical-edit rules supply the content of each update. When that cycle presents a propagation plan, the operator's answer governs. This skill itself edits nothing outside the approved change plan, and Step 7's render is the route for gold dependents.
- **kb-start not loaded:** The skill writes each amendment directly, then runs the `Post-Write Validation Gate`. It never requires kb-start.

### Post-Write Validation Gate

Without kb-start loaded, validate each amended artifact against its bound type definition:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY <kb-start-scripts>/kb_type_validate.py validate <artifact-path> --artifact-type-path <type-definition-path>
```

Run the command once per amended artifact. The validator takes one target per call. Passing the type definition makes its type layer run wherever the repo root sits.

- **Failure:** Any non-zero exit fails the gate, a usage error included. So does a `governed_by` finding that says the type layer did not run, even though that finding alone exits 0.
- **Fix:** If validation reports errors, fix the artifact's frontmatter or sections and re-validate.
- **Unresolved script:** Resolve `<kb-start-scripts>` from the fe-knowledge-base plugin's kb-start skill `scripts/` directory (marketplace plugin cache or source repo). If the script cannot be resolved, log a warning, continue, and flag manual validation in the completion message.

### KB Mode Completion Message

In KB mode, Step 6 and the Step 7 completion name artifacts by path and type instead of file name:

```
Positioning update complete ({scope}).

  Input: {input_path} (provenance: client | research)
  Amended:
    {kb_root}/{path}   ({artifact-type})   confidence: N -> M   gate: passed | failed (fixed and re-validated) | unresolved | kb-start Universal Post-Write
    (one entry per amended artifact)
  Research gaps: [list | none]
  Potentially stale: [paths | none]
  Deliverables: handed off (--scope {scope}) | skipped (--skip-render) | skipped (no deliverables)
```

---

## Execution Pipeline

### Step 1: Context Discovery

**KB mode:** Discover, inventory and check preconditions per `KB Mode (Dual-Mode Output)` > `Read-Side Mapping` instead of items 1 to 3 and 5. The input is the file `--file` named, so skip the paste prompt.

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

**Interactive mode** (default in legacy mode; not available in KB mode, see `Input Source Check`): Multi-turn intake loop.
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

**KB mode:** Map items to artifact types per `KB Mode (Dual-Mode Output)` > `Classification Mapping`.

### Step 4: Change Plan (Checkpoint)

Present a structured change plan. This checkpoint is mandatory, even for a single correction. State the declared `--provenance` value above the item tables, so the user confirms it here.

```
## Change Plan

Input provenance: client | research

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

**KB mode:** Each item below applies to the amended KB artifact, except that `updated` replaces `last_updated`. `KB Mode (Dual-Mode Output)` > `Amendment` adds the KB fields and says which write procedure governs.

**For each file being modified:**

1. Read the full file content
2. Apply changes surgically. Edit only the lines affected by the change. Do not rewrite entire sections or reformat surrounding content.
3. Add provenance tags to changed content:
   - `<!-- amended by positioning-update YYYY-MM-DD -->` on modified sections
   - `<!-- origin: {provenance} -->` on individual data points that came from the input, where `{provenance}` is the declared `--provenance` value (`client` or `research`)
4. Update frontmatter fields:
   - `last_updated: YYYY-MM-DD`
   - `last_updated_by: positioning-update`
   - Preserve `generated_by` (never overwrite)
   - Add `has_client_input: true` if not already present, only when `--provenance` is `client`
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

**KB mode:** Head each file section with the artifact's path and type. The stale list names:
- the scope's `gold-experiment-roadmap`, when one exists;
- each in-scope silver artifact whose `depends_on` lists an artifact this run amended, unless this run amended it too. Re-run the skill that produced it if the change affects it.

### Step 7: Re-render

Unless `--skip-render` is set, hand off to render-default-deliverables in this run's resolved mode.

**Legacy mode:**

1. Check if `.claude/deliverables/` contains rendered deliverables (glob for `manifest.md`)
2. If deliverables exist, invoke `/render-default-deliverables --no-kb` to re-render with updated context. `--no-kb` keeps the render in legacy mode even in a repo with a KB binding.
3. If no deliverables exist, skip with note: "No rendered deliverables found. Run /render-default-deliverables when ready."

If `--context-dir` is set to a non-default path, skip re-render with note:
"Using non-default context directory. Skipping re-render (render-default-deliverables reads from .claude/context/). Run manually if needed."

**KB mode:**

1. Glob `{kb_root}/**/*.md` for files whose `governed_by` is `{kb_type}/gold-strategy-deliverable` or `{kb_type}/gold-battle-card` and whose `scope` matches. Match by type, never by path or `manifest.md`.
2. If any exist, invoke `/render-default-deliverables --scope <scope>`. Its own plan, prior-render search and stops then govern.
3. If none exist, skip with note: "No rendered deliverables found for scope `{scope}`. Run /render-default-deliverables --scope {scope} when ready."

Display completion (**KB mode:** use `KB Mode (Dual-Mode Output)` > `KB Mode Completion Message`):

```
Positioning update complete.

  [N] changes applied across [M] files
  [G] research gaps flagged
  [C] confidence changes: [list any files with changed confidence]
  Deliverables: [re-rendered | handed off (--scope <scope>) | skipped (--skip-render) | skipped (no deliverables) | skipped (non-default context dir)]
```

---

## Confidence Rules (Client Feedback)

These rules apply to `--provenance client` input. `--provenance research` input follows the standard rules in `skills/positioning-framework/agent-header.md` alone, with no additions, and its origin comments read `research`. The authority hierarchy below and `Quality Rules` still hold for research input: a research item that contradicts an `origin: client` data point is a conflict. Flag it in the change plan, and leave the client data point as it is unless the user approves the change.

Client feedback follows a modified confidence protocol. The standard rules from `skills/positioning-framework/agent-header.md` (the shared agent rules governing the context files this skill amends) apply with these additions:

**Authority hierarchy:** `client` > `tier-0` > `research`

Client data is the highest authority source. When client feedback contradicts research findings, the client version wins.

**Raising confidence:**
- Client confirmation of existing research raises section confidence by 1 (cap at 5, requires multi-source corroboration for 5)
- Client-provided data that fills previously empty REQUIRED sections raises section confidence by 1
- Multiple client inputs corroborating the same fact can raise to 5

**Corrections are upgrades:**
- Replacing wrong research data with correct client data does NOT lower confidence
- The section now has more accurate information from a higher-authority source, which is inherently higher quality
- This differs from that file's "contradictions can lower confidence" rule because that rule covers research-vs-research conflicts (genuine uncertainty). Client corrections are authoritative by definition -- there is no uncertainty about which version is correct.
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
