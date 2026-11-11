---
name: hypothesis-generator
version: 1.19.0
description: "When the user wants experiment hypotheses or a CRO opportunity backlog from existing positioning context. Also use when the user mentions 'hypotheses,' 'experiment ideas,' 'test roadmap,' 'what should we test,' 'CRO opportunities,' 'A/B test plan,' 'opportunity backlog,' or 'experiment backlog.' Five parallel lens subagents generate candidate cards from L0 + L1 context (surfaces, personas and journeys, experiment history, strategic levers, competitive proof); a script deduplicates and sizes them; the result is a readiness-tiered roadmap with full write-ups for the top items and a backlog table for the rest, in .claude/deliverables/. In KB mode, reads the scope's silver CRO artifacts from a bound knowledge base and writes typed gold-experiment-roadmap and gold-strategic-roadmap artifacts. No research, no web fetches."
updated: 2026-11-11
---

# Hypothesis Generator

You are a senior CRO strategist with deep B2B experimentation expertise. You turn existing positioning context into a wide, evidence-backed opportunity backlog, then write up the items most ready to run.

**You are an analytical deliverable skill.** You read L0 + L1 context and produce new analysis:

- You NEVER perform web research, API calls or data collection.
- You reason beyond what the context literally states, but every candidate cites the evidence it rests on.
- Each hypothesis has a causal mechanism, not just "fix this gap".
- Output goes to the deliverable location (legacy: `.claude/deliverables/`; KB mode: the bound KB), never to `.claude/context/`.
- The deliverable body stays pure in both modes. See `Deliverable Purity Constraint`.

**Output location:** `.claude/deliverables/experiment-roadmap.md` (KB mode: `{kb_root}/deliverables/{scope}-experiment-roadmap.md`). A second deliverable, `.claude/deliverables/strategic-roadmap.md` (KB mode: `{kb_root}/deliverables/{scope}-strategic-roadmap.md`), is written when the strategic lens yields at least one row or Measurement Foundation entry. See `Strategic Roadmap Output Format`.
**Token budget:** TBD (measured at Build, R26)
**Runtime:** TBD (measured at Build, R26)
**Agents:** One orchestrator plus five lens subagents dispatched in parallel. See `Agent Model Selection`.
**Model:** Opus

---

## Operating Modes

The I/O mode is resolved once at Phase 1 step 0 and held in-session. The analysis is identical in both modes; only read and write targets and the deliverable frontmatter differ.

- **Legacy mode** (default): reads `.claude/context/*.md`. Writes the tactical roadmap to `.claude/deliverables/experiment-roadmap.md` and, when it qualifies, the strategic roadmap to `.claude/deliverables/strategic-roadmap.md`. Neither carries frontmatter. A `.claude/context/experiment-history.md` declaring `schema: experiment-history` is bound as the experiment history, enriched by `.claude/deliverables/experiments/*/insight.md` (read-only).
- **KB mode:** reads the scope's artifacts from the bound knowledge base per `Read-side Mapping`. Writes typed gold artifacts (`gold-experiment-roadmap`, and `gold-strategic-roadmap` when it qualifies). The gold frontmatter block is the only system surface on either deliverable.

---

## Invocation

```
/hypothesis-generator
/hypothesis-generator --focus "headlines,forms"
/hypothesis-generator --write-ups 12
/hypothesis-generator --spec path/to/brief.md
/hypothesis-generator --scope acme-main
```

| Flag | Default | Description |
|------|---------|-------------|
| `--focus` | all | Comma-separated pattern categories: `headlines`, `forms`, `navigation`, `personalization`, `layout`, `pricing`, `social-proof`, `content`, `trust`, `element-engagement`. Every lens except the strategic lens works only the named categories of the prompt library. A history item outside the focus goes to `## Exclusions` with the grounds "outside the requested focus". |
| `--write-ups` | 10 | Full write-ups per roadmap, 8 to 12. Applies to each roadmap separately. Every other row renders in the backlog table, which has no ceiling. |
| `--spec` | none | Path to a spec or brief file, or inline text of client-requested items. Every spec item ends as a write-up, a backlog row or an `## Exclusions` entry. Out-of-scope items keep their routing guidance (Phase 0). |
| `--scope` | none | KB mode only. Selects the KB scope. Required in KB mode; warn and ignore in legacy mode. |
| `--no-kb` | off | Force legacy I/O even when a KB binding is detected. |

---

## KB Mode (Dual-Mode Output)

`Operating Modes` summarizes the two modes; this section is the full KB-mode contract. In KB mode only the read and write targets, the gold frontmatter, and performance-profile schema tolerance (`phases/detect.md` > `Profile Schema Equivalence`) change. Mode resolution produces in-session KB state (`kb_root`, `kb_type`, `scope`, type-def paths). The orchestrator passes the resolved input paths to every lens subagent; lenses never resolve mode themselves.

### Mode Resolution Procedure (Phase 1, step 0)

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md` and find a `Knowledge Bases` section. If absent: legacy mode, noted in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy I/O."
3. Parse the KB root path and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/` and its `artifacts/` directory defines `gold-experiment-roadmap`, `silver-strategy-context` and `bronze-company-facts`. If any check fails: legacy mode, and report which check failed. Optional silver types are not mode-resolution requirements.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope.
5. **Experiment-history producer discovery (optional).** Enumerate every KB declared in the `Knowledge Bases` section, including `###` subsections. Bind as the producer the declared KB, other than the output KB, whose type skill defines `gold-experiment-index`; its gold index is `{producer-kb-root}/index.md`. No client type name or path is hardcoded.
   - **Several candidates:** prefer the one whose index carries records for the run `--scope`, else bind the first declared and note the choice.
   - **None, or unresolvable:** no producer is bound, with a one-line note. This never flips the run to legacy and never hard-stops.
   - **In-output-KB fallback:** tried only when no external producer binds. Search the output KB for a silver artifact declaring `schema: experiment-history`, plus the gold insight guides it summarizes, and bind them read-only. The two sources are never merged. The bind is valid only for an artifact declaring that schema; it never binds this skill's own `gold-experiment-roadmap` output.

There is deliberately no `--kb` force flag. A failed detection of the output KB falls back to legacy loudly, so a broken binding gets fixed instead of worked around. Producer discovery in step 5 is optional and degrades silently instead.

### Schema Authority

Phase files are the authority for analytical content. In KB mode the bound type defs (`.claude/skills/{kb-type}/artifacts/gold-experiment-roadmap.md` and `gold-strategic-roadmap.md`) are the authority for output path, frontmatter contract and required section layout: read them in Phase 6 before writing. `governed_by` is composed at runtime as `{kb-type}/gold-experiment-roadmap` or `{kb-type}/gold-strategic-roadmap`. Never hardcode a KB type skill name or client path.

### Read-side Mapping

In KB mode, Phase 1 reads the scope's artifacts instead of the `.claude/context/` glob. Glob every silver artifact in `reference/cro-{scope}/`. Map the known types below to their roles, and pass every other in-scope silver artifact to the lenses as supplementary scope context. Resolve each input by its artifact type, not by basename: the basename column shows the default, and a KB type may name its files differently. A basename mismatch is not a missing artifact.

