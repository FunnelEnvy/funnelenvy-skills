---
fe-managed: true
name: experiment-roadmap-presentation
description: >
  Render a client-facing, multi-page HTML presentation from an experiment-roadmap
  markdown artifact (KB-mode gold or legacy deliverable): a hub overview page
  (tier-grouped experiment index, sequencing diagram, client asks) plus one
  pitch-focused spoke page per experiment with a control-vs-proposed mockup
  comparison slot fed by experiment-mockup outputs.
governed_by: change-management/change-document
status: Closed
status_note: Closed, unreleased; committed to a branch (no PR yet)
resource_name: roadmap-presentation
resource_version: "TBD"
impact: 4
confidence: 4
ease: 2
version: "0.7.0"
created: 2026-06-10
updated: 2026-06-17
---
# Experiment Roadmap Presentation Render

## Background

A 2026-06-10 working session explored how to visually present the experiment roadmaps this plugin generates. The trigger: a hand-built single-page HTML strategy deliverable from a prior engagement demonstrated how much more effective a styled, navigable presentation is than raw markdown for client review. A wireframe iteration against a live roadmap instance in a client KB repo converged on a validated multi-page design (wireframes retained outside this repo, because they carry client content). This change productizes that design as a repeatable render path from any `gold-experiment-roadmap` artifact.

## Current State

- hypothesis-generator (v1.6.0, dual-mode) writes a single markdown roadmap: legacy `.claude/deliverables/experiment-roadmap.md` or KB-mode `{kb_root}/deliverables/{scope}-experiment-roadmap.md` with gold frontmatter. No rendering path beyond markdown exists.
- experiment-mockup produces standalone HTML mockup artifacts per hypothesis (capture of control state plus injected variant) into a per-hypothesis slug directory, but nothing consumes them downstream.
- render-default-deliverables renders positioning deliverables (separate concern; precedent for a dedicated render skill).
- The markdown roadmap is analytically complete but presents a roadmap's worth of dense rigor (scores, baselines, self-critique, inconclusive protocols) as a wall of prose, the wrong altitude for stakeholder pitch review. Its structure also varies across versions and across scopes (tiers, disposition groups, live-program reconciliation, post-rebuild backlog), so no fixed section shape can be assumed.

## Approach

Render the gold-experiment-roadmap markdown into a self-contained, multi-page static site with a hub-and-spoke structure. The design was validated in the 2026-06-10 wireframe session and the reference implementation below; this Discovery pass settles its structural placement, internal architecture, and external dependencies.

### Change Profile

- **script-affecting: yes.** The renderer is a skill backed by a deterministic scaffolding script (see `Architecture`). Adding that Python script to the new skill's `## Scripts` surface flips this flag and pulls in test authoring. The folded-in experiment-mockup dual-mode work (see `Experiment-mockup dual-mode I/O`) is markdown-only (SKILL.md, agent-header.md, phases) and adds no script, so it does not change this flag's justification.
- **performance-affecting: no.** This skill does not alter a performance-sensitive analytical surface under skill-management's eval policy. The render is mostly deterministic transformation plus a single humanizer pass over render-authored copy; it has no ICE-scoring, pattern-matching, or hypothesis-construction surface that evals govern. The experiment-mockup edits are path-resolution and documentation changes, also non-performance-affecting.
- **test-eval-only: no.** The change adds a production skill and script, not changes confined to `_tests/` or `_evals/`.

### Structural placement: separate skill plus a thin chaining flag

The renderer is a **new, separate skill** (proposed name `roadmap-presentation`), not a mode of hypothesis-generator, with a thin `--present` chaining flag added to hypothesis-generator that invokes the renderer after a successful roadmap write. Three observations from building and regenerating the reference implementation three times drove this:

- **The render lifecycle is decoupled from generation.** The reference site was regenerated three times without re-running any analysis, triggered by markdown edits, newly-added mockups, and design changes. None of those are hypothesis generation, so coupling the render into the generator would force unnecessary re-analysis.
- **The two skills sit at different altitudes.** hypothesis-generator is a single Opus analytical agent at a ~40-60K-token budget. The renderer is mostly deterministic transformation plus a humanizer pass, dragging a ~450-line CSS design system, multi-page templating, a prev/next pager chain, and a mockup contract. Folding that into the analytical agent is the wrong altitude.
- **The invocation intent is distinct** ("regenerate this site" vs. "generate the roadmap").

The `--present` flag preserves one-command discoverability for users who do want generate-then-render in a single step. Because the renderer is the primary new resource, `resource_name` is `roadmap-presentation`; the hypothesis-generator flag is a small companion edit scoped into the same change.

### Architecture: skill backed by a deterministic script

The render is **a skill backed by a deterministic script**, splitting deterministic chrome from judgment work. Hand-authoring the markup on each render caused real template drift: one reference site silently fell two structural versions behind its roadmap. The mitigation is a deterministic scaffolding script that emits the design-system assets (CSS/JS), the page shell, and the prev/next pager chain, so every render is byte-identical in chrome and cannot drift. The LLM does only the parts that genuinely need judgment:

- **Curation.** Apply the pitch-focus principle: drop measurement-design, inconclusive-protocol, and bundled-elements detail from the source markdown so the site pitches rather than documents.
- **Section-mapping.** The source roadmap's structure varies across versions and scopes (it has appeared as three tiers, as disposition groups, and as a live-program-reconciliation table plus preliminary-results cards plus a separate post-rebuild backlog section). The renderer must read whatever sections actually exist and map them, never assuming a fixed shape, and must handle item dispositions (reframed, held, superseded, net-new), not only cleanly scored experiments.
- **Humanizer pass.** See below.

### Page anatomy (validated)

