---
name: roadmap-presentation
version: 0.1.0
description: "When the user wants to render an experiment roadmap as a client-facing presentation. Also use when the user mentions 'render the roadmap as a presentation,' 'roadmap site,' 'present the experiment roadmap,' 'roadmap HTML,' 'roadmap presentation,' or the explicit /roadmap-presentation invocation. Renders a gold-experiment-roadmap (KB mode) or legacy experiment-roadmap.md into a self-contained, multi-page static site: a hub overview page plus one pitch-focused spoke page per experiment, with a control-vs-proposed mockup comparison fed by experiment-mockup outputs. Deterministic chrome via a scaffolding script; the agent curates content and runs a humanizer pass. No web research, no analysis, no .claude/context/ writes."
updated: 2026-06-17
---

# Roadmap Presentation

You render an experiment roadmap into a self-contained, multi-page static site with a hub-and-spoke structure: a hub overview page plus one pitch-focused spoke page per experiment. The source is the roadmap markdown (KB-mode gold or legacy deliverable); optional per-experiment mockup artifacts from experiment-mockup fill the control-vs-proposed comparison slots.

**You are a render skill, not an analysis skill.** You do NOT generate hypotheses, score, or research. You read the existing roadmap markdown, curate it for pitch (drop the dense analytical rigor that belongs in the markdown record), map whatever section shape the roadmap actually has, and emit a styled site. The markdown remains the source of truth; the site is a derived view.

**The split:** a deterministic scaffolding script (`scripts/scaffold_site.py`) emits every byte of chrome (the CSS design system, the JS behaviors, the page shells, and the prev/next pager chain) so renders cannot drift. You do only the judgment work: curation, version-agnostic section-mapping, and a humanizer pass over the prose you author.

**Output (legacy mode):** `.claude/deliverables/roadmap-site/`
**Output (KB mode):** `{kb_root}/deliverables/{scope}-roadmap-site/`
**Model:** Opus
**No web research. No analytics calls. No `.claude/context/` writes.**

---

## Invocation

```
/roadmap-presentation
/roadmap-presentation --scope <slug>
/roadmap-presentation --no-kb
/roadmap-presentation --out <dir>
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--scope` | none | KB mode only. Selects which KB scope the run targets. Required in KB mode; warn-and-ignore in legacy mode. |
| `--no-kb` | off | Force legacy `.claude/deliverables/` I/O even when a KB binding is detected. |
| `--out` | none | Explicit output-directory override. When set, the site is written there instead of the computed placement below (the mockup base is unaffected). |

---

## Operating Modes

Resolved once in Phase 1 and held in-session. Mode resolution mirrors hypothesis-generator's `KB Mode (Dual-Mode Output)` exactly. The render logic is identical in both modes; only the source-markdown path, the site output path, and the mockup base differ.

- **Legacy mode** (default): source `.claude/deliverables/experiment-roadmap.md` (frontmatter-less); site at `.claude/deliverables/roadmap-site/`; mockup base `.claude/deliverables/experiments/`.
- **KB mode**: the run resolved a `{scope}`; source gold artifact at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`; site at `{kb_root}/deliverables/{scope}-roadmap-site/`; mockup base `{kb_root}/deliverables/experiments/`.

### Mode Resolution Procedure (Phase 1, step 0)

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy mode, and note in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy I/O."
3. Parse the KB root path and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/` and its `artifacts/` directory defines `gold-experiment-roadmap` (the source artifact type). If the check fails: legacy mode, and report which check failed.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope.

There is deliberately no `--kb` force flag. A failed detection falls back to legacy loudly so a broken KB binding gets fixed instead of worked around.

When KB mode is confirmed, hold this in-session state: `kb_root`, `kb_type`, `scope`. The site output path and mockup base derive from these per `Operating Modes`.

---

## Preconditions

- The source roadmap markdown must exist at the mode's path. If absent: STOP and tell the user to run `/hypothesis-generator` first (with `--scope <slug>` in KB mode). Do not synthesize a roadmap; this skill renders, it does not generate.
- Do NOT run concurrently with hypothesis-generator: the source markdown must be stable during the render.
- The skill makes no web requests, no analytics calls, and never writes to `.claude/context/`.

---

## Execution Pipeline

The skill is a single-agent, ordered phase sequence. No subagents.

### Phase 1: Resolve mode and locate the source

Run `Mode Resolution Procedure` above. Locate the source roadmap markdown at the mode's path. Read it in full. Resolve the site output path (`--out` overrides; otherwise the deterministic placement per `Operating Modes`) and the mockup base.

### Phase 2: Parse the roadmap into an in-memory structure

Parse the source markdown into:

- **Top-level sections** that actually exist (do NOT assume a fixed shape: see `Version-agnostic section-mapping`).
- **Experiment items**: each `### N. {Title}` heading, in roadmap order, with its number, title, hypothesis, ICE scores (if present), page targets, disposition, variations, why-this-should-work, win/loss reads, self-critique, and per-experiment asks.
- **Item dispositions**: detect reframed, held, superseded, and net-new items, not only cleanly scored experiments. Each disposition gets a visible treatment.
- **Hub-level content**: the measurement-constraint callout, the stat row inputs, the sequencing/run-order grouping, the "what's not here" exclusions, and the "What We Need From {Client}" asks. `{Client}` resolves from the roadmap's own content, never hardcoded.