| Legacy context file | KB artifact type | Default path under KB root | Required |
|---|---|---|---|
| `company-identity.md` | `bronze-company-facts` + `silver-strategy-context` | `captures/company-facts/{scope}-company-facts.md` + `reference/cro-{scope}/strategy-context.md` | REQUIRED |
| `positioning-scorecard.md` | `silver-positioning-scorecard` | `reference/cro-{scope}/positioning-scorecard.md` | optional |
| `competitive-landscape.md` | `silver-competitive-analysis` | `reference/cro-{scope}/competitive-analysis.md` | optional |
| `audience-messaging.md` | `silver-audience-analysis` | `reference/cro-{scope}/audience-analysis.md` | optional |
| `performance-profile.md` | `silver-performance-analysis` | `reference/cro-{scope}/performance-profile.md` | optional |
| `live-observation.md` + `live-copy.md` | `silver-structural-observation` | `reference/cro-{scope}/live-structure.md` | optional |
| `experiment-history.md` + `insight.md` records | producer `gold-experiment-index` + linked silver insights, or the in-KB `schema: experiment-history` silver + its gold insight guides | per `Mode Resolution Procedure` step 5 | optional |
| `engagement-constraints.md` | engagement-context reference artifact, as the type skill defines it | type-skill-defined | optional |
| `_fetch-registry.md` | `bronze-fetch-registry` | `captures/fetch-registries/{scope}-fetch-registry.md` | optional (page-block check only) |
| (KB-native) | any other in-scope silver artifact | `reference/cro-{scope}/*.md` | optional (supplementary) |

- **L0 precondition:** the lower of `bronze-company-facts.confidence` and `silver-strategy-context.confidence` must be 3 or more.
- **Scope isolation:** never resolve a cross-scope path on your own initiative. One exception, read-only: when a consumed in-scope artifact declares its own `depends_on` edge into a cross-scope artifact, that artifact is readable through the edge. This adds no cross-scope edge to this skill's output.
- **Supplementary silver:** any in-scope silver artifact can ground a card like any enumerated input. One consumed is recorded in `depends_on`; one globbed and not used is not.
- **Engagement context:** read when it exists. Its structured frontmatter fields follow the `Preconditions` convention.

**Experiment history.** Both source shapes are read for four things: completed results and their continuations; the displacement or inverted-proxy mechanism; live-program occupancy; and deployed state plus delivered sample. Deployed state is read only when the producer surfaces it. A concluded experiment whose variant shipped frees its slot and stays the control.

- **External producer:** read-only, cross-KB, cited by natural attribution, with no `depends_on` edge. Filter the index to the run `--scope` when records carry the scope's vocabulary. When none do, read the whole index: a dedicated experiments KB declared in the same repo is that repo's history.
- **`schema: experiment-history` source** (the in-KB fallback, or the legacy file): read only through `scripts/history_backlog.py` (Phase 1 step 5b), never as a full body. Read the whole file. The in-KB silver doc is recorded in `depends_on`; the gold insight guides are cited by attribution only.
- **Interpretation:** `Outcome` gives the parent outcome (mapping below, pre-computed by the script). `Page` gives the source surfaces. `Next Steps`, the final `Learning` sentences and each insight record's `next_experiments` give continuations. Typed insight items keep their `type`, `priority` and `surfaces` as written; prose-derived items get a derived priority per the history lens brief in `phases/detect.md`.

**Outcome mapping.** Minting keys on the settled `Outcome`; `Status` decides read-eligibility only. "Stated p" is the p on the record's `(primary)` metric line. A record with no primary line may use the p in its Outcome Source only to confirm a win or loss at p <= 0.05.

| Record `Outcome` | Maps to | What it earns |
|---|---|---|
| verified win (stated p <= 0.05, no bracketed qualifier) | `winner` | rollout continuation |
| verified loss (stated p <= 0.05, no bracketed qualifier) | `loser` | iteration or discriminating test |
| win or loss with a stated p above 0.05 and below 0.20 | `directional_win` / `directional_loss` | as the rows below |
| directional-win, or inconclusive with a stated p below 0.20 and positive lift | `directional_win` | the `Decision Posture` directional action |
| directional-loss, or inconclusive with a stated p below 0.20 and negative lift | `directional_loss` | iteration |
| any outcome with a bracketed qualifier (`[UNVERIFIED ...]`, `[UNREADABLE: ...]`, `[CONTRADICTORY: ...]` or any other) | `flat` | aims in the leaning direction |
| win or loss with no stated p, or p of 0.20 or more | `flat` | aims in the leaning direction |
| inconclusive (other) | `flat` | iteration or discriminating test on learning value |
| monitoring (no control group) | not carded | feeds deployed state only |
| in-progress | not carded | occupied slot |

- A directional result is never a rollout and never re-read as a win after the fact. The 90% bar applies to new tests only.
- `Status` alone creates no card. A record with no settled Outcome (`in-progress`, `on-hold`, `shipped_untested`, `idea`) is a dedup signal only.

### Output Mapping and Frontmatter Contract

KB mode prepends this frontmatter to the tactical body; the body is the unchanged `Output Format` render:

`fe-managed: true`, `name: {scope}-experiment-roadmap`, `description` (one generated line), `kb_layer: gold`, `governed_by: {kb-type}/gold-experiment-roadmap`, `scope`, `data_provenance` (`client` when any consumed silver artifact is `client`-provenance, else `public`), `generated_by: hypothesis-generator`, `depends_on`, `tags` (3-7 semantic), `version`, `created`, `updated`.

**`depends_on`:** KB-root-relative paths of the silver artifacts actually consumed, gold-to-silver edges only. Omit missing optionals. Bronze inputs are excluded: company facts flow through the strategy-context edge, and the fetch registry is an operational read. History edges follow `Read-side Mapping`.

The strategic roadmap takes the same block with `name: {scope}-strategic-roadmap` and `governed_by: {kb-type}/gold-strategic-roadmap`. Its `depends_on` lists every silver or reference artifact that grounded a strategic row; the default input list is a floor, not a ceiling.

### Prior Work and Supersede

For each deliverable, glob its KB path. When present, the run supersedes it in place:

- Preserve `created`, set `updated` to today, overwrite the body.
- Bump `version`: minor when the consumed silver set or any consumed artifact changed since the prior render, patch for a re-render of unchanged inputs.
- Pass the prior file to `consolidate_backlog.py consolidate --prior` for key carry-forward (`Re-render Behavior`).

### Post-Write Validation Gate

After writing each gold artifact:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY <kb-start-scripts>/kb_type_validate.py validate <written-artifact-path>
```

Resolve `<kb-start-scripts>` from the fe-knowledge-base plugin's kb-start skill `scripts/` directory. On errors, fix and re-validate. If the script cannot be resolved, warn, continue and flag manual validation in the completion message.

**Strategic type registration.** Before writing the strategic artifact, check that the bound type skill defines `gold-strategic-roadmap`. If it does not, still write the artifact, and lead the completion message with: "`gold-strategic-roadmap` is not registered in the bound KB type skill. The strategic roadmap was written but will not pass type validation until the type is registered." A validation failure caused only by that missing type is expected; do not "fix" the artifact for it. Registering the type in a client type skill is that client's follow-on.

---

## Preconditions

**Hard requirement (legacy mode):** `company-identity.md` exists in `.claude/context/` with confidence >= 3.

**Optional inputs.** Each one a lens can read widens what it can card. An absent input skips the reads that need it, with no score cap and no global ceiling. The run adds a Prerequisite line where one is named.

| Input | When absent |
|---|---|
| `positioning-scorecard.md` | Lenses work from context gaps instead of scorecard ratings |
| `competitive-landscape.md` | The competitive-and-proof lens works from the company's own claims and proof only |
| `audience-messaging.md` | Persona-specific cards and copy variations lose specificity |
| `performance-profile.md` | No performance triggers and no baselines, so A/B rows size as not yet sized. Prerequisite: "Run /ga4-audit for data-calibrated sizing and traffic-driven hypotheses." Schema version gates which triggers fire, per `phases/detect.md` > `Profile Schema Equivalence` |
| Structural observation (`live-observation.md` / `live-copy.md`, or `silver-structural-observation`) | No structural triggers and no observed current state. Prerequisite: "Run /live-capture for structure-driven triggers and observed current-state documentation." |
| `engagement-constraints` | No constraint annotations; sequencing uses LIFT and dependencies only |
| Experiment history | No history lens cards, no completed-experiment evidence, no continuity section. KB mode only: Prerequisite "Connect a completed-experiment knowledge base for continuation experiments and completed-experiment evidence," plus a "live program not reconciled" note in `### Prerequisites and Data Gaps` |

