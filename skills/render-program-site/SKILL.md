---
name: render-program-site
version: "0.5.1"
description: >
  Render a two-altitude program site from two markdown inputs (a strategic layer of bets
  and a tactical roadmap of page tests): a hub plus one spoke per bet and per test, with
  the cross-altitude edge contract enforced as a hard build gate. Trigger on "render
  program site", "program site", "strategic + tactical roadmap site", or the explicit
  /render-program-site invocation. Deterministic generator for the gate, map, and
  structure; scoped LLM pass curates spoke prose.
updated: 2026-07-05
---

# Render Program Site

> **Model:** Opus (the LLM curation and humanizer passes; the generator itself is deterministic Python)

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
- [KB Mode (Dual-Mode Output)](#kb-mode-dual-mode-output)
- [Execution Pipeline](#execution-pipeline)
- [Scripts](#scripts)
- [References](#references)
- [Output Files](#output-files)
- [Quality Rules](#quality-rules)
- [Changelog](#changelog)

## Invocation

```
/render-program-site [<strategic-md> <tactical-md>] [--edges <path>] [--account-program <path>] [--scope <slug>] [--no-kb] [--out <site-root>]
```

- Two explicit positional paths render those gold roadmaps directly (override mode resolution); pair them with `--edges <path>` for the sidecar.
- `--scope <slug>` names the KB scope; in KB mode it is required and resolves all three inputs (and the optional account program) from the scope, in legacy mode it is warned about and ignored (see below). Mode itself is selected by KB binding detection, not by this flag.
- `--edges <path>` supplies the edge sidecar (required; resolved from the scope in KB mode).
- `--account-program <path>` supplies the optional account-program deliverable (the off-store altitude). When present, the hub gains an "account program" section and one `ap-NN.html` spoke per play; when absent, output is byte-identical to a two-altitude render.
- `--no-kb` forces legacy mode.
- `--out <dir>` overrides the computed output directory in either mode.

## Preconditions

- The two gold roadmaps hypothesis-generator produces, read in place: a strategic gold
  roadmap (`gold-strategic-roadmap`) and a tactical gold roadmap (`gold-experiment-roadmap`).
  This skill derives per-item data from their structure and authors nothing into them.
- The strategic roadmap may carry an optional `## Measurement Foundation` section (source
  contract: hypothesis-generator SKILL.md > Strategic Roadmap Output Format): unscored,
  keyless prerequisite entries authored as bold-labeled items. They render as a hub section
  (`#measurement-foundation`) only: no ICE, no tier, no map presence, no cross-altitude
  edges, no spokes, no sidecar entries (see `edge-contract.md`). A roadmap without the
  section renders byte-identically to a 0.4.x site.
- The edge sidecar (`{scope}-program-edges.md`), the one net-new authored input, carrying the
  cross-altitude edge binding and the gate-classification fields (see `edge-contract.md`).
- The sidecar's `strategic_version` / `tactical_version` match the live gold roadmaps'
  frontmatter `version` (the version-lock gate halts otherwise).
- Optional third input: an account-program deliverable (a `gold-strategy-deliverable` of the
  account-program shape) holding off-store account plays. It is parsed standalone (no sidecar
  binding, no edge participation, not on the map); see `edge-contract.md`. In KB mode it resolves
  to `{kb_root}/deliverables/{scope}-account-program.md`; it is optional per scope, and a missing
  file simply omits the account altitude (mirrors how a per-test `mockup` block is optional).
- Python available (probe-then-run per repo conventions).
- This skill does NOT read L0/L1 `.claude/context/` files and does NOT perform web research.

## Inputs

The three inputs (two gold roadmaps + the edge sidecar) and the validated edge contract are
defined in [`edge-contract.md`](edge-contract.md) (derived-field map, the sidecar schema, the
gate, derived data, and the verbatim type-label map). Read it before authoring the sidecar.

Per-test mockup assets map one-to-one onto `/experiment-mockup` output
(`mockup-screenshot.png`, `mockup.html`, `placement.md` + HTML-comment metadata): when a
test carries a `mockup` block, the generator copies the assets into `<site>/mockups/<id>/`
and renders the tactical "Proposed change" section (screenshot inline, link out to the
interactive `mockup.html` -- never iframed). Tests without a `mockup` block omit the section.
The `mockup` block also accepts an optional `control_screenshot` (experiment-mockup's
`control-screenshot.png`, the unmodified "before" state): when present, the spoke renders a
labeled Before/After pair instead of a single after screenshot; when absent (or its file is
missing), it renders after-only, unchanged.

## KB Mode (Dual-Mode Output)

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

Mode resolution mirrors hypothesis-generator and experiment-mockup exactly:

1. `--no-kb` forces legacy mode. Done.
2. Otherwise detect the KB binding: the working repo's CLAUDE.md must declare a
   `Knowledge Bases` section, and the bound type skill must define
   `gold-experiment-roadmap` (the same consumer check experiment-mockup uses -- this skill
   consumes roadmaps, it does not produce KB artifacts). Binding detected: KB mode.
   Failed detection: legacy mode, loudly, reporting which check failed
   (there is deliberately no `--kb` force flag; a broken binding gets fixed, not worked around).
3. In KB mode, `--scope <slug>` is required and must match a valid scope defined by the
   type skill. Missing or invalid `--scope` is a HARD STOP that lists the valid scopes.
   Do not guess a scope. In legacy mode, a supplied `--scope` is warned about and ignored.
4. Explicit positional input paths override the mode-resolved inputs in either mode (pair them
   with `--edges` for the sidecar).

| | Strategic input | Tactical input | Edge sidecar | Account program (optional) | Output site |
|---|---|---|---|---|---|
| **KB mode** | `{kb_root}/deliverables/{scope}-strategic-roadmap.md` | `{kb_root}/deliverables/{scope}-experiment-roadmap.md` | `{kb_root}/deliverables/{scope}-program-edges.md` | `{kb_root}/deliverables/{scope}-account-program.md` (optional per scope; missing = omit) | `{kb_root}/deliverables/{scope}-program-site/` |
| **Legacy** | explicit path, or `.claude/deliverables/strategic-roadmap.md` | explicit path, or `.claude/deliverables/experiment-roadmap.md` | `--edges`, or `.claude/deliverables/program-edges.md` | `--account-program <path>` (optional; missing = omit) | `.claude/deliverables/program-site/` |

When the account program is present, the site also emits `spoke-account.html`-derived `ap-NN.html`
spokes (one per play) and the hub gains an `#account-program` section; when absent, neither appears
and the render is byte-identical to a two-altitude site.

The strategic and tactical inputs are hypothesis-generator's gold roadmaps, read in place (no
separate hand-authored format; the tactical-path collision with the gold output is resolved by
reading the gold artifact directly). The sidecar is render-program-site's own authored input.

`--out` overrides the output site path in both modes. No emitted file carries `kb_layer`
frontmatter -- the site is a derived view, not a KB artifact.

## Execution Pipeline

**Step or task tracking required** -- use step or task tracking to create an entry for each
phase before starting phase 1. Mark each complete as you finish it. In Claude Code, use
`TaskCreate` and `TaskUpdate`.

### Phase 1 -- Resolve inputs + mode

Resolve the three input paths (strategic gold roadmap, tactical gold roadmap, edge sidecar) and
the output site root per [KB Mode](#kb-mode-dual-mode-io). HARD STOP on a missing/invalid
`--scope` in KB mode (list valid scopes), and on a missing edge sidecar (it is the one input
this skill cannot derive). Confirm all three input files exist before proceeding.

### Phase 2 -- Validate the gate and emit structure

Run the generator:

```
render_site.py --strategic <strategic-md> --tactical <tactical-md> --edges <sidecar-md> --out <site-root> [--account-program <account-md>]
```

The script validates the 7-check edge contract and, on success, emits `styles.css`,
`site.js`, `index.html` (hub), and one `sb-NN.html` / `p-NN.html` spoke per bet/test, plus
`mockups/<id>/` assets. Spoke prose regions are emitted as labeled `<!--PROSE ...-->` slots,
pre-filled with the verbatim source body text as raw material.

When the strategic roadmap carries a `## Measurement Foundation` section, the hub gains a
conditional `#measurement-foundation` section (one card per entry: the bold label as the
data-bound title, the prose through curation slots, no score chips) between the strategy
cards and the experiment backlog, plus a nav link. Foundation entries never enter the edge
gate, need no sidecar entries, and get no spokes; a sidecar edge that targets one is a
dangling-target gate error. When the section is absent, the render is byte-identical to a
site without this feature.

When `--account-program` is supplied, a separate account-binding leg validates the plays
(at least one play, unique ordinals, required labels; see `edge-contract.md`) -- account plays
never enter the seven edge checks or the portfolio map. On success the hub gains a conditional
`#account-program` section (cohort cards + one play card per play) and one `ap-NN.html` spoke is
emitted per play. When the flag is absent the account altitude is skipped entirely and the render
is byte-identical to a two-altitude site.

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

When a Measurement Foundation section is present, its hub slots are curated the same way:
`foundation-lead` introduces the section and each `foundation-<n>` slot maps from that
entry's source prose (keep the confirm-first vs build framing and the dependent-experiment
references; the audience is the client's analytics or operations team).

When an account program is present, its prose slots are curated the same way: the hub
`account-lead` and `cohort-<n>` behavior slots map from the taxonomy, and each `ap-NN` spoke's
`play-lead`, `play`, `play-cohort`, `play-rationale`, `play-measure`, `play-depends`, and
`play-relationship` slots map from the play's `The play` / `Cohort` / `Rationale` /
`How it is measured` / `Dependencies` / `Relationship to the roadmaps` source labels.

### Phase 4 -- Humanizer pass

Run the curated prose (slot contents only) through one humanizer pass applying
[`references/ai-writing-signs.md`](references/ai-writing-signs.md). Verbatim-quoted source
passages are exempt; the pass targets agent-authored prose. No em dashes.

### Phase 5 -- Completion message

Report: output site path, mode (KB/legacy), bet count, test count, account-play count (when an
account program was rendered), per-test mockup status
(rendered / placeholder), the gate result, and the deferred-hosting note (the site is a
static bundle that embeds its own assets except web fonts, which load from the Google
Fonts CDN and degrade gracefully to the CSS fallback stack offline; deploy is a follow-up,
not part of this skill).

## Scripts

| Script | Description | Use when |
|---|---|---|
| [`scripts/render_site.py`](scripts/render_site.py) | Deterministic generator: parse the two gold roadmaps + the edge sidecar, derive per-item data (id/key/title/tier/ICE/page) from the gold bodies -> validate the edge contract (fail-closed, non-zero exit) -> derive reverse edges, intake flags, Impact-by-Ease coordinates, edge classes, tier groups -> emit `styles.css` + `site.js` + `index.html` + `sb-NN`/`p-NN` spokes from `templates/`, with labeled prose slots. Parses the strategic roadmap's optional `## Measurement Foundation` section into unscored, keyless foundation entries rendered as a conditional `#measurement-foundation` hub section (never on the edge gate, map, or spokes). When `--account-program` is given, additionally validates the account-binding leg and emits the `#account-program` hub section + one `ap-NN` spoke per play (never on the edge gate or map). CLI: `render_site.py --strategic <path> --tactical <path> --edges <path> --out <dir> [--account-program <path>] [--templates <dir>]`. Stdlib only. | Phase 2 (every render) |

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
| `<site>/index.html` | Hub: hero, portfolio map, strategy cards, measurement foundation (only when the strategic roadmap carries the section), backlog, sequence, decisions |
| `<site>/sb-NN.html` | One spoke per strategic bet |
| `<site>/p-NN.html` | One spoke per page test (superseded tests omitted) |
| `<site>/ap-NN.html` | One spoke per account play (only when an account program is supplied) |
| `<site>/mockups/<id>/` | Copied `screenshot.png` + `mockup.html` for tests with a mockup block; also `control.png` when the block carries a resolvable `control_screenshot` |

## Quality Rules

- The render path is a hybrid: the gate, map coordinates, edge typing, chrome, and all
  data-bound structure are deterministic code; only prose-slot wording is agent-authored.
- A gate failure halts the build -- never paper over a contract violation.
- Account plays never enter the edge gate or the portfolio map: they carry no ICE, no on-page
  mechanism, and no cross-altitude edge, so they are validated only by the separate
  account-binding leg and rendered as a distinct off-store altitude.
- Measurement Foundation entries never enter the edge gate or the portfolio map either: they
  are keyless and unscored, need no sidecar entries, render as a hub section only (no spokes,
  no score chips), and a sidecar edge that targets one fails as a dangling target.
- The LLM pass edits only `<!--PROSE-->` slot contents; structure is never agent-touched.
- No client content in the skill, generator, templates, or references (client data lives in
  the input files the generator reads, never in this skill directory).
- No `kb_layer` frontmatter on any emitted file. No em dashes in authored prose.

## Changelog

| Version | Changes |
|---|---|
| 0.5.1 | Repo-audit doc corrections, no generator change. Mode resolution rewritten to match hypothesis-generator/experiment-mockup exactly: KB binding detection alone selects KB mode (previously step 2 said binding AND a valid `--scope` select it while step 3 said a missing `--scope` in KB mode is a HARD STOP -- contradictory); `--scope` names the scope (required in KB mode, warn-and-ignore in legacy) and never selects the mode. Section renamed `KB Mode (Dual-Mode Output)` to match the header the other dual-mode skills use and cross-reference. Added the Model declaration (Opus for the curation/humanizer passes). Also gains the `modules/kb-mode.md` canonical-contract pointer in its KB-mode section (drift canary enforced by `scripts/registry_check.py`). |
| 0.5.0 | Measurement Foundation rendering. `render_site.py` now parses the strategic gold roadmap's optional `## Measurement Foundation` section (hypothesis-generator SKILL.md > Strategic Roadmap Output Format) into a new item class: foundation entries (bold-labeled items; unscored, keyless, no ICE, no tier, no map presence, no cross-altitude edges, no spokes). The hub gains a conditional `#measurement-foundation` section between the strategy cards and the backlog (one `.mf` card per entry: label as title, prose through `foundation-lead`/`foundation-<n>` curation slots, no score chips) plus a nav link; new `#measurement-foundation`/`.mf-grid`/`.mf` CSS. Foundation entries are excluded from every sidecar-related gate check (binding completeness, dangling targets, executor-status derivation, version-lock scope) and require no sidecar entries; a sidecar edge whose target names a foundation entry fails as a dangling target (check 2). Composes with the optional account altitude (both, either, or neither). Output is byte-identical to 0.4.0 for any strategic roadmap without the section (empty `{{MEASUREMENT_FOUNDATION}}` reproduces the hub seam; no nav link). Also adds the `informs` edge-direction semantics note to `edge-contract.md` (edges point bet -> test; behavior unchanged). |
| 0.4.0 | Optional account-program altitude. New `--account-program <path>` renders an off-store account layer: `load_account` parses the deliverable standalone (plays sliced from `## The Account-Level Plays`, cohorts from the `## The Account-Cohort Taxonomy` table; no `**Key:**`/`**Scores:**` required), a separate account-binding gate leg validates the plays (>=1 play, unique ordinals, required `Cohort`/`The play`/`How it is measured` labels), the hub gains a conditional `#account-program` section + nav link, and one `ap-NN.html` spoke is emitted per play. Account plays never enter the 7-check edge gate or the Impact-by-Ease map. `extract_sections` id-prefix generalized to `{bet:sb, test:p, play:ap}`. New `templates/spoke-account.html` + `#account-program`/`.cohort`/`.x-tag.off` CSS. Output is byte-identical to 0.3.x for any program supplying no account program (empty `{{ACCOUNT_PROGRAM}}` reproduces the hub seam; no `ap-*.html`; no nav link). Also corrects the stale `0.2.1` version pin in README.md / in-repo CLAUDE.md. |
| 0.3.0 | Optional Before/After mockup render. The `mockup` block accepts an optional `control_screenshot` (experiment-mockup's `control-screenshot.png`): when present and resolvable, the tactical spoke's "Proposed change" section renders a labeled two-frame Before/After comparison (responsive grid, stacks under 760px) instead of a single after screenshot. `copy_mockup_assets` now copies `control.png` alongside `screenshot.png` and returns a dict of resolved paths; the gate rejects a non-string `control_screenshot`; a missing control file degrades to after-only. Output is byte-identical to 0.2.x for any `mockup` block without a resolvable `control_screenshot`. New `.mockup-compare` / `.mockup-label` CSS. |
| 0.2.0 | Inputs reconciled with hypothesis-generator's actual output: the generator now reads the two prose gold roadmaps (`gold-experiment-roadmap`, `gold-strategic-roadmap`) in place and derives per-item data (id from `### N.` ordinal, key from `**Key:**`, title, tier from the enclosing tier H2, ICE from `**Scores:**`, page) from the gold bodies. The cross-altitude edge binding plus the gate-classification fields (`delivery_surface`, `executor_status`, per-test `mechanism_class`, optional `status`/`run_tag`/`keystone`/`mockup`) move to a new render-owned sidecar `{scope}-program-edges.md` keyed by gold Key. KB-mode strategic input renamed `{scope}-strategic-experiment-layer.md` -> `{scope}-strategic-roadmap.md`; tactical collision resolved by reading the gold artifact directly. Gate check 7 redefined as a sidecar-vs-gold version lock; new binding checks (every gold bet bound, every sidecar Key resolves, every live test has a `mechanism_class`). `render_site.py` gains `--edges`. Replaces the bespoke hand-authored `bets:`/`tests:`/`edges:` frontmatter that no deliverable carried. |
| 0.1.0 | Initial skill: deterministic two-altitude program-site generator (`render_site.py`) with a 7-check edge-contract gate, Impact-by-Ease map, dual-mode I/O, and a scoped LLM curation + humanizer pass over spoke prose slots. Replaces roadmap-presentation. |