- **Hub (overview page):** hero with stat row and the roadmap's measurement-constraint callout; tier- or group-grouped experiment index cards (one-line hypothesis, compact ICE, mockup-status indicator, thumbnail strip once mockups exist, so the hub doubles as a mockup-progress tracker); sequencing wave diagram with experiment pills linking to spokes; "what's not here" exclusions; a "What We Need From {Client}" asks section (Provide / Confirm / Approve columns, each ask tagged with the experiments it unblocks).
- **Spoke (one page per experiment):** title/tier/page-chips/hypothesis header with deliberately quiet inline ICE; centerpiece control-vs-proposed mockup comparison with per-image change annotations and variation tabs (tabs collapse for single-variation experiments; mobile-scoped experiments render phone-width frames); why-this-should-work; win/loss panels; self-critique (kept, because preempting objections is persuasive); per-experiment before-launch asks; breadcrumb plus prev/next pager.
- **Visual system:** FunnelEnvy design language per the prior single-page deliverable pattern: IBM Plex Sans, CSS-variable palette, color-coded tier badges and callouts, browser-chrome mockup frames with lightbox zoom, sticky scroll-spy nav. These assets are emitted by the scaffolding script so they stay byte-identical across renders.
- **Pitch-focus principle:** the HTML curates; the markdown remains the analytical record. Measurement design (target metric, guardrail, threshold cells), inconclusive protocols, and bundled-elements disclosures stay markdown-only.

### Inputs and re-render

The sole content source is the gold roadmap markdown, plus optional per-experiment mockup artifacts from experiment-mockup. Re-render is a complete projection of the current markdown, mirroring hypothesis-generator's `Re-render Behavior` (no diffing, no merging).

**Mockup resolution contract.** The renderer resolves each roadmap experiment to its mockup artifacts deterministically: mockups are build inputs, not site-owned outputs. The renderer never produces or mutates mockup artifacts. In KB mode the renderer resolves them at `{kb_root}/deliverables/experiments/{slug}/`; this change adds the experiment-mockup KB write side that populates that base (see `Experiment-mockup dual-mode I/O`), so the KB mockup slots are populated once experiment-mockup has run for the same scope rather than always degrading to placeholders.

- For each experiment heading `### N. {Title}`, derive the mockup slug by applying `modules/slugify.md` to `{Title}`, using the same module and rules experiment-mockup uses (`Step 4: Generate Output Directory Slug`), so identical titles resolve to identical slugs.
- Resolve the source mockup directory at experiment-mockup's output base, `{deliverables}/experiments/{slug}/` (where `{deliverables}` is the deliverable root for the active mode per `Output placement`).
- When that directory exists with mockup artifacts (`mockup.html` plus screenshots), copy the display assets into the site's own asset tree at a number-keyed path, `{scope}-roadmap-site/assets/mockups/experiment-NN/`, and reference them with relative paths so the deployed site is self-contained. When it is absent, render labeled placeholder frames.
- The completion message reports any experiment with no matching mockup directory and any mockup directory matching no current experiment (an orphan signals a title rename between roadmap versions), surfacing drift rather than hiding it.

The number-keyed in-site asset path is stable within a render, so the deployed site never depends on slug stability; slug matching is used only to locate the source artifacts at build time.

### Experiment-mockup dual-mode I/O (folded into scope)

QA surfaced that the renderer's KB-mode mockup base (`{kb_root}/deliverables/experiments/{slug}/`) had no producer: experiment-mockup was legacy-only (no KB awareness, no `--scope`, no `kb_root`, writing only to `.claude/deliverables/experiments/`). The whole purpose of this change is to support the KB structure, so rather than ship a renderer whose KB mockup path is permanently empty, the user approved folding the experiment-mockup KB retrofit into this change.

experiment-mockup gains dual-mode I/O with parity to hypothesis-generator and roadmap-presentation:

- **Read side.** In KB mode, experiment-mockup reads the roadmap from `{kb_root}/deliverables/{scope}-experiment-roadmap.md` (the gold artifact) instead of `.claude/deliverables/experiment-roadmap.md`. Legacy mode is unchanged.
- **Write side.** In KB mode, mockups are written to `{kb_root}/deliverables/experiments/{slug}/`; legacy mode unchanged (`.claude/deliverables/experiments/{slug}/`). The KB-mode mockup output is co-located under the KB deliverables tree so roadmap-presentation resolves it via the mockup-resolution contract, but it is NOT a KB artifact (no `kb_layer` frontmatter): it is a derived deliverable, the same posture as the rendered site.
- **Mode resolution.** experiment-mockup adds `--scope` and `--no-kb` and mirrors hypothesis-generator and roadmap-presentation exactly: `--no-kb` forces legacy; a detected `Knowledge Bases` binding in the working repo CLAUDE.md plus a valid `--scope` selects KB mode; a missing or invalid `--scope` in KB mode is a HARD STOP that lists valid scopes; a failed detection falls back to legacy loudly (no `--kb` force flag). Because experiment-mockup consumes only the roadmap (the same input roadmap-presentation consumes), its mode-resolution check verifies only that the bound type skill defines `gold-experiment-roadmap`, identical to roadmap-presentation, not the fuller silver-artifact verification hypothesis-generator performs as a roadmap producer.

This is markdown-only (no Python scripts): SKILL.md (frontmatter `description`, Invocation flags, a new `KB Mode (Dual-Mode Output)` section, mode-aware preconditions/orchestrator steps/completion message/architecture notes, an inline changelog table with an `[Unreleased]` entry), `agent-header.md` (mode-aware I/O table), and the phase files (`capture.md`, `annotate.md`, `static-build.md` output-path references generalized to the orchestrator-provided directory). roadmap-presentation's mockup-resolution contract wording is updated so KB mockups read as "populated when experiment-mockup has run in the same scope," not "always placeholders."

### Output placement

The rendered site is written to a **sibling directory next to the roadmap markdown**, with **no `kb_layer` frontmatter**: it is a derived view, not a knowledge-base artifact, and the markdown remains the source of truth. The renderer is **dual-mode**, mirroring hypothesis-generator and experiment-mockup:

- **KB mode** (the run resolved a `{scope}`; gold artifact at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`): site at `{kb_root}/deliverables/{scope}-roadmap-site/`; mockup base at `{kb_root}/deliverables/experiments/`.
- **Legacy mode** (frontmatter-less `.claude/deliverables/experiment-roadmap.md`, no scope): site at `.claude/deliverables/roadmap-site/`; mockup base at `.claude/deliverables/experiments/`.

The sibling-directory placement was confirmed across all three reference renders (KB mode); the legacy path mirrors it with the scope prefix dropped. The `--present` chaining flag fires in both modes, rendering whichever roadmap the hypothesis-generator run just wrote. The design was validated in KB mode only, so Design adds a legacy-mode render case to `Verification Design > Validation`.

### Humanizer pass

Because the output is a client-facing deliverable, render-authored copy (condensed card hypotheses, mockup annotations, section leads: anywhere the renderer phrases rather than quotes) runs through a final humanizer pass before write. Rather than depend on the `humanizer` skill, which lives only at the requesting user's device level and cannot be a declared dependency of a plugin skill, the renderer **embeds the AI-writing-sign style rules as its own reference doc** (a lean embed for portability) and applies them in this pass. Passages quoted verbatim from the source markdown are already deliverable-grade and are exempt; the pass targets only prose the renderer authors.

### Non-goals (v1)

- **Hosting/deploy is out of scope for v1.** The multi-page output wants hosting rather than file sharing, but the deploy step is deferred: the skill's completion message documents the one-line static-host deploy command, and a managed deploy step is revisited as a follow-up once the render pipeline is proven.

### Reference implementation

A hand-built instance of the full design exists in the consuming client KB repo (PR-reviewed) and was regenerated three times during this Discovery work. It gives Design a concrete template for the page anatomy, shared stylesheet, and JS behaviors rather than a from-scratch spec, and it is the source of the drift, decoupling, and altitude observations above. The reference artifacts carry client content and are retained outside this repo.

## Requirements

These instructions implement the approved `Approach`. They cover the new `roadmap-presentation` skill, its scaffolding script, its reference docs, the section-mapping and curation logic, the mockup-resolution contract, dual-mode output placement, and the thin `--present` flag added to hypothesis-generator.

### R1. New skill: `roadmap-presentation`

Create `skills/roadmap-presentation/SKILL.md` following the SKILL.md format used by the other skills in this repo (YAML frontmatter with `name`, `version`, `description`; trigger-matching `description`; workflow sections; `## Scripts`; `## Output Files`; preconditions; quality checks; inline changelog table). Set initial `version: "0.1.0"` (released version set at release per the version cascade).

- **Trigger surface.** The `description` must match intents like "render the roadmap as a presentation", "roadmap site", "present the experiment roadmap", "roadmap HTML", plus the explicit `/roadmap-presentation` invocation.
- **Invocation.** `/roadmap-presentation [--scope <slug>] [--no-kb] [--out <dir>]`. Mode resolution mirrors hypothesis-generator's `KB Mode (Dual-Mode Output)` exactly: `--no-kb` forces legacy; a detected KB binding plus a valid `--scope` selects KB mode; KB mode with missing or invalid `--scope` is a HARD STOP that lists valid scopes. `--out` is an optional explicit output-directory override (otherwise the deterministic placement in R6 applies).
- **Single-agent skill.** No subagents. The skill is mostly deterministic transformation (the script in R2) plus three judgment passes (curation R4, section-mapping R4, humanizer R5). It does NOT perform web research, GA4/analytics calls, or any `.claude/context/` writes.
- **Phase shape.** Author the skill as an ordered phase sequence: (1) resolve mode and locate the source roadmap markdown; (2) parse the roadmap into an in-memory structure (sections, experiment items, dispositions); (3) resolve mockups per R3; (4) run the scaffolding script per R2 to emit chrome; (5) author per-page content (curation + section-mapping + humanizer) into the script-emitted shell; (6) write the site and emit the completion message per R3/R7. Inline each phase in SKILL.md or split into a `phases/` subdirectory consistent with the repo's larger skills; the deterministic-vs-judgment split in the Approach governs which work the script owns versus the agent.

### R2. Deterministic scaffolding script

Add `skills/roadmap-presentation/scripts/scaffold_site.py` (snake_case matching the skill, per repo conventions) and register it in the SKILL.md `## Scripts` table. The script is the drift mitigation from the `Approach > Architecture`: it emits every byte of chrome so renders cannot drift.

The script MUST emit, deterministically (byte-identical across runs given the same experiment count and page list):

- The shared CSS design system (FunnelEnvy visual language per `Approach > Page anatomy`: IBM Plex Sans, CSS-variable palette, color-coded tier badges and callouts, browser-chrome mockup frames, lightbox styles, sticky scroll-spy nav). Emitted as a single stylesheet asset referenced by every page.
- The shared JS behaviors (lightbox zoom, scroll-spy nav, variation-tab switching). Emitted as a single script asset.
- The page shell (HTML skeleton: head, asset links, nav container, content slot, footer) for the hub and for each spoke.
- The prev/next pager chain and breadcrumbs: given the ordered experiment list, the script wires each spoke's prev/next/hub links so navigation is correct without agent authoring.

**Inputs to the script.** A small JSON manifest the skill builds after parsing the roadmap: ordered experiment list (number, title, in-site asset path, mockup-present boolean), and output directory. **Outputs.** The directory tree with chrome in place and labeled content slots the agent then fills. Slug rules needed by the script (if any) are lifted from the `modules/slugify.md` Python fallback verbatim so script and skill agree.

The script contains no client content and no judgment logic (no curation, no copywriting): it is pure scaffolding.

### R3. Mockup-resolution contract

Implement exactly the contract in `Approach > Inputs and re-render`. For each roadmap experiment heading `### N. {Title}`:

- Derive the mockup slug by applying `modules/slugify.md` rules to `{Title}`, identical to experiment-mockup `Step 4: Generate Output Directory Slug`, so identical titles resolve to identical slugs.
- Resolve the source mockup directory at experiment-mockup's output base for the active mode: KB mode `{kb_root}/deliverables/experiments/{slug}/`; legacy mode `.claude/deliverables/experiments/{slug}/`.
- When that directory exists with `mockup.html` plus screenshot(s), copy the display assets into the site's own asset tree at a number-keyed path, `{site}/assets/mockups/experiment-NN/` (NN = the experiment's roadmap number, zero-padded), and reference them with relative paths so the deployed site is self-contained. The number-keyed in-site path is stable within a render; slug matching is used only to locate source artifacts at build time.
- When the source directory is absent, render labeled placeholder frames (per R4 spoke layout) instead.
- The completion message (R7) reports any experiment with no matching mockup directory and any mockup directory matching no current experiment (orphan = a title rename between roadmap versions), surfacing drift rather than hiding it.

The renderer never produces or mutates mockup artifacts: mockups are build inputs, not site-owned outputs. The KB-mode mockup base is populated by experiment-mockup's KB write side, added by this change in R10 (originally scoped as "no experiment-mockup change," reopened from QA when the KB mockup base was found to have no producer).

### R4. Curation and version-agnostic section-mapping (judgment work)

These are the agent's parse-and-map responsibilities, run against the parsed roadmap from R1 phase 2.