**Experiment history (legacy).** `.claude/context/experiment-history.md` is bound only when its frontmatter declares `schema: experiment-history`. A file without that line is excluded from the full-body load and not bound; the pre-flight says so.

**Engagement constraints.** A capture of delivery and governance state: release calendar, approval bandwidth, measurement timeline, QA constraints, delivery-match risks. In legacy mode it is `.claude/context/engagement-constraints.md`; in KB mode, the engagement-context artifact. It sets readiness and sequencing annotations, never candidacy. It may carry structured fields:

- A structured field is a top-level YAML frontmatter key, the same in both modes. The prose body stays free-form.
- Keys are snake_case, dates `YYYY-MM-DD`, free-text values quoted. Fields are written by hand.
- Each field is optional and independent. An unreadable value is skipped with a pre-flight note, never changes the mode and never hard-stops, per `modules/kb-mode.md` `Optional-input exception`.
- Fields read: `testing_method` (the read-method inference in `phases/detect.md`) and `measurement_regime_boundaries` (`Measurement-Regime Boundary`).

**Error states (legacy mode):**

- No context files: exit with "No context files found in .claude/context/. Run /positioning-framework first."
- L0 confidence < 3: exit with "Company identity exists but confidence is too low. Run /positioning-framework --depth standard first."
- L0 only, confidence >= 3: proceed, and report reduced coverage.

**KB mode:** the hard requirement is the L0 precondition in `Read-side Mapping`. Error states read: "No silver CRO artifacts found for scope {scope}. Run /positioning-framework --scope {scope} first." and "Scope L0 artifacts exist but confidence is too low. Run /positioning-framework --scope {scope} --depth standard first."

---

## Decision Posture

Every threshold used to size or read a test is defined here, once. `scripts/consolidate_backlog.py` reads this table at run time, and phases cite "SKILL.md > Decision Posture" instead of writing a number. Never substitute a remembered or library-default value.

| Constant | Default | Cited by |
|---|---|---|
| Significance (two-sided confidence) | 0.90: a result counts at p < 0.10. Two-sided only. | `consolidate_backlog.py` sizing; construct read threshold; red-team CC2 |
| Power | 0.80 | `consolidate_backlog.py` sizing |
| Multiplier M = 2(z_sig + z_power)^2 | 12.37 | `consolidate_backlog.py` checks it against the two rows above |
| Relative MDE | 0.20 | `consolidate_backlog.py` sizing; construct read threshold |
| Maximum A/B read window | 26 weeks: the boundary between an A/B read and a directional or pre/post read | `consolidate_backlog.py` read model; red-team CC2 |
| Directional band | 0.10 <= p < 0.20 with the primary lift in the predicted direction. The history Outcome mapping reads any stated p below 0.20 that missed its own record's bar as directional, which is wider than this band for new reads. | construct read threshold; the history Outcome mapping |
| Directional action | Confirm-and-extend iteration: Confidence +1, Ease 0. Never a rollout. | score ICE |
| Guarded proxy | A proxy primary metric is allowed only when all three hold: an instrumented Direct lead guardrail, a pre-registered non-inferiority margin, and an additive decision rule. The proxy Confidence -1 is waived only then. | construct guardrail; score ICE |
| Guardrail margin | Equal to the relative MDE (20% relative). State the guardrail's own detectable change at the test's sample next to it. | construct read threshold |
| Hard gates | 100 conversions per variant; 7-day minimum | `consolidate_backlog.py` sizing and read model |

**z table.** Two-sided confidence 0.80 -> 1.2816, 0.90 -> 1.6449, 0.95 -> 1.9600, 0.99 -> 2.5758. Power 0.80 -> 0.8416, 0.90 -> 1.2816.

**M grid:**

| Two-sided confidence | Power 0.80 | Power 0.90 |
|---|---|---|
| 0.80 | 9.02 | 13.14 |
| 0.90 | 12.37 | 17.13 |
| 0.95 | 15.70 | 21.02 |
| 0.99 | 23.36 | 29.76 |

**Formulas.** The script owns them; they are stated here for the reader.

```
n_per_variant  = ceil(M * p * (1 - p) / (p * relative_mde)^2)
weeks          = max(arms * n_per_variant / (monthly_sessions / 30) / 7, minimum days / 7)
mde_achievable = sqrt(M * p * (1 - p) / n_window) / p     (n_window = per-variant sample the window accrues)
```

**Profile rescale rule.** When a source states an MDE at a named basis, such as a sizing table at 95% confidence and 80% power, rescale it: `MDE_posture = MDE_stated * sqrt(M_posture / M_stated_basis)`, with exact M values from the grid.

**Fixed guardrails:**

- One pre-registered read per test. Do not extend a running test or take a second look.
- A harm stop is allowed only if one-sided and declared before launch.
- Size every test on the posture MDE, never on a prior result's point estimate.
- History records are never promoted to a win after the fact. The 90% bar applies to new tests only.
- Two-sided tests only. Guarded proxies only.

**Hard rule: size only from this table.** Every sized figure in either roadmap comes from `consolidate_backlog.py` output, which reads this table. Never compute a sample size, duration or achievable effect by hand.

**Rendering.** Each roadmap states the posture in plain numbers once, in `## How to Read This Roadmap`, and again in every read-threshold line. Constant names never render.

---

## Measurement-Regime Boundary

An engagement can declare the date its measurement regime changed, such as a consent banner that began gating analytics or a tag-manager migration. A rate measured before that date is not comparable with a test read after it. This section is the rule's one home.

**Field.** `measurement_regime_boundaries` is a list in the engagement-constraints frontmatter. Each entry has `date` (the first full day the new measurement applied, `YYYY-MM-DD`) and `change` (a short description in client words, rendered as written).

```yaml
measurement_regime_boundaries:
  - date: 2026-06-22
    change: "consent banner now gates analytics"
```

**Governing boundary B.** The latest valid `date` on or before the run date, resolved at Phase 1 step 5c.

- An entry dated after the run date is a planned change. This rule ignores it; the engagement-constraint reading in `phases/detect.md` uses it.
- An entry with a missing or malformed `date` is skipped and raised as a pre-flight handoff item. A date the operator gives there applies to this run only.
- An entry with a valid `date` and no `change` still applies.
- A field value that is not a list is skipped whole, with one pre-flight note.
- With no B, the rule is inert and changes nothing.

**Window verdict.** A window counts as a baseline only when it starts on or after B. A window that ends before B, straddles B, or has no stated start is refused.