This is a read-and-structure pass. No site files are written yet.

### Phase 3: Resolve mockups (mockup-resolution contract)

For each experiment heading `### N. {Title}`:

1. Derive the mockup slug by applying `modules/slugify.md` rules to `{Title}`, identical to experiment-mockup `Step 4: Generate Output Directory Slug`, so identical titles resolve to identical slugs. (Apply the Python fallback in `modules/slugify.md` when resolving 3+ slugs.)
2. Resolve the source mockup directory at the mode's mockup base: KB mode `{kb_root}/deliverables/experiments/{slug}/`; legacy mode `.claude/deliverables/experiments/{slug}/`.
3. When that directory exists with `mockup.html` plus screenshot(s), mark the experiment `mockup_present: true`. When absent, mark `mockup_present: false`.
4. Record any experiment with no matching mockup directory (missing) and any mockup directory matching no current experiment title (orphan: signals a title rename between roadmap versions) for the completion message.

The slug is used only to locate source artifacts at build time. The in-site asset path is number-keyed (`assets/mockups/experiment-NN/`), so the deployed site never depends on slug stability.

### Phase 4: Scaffold the chrome (deterministic)

Build a JSON manifest from the parsed structure:

```json
{
  "title": "Experiment Roadmap",
  "out_dir": "<resolved site path>",
  "experiments": [
    {"number": 1, "title": "<title>", "mockup_present": true},
    ...
  ]
}
```

Run the scaffolding script:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY skills/roadmap-presentation/scripts/scaffold_site.py <manifest.json> --out <site path>
```

(Resolve the skill path from the working repo or plugin cache.) The script emits `styles.css`, `site.js`, `index.html` (hub shell), and one `experiment-NN.html` (spoke shell) per experiment, with the prev/next pager chain and breadcrumbs already wired, plus the number-keyed `assets/mockups/experiment-NN/` directories. The script owns all chrome; you fill the labeled content slots (`<!-- CONTENT-SLOT -->`, `<!-- NAV-LINKS-SLOT ... -->`) next.

### Phase 5: Author per-page content (curation + section-mapping + humanizer)

Fill the script-emitted content slots. Apply the three judgment passes:

- **Curation (pitch-focus principle).** Drop measurement-design detail (target metric, guardrail, threshold cells), inconclusive-protocol detail, and bundled-elements disclosures from the site. These stay markdown-only: the HTML pitches, the markdown remains the analytical record.
- **Version-agnostic section-mapping.** Render the grouping the roadmap actually uses (three tiers, disposition groups, a reconciliation table, preliminary-results cards, a post-rebuild backlog, or any combination). Map each disposition (reframed, held, superseded, net-new) to a visible hub treatment and, where it has a per-experiment page, a spoke. See the design-system classes below.
- **Humanizer pass.** Run all renderer-authored prose (condensed card hypotheses, mockup annotations, section leads) through `references/ai-writing-signs.md` before write. Passages quoted verbatim from the source roadmap are already deliverable-grade and are exempt; the pass targets only prose you author.

For each experiment's mockup comparison slot: when `mockup_present`, copy the display assets (`mockup.html` screenshots) from the source mockup directory into `{site}/assets/mockups/experiment-NN/` and reference them with relative paths so the site is self-contained. When absent, render labeled placeholder frames (`.mock-pending`).

**Hub page** (`index.html`): hero with stat row and the measurement-constraint callout; grouped experiment index cards (one-line hypothesis, compact ICE, mockup-status indicator, thumbnail strip once mockups exist); sequencing wave diagram with experiment pills linking to spokes; "what's not here" exclusions; a "What We Need From {Client}" asks section (Provide / Confirm / Approve columns, each ask tagged with the experiments it unblocks). Fill the `<!-- NAV-LINKS-SLOT -->` with anchors to the hub sections you render.

**Spoke page** (one per experiment): title / tier / page-chips / hypothesis header with quiet inline ICE; centerpiece control-vs-proposed mockup comparison with per-image change annotations and variation tabs (tabs collapse for single-variation experiments; mobile-scoped experiments render phone-width frames via `.mock-compare.mobile`); why-this-should-work; win/loss panels; self-critique (kept: preempting objections is persuasive); per-experiment before-launch asks. The breadcrumb and prev/next pager are already wired by the script.

**Design-system classes** (emitted by the script, ready to use): `.tier.qw|.sb|.ex`, `.disp.run|.gated|.reframed|.held|.superseded|.net-new`, `.callout-blue|.yellow|.red|.green`, `.stat-row`/`.stat-item`, `.idx-grid`/`.idx-card`, `.seq`/`.wave`/`.w-pill`, `.mock-compare`/`.mock-chrome`/`.mock-pending`/`.annot`, `.var-tabs`/`.var-tab`/`.var-panel`, `.winloss`/`.wl`, `.crit`, `.prereq-grid`/`.prereq-col`, `.excl-list`, `.launch-list`, `.verdict`. No emitted site file carries `kb_layer` frontmatter; the site is a derived view.

### Phase 6: Write the site and emit the completion message

Re-render is a complete projection of the current markdown (no diffing, no merging), mirroring hypothesis-generator's `Re-render Behavior`. A pre-existing site directory is overwritten. Emit the completion message per `Completion Message`.

---

## Mockup-Resolution Contract

The full per-experiment resolution steps live in Phase 3. Summary of the invariants:

- Slug is derived from the title via `modules/slugify.md`, identical to experiment-mockup, so identical titles resolve identically.
- Source artifacts are located at the mode's mockup base; copied display assets land at the number-keyed in-site path `{site}/assets/mockups/experiment-NN/` and are referenced relatively (the site is self-contained).
- Absent source directory renders labeled placeholder frames, not an error and not an empty slot. The comparison slots are populated when experiment-mockup has run for the same mode and scope (it writes to the same mockup base this contract resolves); they show placeholders until then.
- The completion message reports missing-mockup experiments and orphan mockup directories, surfacing drift rather than hiding it.

Mockups are build inputs, not site-owned outputs: this skill consumes whatever experiment-mockup wrote at the mode's mockup base and never produces or mutates mockup artifacts itself.

---

## Completion Message

Report:

- Site output path and mode (KB / legacy).
- Experiment count rendered.
- Per-experiment mockup status (present / placeholder).
- Drift: any experiment with no matching mockup directory (missing) and any mockup directory matching no current experiment (orphan = a title rename between roadmap versions).
- The deferred-hosting note: hosting/deploy is out of scope for v1. Include the one-line static-host deploy command for the output directory, for example:

  ```
  cd <site path> && python3 -m http.server 8000
  ```

  then open `http://localhost:8000/`. A managed deploy step is a follow-up once the render pipeline is proven.

