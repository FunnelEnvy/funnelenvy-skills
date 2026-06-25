---
name: render-program-site
version: "0.1.0"
description: >
  Render a two-altitude program site from two markdown inputs (a strategic layer of bets
  and a tactical roadmap of page tests): a hub plus one spoke per bet and per test, with
  the cross-altitude edge contract enforced as a hard build gate. Trigger on "render
  program site", "program site", "strategic + tactical roadmap site", or the explicit
  /render-program-site invocation. Deterministic generator for the gate, map, and
  structure; scoped LLM pass curates spoke prose.
updated: 2026-06-24
---

# Render Program Site

Renders a client-facing, multi-page static site that reads one CRO program at two
altitudes: the **strategy** (program-level bets) and the **experiment backlog**
(page-level tests). A deterministic generator (`render_site.py`) validates the
cross-altitude edge contract and emits all structure and chrome; a scoped LLM pass
then curates the spoke prose. This is a **hybrid** skill: everything drift-sensitive
is code; only prose wording is agent-authored.

## Contents

- [Invocation](#invocation)
- [Preconditions](#preconditions)
- [Inputs](#inputs)
- [KB Mode (Dual-Mode I/O)](#kb-mode-dual-mode-io)
- [Execution Pipeline](#execution-pipeline)
- [Scripts](#scripts)
- [References](#references)
- [Output Files](#output-files)
- [Quality Rules](#quality-rules)
- [Changelog](#changelog)

## Invocation

```
/render-program-site [<strategic-md> <tactical-md>] [--scope <slug>] [--no-kb] [--out <site-root>]
```

- Two explicit positional paths render those files directly (override mode resolution).
- `--scope <slug>` selects KB mode (see below).
- `--no-kb` forces legacy mode.
- `--out <dir>` overrides the computed output directory in either mode.

## Preconditions

- A strategic experiment-layer markdown and a tactical experiment-roadmap markdown,
  both carrying the edge-contract frontmatter (see `edge-contract.md`). In KB mode these
  are resolved from the scope; in legacy mode they are explicit paths or the legacy paths.
- The two `program_version` values match (the gate halts otherwise).
- Python available (probe-then-run per repo conventions).
- This skill does NOT read L0/L1 `.claude/context/` files and does NOT perform web research.

## Inputs

The two markdown inputs and the validated edge contract are defined in
[`edge-contract.md`](edge-contract.md) (input schemas, the 7-check gate, derived data,
and the verbatim type-label map). Read it before authoring or migrating source files.

Per-test mockup assets map one-to-one onto `/experiment-mockup` output
(`mockup-screenshot.png`, `mockup.html`, `placement.md` + HTML-comment metadata): when a
test carries a `mockup` block, the generator copies the assets into `<site>/mockups/<id>/`
and renders the tactical "Proposed change" section (screenshot inline, link out to the
interactive `mockup.html` -- never iframed). Tests without a `mockup` block omit the section.

## KB Mode (Dual-Mode I/O)

Mode resolution mirrors hypothesis-generator and experiment-mockup:

1. `--no-kb` forces legacy mode.
2. Otherwise, if the working repo's CLAUDE.md declares a `Knowledge Bases` binding AND a
   valid `--scope <slug>` is given, select KB mode. The bound type skill must define
   `gold-experiment-roadmap` (the same consumer check experiment-mockup uses -- this skill
   consumes roadmaps, it does not produce KB artifacts).
3. KB mode with a missing or invalid `--scope` is a HARD STOP that lists the valid scopes.
4. Failed binding detection falls back to legacy mode loudly (no `--kb` force flag).
5. Explicit positional input paths override the mode-resolved inputs in either mode.

| | Strategic input | Tactical input | Output site |
|---|---|---|---|
| **KB mode** | `{kb_root}/deliverables/{scope}-strategic-experiment-layer.md` | `{kb_root}/deliverables/{scope}-experiment-roadmap.md` | `{kb_root}/deliverables/{scope}-program-site/` |
| **Legacy** | explicit path, or `.claude/deliverables/strategic-experiment-layer.md` | explicit path, or `.claude/deliverables/experiment-roadmap.md` | `.claude/deliverables/program-site/` |

`--out` overrides the output site path in both modes. No emitted file carries `kb_layer`
frontmatter -- the site is a derived view, not a KB artifact.

## Execution Pipeline

**Step or task tracking required** -- use step or task tracking to create an entry for each
phase before starting phase 1. Mark each complete as you finish it. In Claude Code, use
`TaskCreate` and `TaskUpdate`.

### Phase 1 -- Resolve inputs + mode

Resolve the two input paths and the output site root per [KB Mode](#kb-mode-dual-mode-io).
HARD STOP on a missing/invalid `--scope` in KB mode (list valid scopes). Confirm both input
files exist before proceeding.

### Phase 2 -- Validate the gate and emit structure

Run the generator:

```
render_site.py --strategic <strategic-md> --tactical <tactical-md> --out <site-root>
```

The script validates the 7-check edge contract and, on success, emits `styles.css`,
`site.js`, `index.html` (hub), and one `sb-NN.html` / `p-NN.html` spoke per bet/test, plus
`mockups/<id>/` assets. Spoke prose regions are emitted as labeled `<!--PROSE ...-->` slots,
pre-filled with the verbatim source body text as raw material.

If the script exits non-zero, the gate failed: surface its printed violations verbatim and
STOP. Do not edit inputs to "make it pass" without the user -- a gate failure is a real
contract violation (mechanism mismatch, dangling target, version skew, ...).

### Phase 3 -- Curate spoke prose (scoped LLM pass)

For each emitted page, rewrite ONLY the content between `<!--PROSE id=.. slot=..-->` and
`<!--/PROSE-->` markers, mapping the matching source body section to pitch-quality prose per
the label->region map in `edge-contract.md`. Apply the curation drop-list: measurement-design
detail, inconclusive-protocol detail, full score rationale, win/loss/key-risk blocks, and
bundled-element disclosures stay in the source markdown and are NOT rendered to the site.

You MUST NOT alter anything outside the prose slots -- the gate result, map coordinates
(cx/cy), edge type labels, ICE values, tier badges, chips, links, and all structure are
emitted by the script and are never agent-authored. The hub `sequence` and `decisions` slots
are assembled from the source `## Sequencing` / decisions sections into the `.tl` / `.dec-grid`
structures the comps use.

### Phase 4 -- Humanizer pass

Run the curated prose (slot contents only) through one humanizer pass applying
[`references/ai-writing-signs.md`](references/ai-writing-signs.md). Verbatim-quoted source
passages are exempt; the pass targets agent-authored prose. No em dashes.

### Phase 5 -- Completion message

Report: output site path, mode (KB/legacy), bet count, test count, per-test mockup status
(rendered / placeholder), the gate result, and the deferred-hosting note (the site is a
static bundle that embeds its own assets except web fonts, which load from the Google
Fonts CDN and degrade gracefully to the CSS fallback stack offline; deploy is a follow-up,
not part of this skill).

## Scripts

| Script | Description | Use when |
|---|---|---|
| [`scripts/render_site.py`](scripts/render_site.py) | Deterministic generator: parse two markdown inputs -> validate the 7-check edge contract (fail-closed, non-zero exit) -> derive reverse edges, intake flags, Impact-by-Ease coordinates, edge classes, tier groups -> emit `styles.css` + `site.js` + `index.html` + `sb-NN`/`p-NN` spokes from `templates/`, with labeled prose slots. CLI: `render_site.py --strategic <path> --tactical <path> --out <dir> [--templates <dir>]`. Stdlib only. | Phase 2 (every render) |

## References

| Reference | Description | Load when |
|---|---|---|
| [`edge-contract.md`](edge-contract.md) | Input schemas, the 7-check gate, derived data, and the verbatim type-label map | Always (authoring/migrating inputs, Phase 2/3) |
| [`references/ai-writing-signs.md`](references/ai-writing-signs.md) | Embedded AI-writing-sign rules for the humanizer pass | Phase 4 |

## Output Files

| File | Description |
|---|---|
| `<site>/styles.css` | Shared stylesheet (copied from `templates/styles.css`) |
| `<site>/site.js` | Shared behaviors: nav shadow, scroll-spy, portfolio-map hover-trace |
| `<site>/index.html` | Hub: hero, portfolio map, strategy cards, backlog, sequence, decisions |
| `<site>/sb-NN.html` | One spoke per strategic bet |
| `<site>/p-NN.html` | One spoke per page test (superseded tests omitted) |
| `<site>/mockups/<id>/` | Copied `screenshot.png` + `mockup.html` for tests with a mockup block |

## Quality Rules

- The render path is a hybrid: the gate, map coordinates, edge typing, chrome, and all
  data-bound structure are deterministic code; only prose-slot wording is agent-authored.
- A gate failure halts the build -- never paper over a contract violation.
- The LLM pass edits only `<!--PROSE-->` slot contents; structure is never agent-touched.
- No client content in the skill, generator, templates, or references (client data lives in
  the input files the generator reads, never in this skill directory).
- No `kb_layer` frontmatter on any emitted file. No em dashes in authored prose.

## Changelog

| Version | Changes |
|---|---|
| 0.1.0 | Initial skill: deterministic two-altitude program-site generator (`render_site.py`) with a 7-check edge-contract gate, Impact-by-Ease map, dual-mode I/O, and a scoped LLM curation + humanizer pass over spoke prose slots. Replaces roadmap-presentation. |