- **Version-agnostic section-mapping.** The renderer MUST read whatever top-level sections actually exist in the source roadmap and map them, never assuming a fixed shape. The source has appeared as three tiers, as disposition groups, and as a live-program-reconciliation table plus preliminary-results cards plus a separate post-rebuild backlog section (per `Approach > Architecture`). The mapper detects the present grouping and renders the hub index accordingly. It MUST handle item dispositions (reframed, held, superseded, net-new), not only cleanly scored experiments: each disposition gets a visible treatment on the hub and, where it has a per-experiment page, a spoke.
- **Curation (pitch-focus principle).** Drop measurement-design detail (target metric, guardrail, threshold cells), inconclusive-protocol detail, and bundled-elements disclosures from the rendered site. These stay markdown-only: the HTML pitches, the markdown remains the analytical record.
- **Hub page** per `Approach > Page anatomy`: hero with stat row and the roadmap's measurement-constraint callout; grouped experiment index cards (one-line hypothesis, compact ICE, mockup-status indicator, thumbnail strip once mockups exist); sequencing wave diagram with experiment pills linking to spokes; "what's not here" exclusions; a "What We Need From {Client}" asks section (Provide / Confirm / Approve columns, each ask tagged with the experiments it unblocks). `{Client}` resolves from the roadmap's own content, never hardcoded.
- **Spoke page** (one per experiment) per `Approach > Page anatomy`: title / tier / page-chips / hypothesis header with quiet inline ICE; centerpiece control-vs-proposed mockup comparison (per R3) with per-image change annotations and variation tabs (tabs collapse for single-variation experiments; mobile-scoped experiments render phone-width frames); why-this-should-work; win/loss panels; self-critique (kept: preempting objections is persuasive); per-experiment before-launch asks; breadcrumb plus prev/next pager (wired by R2).

### R5. Humanizer reference doc and pass

Because the renderer cannot declare the device-level `humanizer` skill as a dependency, embed the AI-writing-sign style rules as the skill's own reference doc.

- Add `skills/roadmap-presentation/references/ai-writing-signs.md` (a lean, portable embed of the AI-writing-sign rules: inflated symbolism, promotional language, vague attributions, em-dash overuse, rule of three, AI vocabulary, negative parallelisms, excessive conjunctive phrases). Register it in a SKILL.md reference table.
- Before write, the skill runs render-authored copy (condensed card hypotheses, mockup annotations, section leads: anywhere the renderer phrases rather than quotes) through one humanizer pass applying these rules. Passages quoted verbatim from the source roadmap markdown are already deliverable-grade and are exempt; the pass targets only renderer-authored prose.

### R6. Dual-mode output placement

The rendered site is written to a sibling directory next to the roadmap markdown, with NO `kb_layer` frontmatter (it is a derived view, not a KB artifact; the markdown remains the source of truth). Mirror hypothesis-generator and experiment-mockup:

- **KB mode** (resolved `{scope}`, gold at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`): site at `{kb_root}/deliverables/{scope}-roadmap-site/`; mockup base `{kb_root}/deliverables/experiments/`.
- **Legacy mode** (frontmatter-less `.claude/deliverables/experiment-roadmap.md`, no scope): site at `.claude/deliverables/roadmap-site/`; mockup base `.claude/deliverables/experiments/`.
- An explicit `--out <dir>` overrides the computed site path in either mode (mockup base is unaffected).
- Re-render is a complete projection of the current markdown (no diffing, no merging), mirroring hypothesis-generator's `Re-render Behavior`. A pre-existing site directory is overwritten.

### R7. Completion message

The skill's completion message reports: site output path, mode (KB/legacy), experiment count rendered, per-experiment mockup status (present / placeholder), any missing-mockup and orphan-mockup drift per R3, and the deferred-hosting note from `Approach > Non-goals` (the one-line static-host deploy command for the output directory). Hosting/deploy remains out of scope for v1.

### R8. Thin `--present` flag on hypothesis-generator

Add a `--present` flag to hypothesis-generator as a small companion edit (the renderer is the primary resource; this is the chaining affordance).

- Add a `--present` row to the `## Invocation` flags table (`skills/hypothesis-generator/SKILL.md` lines 50-56): default off; when set, invoke `roadmap-presentation` after a successful roadmap write, passing the same mode (KB `--scope` or legacy) so it renders whichever roadmap the run just wrote. Fires in both modes.
- The flag is purely a chaining affordance: it adds no analytical behavior and changes no scoring, pattern, or output-content logic. Note in the flag description that it runs the separate `roadmap-presentation` skill after write.
- Update the SKILL.md inline changelog with the `--present` addition. No version bump here (release-time per the cascade); the addition surfaces in the change doc's Closed-step CHANGELOG entry.

### R9. Repo registration (skill-is-a-package-deal)

Registering the new skill is a package deal: in the same change, update `README.md` (skills table row linking `skills/roadmap-presentation/SKILL.md`, skill count, and a `/roadmap-presentation` invocation example per the repo's `README Sync Rule`), the marketplace manifest if one lists skills, and `CLAUDE.md` (file map, skill list, workflow order entry after hypothesis-generator). No client names or client content in any registration edit.

### R10. experiment-mockup dual-mode I/O retrofit

Implement the experiment-mockup dual-mode I/O from `Approach > Experiment-mockup dual-mode I/O (folded into scope)`. Markdown-only (no scripts), with parity to hypothesis-generator and roadmap-presentation.

- **Read path.** In KB mode, experiment-mockup reads the roadmap from `{kb_root}/deliverables/{scope}-experiment-roadmap.md` (the gold artifact); legacy mode reads `.claude/deliverables/experiment-roadmap.md` unchanged.
- **Write path.** In KB mode, mockups write to `{kb_root}/deliverables/experiments/{slug}/`; legacy mode writes `.claude/deliverables/experiments/{slug}/` unchanged. The KB-mode output carries NO `kb_layer` frontmatter (derived deliverable, not a KB artifact); it is co-located so roadmap-presentation resolves it.
- **`--scope` and KB detection.** Add `--scope` and `--no-kb` flags. Mirror hypothesis-generator and roadmap-presentation exactly: `--no-kb` forces legacy; a detected `Knowledge Bases` binding plus a valid `--scope` selects KB mode; missing/invalid `--scope` in KB mode is a HARD STOP listing valid scopes; failed detection falls back to legacy loudly; no `--kb` force flag. The detection verifies only that the bound type skill defines `gold-experiment-roadmap` (experiment-mockup consumes only the roadmap, like roadmap-presentation).
- **Error states and hard precondition.** The roadmap-exists hard gate becomes mode-aware (it checks the resolved mode's roadmap path and reports it in the STOP message). The hypothesis-not-found gate is mode-agnostic.
- **Completion message.** Report the resolved I/O mode (KB scope or legacy) and the resolved output directory, alongside the existing browser-mode line.
- **`description` + changelog.** Update the SKILL.md `description` frontmatter to mention KB mode. experiment-mockup has no changelog surface today; add an inline `## Changelog` table (matching roadmap-presentation's format) and record the dual-mode retrofit as an `[Unreleased]` entry. Do NOT bump the version number (release-time per the cascade).
- **Path sweep.** Update every roadmap-read and mockup-write path reference across SKILL.md AND `phases/*.md` (`capture.md`, `annotate.md`, `static-build.md`) AND `agent-header.md`. Generalize phase output-path references to the orchestrator-provided output directory, keeping the legacy path as the canonical example.
- **roadmap-presentation wording.** Update roadmap-presentation's mockup-resolution wording so KB mockups read as "populated when experiment-mockup has run in the same scope," not framed as always degrading to placeholders. Keep the change minimal.
- No client names or client content in any edit.

## Verification Design

### Validation

Universal acceptance criteria derived from `Requirements`. Each is confirmed during QA against the implemented skill. The render passes below use a non-client gold roadmap fixture (or a sanitized local roadmap) so no client content enters this public repo.

1. **KB-mode full render (R1, R2, R4, R6).** Running `/roadmap-presentation --scope <slug>` against a real gold-experiment-roadmap artifact produces a site at `{kb_root}/deliverables/{scope}-roadmap-site/` containing a hub page plus exactly one spoke per experiment in the roadmap, with the shared stylesheet and JS assets present and referenced by every page.
2. **Working relative navigation (R2).** Every spoke's breadcrumb and prev/next pager links resolve to the correct sibling pages and the hub via relative paths; the hub's index cards and sequencing-diagram pills link to the correct spokes. No absolute or broken links (verified by opening the site from its directory and by link audit of the emitted HTML).
3. **Legacy-mode render (R6).** Running `/roadmap-presentation --no-kb` (or with no KB binding) against `.claude/deliverables/experiment-roadmap.md` produces a site at `.claude/deliverables/roadmap-site/` with the same hub-plus-spoke structure and working navigation, scope prefix dropped.
4. **Placeholder behavior (R3, R4).** For an experiment with no matching mockup directory, the spoke renders labeled placeholder frames in the comparison slot (not an error, not an empty slot), and the completion message lists that experiment as missing a mockup.
5. **Mockup-present behavior (R3).** For at least one experiment with experiment-mockup output present, the spoke renders the control-vs-proposed comparison from the copied assets, the assets are copied into `{site}/assets/mockups/experiment-NN/` and referenced relatively (the site is self-contained: it renders correctly when the source mockup directory is removed after build), and the experiment is reported as mockup-present.
6. **Drift surfacing (R3, R7).** Given a mockup directory whose slug matches no current experiment title, the completion message reports it as an orphan; given an experiment with no mockup directory, it reports it as missing.
7. **Version-agnostic section-mapping (R4).** The renderer maps a roadmap whose grouping is not three clean tiers (e.g., disposition groups or a reconciliation-table shape) without error, rendering each disposition (reframed, held, superseded, net-new) with a visible hub treatment.
8. **Curation (R4).** The rendered HTML omits measurement-design cells, inconclusive-protocol detail, and bundled-elements disclosures; those remain present in the source markdown (the markdown is unmodified by the render).
9. **Humanizer pass (R5).** Renderer-authored prose (card hypotheses, annotations, section leads) shows no uncorrected AI-writing signs per the embedded `references/ai-writing-signs.md`; verbatim-quoted roadmap passages are unchanged.
10. **No `kb_layer` on the site (R6).** No emitted site file carries `kb_layer` frontmatter; the site is a derived view, not a KB artifact.
11. **`--present` chaining (R8).** `/hypothesis-generator --present` (and `--present --scope <slug>` in KB mode) writes the roadmap and then invokes `roadmap-presentation` against the just-written roadmap in the same mode; the flag adds no change to roadmap analytical content.
12. **Repo registration (R9).** `README.md` skills table, skill count, and invocation examples include `roadmap-presentation`; `CLAUDE.md` file map / skill list / workflow order include it; the marketplace manifest (if it lists skills) includes it.
13. **No client content committed (hard constraint).** No client names or client content appear in any file added or modified by this change (`grep -icE` sweep clean across the skill, script, references, tests, fixtures, and the change doc).
14. **experiment-mockup KB-mode roadmap read (R10).** In KB mode (resolved `{scope}`), experiment-mockup reads the gold roadmap at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`, not the legacy path. The roadmap-exists hard precondition checks and reports that resolved path. Legacy mode still reads `.claude/deliverables/experiment-roadmap.md`.
15. **experiment-mockup KB-mode mockup write (R10).** In KB mode, mockups are written to `{kb_root}/deliverables/experiments/{slug}/` (no `kb_layer` frontmatter on any output file). Legacy mode still writes `.claude/deliverables/experiments/{slug}/`. The completion message reports the resolved I/O mode and output directory.
16. **experiment-mockup legacy paths unchanged (R10).** With `--no-kb` or no KB binding, experiment-mockup's read path, write path, and completion message match pre-change behavior exactly (the only legacy-mode diffs are additive: the new flags exist but are inert).
17. **End-to-end KB mockup resolution (R3, R10).** With experiment-mockup having run in KB mode for a scope, roadmap-presentation's mockup-resolution contract resolves the populated `{kb_root}/deliverables/experiments/{slug}/` directory and renders the control-vs-proposed comparison (not a placeholder) for that experiment; an experiment with no mockup still renders placeholders. roadmap-presentation wording no longer frames KB mockups as always-placeholder.
18. **Detection parity with hypothesis-generator (R10).** experiment-mockup's `--scope`/`--no-kb` semantics, the `Knowledge Bases` detection trigger, the missing/invalid `--scope` HARD STOP, and the loud legacy fallback behave identically to hypothesis-generator and roadmap-presentation (verified by reading the three skills' Mode Resolution Procedures side by side).

### Tests

Required because `Approach > Change Profile` records `script-affecting: yes` (R2 adds `skills/roadmap-presentation/scripts/scaffold_site.py` to a `## Scripts` table).

#### Affected scripts

| Script | Path | Change | Test layer |
|--------|------|--------|------------|
| `scaffold_site.py` | `skills/roadmap-presentation/scripts/scaffold_site.py` | Added (new deterministic scaffolding script: emits CSS/JS/page-shell/pager-chain from a manifest) | `unit` |

No other scripts are added or modified. The `--present` flag on hypothesis-generator (R8) is a SKILL.md prose edit, not a script change; the rest of the skill (R1, R3, R4, R5) is agent judgment work that is not unit-testable and is covered by `Verification Design > Validation` instead. The folded-in experiment-mockup dual-mode work (R10) is markdown-only (SKILL.md, agent-header.md, phases) and adds no Python scripts, so it introduces no new unit tests; its behavior is covered by `Verification Design > Validation` criteria 14-18. The `scaffold_site.py` test suite is unchanged by the scope expansion.

#### Coverage analysis

`scaffold_site.py` is a new script with no existing test coverage. There is no existing `_tests/` file that exercises it. The repo's test layout (`_tests/unit/test_<script_name>.py`, importlib-loaded module, `unittest`, established by `test_page_select.py` and `test_content_hash.py`) is the pattern to follow. No `_tests/fixtures/` or `_tests/helpers.py` exist yet; this change introduces fixtures under `_tests/fixtures/` only if a static input file is cleaner than an inline dict (see below).

#### New test files, cases, and fixtures

- **New test file:** `_tests/unit/test_scaffold_site.py`, importlib-loading `skills/roadmap-presentation/scripts/scaffold_site.py`, matching the `test_page_select.py` structure (module loader helper + `unittest.TestCase` classes).
- **Key cases:**
  1. **Determinism:** scaffolding the same manifest twice yields byte-identical chrome (CSS, JS, page shells, pager links) - the core drift-mitigation guarantee.
  2. **Pager chain correctness:** for an N-experiment manifest, spoke 1 has no prev (or links to hub), spoke N has no next, interior spokes link to correct neighbors, every spoke links back to the hub.
  3. **Page count:** one hub shell plus exactly N spoke shells emitted for N experiments.
  4. **Number-keyed asset paths:** spoke N references `assets/mockups/experiment-NN/` with correct zero-padding, and mockup-present vs placeholder is reflected in the emitted shell per the manifest boolean.
  5. **Asset references are relative:** emitted HTML references the stylesheet and JS via relative paths (no absolute paths, no client domains).
  6. **No client content / no judgment content:** emitted chrome contains no client names and no curated copy (the script emits structure only; content slots are empty/labeled). A regex sweep of the output asserts the client-name denylist is absent.
  7. **Edge cases:** single-experiment manifest (pager collapses correctly: spoke 1 is both first and last); empty manifest (zero experiments) handled without crash (hub-only or explicit error per the script's contract).
- **Fixtures:** prefer inline manifest dicts in the test for readability; add a static `_tests/fixtures/roadmap_manifest_sample.json` only if multiple cases share a non-trivial manifest. Any fixture carries synthetic (non-client) experiment titles.

#### Expected test outcomes

- All cases pass under `python -m unittest _tests.unit.test_scaffold_site -v`.
- Determinism case catches any future nondeterministic emission (dict ordering, timestamp injection) that would reintroduce drift.
- Pager and page-count cases catch navigation regressions (the failure that put a reference site two structural versions behind).
- The client-content case is a guardrail regression: it fails if any client string ever enters the scaffold output.
- The full suite (`python -m unittest discover _tests/ -v`) passes with the new file added (no regression to `test_page_select.py`, `test_content_hash.py`, `test_aa_audit.py`).

## Verification Results

### Validation Outcomes

Fresh re-QA walk over all 18 criteria (prior-pass outcomes re-confirmed against observed file state, not inherited). 13/18 confirmed by code, test, or contract inspection; 5 design-reviewed and deferred to a live LLM render or live browser-mockup run (which QA cannot execute). The `scaffold_site.py` chrome and the full triangle of mode-resolution and producer/consumer paths were verified directly: the full suite is 74/74; the producer (experiment-mockup KB write) and consumer (roadmap-presentation KB resolve) paths agree exactly at `{kb_root}/deliverables/experiments/<slug>/`; both read the same gold roadmap hypothesis-generator writes at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`.

- 1 (KB-mode full render): partial. The script half (hub + N spokes, shared `styles.css` + `site.js` referenced by every page, number-keyed asset dirs) confirmed via `TestPageCount`/`TestRelativeReferences`/`TestWriteSite`. KB-path resolution + per-page content authoring requires the LLM renderer. Deferred to a live KB render run.
- 2 (working relative navigation): confirmed. `TestPagerChain` covers the chain: spoke 1 prev-disabled + links forward; last spoke next-disabled; interior spokes link both neighbors; every spoke links to the hub. `TestRelativeReferences` confirms `styles.css`/`site.js` referenced by bare relative path with no absolute or client-domain links.
- 3 (legacy-mode render): partial, same split as criterion 1. The placement logic (scope prefix dropped) is design-reviewed in `Operating Modes`; the script is mode-agnostic (output path passed in). Deferred to a live legacy render run for the content half.
- 4 (placeholder behavior): confirmed at the script and contract level. Manifest `mockup_present: false` is carried into the shell; Phase 5 renders `.mock-pending` frames (CSS class emitted by the script, verified in `STYLES_CSS`) and the completion message lists the experiment as missing. Live render confirms the agent half.
- 5 (mockup-present + self-contained): design-reviewed. The number-keyed in-site asset copy and relative referencing are specified in Phase 5 and Quality Rule 5; asset dirs are pre-created by the script (`TestWriteSite` confirms `assets/mockups/experiment-NN/` dirs are created). The "renders after source removal" assertion needs a live render with real mockup artifacts. Deferred.
- 6 (drift surfacing): design-reviewed in Phase 3 step 4 and `Completion Message`. Missing and orphan reporting is agent-side; no script surface to execute. Deferred to a live render.
- 7 (version-agnostic section-mapping): design-reviewed in Phase 2, Phase 5, and Quality Rule 3 (dispositions reframed/held/superseded/net-new have emitted CSS classes `.disp.reframed|.held|.superseded|.net-new`, verified in `STYLES_CSS`). Agent judgment work; deferred to a live render against a non-tier-shaped roadmap.
- 8 (curation): confirmed by construction. Phase 5 and Quality Rule 4 drop measurement-design/inconclusive/bundled detail; the skill has no write path back to the source markdown (it reads only), so "markdown unmodified" holds structurally.
- 9 (humanizer pass): design-reviewed. `references/ai-writing-signs.md` is present (10 signs, em-dash ban included), registered in the SKILL.md reference table, and applied in Phase 5 over authored prose only (verbatim quotes exempt per Quality Rule 8). Output quality is a live-render check.
- 10 (no `kb_layer` on the site): confirmed. The script emits no frontmatter on any file (HTML shells + CSS + JS, inspected in `scaffold_site.py`). Quality Rule 7 reinforces it for agent-authored content.
- 11 (`--present` chaining): confirmed by inspection. hypothesis-generator SKILL.md line 57 has the `--present` flags-table row, line 569 has the `Re-render Behavior` chaining note, and the CHANGELOG carries the addition; the flag is documented as a pure chaining affordance with no analytical change. Live chained run deferred.
- 12 (repo registration): confirmed. README skills table (11 rows, roadmap-presentation at line 20), Quick Start examples (lines 47-48), and narrative (line 120) include it; marketplace.json lists 11 skills including roadmap-presentation; CLAUDE.md file map (line 80), workflow order entry 12 (line 280), and dedicated skill section (line 483) include it.
- 13 (no client content committed): confirmed. Client denylist sweep (`grep -ricE`) is 0 across both skill dirs, the script, references, test, README, marketplace.json, the in-repo CLAUDE.md edits, and the hypothesis-generator edits. The test denylist is fragment-reassembled (`"emb" + "ark"`) so literal client strings never appear in the public-repo file while the guardrail still tests for them (`TestNoClientContent`).
- 14 (experiment-mockup KB-mode roadmap read): confirmed by inspection. KB-mode read resolves to `{kb_root}/deliverables/{scope}-experiment-roadmap.md` (SKILL.md lines 62, 81, 125); the roadmap-exists hard precondition (line 92) is mode-aware and reports the resolved path; legacy reads `.claude/deliverables/experiment-roadmap.md` unchanged.
- 15 (experiment-mockup KB-mode mockup write): confirmed by inspection. KB-mode write resolves to `{kb_root}/deliverables/experiments/<slug>/` (SKILL.md lines 62, 82, 157); the output carries no `kb_layer` (lines 84, 352); the Step 7 completion message reports resolved I/O mode + output directory (lines 327-328). Legacy writes `.claude/deliverables/experiments/<slug>/` unchanged.
- 16 (experiment-mockup legacy paths unchanged): confirmed. With `--no-kb` or no KB binding, the read path, write path, and completion message match pre-change behavior; the only legacy-mode diffs are additive (`--scope` warn-and-ignore, `--no-kb` inert-when-no-binding). Step 1b mode resolution returns legacy on `--no-kb` (line 68) or absent `Knowledge Bases` section (line 69).
- 17 (end-to-end KB mockup resolution): confirmed at the contract level. experiment-mockup's KB write base and roadmap-presentation's KB mockup base are the byte-identical path `{kb_root}/deliverables/experiments/<slug>/`; both derive the slug from the title via the shared `modules/slugify.md` rules, so producer-write and consumer-read directory names agree. roadmap-presentation's mockup-resolution wording (SKILL.md lines 152, 94) now reads "populated when experiment-mockup has run for the same mode and scope," no longer always-placeholder. The live render half (renders comparison not placeholder for a populated experiment) is deferred.
- 18 (detection parity with hypothesis-generator): confirmed by side-by-side read. experiment-mockup's mode-resolution steps 1, 2, 4 and the no-`--kb` note are byte-identical to roadmap-presentation; step 3 differs only in a parenthetical descriptor and both verify only `gold-experiment-roadmap`. This is correct consumer parity (both consume only the roadmap): the intended, documented deviation from hypothesis-generator's step 3, which additionally verifies `silver-strategy-context` + `bronze-company-facts` as a roadmap producer. The `--scope`/`--no-kb` semantics, the `Knowledge Bases` detection trigger, the missing/invalid `--scope` HARD STOP, and the loud legacy fallback behave identically across all three.

### Tests Results

| Metric | Value |
|--------|-------|
| Total  | 74    |
| Passed | 74    |
| Failed | 0     |

Full suite `python -m unittest discover _tests/ -v`: 74/74 pass (18 new `test_scaffold_site.py` cases plus the pre-existing `test_page_select.py`, `test_content_hash.py`, `test_aa_audit.py` with no regression). The new cases cover determinism, order-independence, pager chain, page count, number-keyed assets, relative refs, no-client-content, no-em-dash, edge cases (single-experiment, empty, missing-field-raises), and `write_site` disk output.

## Changelog

| Version | Changes |
|---------|---------|
| 0.7.0 | Reopened from QA to Build: user approved folding experiment-mockup KB dual-mode into scope (resolves QA Open Issue 1: the renderer's KB mockup base had no producer; rather than ship a permanently-empty KB mockup path, experiment-mockup gains a KB write side). QA Open Issue 2 (root working-copy CLAUDE.md pre-existing-stale, outside the public repo) stays out of scope and is deferred to a separate cleanup. `## Open Issues` section removed. Approach expanded: new `Experiment-mockup dual-mode I/O (folded into scope)` subsection; the "no experiment-mockup change required" statements in `Inputs and re-render` and R3 corrected. New R10 (experiment-mockup dual-mode: read path, write path, `--scope`/`--no-kb` detection mirroring hypothesis-generator and roadmap-presentation, mode-aware error states + hard precondition + completion message, `description` + inline changelog touch, phases path sweep, roadmap-presentation wording fix). Five new Validation criteria (14-18). Tests note: experiment-mockup adds no scripts, scaffold_site.py suite unchanged. Implemented R10: experiment-mockup SKILL.md (description, flags, new `KB Mode (Dual-Mode Output)` section, mode-aware Steps 1b/2/4 + preconditions + completion + architecture, inline `## Changelog` with `[Unreleased]`), agent-header.md (mode-aware I/O table), phases (`capture.md`, `annotate.md`, `static-build.md` output-path generalization); roadmap-presentation mockup-resolution wording updated; in-repo CLAUDE.md experiment-mockup entry gains dual-mode I/O + flags. Full suite re-run: 74/74 pass (experiment-mockup adds no tests). Validators clean; em-dash sweep 0; client-name sweep 0 across all touched files. Change Profile unchanged (script-affecting yes via scaffold_site.py; experiment-mockup edits markdown-only). Re-QA: 18/18 criteria walked (13 confirmed, 5 deferred to a live render); producer/consumer paths confirmed in agreement. One QA finding resolved in place by folding in a CLAUDE.md dual-mode consistency fix (Cross-Layer Contracts exception + L2 deliverable table note now reflect experiment-mockup KB-mode paths). |
| 0.6.0 | Build: moved to `_dev/5-build/`, status Build. Entry re-review confirmed Requirements against observed file state (reference site design system, `modules/slugify.md` rules, hypothesis-generator `Invocation` flags table + `Re-render Behavior`, `_tests/unit/test_<script>.py` importlib+unittest convention); no material findings. Implemented R1 (new `skills/roadmap-presentation/SKILL.md`: dual-mode resolution, 6-phase pipeline, mockup-resolution contract, completion message, scripts + reference tables), R2 (`scripts/scaffold_site.py`: deterministic CSS/JS/page-shell/pager-chain emission from a JSON manifest, number-keyed asset dirs, no client content), R3 (slug-based mockup resolution inlined in Phase 3 + summary), R4 (curation + version-agnostic section-mapping in Phase 5 with disposition handling), R5 (`references/ai-writing-signs.md` embed + Phase 5 humanizer pass), R6 (dual-mode placement, no `kb_layer`, `--out` override), R7 (completion message + deferred-hosting note), R8 (thin `--present` flag on hypothesis-generator: Invocation table row + Re-render Behavior note + CHANGELOG `[Unreleased]` entry, no version bump), R9 (README skills table + invocation + narrative, marketplace.json skill path + count, both CLAUDE.md file maps/skill lists/workflow order). Authored `_tests/unit/test_scaffold_site.py` (18 cases: determinism, order-independence, pager chain, page count, asset paths, relative refs, no-client-content, no-em-dash, edge cases, write_site); all pass. Full suite 74/74 pass. Mechanical validators clean (frontmatter_validate `[]`, link_audit `[]`); em-dash sweep 0; client denylist sweep 0 across skill + test. Open finding for QA: the root working-copy `CLAUDE.md` (project-root context file, outside the public repo) file map is pre-existing-stale (missing landing-page-generator, voice-inference, live-capture, experiment-mockup, aa-audit); roadmap-presentation added per R9, broader reconciliation out of scope. |
| 0.5.0 | Design: moved to `_dev/3-design/`, status Design. Entry re-review confirmed the Approach against observed file state (experiment-mockup `Step 4` title-derived slug + `mockup.html`/`mockup-screenshot.png` Output Files; hypothesis-generator `Invocation` flags table and `Re-render Behavior`; `modules/slugify.md` 6-step rules + Python fallback; `_tests/unit/test_<script>.py` importlib+unittest convention). Authored `Requirements` (R1 new `roadmap-presentation` skill, R2 deterministic `scaffold_site.py`, R3 mockup-resolution contract, R4 curation + version-agnostic section-mapping, R5 embedded humanizer reference doc + pass, R6 dual-mode output placement, R7 completion message, R8 thin `--present` flag on hypothesis-generator, R9 repo registration). Authored `Verification Design > Validation` (13 acceptance criteria incl. KB-mode and legacy-mode renders, placeholder + mockup-present behavior, drift surfacing, no-client-content). Authored `Verification Design > Tests` (script-affecting: `scaffold_site.py` unit tests at `_tests/unit/test_scaffold_site.py`: determinism, pager chain, page count, number-keyed assets, relative refs, client-content guardrail, edge cases). Added `Tests Results` stub. Scores unchanged (impact 4 / confidence 4 / ease 2). |
| 0.4.0 | Discovery (entry re-review + OQ resolution): grounded the Approach against observed file state (hypothesis-generator v1.6.0 `Re-render Behavior`; experiment-mockup v1.2.0 name-slug output dir). Resolved both remaining Open Issues into the Approach and removed `## Open Issues`. OQ1 (mockup contract): concrete slug-based resolution contract under `Inputs and re-render`: renderer slugifies titles via `modules/slugify.md` to locate experiment-mockup output, copies display assets into a number-keyed in-site asset tree (`{scope}-roadmap-site/assets/mockups/experiment-NN/`) for a self-contained deployable site, placeholder frames when absent, orphan/missing reporting in the completion message; no experiment-mockup change required. OQ2 (mode scope): renderer is dual-mode, KB `{kb_root}/deliverables/{scope}-roadmap-site/` and legacy `.claude/deliverables/roadmap-site/`, `--present` fires in both; Design adds a legacy-mode validation case. `description` frontmatter de-narrowed from gold-only to gold-or-legacy. |
| 0.3.0 | Discovery: moved to `_dev/2-discovery/`, status Discovery. Authored `Approach > Change Profile` (script-affecting yes, performance-affecting no, test-eval-only no). Resolved four of five OQs into the Approach narrative: separate `roadmap-presentation` skill plus a thin `--present` flag on hypothesis-generator (OQ1); sibling `deliverables/{scope}-roadmap-site/` output with no `kb_layer` (OQ3); deploy deferred as a v1 non-goal (OQ4); embedded humanizer style rules instead of a `humanizer` skill dependency (OQ5). Added the skill-backed-by-deterministic-script architecture (drift mitigation; curation, version-agnostic section-mapping, and humanizer as the judgment work). Re-targeted `resource_name` to `roadmap-presentation`. Fixed Current State drift (hypothesis-generator v1.5.0 to v1.6.0). One OQ remains for Design (precise experiment-number-to-mockup-directory mapping). |
| 0.2.0 | Humanizer pass added to Approach as a user requirement (render-authored copy only; verbatim gold-markdown passages exempt); OQ 5 seeded for the humanizer dependency (device-level skill: detect-and-degrade vs embedded style rules); reference-implementation note added (hand-built instance now exists in the consuming client KB repo). |
| 0.1.0 | Initial backlog change document: multi-page roadmap presentation render from gold-experiment-roadmap markdown, design validated via wireframe session; four approach OQs seeded (flag vs. skill, mockup contract, output placement, deploy). |