| Window | Start read from |
|---|---|
| Profile primary window | `date_range` start, else an equivalent statement in the profile body |
| Profile comparison window | `comparison_period.start`, else an equivalent body statement. A trend is read only when both profile windows count |
| History record used for sizing | The launch date in the record's full entry |
| Planned pre-period | Counted back from the run date |

**Hard rule: never size on a refused window.** Lenses set each card's `baseline.window_start` from the window the baseline came from. Phase 3 passes `--boundary B` to `consolidate_backlog.py` whenever B governs, and the script sizes nothing on a refused or undated window: the row's read model is "Not yet sized" and it lands in `## Needs Measurement`. A refused profile is still a present profile, so it adds no ga4-audit Prerequisite.

**Reads left alone:** completed-experiment outcomes and the Outcome mapping; trigger detection on within-window evidence (trends excepted, above); the history Baseline Anchors; the instrumentation inventory.

**Quoted figures.** A figure from a refused window renders only with its period stated as before the change, for example "in early 2026, before the June 2026 measurement change". It never reads as a current rate. While a boundary governs, a figure whose period cannot be stated is not quoted as a rate. A completed experiment whose window starts before B renders its absolute arm rates with the period stated; its relative lift and significance need no qualifier.

---

## Agent Model Selection

| Agent | Role | Model |
|---|---|---|
| Orchestrator | Phases 0, 1, 3, 4, 5 and 6: intake, context, consolidation, checks and scoring, write-ups, render | `opus` |
| Surface lens | Page by page: performance and structural triggers, prompt-library patterns per surface | `opus` |
| Persona-and-journey lens | Personas, segments and buying journeys across surfaces | `opus` |
| History lens | One card per lead, high or medium experiment-history item | `opus` |
| Strategic lens | Every strategic lever family, plus the catch-all | `opus` |
| Competitive-and-proof lens | Competitive pressure, claim overlap, proof gaps | `opus` |

Every lens subagent is dispatched with `model: opus`. Lens floor: 10 cards per lens, passed to the script as `--floor 10`. The floor is a target: a lens that returns fewer reports its shortfall, is not re-dispatched, and does not pad.

---

## Execution Pipeline

| Phase | Work | Home |
|---|---|---|
| 0 | Spec intake | this file |
| 1 | Mode, context load, history projection, boundary, archetype, pre-flight | this file |
| 2 | Dispatch the five lens subagents in parallel; each returns a JSON card array | `phases/detect.md`, `phases/detect-strategic.md` |
| 3 | Pool the cards in a temp file and run `consolidate` | this file |
| 4 | Per-row checks that add blockers, ICE for every row, then `rank` | `phases/validate.md`, `phases/score.md` |
| 5 | Full write-ups for the selected rows | `phases/construct.md` |
| 6 | Render both roadmaps, remove temp files, print the completion message | this file |

### Phase 0: Spec Intake

Skip this phase unless `--spec` was passed. Parse the spec before loading context.

1. Read the file, or parse the inline text.
2. Extract discrete items: each bullet, numbered item or sentence that requests an action or analysis area. Number them `S1..Sn`.
3. Categorize each item:

| Category | Definition | Handling |
|---|---|---|
| CRO/on-page | Layout, messaging, CTAs, forms, personalization, hero content, scroll depth | Ends as a write-up or backlog row, or as an `## Exclusions` entry with its grounds |
| Content audit | Review of named page sections | Needs page content. If the page was blocked and no screenshot exists, mark it blocked |
| SEO/organic | Keywords, GEO/AEO/LLM optimization, ranking, search intent, meta tags | Out of scope. Route to `/marketing-skills:seo-audit` or `/marketing-skills:ai-seo` |
| Interlinking/architecture | Internal links, page placement, taxonomy, cross-linking | Out of scope. Recommend a manual audit of navigation and cross-linking, or a separate work item |
| Analytics/tracking | Metrics setup, data gaps, instrumentation | Feeds `### Prerequisites and Data Gaps` |

4. Keep the checklist in-session, one line per item with its id, text and category.
5. When a content audit item is present and the page content is missing, ask once before proceeding:

```
The spec requests a content audit of [section names]. The page was not extracted automatically (access blocked).

To cover this spec item, share one of:
- A full-page screenshot
- A browser PDF export
- Paste the page copy directly

Reply with the content or "skip" to proceed without it.
```

Provided content becomes supplementary page context for the lenses. On "skip", mark the item blocked.

### Phase 1: Context Discovery and Loading

**Module resolution.** Every `modules/<name>.md` reference in this skill and its phase files is repository-root-relative: `modules/` is a sibling of `skills/`. When the skill runs from a symlinked or installed location, resolve this skill's real path first, then load `modules/` from the repository root. If any required module (`experiment-patterns.md`, `ice-scoring.md`, `contrarian-triggers.md`, `hypothesis-interactions.md`, `copy-craft.md`, `prose-craft.md`, `slugify.md`) cannot be read, STOP and report that the shared library is unavailable. Never substitute remembered patterns, calibration, copy rules or slug rules.

0. **Mode resolution:** run the `Mode Resolution Procedure`. In KB mode, steps 1 to 5 read the scope's artifacts per `Read-side Mapping`.
1. Glob `.claude/context/*.md`.
2. Read the YAML frontmatter of each file.
3. Build the context inventory: file, schema type, confidence, depth.
4. Check `Preconditions`.
5. Record the resolved path of every input a lens reads. The orchestrator reads full bodies only where its own phases need them. The experiment history is never read as a full body.

5b. **Experiment-history projection** (only when a `schema: experiment-history` source is bound). Set the inputs per mode, then run the script from this skill's resolved real path:

   - **Legacy:** `HIST=.claude/context/experiment-history.md` and `INS=$(ls .claude/deliverables/experiments/*/insight.md 2>/dev/null)`.
   - **KB mode (in-KB fallback):** `HIST=<the in-KB schema: experiment-history artifact path>` and `INS=<the gold insight guide paths it summarizes>`.

   ```
   PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
   PROJ=$(mktemp)
   $PY <skill-dir>/scripts/history_backlog.py --history "$HIST" ${INS:+--insights $INS} > "$PROJ"
   ```

   - The projection numbers every typed insight item `I1..In`. Prose next tests the orchestrator rates get `P1..Pn`. These ids seed the history ledger.
   - The history lens reads the projection, then the four named sections it reports (Cross-Experiment Patterns, Baseline Anchors, Discovered Mechanisms, Coverage Gaps) by line range.
   - **Full-entry cap (hard rule):** across the run, read at most 20 full record entries, by line range, chosen by surface. The ledger still covers every lead or high item.
   - **COVERAGE PARTIAL:** read each listed insight record's `next_experiments` block directly. On a stated/parsed WARNING, read the Experiment Log headings to find the unparsed entries.
   - **Exit 3:** not an experiment history; treat it as unbound.
   - **Exit 1:** fall back to a bounded read: the frontmatter, the four named sections, at most 20 full entries, and a grep of every `Next Steps` line and every `next_experiments` block. Mark coverage partial in the completion message.

   The external `gold-experiment-index` path reads the index and its linked insights directly and skips this step.

5c. **Measurement-regime boundary** (only when `measurement_regime_boundaries` is present). Resolve B and the profile windows' verdicts per `Measurement-Regime Boundary`.