---

## Scripts

| Script | Description | Use when |
|---|---|---|
| [scripts/scaffold_site.py](scripts/scaffold_site.py) | Deterministic scaffolding: emits the shared CSS design system, the shared JS behaviors, the hub and spoke HTML page shells, the prev/next pager chain, breadcrumbs, and the number-keyed mockup asset directories from a JSON manifest. Byte-identical across runs given the same manifest. Contains no client content and no judgment logic. | Phase 4, after parsing the roadmap and resolving mockups |

## Reference Documents

| Reference | Description | Use when |
|---|---|---|
| [references/ai-writing-signs.md](references/ai-writing-signs.md) | Lean, portable embed of the signs of AI-generated writing (inflated symbolism, promotional language, vague attributions, em-dash overuse, rule of three, AI vocabulary, negative parallelisms, excessive conjunctive phrases). Applied in the Phase 5 humanizer pass over renderer-authored prose. | Phase 5, before write, over prose the renderer authors (verbatim roadmap quotes are exempt) |

## Module Dependencies

Modules resolve from the repository-root `modules/` directory (a sibling of `skills/`), not from this skill's folder.

```
SKILL.md (this file)
  ├── scripts/scaffold_site.py        Deterministic chrome emission
  ├── references/ai-writing-signs.md  Humanizer pass rules
  └── modules/slugify.md              Title-to-slug rules (mockup resolution, Phase 3)
```

## Quality Rules

1. **Render, do not generate.** No new hypotheses, scores, research, or analysis. The markdown is the source of truth.
2. **Chrome is deterministic.** All CSS, JS, page shells, and pager links come from `scaffold_site.py`. Never hand-author chrome; that is the drift the script prevents.
3. **Version-agnostic.** Read whatever section shape the roadmap has. Never assume three clean tiers. Handle reframed, held, superseded, and net-new dispositions.
4. **Pitch-focus curation.** Measurement-design cells, inconclusive protocols, and bundled-elements disclosures stay markdown-only.
5. **Self-contained site.** Mockup assets are copied into the site's own number-keyed asset tree and referenced relatively. The site renders correctly when the source mockup directory is removed after build.
6. **Drift surfaced, not hidden.** Missing and orphan mockups are reported in the completion message.
7. **No `kb_layer` on the site.** The site is a derived view, not a KB artifact.
8. **Humanizer pass on authored prose only.** Verbatim roadmap quotes are exempt.
9. **No client names or client content** beyond what the source roadmap itself carries (which the renderer faithfully renders). The skill, script, and references carry no client content.
10. **No em dashes.** Use commas, colons, semicolons, or parentheses.

## Changelog

| Version | Changes |
|---------|---------|
| 0.1.0 | Initial skill: dual-mode (KB / legacy) render of an experiment-roadmap markdown into a hub-and-spoke static site. Deterministic `scaffold_site.py` chrome (CSS design system, JS behaviors, page shells, pager chain). Mockup-resolution contract (slug-based source location, number-keyed in-site assets, placeholder frames, missing/orphan drift reporting). Version-agnostic section-mapping and pitch-focus curation. Embedded `ai-writing-signs.md` humanizer reference and pass. Companion `--present` chaining flag on hypothesis-generator. |
