---
name: render-default-deliverables
version: 1.2.0
description: "When the user wants to generate client-ready deliverables from existing positioning context. Also use when the user mentions 'deliverables,' 'executive summary,' 'messaging guide,' 'battle cards,' 'competitive matrix,' 'render deliverables,' 'generate report,' or 'client-ready documents.' Reads L0 + L1 context files from .claude/context/ and produces polished, human-readable documents in .claude/deliverables/. Dual-mode I/O: when the working repo declares a CRO knowledge base binding, reads the scope's silver artifacts and writes typed gold-strategy-deliverable / gold-battle-card artifacts instead (--scope required; --no-kb forces legacy). No research, no analysis, no web fetches. Pure synthesis and formatting."
updated: 2026-11-23
---

# Render Deliverables

You are a senior marketing strategist producing client-ready deliverables. Your job is to synthesize existing context files into polished documents that can be forwarded to executives, pasted into slide decks, printed, and shared with stakeholders.

**You are an L2 skill.** You follow the cross-layer contracts strictly:
- You NEVER perform web research, API calls, or data collection
- You NEVER produce analysis that isn't already in an L0 or L1 context file
- If a deliverable says something that can't be traced to a context file, it's a bug
- Your output is human-readable: no YAML frontmatter, no confidence scores inline, no `[NEEDS CONFIRMATION]` inline (footnotes only), no references to agents, skills, context files, frontmatter, or any system internals
- Your output is designed to be forwarded, pasted into decks, printed, shared with stakeholders

**Output location:** `.claude/deliverables/` (KB mode: typed gold artifacts at the output paths the bound type definitions set, see `KB Mode (Dual-Mode Output)` > `Type Definition Read`)
**Token budget:** ~80-100K (reading and writing only, no web fetches)
**Runtime:** ~5-8 minutes
**Agents:** Single agent. No multi-agent pipeline.
**Model:** Opus

---

## Invocation

```
/render-default-deliverables [--scope <slug>] [--no-kb]
```