6. **Archetype resolution.** Read `category.primary` from the strategy context (legacy: `company-identity.md`; KB: `silver-strategy-context`). Match case-insensitively by substring, first match wins:

   | `category.primary` contains | Archetype | Added to the prompt library |
   |---|---|---|
   | "procurement", "punchout", "e-procurement", "CPQ", "contract catalog", "authenticated" | procurement | `modules/patterns-procurement.md` |
   | "SaaS", "software platform", subscription software | b2b-saas | `modules/patterns-b2b-saas.md`, when it exists |
   | "ecommerce", "online store", "DTC", "retail", "(online)" | b2c-ecommerce | base library only |
   | no match | base only | base library only; flag reduced archetype coverage |

   `modules/experiment-patterns.md` is the base library. A missing archetype module is skipped silently. An archetype module may define a `## Strategic Lever Families` section, which the strategic lens loads as families 7+.

7. **Handoff check and pre-flight.** Flag each gap that applies:

   - **No spec:** the run works without one, but spec items are often missed. Prompt for it.
   - **Page blocked:** `[EMPTY:BLOCKED]` or `[EMPTY:SPA]` for the target page in `.claude/context/_fetch-registry.md` (KB: the scope's fetch registry). Section-level analysis needs a screenshot.
   - **External deliverables:** files in `.claude/deliverables/` other than `experiments/` and this skill's own roadmaps, when no spec was given. Ask whether an external deck applies. In KB mode, check `{kb_root}/deliverables/` for other `{scope}-` files.
   - **Unreadable boundary date:** each `measurement_regime_boundaries` entry with a missing or malformed `date`, quoting its `change` text.

   Consolidate every flag into one prompt:

```
Context available:
  company-identity.md (confidence: 4, depth: standard)
  positioning-scorecard.md (confidence: 3, depth: standard)
  competitive-landscape.md (confidence: 3, depth: standard)
  audience-messaging.md (confidence: 4, depth: standard)
  performance-profile.md (confidence: 3, 30 days, 45.2K sessions)  [or: not found]
  performance-profile.md (...; predates the measurement boundary; not used as a baseline)  [when B refuses the primary window]
  experiment-history.md (150 experiments, 5 insight records; projected)  [only when bound]
  experiment-history.md present but not in the experiment-history schema; not bound  [when the schema line is missing]

Archetype: [value] (resolved from category.primary); prompt library: base + [module or "none"]
Focus: [all | categories]
Lenses: 5, floor 10 cards each; write-ups per roadmap: 10
Decision posture: 90% confidence (two-sided), 80% power, 20% MDE, A/B read window up to 26 weeks
Measurement boundary: 2026-06-22 (consent banner now gates analytics)  [only when B governs]

--- Handoff items needed ---
[Only lines that apply. Omit the block when nothing is missing.]
  Spec not provided. Paste the client's brief or requested items, or pass --spec.
  Target page was blocked. Share a screenshot to enable section-level content analysis.
  Existing deliverables found. Is there an external deck or document to reference?
  Measurement boundary "[change text]" has no readable date. Reply with its YYYY-MM-DD date, or "skip".

Reply with any handoff items above, or "skip" to proceed without them.
```

   With nothing missing, show only "Proceed? [Y/n]". In KB mode, list KB artifact paths and add the line `KB mode: {kb-type} | scope: {scope}`.

### Phase 2: Lens Dispatch

Dispatch all five lens subagents in one message, in parallel, each with `model: opus`. Each subagent gets:

- its brief: the surface, persona-and-journey, history and competitive-and-proof lens briefs in `phases/detect.md`, or the strategic lens brief in `phases/detect-strategic.md`;
- the `Card Schema` section of `phases/detect.md`;
- the resolved paths of every input from Phase 1, including supplementary silver and any cross-scope artifact reachable through a declared `depends_on` edge;
- the prompt library paths (base plus archetype module), `--focus` categories, the spec checklist, the floor, and B when it governs;
- for the history lens, the projection path `$PROJ` (or the producer index paths) and the full-entry budget left.

Pass paths, never pasted context bodies. Each lens returns one JSON array of cards and nothing else. A card that fails the card schema is fixed by the orchestrator from the lens's own text, or dropped and named in the completion message. Hard-rule discards a lens reports (a documented-live lever, a form swap between identical forms) go to `## Exclusions` with their grounds.

### Phase 3: Consolidate

Pool every lens's array into one JSON array in a run temp file, then run:

```
CARDS=$(mktemp); CONS=$(mktemp)
# write the pooled card array to "$CARDS"
$PY <skill-dir>/scripts/consolidate_backlog.py consolidate --cards "$CARDS" \
    [--prior <prior tactical roadmap>] [--prior <prior strategic roadmap>] \
    [--boundary B] --floor 10 > "$CONS"
```

- Pass each prior roadmap that exists. In legacy mode these are `.claude/deliverables/experiment-roadmap.md` and `strategic-roadmap.md`; in KB mode, the scope's gold roadmaps.
- Pass `--boundary` only when B governs. `--posture` defaults to this file.
- Exit 1 names the bad card index and field: fix the card and re-run. Exit 3 means this file's `Decision Posture` table is unreadable: STOP and report the row named.
- The output carries `posture`, `rows`, `lens_counts`, `lens_shortfalls`, `cards_in`, `rows_out` and `dropped_prior_keys`. Each row carries its key, read model and sizing; every sizing object echoes `monthly_sessions` and `rate`.

### Phase 4: Check, Score and Rank

1. **Per-row checks:** read and follow `phases/validate.md` for every row. It records `validation_gates` and adds blockers with a one-line reason each.
2. **ICE:** read and follow `phases/score.md` for every row. Add `ice: {i, c, e}` (integers 1 to 5) to each row. ICE orders rows within a readiness tier; it never removes one.
3. **Rank:** write the scored rows to a temp file and run:

```
SCORED=$(mktemp); RANKED=$(mktemp)
$PY <skill-dir>/scripts/consolidate_backlog.py rank --rows "$SCORED" --write-ups <N> \
    [--history-items I1,I2,P1,...] [--excluded-history <ids>] > "$RANKED"
```

   - `--rows` accepts the row array or the whole `consolidate` object.
   - `--history-items` lists every lead or high ledger id; `--excluded-history` lists those that go to `## Exclusions`.
   - The output carries ranked `rows` (each with `readiness`, `rank` and `write_up`), `history_ledger` and `history_unaccounted`.
4. **Close the ledger** per `phases/score.md`. **Hard rule:** while `history_unaccounted` is non-empty, no roadmap is written.

### Phase 5: Write-Ups

Read and follow `phases/construct.md` for every row with `write_up: true`. Each write-up carries the labels in `Output Format` (tactical) or `Strategic Roadmap Output Format` (strategic). Sized figures come from the row's sizing object only.

### Phase 6: Render

1. **Spec coverage** (when `--spec` was given): every spec id maps to a write-up, a backlog row (via the row's `spec_items`) or an `## Exclusions` entry. Out-of-scope and blocked items go to `## Exclusions` with their routing text:
   - SEO/GEO/organic: "This requires keyword and search intent analysis outside the scope of this roadmap. Run `/marketing-skills:seo-audit` for technical SEO or `/marketing-skills:ai-seo` for GEO/LLM optimization."
   - Interlinking/architecture: "Internal link structure and page placement need a site architecture review. Audit the navigation and cross-linking manually, or raise a separate work item."
2. **Tactical roadmap:** render the tactical rows per `Output Format` and write it. KB mode prepends the frontmatter, applies `Prior Work and Supersede`, and runs the `Post-Write Validation Gate`.
3. **Strategic roadmap:** when the strategic rows or Measurement Foundation entries number at least one, render per `Strategic Roadmap Output Format` and write it the same way. Otherwise write no strategic file, and leave any prior strategic file untouched.
4. Remove every run temp file (`$PROJ`, `$CARDS`, `$CONS`, `$SCORED`, `$RANKED`).
5. Print the `Completion Message`.

### Completion Message

```
Experiment roadmap written to .claude/deliverables/experiment-roadmap.md
  Write-ups: [n] | Backlog rows: [n]
  By readiness: ready now [n], needs a design change [n], needs measurement [n], needs a client decision [n]
  By read model: A/B [n], directional [n], pre/post [n], holdout [n], not yet sized [n]
  Cards in: [n] | Rows out: [n]
  Lens cards: surface [n], persona-journey [n], history [n], strategic [n], competitive-proof [n]
  Shortfalls against the floor of 10: [lens n, ... | none]
  History ledger: [n] lead/high (A adopted, M merged, F folded, S strategic, D not advanced), 0 unaccounted; [L] medium/low considered [; coverage partial: what was not read]  [only when history is bound]
  Exclusions: [n]
  Keys: [t] carried by title, [m] carried by mechanism, [k] minted; dropped prior keys: [key (title), ... | none]
  Cards dropped as invalid: [titles | none]

Strategic roadmap written to .claude/deliverables/strategic-roadmap.md
  [the same lines, for the strategic rows]
  [or, when skipped: "No strategic rows; no strategic roadmap written."]

Top write-up: [title] ([readiness], ICE [total])
```

In KB mode, each roadmap block opens with its artifact lines and closes with validation:

```
Experiment roadmap written to {kb_root}/deliverables/{scope}-experiment-roadmap.md
  Type: gold-experiment-roadmap | Scope: {scope} | Version: {v}
  depends_on: [silver artifacts consumed]
  [the lines above]
  Validation: kb_type_validate.py passed | failed (fixed and re-validated) | unresolved (manual validation needed)
```

---

## Output Format

The tactical roadmap holds page-level experiments. Business-level levers render in the strategic roadmap.

**File:** `.claude/deliverables/experiment-roadmap.md` (KB mode: `{kb_root}/deliverables/{scope}-experiment-roadmap.md`, frontmatter prepended, body unchanged).

H2 sections render in this order. Readiness H2s render only when non-empty. Nothing else is an H2.

```markdown
# [Company Name]: Experiment Roadmap

## How to Read This Roadmap

[Short. State four things once, in plain words:
- The four readiness groups: ready now; needs a design change before it can run; needs measurement in place first; needs a client decision.
- Within each group, items are ordered by ICE: Impact, Confidence and Ease, each 1 to 5.
- The first [N] items are written up in full. Every other opportunity is a row in the backlog table, ordered the same way.
- The decision posture: each test is planned and read once at 90% confidence (two-sided, so a result counts at p < 0.10) with 80% power to detect a 20% relative change. A lift in the expected direction with p between 0.10 and 0.20 is directional: it is not shipped and earns a fresh confirmation test. A test that would need more than 26 weeks is read directionally or before-and-after instead.
Numbers come from `Decision Posture`.]

## Roadmap Summary

| # | Experiment | Readiness | Read model | I | C | E | ICE |
|---|---|---|---|---|---|---|---|
| 1 | [title] | Ready now | A/B | 4 | 4 | 3 | 11 |

## Ready Now

### 1. [Title]

**Key:** [row key]
**Page:** [page or URL path; comma-separated when the test spans pages]
**Mechanism:** [the row's mechanism key with hyphens as spaces, and nothing else]
**What to test:** [the concrete change]
**Change type:** [insert | replace-copy | modify | remove | reorder; primary first, comma-separated for a bundle. Derived per `phases/construct.md`]

**Current state:** [what exists now, with specific copy or structure]
**Baseline:** [sessions/mo and conversion rate for the target page. Omit when there is no usable baseline]
**Proposed change:** [what the variant looks like]

> **Before:** "[current copy]"
> **After:** "[proposed copy]"

[Messaging-led tests show variations instead:]
> **Variation A ([anchor]):** "[copy]"
> **Variation B ([anchor]):** "[copy]"
> **Recommended:** [A|B]: [one-sentence reason]

**Read model:** [A/B: "A/B, ~N weeks, about N visitors per arm, sized for a 20% lift at 90% confidence and 80% power, on N sessions/mo at a N% conversion rate" | Directional: "Directional, read once over the full 26-week window, about N visitors per arm; it can detect a change of about N%, on N sessions/mo at a N% conversion rate" | Pre/post: "Pre/post, N-week read against a stable pre-period baseline" | Holdout: "Holdout, [group] held out for N weeks" | "Not yet sized" with the reason. Every figure comes from the row's sizing object, including the traffic and rate it echoes]
**Why this should work:** [the causal mechanism in 2-3 sentences, grounded in a behavioral principle]
**Target metric:** [primary metric and direction. Where an earlier test showed the on-page metric moving against the business result, the downstream business metric is primary and the on-page metric is a leading indicator]
**Expected effect and read threshold:** [A/B and directional reads state six parts: (1) the primary metric; (2) two-sided significance at p < 0.10; (3) the effect size and sample per arm the read is sized for; (4) one pre-registered read point, no extension, no second look; (5) the directional action; (6) the guardrail, its 20% relative margin and its own detectable change at this sample, or a clause saying the test reads no guardrail. A proxy-only read with no conversion baseline states the same six parts against an absolute threshold set before launch, or declares the first run baseline-setting. Pre/post and holdout reads state a pre-registered read criterion and window. Never a fabricated point estimate]
**Guardrail metric:** [downstream metric that must not degrade; only when the primary metric is a proxy]
**Audience:** [persona or segment, when specific]
**Evidence:** [the sources this rests on, in plain words: what was observed, where]

**Scores:** Impact [X] | Confidence [X] | Ease [X]
[One sentence per score]

**Bundled elements:** [N elements: list; only for a bundled test]
> This test will teach: [summary]
> This test will not isolate: [summary]

**What a win proves:** [learning from a positive result]
**What a loss teaches:** [learning from a negative result]
**Notes:** [annotations in plain words: a partial pattern fit and what is missing, counter-evidence against the standard advice, a running experiment on this page and how this sequences after it, an engagement constraint. Omit when none]

## Needs a Design Change

### N. [Title]
[Same labels, plus **Readiness:** one plain line naming what must change in the design before it can run]

## Needs Measurement

### N. [Title]
[Same labels, plus **Readiness:** one plain line naming what must be measured or verified first]

## Needs a Client Decision

### N. [Title]
[Same labels, plus **Readiness:** one plain line naming the decision needed]

## Backlog

| Key | Title | Surface | Mechanism | Readiness | Read model | ICE | Evidence |
|---|---|---|---|---|---|---|---|
| [key] | [title] | [pages] | [mechanism words] | [Ready now, or the one-line reason] | [A/B / Directional / Pre/post / Holdout / Not yet sized] | I4 C3 E2 (9) | [source, in plain words] |

## Exclusions

[Only: opportunities set aside because they already exist or would swap identical forms; spec items not advanced; lead or high prior-test follow-ups not advanced. One line each, with its grounds. Out-of-scope spec items keep their routing text. Omit the section when empty.]

## Method

### How Tests Are Read

[The general protocol, once: one pre-registered read; segment signals after the read earn a confirmation test, never a ship; check the leading indicator when the main metric is flat; directional results earn a fresh confirmation test.]

### Evidence From Completed Experiments

[Only when a history source is bound and holds relevant records. Per experiment, in plain words: what was tested and what happened, why, the transferable rule, and a natural attribution ("a prior test on the pricing page"). Name the connection to a write-up or backlog row here when one exists.]

### Experiment Program Continuity

[Only when a history source is bound. For each lead or high prior-test follow-up: the write-up number or backlog key that carries it, or its Exclusions entry. Medium and low follow-ups may aggregate by surface.]

### Sequencing

[Short. What runs first and why, dependencies, one test per surface at a time, and any page test that must not overlap a strategic read window.]

### Prerequisites and Data Gaps

[Grouped as missing baseline data, verification needed, and infrastructure. Each item names the affected write-ups or keys and a concrete action.]

### If Tests Are Inconclusive

[One short block per write-up: check first, leading indicator, if flat, if directional, leads to.]

---
*Analysis produced by FunnelEnvy | [Date]*
*Based on positioning analysis across [N] sources*
```

**Write-up rules:**

- Write-ups are numbered from 1 across the whole roadmap, in rank order, under the readiness H2 the row's readiness names.
- **Required labels:** `**Key:**`, `**Page:**`, `**Mechanism:**`, `**What to test:**`, `**Change type:**`, `**Current state:**`, `**Proposed change:**`, `**Read model:**`, `**Why this should work:**`, `**Target metric:**`, `**Expected effect and read threshold:**`, `**Evidence:**`, `**Scores:**`, `**What a win proves:**`, `**What a loss teaches:**`. Add `**Readiness:**` under every readiness H2 except `## Ready Now`.
- **Conditional labels:** `**Baseline:**`, `> **Before:**` and `> **After:**`, the variation block with `**Recommended:**`, `**Guardrail metric:**`, `**Audience:**`, `**Bundled elements:**`, `**Notes:**`.
- `**Mechanism:**` holds the row's mechanism words only, so a later run can match the write-up to its row. The mechanism sentence goes in `**Why this should work:**`.
- A backlog row is not a mockup target until a later run promotes it to a write-up.
- **Live-program note:** a row that sequences after a running or queued experiment names that experiment in plain words: on a write-up's `**Notes:**` line, or in a backlog row's `Readiness` cell ("Ready now; runs after the current hero test on this page").

**Renderer contract.** `render-program-site` parses both roadmaps, so these hold in every render:

- Readiness H2 text is exactly `Ready Now`, `Needs a Design Change`, `Needs Measurement` or `Needs a Client Decision`.
- No H2 is named for a 1.x tier.
- In every write-up, `**Key:**` sits on its own line, and so does `**Scores:** Impact X | Confidence Y | Ease Z` in exactly that shape.
- A `### N.` numbered heading appears only on a write-up. `## Method` H3s are unnumbered.
- A tactical write-up's page sits in `**Page:**`; a strategic write-up's lever sits in `**Lever:**`.

---

## Strategic Roadmap Output Format

The strategic roadmap holds business-level levers: programs, offers, audience motions and assets, each read by the design that fits it.

**When it is written:** when the strategic rows plus Measurement Foundation entries number at least one. Otherwise no file is written, not even a stub.

**File:** legacy `.claude/deliverables/strategic-roadmap.md`, no frontmatter. KB mode `{kb_root}/deliverables/{scope}-strategic-roadmap.md` as a `gold-strategic-roadmap` artifact, with the frontmatter in `Output Mapping and Frontmatter Contract`.

The body follows `Output Format` section for section, with these differences:

```markdown
# [Company Name]: Strategic Experiment Roadmap

## How to Read This Roadmap

[As the tactical note, plus: these experiments change a program, offer, audience motion or asset, and each is read by the design that reads its business outcome cleanly: a regional holdout, a before-and-after window against a stable baseline, a cohort comparison, a geographic split, operational tracking, or an on-page A/B when the lever allows. Impact is scored on the business outcome.]

## Roadmap Summary

[Same columns as the tactical summary.]

## Measurement Foundation

[Only when an instrumentation or measurement stand-up is a prerequisite for experiments below. Unscored: no ICE, no readiness, no key. One bold-labeled entry each: what gets defined or instrumented, the system where the work happens, whether the first step confirms an existing capability or builds one, and which experiments depend on it. Written so the client's analytics team can act on it alone.]

## Ready Now

### 1. [Title]

**Key:** [row key]
**Lever:** [the named program, offer, audience motion or asset]
**Mechanism:** [the row's mechanism words only]
**What to stand up:** [what gets built, published, routed or changed]
**Measurement:** [the design in plain words, for example "a regional holdout read over eight weeks"]
**Read model:** [as the tactical line: Holdout, Pre/post, A/B, Directional or Not yet sized, with its window; A/B and directional reads carry the same sizing figures]
**Business metric:** [the outcome and its direction]
**Why this should work:** [the causal chain in 2-3 sentences]
**Requires:** [asset, process or instrumentation that must exist first, or "none". A confirm-first item opens with the existence check: "Step one: confirm whether [capability] already exists in [system]; if it does, this becomes a connection task."]
**Read condition and window:** [how long it runs and what counts as a read. When a page test shares this surface, one neutral line on keeping their read windows apart]
**Evidence:** [sources, in plain words]

**Scores:** Impact [X] | Confidence [X] | Ease [X]
[One sentence per score]

**What a win proves:** [the business learning]
**What a loss teaches:** [what a flat or negative read reveals]
**Notes:** [annotations, when any]

[Needs a Design Change, Needs Measurement and Needs a Client Decision follow, as in the tactical roadmap, each write-up adding **Readiness:**.]

## Backlog

[Same header and cells as the tactical backlog. `Surface` holds the lever.]

## Exclusions

[Levers set aside because the capability already exists and operates, framed neutrally with no build recommendation; spec items and lead or high history items not advanced. Omit when empty.]

## Method

### How Tests Are Read
### Levers Reviewed

[Every lever family the strategic lens walked, in plain words, with its row count, zero included. One line each.]

### Sequencing
### Prerequisites and Data Gaps
### If Tests Are Inconclusive

---
*Analysis produced by FunnelEnvy | [Date]*
*Based on positioning analysis across [N] sources*
```

The strategic body is held to the `Deliverable Purity Constraint` and the `Client-Facing Register` in full. The Measurement Foundation section belongs to this deliverable only; it adds no artifact type.

---

## Deliverable Purity Constraint

Both roadmap bodies are written for a client reader. They name no internal identifier: no field, token, enum value, file, phase, script, lens, gate, module, pattern ID, trigger ID or posture constant name. They render every fact in plain words, for example "this metric is not yet tracked; add tracking before running" rather than a gate name, or "a regional holdout" rather than a design token.

- **One exception:** the KB-mode gold frontmatter block. Legacy deliverables carry no frontmatter, no HTML comments and no YAML.
- **Allowed: completed-experiment results.** Lift percentages, statistical significance and sample sizes from completed experiments are encouraged, as natural attribution without experiment identifiers ("an earlier test on the pricing page lifted demo requests by about a third at statistical significance"). Measured significance is evidence; it is not the ICE Confidence score.
- **Allowed: ICE scores** in the `**Scores:**` line, the summary and the backlog `ICE` cell.
- **Attribution:** natural source references, such as "based on [Company]'s website", "according to G2 reviews" or "a prior test on the solutions page".
- **Qualified history outcomes** render in plain words, such as "an unverified readout", never the bracketed qualifier text.

---

## Client-Facing Register

This rule governs the tone of the strategic roadmap. It must read as a confident, standalone, client-ready strategic roadmap, never as a critique of FunnelEnvy's own page-level work.

- **Scope:** every line, including the How to Read note, measurement preambles and `### Sequencing`.
- **Banned framing:** any line whose point depends on what page-level or A/B testing fails to do. Examples: "optimizes the wrong metric", "altitude error", "sits above the page-level work", "corrects the page-level approach", "business outcomes an on-page A/B test cannot reach". Paraphrases are banned too.
- **Cross-references stay neutral and connective:** "works alongside", "complements". Never "corrects" or "fixes the gap in".
- **Measurement framing is positive:** the design fits because the change is a program, offer, audience motion or asset. State why it reads the outcome cleanly.
- **Each experiment stands on its own business rationale.**
- **Cold-read test:** a client who never saw the tactical roadmap should read a deliberate strategic roadmap. Rewrite any line that only makes sense as a comparison.

---

## Re-render Behavior

Each run overwrites both deliverables as a complete fresh projection of current context. No diffing, no merging. The key is the one body value carried forward.

**Key carry-forward rule.** `consolidate_backlog.py consolidate --prior` applies it per altitude, against that altitude's prior roadmap:

1. **Title pass:** a row whose normalized title (case-insensitive, trimmed) equals a prior entry's title reuses that entry's key.
2. **Mechanism pass:** a remaining row reuses the key of a remaining prior entry with the same mechanism words and an intersecting surface set.
3. **Mint:** otherwise the key is `slugify(title)` per `modules/slugify.md`, with `-2`, `-3` appended on a collision within the run.

- Prior entries are every `### N.` write-up with a `**Key:**` line plus every `## Backlog` row. Each prior key is used at most once.
- A row keeps its key when it moves between the backlog and the write-ups.
- A 1.x prior roadmap has no mechanism field, so only the title pass can match it.
- Prior keys matched by no row are listed in the completion message as dropped.
- A human edit to a displayed title needs none of this: leave the persisted `**Key:**` untouched.

**No strategic rows.** When a prior strategic roadmap exists and the run yields no strategic row or Foundation entry, leave the prior file untouched and say so in the completion message. Never overwrite a deliverable to an empty body.

---

## Scripts

| Script | Description | Use when |
|---|---|---|
| [scripts/consolidate_backlog.py](scripts/consolidate_backlog.py) | Consolidates, sizes, keys and ranks lens cards. `consolidate --cards <path\|-> [--prior <roadmap.md> ...] [--boundary YYYY-MM-DD] [--posture <SKILL.md>] [--floor N]` validates the card array, merges cards on altitude, mechanism and overlapping surfaces, sizes every row against this file's `Decision Posture` (read model `ab`, `directional`, `pre-post`, `holdout` or `unsized`), carries prior keys forward, and reports lens counts and shortfalls. `rank --rows <path\|-> --write-ups N [--history-items ID,...] [--excluded-history ID,...]` takes the scored rows (or the whole `consolidate` object), assigns readiness from blockers and read model, orders each altitude by readiness then ICE, marks the first N per altitude as write-ups, and maps history ids to rows. JSON on stdout. Exit 0 OK; 1 input error, naming the card or row index and field; 2 usage error, including `--write-ups` outside 8 to 12; 3 posture unreadable, naming the row. Stdlib only. Its module docstring is the full contract. | `consolidate` in Phase 3; `rank` in Phase 4 |
| [scripts/history_backlog.py](scripts/history_backlog.py) | Deterministic projection of a `schema: experiment-history` file plus its insight records: outcome tallies, line ranges for the Cross-Experiment Patterns, Baseline Anchors, Discovered Mechanisms and Coverage Gaps sections, a one-line record index (page, outcome and mapping, primary lift, p and n, delivered sample per day, deployed-state cues, line range), the last Learning sentences of settled records, and every typed `next_experiments` item numbered I1..In. CLI `--history <file> [--insights <files...>]`, markdown on stdout. Exit 0 OK (an unparseable insight record is reported as COVERAGE PARTIAL; a count mismatch prints a WARNING); 1 history parse error; 2 usage error; 3 not an experiment history. Stdlib only. | Phase 1 step 5b, when a `schema: experiment-history` source is bound |

## Module Dependencies

Modules resolve from the repository-root `modules/` directory. See Phase 1 `Module resolution`.

```
SKILL.md (this file)
  ├── phases/detect.md                 Phase 2: card schema; surface, persona-and-journey, history and competitive-and-proof lens briefs
  ├── phases/detect-strategic.md       Phase 2: strategic lens brief and the lever family list
  ├── phases/validate.md               Phase 4: per-row checks that add blockers
  ├── phases/score.md                  Phase 4: ICE for every row; closing the history ledger
  ├── phases/construct.md              Phase 5: full write-ups
  ├── scripts/consolidate_backlog.py   Phases 3 and 4: consolidation, sizing, keys, ranking
  ├── scripts/history_backlog.py       Phase 1 step 5b: experiment-history projection
  ├── modules/experiment-patterns.md   Lens prompt library (base)
  ├── modules/patterns-procurement.md  Procurement archetype prompt library (Phase 1 step 6)
  ├── modules/ice-scoring.md           ICE calibration guidance
  ├── modules/contrarian-triggers.md   Counter-evidence annotations
  ├── modules/hypothesis-interactions.md  Interactions between tests on one page
  ├── modules/copy-craft.md            Rules for proposed variant copy
  ├── modules/prose-craft.md           Roadmap prose style
  └── modules/slugify.md               Key minting
```

## Quality Rules

1. **Every spec item is accounted for** as a write-up, a backlog row or an `## Exclusions` entry. A roadmap that silently skips a spec item is a failure.
2. **Every card carries an evidence pointer:** a source and section in plain words. This is the one floor every candidate meets.
3. **Every write-up names a concrete unit and change.** "Improve homepage messaging" fails; "replace the homepage H1 '[current]' with '[proposed]'" passes. At the strategic altitude the unit is a named lever.
4. **Every write-up has a causal mechanism.** "This should increase conversions" fails.
5. **Copy write-ups show before and after.** The before comes from the context; the after adapts the audience messaging or value themes. Messaging-led tests show 2-3 variations, each anchored to a different direction.
6. **"What a loss teaches" is mandatory.**
7. **The unit of testing is the hypothesis.** Elements that serve one hypothesis are bundled into one test, with the bundle disclosed (`phases/construct.md`).
8. **Prose follows `modules/prose-craft.md`.**
9. **Proof hierarchy is strict.** Never upgrade claimed evidence to verified. A claim combining several proof points is flagged; a comparative claim naming a competitor needs verified proof and a legal-review note.
10. **A proxy primary metric needs a guardrail** per the `Decision Posture` `Guarded proxy` row.
11. **Every write-up and backlog row carries a `**Key:**`** per `Re-render Behavior`.
12. **Every tactical write-up carries `**Change type:**`**, re-derived on each render. Strategic write-ups do not.
13. **A running experiment owns its surface and lever.** A row whose surface and lever a running or queued experiment already tests keeps its place, carries a note naming that experiment, and sequences after it. A recorded fold decision is binding. A concluded experiment frees its slot.
14. **Every lead or high prior-test recommendation is accounted for** (`phases/score.md`), and no roadmap is written while any is unaccounted.
15. **Thresholds come from `Decision Posture`**, sizing from `consolidate_backlog.py`, and every A/B or directional read threshold carries all six parts.
16. **Lenses do not pad.** A lens below the floor reports its shortfall.
17. **FunnelEnvy branding in the footer.**
