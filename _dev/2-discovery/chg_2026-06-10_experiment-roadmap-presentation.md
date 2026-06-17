---
fe-managed: true
name: experiment-roadmap-presentation
description: >
  Render a client-facing, multi-page HTML presentation from a gold-experiment-roadmap
  markdown artifact: a hub overview page (tier-grouped experiment index, sequencing
  diagram, client asks) plus one pitch-focused spoke page per experiment with a
  control-vs-proposed mockup comparison slot fed by experiment-mockup outputs.
governed_by: change-management/change-document
status: Discovery
resource_name: roadmap-presentation
resource_version: "TBD"
impact: 4
confidence: 4
ease: 2
version: "0.3.0"
created: 2026-06-10
updated: 2026-06-17
---
# Experiment Roadmap Presentation Render

## Open Issues

**Source:** Approach OQ
**Generated:** 2026-06-10 PT

### Findings Detail

| # | Source | Finding | Description | Recommendation |
|---|---|---|---|---|
| 1 | Approach OQ | Mockup integration contract (precise per-number mapping) | The chosen direction is set in the Approach: a per-scope mockup directory convention keyed to the roadmap experiment, aligned with experiment-mockup's `Output Files` convention (which writes to a per-hypothesis slug directory keyed off the slugified experiment name, not the experiment number). The renderer needs one deterministic glob to populate each spoke's comparison frames and the hub's per-card mockup-status indicator. The exact mapping (experiment number to mockup directory, given experiment-mockup keys by name-slug) is the remaining detail. | Specify the number-to-directory mapping during Design, deriving it from experiment-mockup's slug rules so a roadmap experiment resolves deterministically to its mockup directory; absent mockups render as labeled placeholder frames. |

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

- **script-affecting: yes.** The renderer is a skill backed by a deterministic scaffolding script (see `Architecture`). Adding that Python script to the new skill's `## Scripts` surface flips this flag and pulls in test authoring.
- **performance-affecting: no.** This skill does not alter a performance-sensitive analytical surface under skill-management's eval policy. The render is mostly deterministic transformation plus a single humanizer pass over render-authored copy; it has no ICE-scoring, pattern-matching, or hypothesis-construction surface that evals govern.
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

The sole content source is the gold roadmap markdown, plus optional per-experiment mockup artifacts from experiment-mockup. Re-render is a complete projection of the current markdown, mirroring hypothesis-generator's `Re-render Behavior` (no diffing, no merging). The precise mapping from a roadmap experiment to its mockup directory is the one remaining Design detail (see `## Open Issues`): the direction is a per-scope mockup directory convention aligned with experiment-mockup's `Output Files` convention, with absent mockups rendering as labeled placeholder frames.

### Output placement

The rendered site is written to a **sibling directory next to the gold roadmap markdown** (`deliverables/{scope}-roadmap-site/`), with **no `kb_layer` frontmatter**: it is a derived view, not a knowledge-base artifact, and the markdown remains the source of truth. This was confirmed across all three reference renders.

### Humanizer pass

Because the output is a client-facing deliverable, render-authored copy (condensed card hypotheses, mockup annotations, section leads: anywhere the renderer phrases rather than quotes) runs through a final humanizer pass before write. Rather than depend on the `humanizer` skill, which lives only at the requesting user's device level and cannot be a declared dependency of a plugin skill, the renderer **embeds the AI-writing-sign style rules as its own reference doc** (a lean embed for portability) and applies them in this pass. Passages quoted verbatim from the source markdown are already deliverable-grade and are exempt; the pass targets only prose the renderer authors.

### Non-goals (v1)

- **Hosting/deploy is out of scope for v1.** The multi-page output wants hosting rather than file sharing, but the deploy step is deferred: the skill's completion message documents the one-line static-host deploy command, and a managed deploy step is revisited as a follow-up once the render pipeline is proven.

### Reference implementation

A hand-built instance of the full design exists in the consuming client KB repo (PR-reviewed) and was regenerated three times during this Discovery work. It gives Design a concrete template for the page anatomy, shared stylesheet, and JS behaviors rather than a from-scratch spec, and it is the source of the drift, decoupling, and altitude observations above. The reference artifacts carry client content and are retained outside this repo.

## Requirements

Stub. Filled during Design.

## Verification Design

### Validation

Stub. Filled during Design. Must include: a render pass against a real gold-experiment-roadmap artifact producing the hub plus one spoke per experiment with working relative navigation; placeholder behavior verified for experiments without mockups; mockup-present behavior verified for at least one experiment with experiment-mockup output; no client content committed to this repo.

## Verification Results

### Validation Outcomes

Pending. Populated during QA.

## Changelog

| Version | Changes |
|---------|---------|
| 0.3.0 | Discovery: moved to `_dev/2-discovery/`, status Discovery. Authored `Approach > Change Profile` (script-affecting yes, performance-affecting no, test-eval-only no). Resolved four of five OQs into the Approach narrative: separate `roadmap-presentation` skill plus a thin `--present` flag on hypothesis-generator (OQ1); sibling `deliverables/{scope}-roadmap-site/` output with no `kb_layer` (OQ3); deploy deferred as a v1 non-goal (OQ4); embedded humanizer style rules instead of a `humanizer` skill dependency (OQ5). Added the skill-backed-by-deterministic-script architecture (drift mitigation; curation, version-agnostic section-mapping, and humanizer as the judgment work). Re-targeted `resource_name` to `roadmap-presentation`. Fixed Current State drift (hypothesis-generator v1.5.0 to v1.6.0). One OQ remains for Design (precise experiment-number-to-mockup-directory mapping). |
| 0.2.0 | Humanizer pass added to Approach as a user requirement (render-authored copy only; verbatim gold-markdown passages exempt); OQ 5 seeded for the humanizer dependency (device-level skill — detect-and-degrade vs embedded style rules); reference-implementation note added (hand-built instance now exists in the consuming client KB repo). |
| 0.1.0 | Initial backlog change document — multi-page roadmap presentation render from gold-experiment-roadmap markdown, design validated via wireframe session; four approach OQs seeded (flag vs. skill, mockup contract, output placement, deploy). |