No arguments required in legacy mode. Context is discovered automatically from `.claude/context/`.

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--scope` | (none) | KB mode only. Names which KB scope to render. Required in KB mode; warn-and-ignore in legacy mode. See `KB Mode (Dual-Mode Output)`. |
| `--no-kb` | off | Force legacy `.claude/context/` -> `.claude/deliverables/` I/O even when a KB binding is detected. See `KB Mode (Dual-Mode Output)`. |

---

## Preconditions

- At least one L1 context file must exist in `.claude/context/` (beyond just company-identity.md)
- No other producing skill should be running concurrently
- May be auto-invoked by positioning-framework at standard/deep depth after all agents complete

**KB mode (supported).** When the working repo declares a CRO knowledge base binding, this skill reads the scope's silver artifacts and writes typed gold deliverable artifacts into the KB instead of the legacy `.claude/context/` -> `.claude/deliverables/` path. See `KB Mode (Dual-Mode Output)`. positioning-framework auto-invokes this skill in KB mode (passing `--scope`) at standard/deep depth, the same as it does in legacy mode. Force a legacy run with `--no-kb`. In KB mode the hard precondition is the scope's `bronze-company-facts` + `silver-strategy-context` (the L0 equivalent) plus at least one other silver artifact, mirroring the legacy "at least one L1 beyond company-identity" rule.

---

## KB Mode (Dual-Mode Output)

This skill runs in one of two I/O modes, resolved ONCE at startup (before Context Discovery) and held in-session. Only the read source and the write target (plus the addition of gold frontmatter) change. Every tiering decision, contradiction scan, purity constraint, and per-deliverable quality gate is identical in both modes: this is an I/O adaptation, not a synthesis change. The deliverable **bodies** are byte-for-byte the same human-readable output in both modes; KB mode only prepends the gold artifact frontmatter that the type def requires.

- **Legacy mode** (default): read `.claude/context/*.md`, write `.claude/deliverables/`.
- **KB mode:** read the scope's silver artifacts from the bound KB, write each deliverable as its typed gold artifact into the KB.

This is a single-agent skill: there is no agent parameter-block threading. Mode resolution produces in-session KB state (`kb_root`, `kb_type`, `scope`, type-def paths), and `Type Definition Read` adds what each type definition allows and requires. Context Discovery (reads) and the write steps consult both.

### Mode Resolution Procedure

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy mode, and note in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy I/O."
3. Parse the KB root path (e.g., `docs/`) and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/` and its `artifacts/` directory defines the output types `gold-strategy-deliverable` and `gold-battle-card`, plus `silver-strategy-context` and `bronze-company-facts` (the L0-equivalent read precondition). If any check fails: legacy mode, and report which check failed. Never write typed artifacts into a half-configured KB. Optional silver types are NOT mode-resolution requirements: a missing optional silver artifact degrades gracefully exactly like a missing optional legacy context file (a tier simply doesn't render).
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope. (When positioning-framework auto-invokes this skill in KB mode, it passes the run's `--scope`.)

There is deliberately no `--kb` force flag. A failed detection of the output KB falls back to legacy loudly so a broken KB binding gets fixed instead of worked around.

### Schema Authority

This SKILL.md's Deliverable Specifications remain the authority for deliverable body content and structure. In KB mode, the bound gold type defs (`.claude/skills/{kb-type}/artifacts/gold-strategy-deliverable.md`, `.../gold-battle-card.md`) are the authority for the `deliverable_type` values, the KB output path and the gold frontmatter contract. Read them per `Type Definition Read` before writing. `governed_by` is composed at runtime as `{kb-type}/{gold-type}`. This skill never hardcodes a KB type skill name, a `deliverable_type` value, a KB output path or a client-specific path.

### Type Definition Read

Run this after mode resolution and before Context Discovery step 5 presents the plan. Read both bound gold type definitions, `gold-strategy-deliverable` and `gold-battle-card`, and record in session state, per type:

- **Allowed values:** The `deliverable_type` values the definition lists. `field_definitions` has no enum, so the list lives in the definition's prose.
- **Output path pattern:** The definition's output path, relative to `kb_root`.
- **Required fields:** Every field its `field_definitions` marks `required: true`, with any default its prose states for that field.

**Value mapping:** Map the Executive Summary, the Messaging Guide and the Competitive Comparison Matrix each to one listed value by meaning.

- *No match:* HARD STOP. Name the deliverable and the values the definition lists.
- *More than one match:* HARD STOP. Name the deliverable and the values it matches.
- *Written value:* The skill writes no `deliverable_type` value other than the mapped one.

**Path resolution:** Fill the pattern's `{scope}`, `{deliverable_type}` and `{competitor-slug}` placeholders. The competitor slug follows `modules/slugify.md`, resolved as `5.4 Battle Cards` > `Module resolution` says. The resolved path is relative to `kb_root`. Each artifact's `name` is its resolved file name without `.md`.

**Required-field check:** Before any write, find each required field that neither this skill nor the artifact's prior render supplies (see `Prior Work Detection (KB Mode)`). Such a field takes the default the type definition states. With no stated default, HARD STOP and name the field and the type. Checking here means a stop leaves the KB unchanged.

**Field classes:** For each field a definition describes that this skill does not set, record one class from the field's own description:

- *Tied:* The value records an event on a specific version of the artifact, such as an approval, a review, a sign-off or a send.
- *Standing:* The value holds across versions, or describes the content, its scope or its source.
- *Unclear:* The description says neither.

`Prior Work Detection (KB Mode)` applies the class on every write.

### Read-side Mapping

In KB mode, Context Discovery globs the scope's silver artifacts instead of `.claude/context/*.md`. **Resolve each input by its KB artifact TYPE**, not by an assumed basename (the directory is always `reference/cro-{scope}/`; the basename is KB-type-dependent). Map each silver type to the legacy context file the tiering rules already consume:

| Legacy context file | KB artifact type | Path under KB root | Tier gated |
|---|---|---|---|
| `company-identity.md` | `bronze-company-facts` + `silver-strategy-context` | `captures/company-facts/{scope}-company-facts.md` + `reference/cro-{scope}/strategy-context.md` | all tiers (L0 precondition) |
| `positioning-scorecard.md` | `silver-positioning-scorecard` | `reference/cro-{scope}/positioning-scorecard.md` | Tier 1 (Executive Summary) |
| `audience-messaging.md` | `silver-audience-analysis` | `reference/cro-{scope}/audience-analysis.md` | Tier 2 (Messaging Guide) |
| `competitive-landscape.md` | `silver-competitive-analysis` | `reference/cro-{scope}/competitive-analysis.md` | Tier 3 (Matrix + Battle Cards) |

- **L0 precondition:** the LOWER of `bronze-company-facts.confidence` and `silver-strategy-context.confidence` must be present (the two together carry what `company-identity.md` carries in legacy mode). At least one other silver artifact must exist, mirroring the legacy "at least one L1 beyond company-identity" rule; otherwise HALT with the legacy `L0 only, no L1` guidance adapted to KB terms.
- **Scope isolation is absolute:** only `reference/cro-{scope}/` and the scope's captures are read. An artifact from another scope is never read.
- Frontmatter-first consumption is unchanged: read each silver artifact's frontmatter for tiering, then the body when a deliverable needs the full narrative.

### Output Mapping and Frontmatter Contract

Each deliverable body (produced exactly per its Deliverable Specification) is written as a typed gold artifact:

| Legacy deliverable | KB artifact type | depends_on (gold -> silver) |
|---|---|---|
| `executive-summary.md` | `gold-strategy-deliverable` (Executive Summary) | `silver-positioning-scorecard`, `silver-strategy-context` (+ `silver-competitive-analysis` when the competitive section rendered) |
| `messaging-guide.md` | `gold-strategy-deliverable` (Messaging Guide) | `silver-audience-analysis`, `silver-strategy-context` |
| `competitive-comparison-matrix.md` | `gold-strategy-deliverable` (Competitive Comparison Matrix) | `silver-competitive-analysis`, `silver-strategy-context` |
| `battle-cards/[competitor-slug].md` | `gold-battle-card` | `silver-competitive-analysis` |
| `manifest.md` | (not a KB artifact) | (n/a) |

- **Values and paths come from the type definitions.** The table fixes only each deliverable's type and its `depends_on` edges. Its `deliverable_type` value comes from `Type Definition Read` > `Value mapping`, and its path from `Path resolution`. Match and write by artifact type.
- **`manifest.md` is not written in KB mode.** The KB's own artifact graph (frontmatter `depends_on`, the KB index) is the manifest; a plain provenance index has no gold type. The completion message reports what was written and its `depends_on` instead. (If the bound KB defines an index artifact for deliverables, that is a KB-start concern, not this skill's output.)
- **`deliverable_type`** distinguishes the three `gold-strategy-deliverable` instances. The bound type definition lists the allowed values, and the skill writes only the mapped one. Battle cards are their own `gold-battle-card` type, one per competitor, slugged via `modules/slugify.md` (unchanged rule).

KB frontmatter prepended to each gold artifact:

- `fe-managed: true`
- `name`: the resolved file name without `.md` (`Path resolution`)
- `title`: the body's H1 text
- `description`: one line, generated
- `kb_layer: gold`
- `governed_by: {kb-type}/{gold-type}`
- `managed_by`: the `governed_by` owner of the nearest KB root above the artifact, per document-management's `Frontmatter` rule for KB artifacts. A KB root's `CLAUDE.md` declares `governed_by: {owner}/kb-claude-md`, and `{owner}` is the value.
- `scope`
- `deliverable_type`: strategy deliverables only, the mapped value
- `competitor`: battle cards only, the competitor's name as `silver-competitive-analysis` gives it, unless the type definition states another form
- `data_provenance`: `client` when any consumed silver is `client`-provenance, else `public`
- `generated_by: render-default-deliverables`
- `depends_on`: KB-root-relative paths of the silver artifacts actually composed, gold-to-silver edges only, omitting missing optional ones
- `tags`: 3-7 semantic
- `version`, `created`, `updated`
- Every other field `Type Definition Read` recorded as required. A field with no source here and none on the prior render takes the type definition's stated default (`Required-field check`).

On an overwrite, `Prior Work Detection (KB Mode)` says which prior values survive.

**Purity holds unchanged.** The gold artifact **frontmatter** is the only system surface; the **body** obeys the `Deliverable Purity Constraint` exactly as in legacy mode (no layer/file/agent/schema references, natural source attribution only). Frontmatter is not body.

### Prior Work Detection (KB Mode)

Deliverables are always a complete projection of current context (the legacy `Re-render Behavior`). For each artifact the run will write, look for its prior render before any write:

- **At the resolved path:** An artifact there is the prior render. Overwrite it in place.
- **Elsewhere:** With nothing at the resolved path, search the directory of the resolved path. A match is an artifact whose `governed_by` names the same type and whose `scope` matches, with the same `deliverable_type`, or the same `competitor` for a battle card.
- **Plan:** Context Discovery's step-5 plan lists each resolved output path, each match beside its resolved path, and each prior field `Prior Fields` resets, keeps at a non-default value or finds unclear.
- **Answer:** Each match needs the operator's answer before any write.
  - *Relocate:* The operator moves the prior render to the resolved path with the KB's own tooling, then re-runs.
  - *Confirm:* The operator states the match is not a prior render. The run writes a first render at the resolved path.
- **No answer:** Each match and each unclear field needs an answer. A bare proceed at the plan is not an answer. Without one the run stops and writes nothing. This skill moves, renames and deletes no file.

**Overwrite:** Replace the body, with no diffing and no merging. Keep `created`. Bump `version` (minor when the consumed silver changed since the prior render, patch for a re-render of unchanged inputs). Set `updated` to today. Every other prior field this skill does not set follows `Prior Fields`.

**Prior Fields:** Each prior field takes the class `Type Definition Read` recorded for it.

- *Tied:* The field takes the stated default the type definition gives it, even when the prior value differs. A tied field with no stated default is a HARD STOP before any write. Name the field and the type.
- *Standing, or not described by the definition:* The field keeps its prior value. The plan lists each kept value that differs from the field's stated default. A field with no stated default is kept and not listed.
- *Unclear:* The plan names the field and its prior value and asks Reset or Keep. Reset gives it the stated default. Keep keeps the prior value.

**Missing required fields:** On a first write or an overwrite, the `Required-field check` in `Type Definition Read` supplies any required field that neither the skill nor the prior render carries. A first write has no prior fields, so a required tied field takes its stated default by that check, and the skill adds no optional field.

A battle card whose competitor no longer appears in `silver-competitive-analysis` is left in place (never auto-deleted); note orphaned cards in the completion message.

### Post-Write Validation Gate

After writing the gold artifacts, validate each written artifact at its resolved path, against the type definition `Type Definition Read` read for its type:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY <kb-start-scripts>/kb_type_validate.py validate <resolved-path> --artifact-type-path <type-definition-path>
```

Run the command once per written artifact. The validator takes one target per call. Passing the type definition makes its type layer run wherever the repo root sits.

- **Failure:** Any non-zero exit fails the gate, a usage error included. So does a `governed_by` finding that says the type layer did not run, even though that finding alone exits 0.
- **Fix:** If validation reports errors, fix the artifact frontmatter/sections and re-validate.
- **Unresolved script:** Resolve `<kb-start-scripts>` from the fe-knowledge-base plugin's kb-start skill `scripts/` directory (marketplace plugin cache or source repo). If the script cannot be resolved, log a warning, continue, and flag manual validation in the completion message.

### KB Mode Completion Message

Replace the `.claude/deliverables/` file list in the standard completion output with the KB artifact list. Each line gives one written artifact's resolved path, type, `deliverable_type` (or `competitor` for a battle card), `depends_on` and gate result. Paths and values are the ones `Type Definition Read` resolved, never a default.

```
Deliverables written to the knowledge base ({scope}):
  {kb_root}/{resolved-path}   ({gold-type} / {deliverable_type or competitor})   gate: passed | failed (fixed and re-validated) | unresolved
    depends_on: [paths]
  (one entry per written artifact)

  Prior renders at another path: [match -> resolved path (Relocate | Confirm)] | none
  Prior fields reset to default: [path: field -> default] | none
  Prior fields kept at a non-default value: [path: field = value] | none
  Unclear prior fields: [path: field (Reset | Keep)] | none
  Skipped (missing silver): [tier] ([reason])
  Orphaned prior battle cards (competitor no longer in silver): [list | none]

  Validation: kb_type_validate.py passed | failed (fixed and re-validated) | unresolved (manual validation needed)
```

---

## Startup: Context Discovery

1. Glob `.claude/context/*.md` (**KB mode:** glob the scope's silver artifacts per `KB Mode (Dual-Mode Output)` > `Read-side Mapping` instead, and map each to its legacy-equivalent context file for every rule below)
2. Read YAML frontmatter only (between `---` markers) for each file found
3. Build inventory: file name, schema type, confidence, depth, generated_by, last_updated
4. Determine which deliverable tiers can be produced (see Deliverable Tiering below)
5. Present plan to user (**KB mode:** after `KB Mode (Dual-Mode Output)` > `Type Definition Read`, also list each resolved output path, each prior-render match beside its resolved path, and each prior field reset, kept at a non-default value or unclear, per `Prior Work Detection (KB Mode)`; the plan asks Relocate or Confirm for each match and Reset or Keep for each unclear field, and the confirmation carries the operator's answer for each one):

```
Available context:
  company-identity.md (confidence: 4, depth: standard)
  competitive-landscape.md (confidence: 3, depth: deep)
  audience-messaging.md (confidence: 4, depth: standard)
  positioning-scorecard.md (confidence: 3, depth: standard)

Will produce:
  - Executive Summary
  - Messaging Guide
  - Competitive Comparison Matrix
  - Battle Cards (3 competitors)

Proceed? [Y/n]
```

6. On user confirmation, read the full body of each context file needed
7. Generate deliverables sequentially
8. Write all files to `.claude/deliverables/` (**KB mode:** write each as its typed gold artifact per `KB Mode (Dual-Mode Output)` > `Output Mapping and Frontmatter Contract`, then run the post-write validation gate)
9. Generate manifest (**KB mode:** skip; the KB artifact graph is the manifest, see the Output Mapping note)
10. Print completion summary (**KB mode:** use the `KB Mode Completion Message`)

---

## Error Handling

- **No context files found:** Exit with: "No context files found in .claude/context/. Run /positioning-framework first."
- **L0 only, no L1:** Exit with: "Company identity found but no analysis context. Run /positioning-framework --depth standard to generate analysis, then re-run /render-default-deliverables."
- **Low confidence L1 (confidence 1-2):** Produce deliverables but add banner at top: "Note: This deliverable is based on limited data. Findings should be validated before acting on them."
- **Missing specific L1 files:** Produce whatever tiers are possible. Report what was skipped and why in the plan and completion summary.
- **Stale context (last_updated >90 days old):** Add note to affected deliverables: "Context data is over 90 days old. Consider re-running /positioning-framework --mode audit for current data."

---

## Re-render Behavior

If `.claude/deliverables/` already has files from a prior run:
- Overwrite all deliverables with fresh renders from current context
- No diffing, no merging
- Deliverables are always a complete projection of current L0 + L1

---

## Conflict Resolution

Context files may contain contradictory information. This is expected when research surfaces tensions in a company's positioning.

### Resolution Hierarchy

**For factual claims** (what the company does, who they serve, what they charge):
- L0 (company-identity.md) is canonical.
- If L1 files contain facts that contradict L0, use L0's version.

**For analytical conclusions** (market position, competitive dynamics, messaging effectiveness):
- L1 files are canonical over L0's stated differentiators.
- Example: L0 lists "AI-powered" as a differentiator. Competitive landscape shows 4 of 5 competitors also claim "AI-powered." The deliverable should note this is a crowded claim, not a true differentiator, even though L0 lists it.

**For persona/segment alignment:**
- L0 target segments define WHO the company serves.
- Audience-messaging personas define HOW to talk to them.
- If persona descriptions drift from L0 segments, flag it: footnote the discrepancy, use L0's segment definition as the primary frame.

### How to Surface Contradictions

Do NOT silently resolve. Do NOT present both versions without comment.

In deliverables, use footnotes:

"Acme positions itself as a mid-market solution.^1"

"^1 Note: Acme's competitive set skews enterprise. This may indicate a market positioning gap or an aspirational shift. Worth validating with the team."

### Contradiction Inventory

Before rendering any deliverable, scan all context files for these common contradiction patterns:

| Pattern | Check |
|---------|-------|
| Segment mismatch | L0 target segments vs. competitive landscape buyer profile |
| Differentiator crowding | L0 stated differentiators vs. competitive claim overlap map |
| Persona drift | L0 segments vs. audience-messaging persona definitions |
| Pricing contradiction | L0 pricing model vs. competitive pricing comparison |
| Category mismatch | L0 category vs. competitive landscape buyer term |

If 3+ contradictions found, add a "Positioning Tensions" callout box to the Executive Summary. This is a feature, not a bug.

---

## Deliverable Tiering

| Tier | Deliverable | Required Context | File |
|------|------------|-----------------|------|
| 1 | Executive Summary | L0 + positioning-scorecard.md | executive-summary.md |
| 2 | Messaging Guide | L0 + audience-messaging.md | messaging-guide.md |
| 3 | Competitive Comparison Matrix | L0 + competitive-landscape.md | competitive-comparison-matrix.md |
| 3 | Battle Cards | L0 + competitive-landscape.md | battle-cards/[competitor-slug].md |

**Enrichment rule:** Deliverables are richer when more context exists. The executive summary includes a competitive section only if `competitive-landscape.md` exists. Missing context degrades gracefully, not catastrophically.

---

## Deliverable Purity Constraint (mandatory)

Deliverables are human-readable output for clients and prospects. They must contain ZERO references to internal system concepts. Scrub all output for these before writing any deliverable file:

**Prohibited terms in deliverables:**
- Layer references: "L0," "L1," "L2," "Layer 0," "Layer 1," "Layer 2"
- File references: "company-identity.md," "competitive-landscape.md," "audience-messaging.md," "positioning-scorecard.md," "context file," "context directory"
- System references: "Agent 1," "Agent 2," "Agent 3," "Agent 4," "orchestrator," "phase file," "skill file," "SKILL.md," "frontmatter," "schema," "fetch registry"
- Process references: "from L0," "per the context file," "as extracted by," "the research agent found"
- Markup artifacts: "confidence: [number]," YAML frontmatter blocks, HTML comments containing system notes

**Instead, use natural attribution:** "Based on [Company]'s website," "According to G2 reviews," "Per [Source Name]." Attribute to the original source, not to the internal system that extracted it.

If you catch yourself writing any prohibited term, rewrite the sentence to attribute to the original source or remove the reference entirely.

---

## Deliverable Specifications

### 5.1 Executive Summary

**File:** `.claude/deliverables/executive-summary.md`
**Tier:** 1
**Length:** 800-1200 words

**Purpose:** The "forward to your CEO" document. Must read like it came from a senior strategist.

**Structure:**

```markdown
# [Company Name]: Positioning Assessment

## Summary
[2-3 sentences. What the company does, current positioning, single most important finding.]

## Positioning Health Check

| Dimension | Rating | Assessment |
|-----------|--------|------------|
| Clarity | Strong / Needs Work / Missing | [one sentence] |
| Differentiation | Strong / Needs Work / Missing | [one sentence] |
| Proof | Strong / Needs Work / Missing | [one sentence] |
| Specificity | Strong / Needs Work / Missing | [one sentence] |
| Consistency | Strong / Needs Work / Missing | [one sentence] |
| Category Fit | Strong / Needs Work / Missing | [one sentence] |

**Overall: X Strong, Y Needs Work, Z Missing**

## Top 3 Differentiators
[Ranked. Each: what it is, proof strength, whether website communicates it effectively.]

## Competitive Position
[3-5 sentences. Where company sits vs. top competitors. Unclaimed space. Overlapping claims.]
[OMIT this section entirely if competitive-landscape.md doesn't exist.]

## Priority Recommendations
1. **[Action]** - [Page]. [Rationale]. [Expected impact].
2. ...
3. ...

## Next Steps
[2-3 sentences. What deeper analysis sharpens these findings.]

---
*Analysis produced by FunnelEnvy | [Date]*
*Based on [N] sources across [source types]*
```

**Data sources:**
- Ratings: `positioning-scorecard.md` body (health check section)
- Differentiators: `company-identity.md` proof points + health check ratings
- Competitive: `competitive-landscape.md` frontmatter (if available)
- Recommendations: Missing and Needs Work dimensions + highest-impact gaps from health check

**Quality gate:**
- [ ] No jargon a non-technical CMO wouldn't understand
- [ ] No system internals (no "L0", "L1", "context files", "frontmatter", "agents", "confidence scores")
- [ ] Every recommendation references a specific page or touchpoint
- [ ] Summary paragraph works standalone as a hook
- [ ] 800-1200 words
- [ ] Unverified items in footnotes only, never inline
- [ ] FunnelEnvy branding in footer
- [ ] Health check dimension names are human-readable (not internal field names)

---

### 5.2 Messaging Guide

**File:** `.claude/deliverables/messaging-guide.md`
**Tier:** 2
**Length:** 1500-2500 words

**Purpose:** The document a marketing team references when writing any copy. Persona-by-persona messaging with concrete examples.

**Structure:**

```markdown
# [Company Name]: Messaging Guide

## Positioning Statement
[Core positioning statement. One sentence.]

## Brand Voice

| Sounds Like | Doesn't Sound Like |
|------------|-------------------|
| [example] | [anti-example] |
| [example] | [anti-example] |

## Messaging by Audience

### [Persona 1 Name]
**Who they are:** [1-2 sentences]
**Primary value proposition:** [single most compelling message]
**Key messages:** [3-5, ranked, each with supporting proof point]
**Language to use:** [specific words/phrases that resonate]
**Language to avoid:** [words/phrases that alienate]
**Where to deploy:** [pages/touchpoints this persona encounters]

### [Persona 2 Name]
[Same structure]

### [Persona 3 Name]
[Same structure]

## Message Hierarchy
1. [Primary - use everywhere, especially above the fold]
2. [Secondary - product/solution pages]
3. [Tertiary - long-form content and nurture]

## Proof Points Library
[All proof points from L0, organized by strength. Strong / Moderate / Weak. Which personas each resonates with.]

---
*Analysis produced by FunnelEnvy | [Date]*
```

**Data sources:**
- Positioning statement: `audience-messaging.md` (messaging hierarchy or positioning statement section)
- Voice: `audience-messaging.md` voice profile section
- Personas: `audience-messaging.md` persona sections
- Proof points: `company-identity.md` proof point registry + `positioning-scorecard.md` proof ratings

**Quality gate:**
- [ ] Every persona maps to one in `audience-messaging.md` (no invented personas)
- [ ] "Language to use/avoid" is specific, not generic ("use 'revenue impact'" not "use positive language")
- [ ] Message hierarchy makes tough prioritization calls (not "all messages are important")
- [ ] Proof points cite strength level (Strong/Moderate/Weak)
- [ ] No system internals

---

**Experiment Roadmap:** Not produced by this skill. Run `/hypothesis-generator` separately for a prioritized experiment plan with ICE scoring and causal reasoning.

---

### 5.3 Competitive Comparison Matrix

**File:** `.claude/deliverables/competitive-comparison-matrix.md`
**Tier:** 3
**Length:** 800-1500 words

**Purpose:** Structured comparison grid. Print it, pin it to a wall, paste it in a deck.

**Structure:**

```markdown
# Competitive Comparison: [Company Name] vs. Market

## How to Read This Matrix
[2 sentences. Rating system: Strong (claimed + proven), Moderate (claimed, weak proof), Weak (absent or contradicted), N/A (not applicable to this competitor).]

## Comparison Grid

| Dimension | [Company] | [Comp 1] | [Comp 2] | [Comp 3] |
|-----------|-----------|----------|----------|----------|
| **Primary Audience** | ... | ... | ... | ... |
| **Core Positioning** | ... | ... | ... | ... |
| **[Differentiator 1]** | Strong | Weak | Moderate | N/A |
| **[Differentiator 2]** | ... | ... | ... | ... |
| **Proof Strength** | X/5 | X/5 | X/5 | X/5 |
| **Pricing Model** | ... | ... | ... | ... |
| **Review Sentiment** | pos/mixed/neg | ... | ... | ... |

## Key Findings

### Where [Company] Wins
[2-3 items with evidence]

### Where [Company] Loses
[2-3 items with evidence]

### White Space
[2-3 positioning territories no competitor has claimed]

### Claim Overlap (Danger Zone)
[1-2 claims multiple competitors make, diluting differentiation]

## Competitor Snapshots
[3-4 sentences per competitor. Who they are, core pitch, biggest threat.]

---
*Analysis produced by FunnelEnvy | [Date]*
```

**Dimension selection rules:**
- Pull from `competitive-landscape.md` competitive dynamics and claim overlap, not generic categories
- Minimum 4 dimensions, maximum 8
- Always include: Primary Audience, Core Positioning, Proof Strength, Pricing Model
- Add market-specific dimensions from research (e.g., "AI Capabilities", "Enterprise Features", "Integration Depth")

**Rating methodology:**
- **Strong:** Explicitly claimed AND verifiable proof exists
- **Moderate:** Claimed but thin or no independent proof
- **Weak:** Not claimed, or actively contradicted by evidence
- **N/A:** Doesn't apply to this competitor's market segment

**Quality gate:**
- [ ] Every rating traces to data in `competitive-landscape.md`
- [ ] Dimensions are market-specific, not generic
- [ ] Target company is NOT rated Strong on everything (bias check)
- [ ] At least one "Where [Company] Loses" item (credibility check)
- [ ] Grid renders cleanly in markdown (test column alignment)
- [ ] No system internals

---

### 5.4 Battle Cards

**Files:** `.claude/deliverables/battle-cards/[competitor-slug].md` (one per competitor)

**Battle card file naming:** Read `modules/slugify.md` before generating any battle card filenames. Generate slugs using the slugification rules in that module. The canonical input is the `name` field from each competitor entry in `competitive-landscape.md`.

**Module resolution.** `modules/slugify.md` is repository-root-relative: `modules/` lives at the repo root, a sibling of `skills/`, not inside this skill's folder. When running from a symlinked install (e.g., `~/.claude/skills/render-default-deliverables/`), resolve this skill's real path and load `modules/` from the repo root (the parent of `skills/`). If `slugify.md` cannot be read, note it in the run output and apply the documented fallback (lowercase, spaces and non-alphanumerics to single hyphens, trim leading/trailing hyphens) rather than guessing per-file slug formats.

**Tier:** 3
**Length:** 400-700 words per card

**Purpose:** One-page competitor reference. Sales teams and marketers. Read in 60 seconds.

**Structure (per competitor):**

```markdown
# Battle Card: [Competitor Name]

**Last Updated:** [date]
**Threat Level:** High / Medium / Low

## In One Sentence
[What they do and who they serve.]

## Their Positioning
[2-3 sentences. Homepage hero, core claim.]

## What's Actually True
[2-3 sentences. Where their claims hold up. Evidence.]

## Where They're Weak
[2-3 items. Specific, evidence-backed.]

## Where We Win
[2-3 items. Advantages vs. THIS specific competitor, with proof.]

## Where We Lose
[1-2 items. Honest. Prevents walking into traps.]

## Landmines
**Landmines:** What their sales team likely says about us.
- Source: competitive-landscape.md per-competitor profile > "Strategic Signals" or "Specific Tactic" sections.
- If no competitive intelligence about competitor sales tactics exists in context files: write "No competitive sales intelligence available. Gather from sales team debriefs." Do not fabricate likely objections.

## Key Stats

| Metric | Value |
|--------|-------|
| Founded | [year] |
| Funding | [amount/status] |
| Headcount | [estimate] |
| Review Score | [G2/Capterra avg] |
| Pricing | [model + range] |

---
*Source: FunnelEnvy competitive analysis | [Date]*
```

**Data sourcing:** All data from `competitive-landscape.md` competitor profiles and battle card data. Reformat and tighten. Do NOT add new intelligence or make claims beyond what the context file contains.

**Which competitors get cards:** All competitors marked as "Major" in `competitive-landscape.md`. If no sizing data exists, produce cards for all competitors with full profiles (skip table-row-only minor competitors).

**Quality gate per card:**
- [ ] "Where We Lose" section exists and is honest (not "they have a slightly different focus")
- [ ] Every claim sourced from `competitive-landscape.md`
- [ ] "Landmines" section is actionable (specific objection + specific response)
- [ ] 400-700 words (fits on one printed page)
- [ ] Filename matches `modules/slugify.md` rules (e.g., `acme-corp.md`)
- [ ] No system internals

---

## Manifest

**Legacy mode only.** In KB mode the manifest is not written (the KB's own artifact graph and `depends_on` edges are the index, see `KB Mode (Dual-Mode Output)` > `Output Mapping`). After writing all deliverables in legacy mode, produce `.claude/deliverables/manifest.md`:

```markdown
# Deliverables Package

**Generated:** [YYYY-MM-DD]
**Company:** [company name from L0]

## Documents

| Deliverable | File | Context Sources |
|-------------|------|-----------------|
| Executive Summary | executive-summary.md | company-identity, positioning-scorecard |
| Messaging Guide | messaging-guide.md | company-identity, audience-messaging |
| Competitive Matrix | competitive-comparison-matrix.md | company-identity, competitive-landscape |
| Battle Card: [Name] | battle-cards/[slug].md | competitive-landscape |

## Not Produced

| Deliverable | Reason |
|-------------|--------|
| [any skipped] | [reason] |

## Context at Time of Rendering

| File | Confidence | Depth | Last Updated |
|------|-----------|-------|-------------|
| company-identity.md | [N] | [level] | [date] |
| competitive-landscape.md | [N] | [level] | [date] |
| audience-messaging.md | [N] | [level] | [date] |
| positioning-scorecard.md | [N] | [level] | [date] |
```

---

## Completion Output

After all deliverables are written, display:

```
Deliverables written to .claude/deliverables/

  executive-summary.md
  messaging-guide.md
  competitive-comparison-matrix.md
  battle-cards/[competitor-1].md
  battle-cards/[competitor-2].md
  battle-cards/[competitor-3].md
  manifest.md

Skipped (missing context):
  [deliverable] ([reason])

Review the deliverables and let me know if any need adjustment.
```

---

## Quality Rules (Global)

These apply to ALL deliverables, in addition to per-deliverable quality gates:

1. **No system internals.** Never mention: L0, L1, L2, context files, frontmatter, confidence scores, agents, skills, YAML, schemas, depth levels, or any implementation detail. The reader should have no idea these documents were generated by a structured pipeline.

2. **Every claim is traceable.** If you write something in a deliverable, you must be able to point to the specific context file and section it came from. Do not synthesize new conclusions, interpret data in new ways, or add analysis that doesn't exist in the context.

3. **Human tone.** Write like a senior strategist presenting findings to an executive. Conversational but authoritative. No bullet-point dumps. No "in today's competitive landscape" filler. No hedge words ("potentially", "it seems", "perhaps").

4. **Footnotes for uncertainty.** If a finding has caveats (low confidence, limited data), put the caveat in a footnote, not inline. The main text reads cleanly. Footnotes add precision for careful readers.

5. **Consistent branding.** Every deliverable ends with: `*Analysis produced by FunnelEnvy | [Date]*`. Battle cards end with: `*Source: FunnelEnvy competitive analysis | [Date]*`.

6. **No em dashes.** Use commas, periods, or colons instead.

7. **No padding.** If you don't have enough data for a section, make it shorter. A tight 600-word executive summary from limited data is better than an 1100-word one padded with generic observations.

8. **Proof hierarchy is strict.** When citing proof points: Named customer + specific metric = "verified." Named customer + general praise = "supported." Unattributed aggregate claim = "claimed." Never upgrade proof strength beyond what the context file assigns.
