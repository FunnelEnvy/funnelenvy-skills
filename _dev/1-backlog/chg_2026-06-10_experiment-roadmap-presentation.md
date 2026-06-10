---
fe-managed: true
name: experiment-roadmap-presentation
description: >
  Render a client-facing, multi-page HTML presentation from a gold-experiment-roadmap
  markdown artifact: a hub overview page (tier-grouped experiment index, sequencing
  diagram, client asks) plus one pitch-focused spoke page per experiment with a
  control-vs-proposed mockup comparison slot fed by experiment-mockup outputs.
governed_by: change-management/change-document
status: Backlog
resource_name: hypothesis-generator
resource_version: "TBD"
impact: 4
confidence: 4
ease: 2
version: "0.2.0"
created: 2026-06-10
updated: 2026-06-10
---
# Experiment Roadmap Presentation Render

## Open Issues

**Source:** Approach OQ
**Generated:** 2026-06-10 PT

### Findings Detail

| # | Source | Finding | Description | Recommendation |
|---|---|---|---|---|
| 1 | Approach OQ | Flag vs. separate skill | User framing was "maybe as a flag" on hypothesis-generator. Skill-management decision factors lean toward a separate renderer skill: it is invoked by its own user intent ("render the roadmap presentation"), its re-render lifecycle is decoupled from generation (re-runs whenever experiment-mockup adds mockups, without regenerating analysis), and rendering is formatting work, not Opus-grade analysis. | Separate skill (e.g., `roadmap-presentation`) plus a thin chaining flag on hypothesis-generator (e.g., `--present`) that invokes it after a successful roadmap write. Resolve at Discovery; `resource_name` re-targets if accepted. |
| 2 | Approach OQ | Mockup integration contract | Spoke pages center on a control-vs-proposed comparison fed by experiment-mockup outputs. There is no defined naming/location convention linking a mockup artifact to a roadmap experiment number, and the renderer needs a deterministic glob to populate frames and the hub's per-card mockup-status indicator. | Define a per-scope mockup directory convention keyed by experiment number during Design, aligned with experiment-mockup's existing `Output Files` conventions; absent mockups render as labeled placeholder frames. |
| 3 | Approach OQ | Rendered HTML placement in KB repos | The gold artifact is the markdown; the HTML presentation is a derived view, not a `kb_layer` artifact. Where the rendered site lives in a consuming KB repo (and whether it is committed) is ungoverned. | Sibling directory next to the gold artifact (e.g., `deliverables/{scope}-roadmap-site/`), no `kb_layer` frontmatter, markdown remains source of truth. Confirm against kb-start governance during Discovery. |
| 4 | Approach OQ | Hosting/deploy step | The multi-page output wants hosting (Cloudflare Pages discussed) rather than file sharing. Deploy could be a skill step or stay manual. | Out of scope for v1 — document the one-line `wrangler pages deploy` command in the skill's completion message; revisit as a follow-up once the render pipeline is proven. |
| 5 | Approach OQ | Humanizer dependency resolution | The required humanizer pass depends on the `humanizer` skill, which currently lives at the requesting user's device level — not in this plugin or a marketplace plugin this skill can declare a dependency on. A plugin skill cannot assume a device-level skill exists at run time. | Resolve at Discovery: either (a) detect-and-degrade — run the pass when `humanizer` resolves, warn and skip when absent; or (b) embed the relevant style rules (the AI-writing-sign checklist) as a renderer-owned reference doc so the pass has no external dependency. Lean (b) for portability. |

## Background

A 2026-06-10 working session explored how to visually present the experiment roadmaps this plugin generates. The trigger: a hand-built single-page HTML strategy deliverable from a prior engagement demonstrated how much more effective a styled, navigable presentation is than raw markdown for client review. A wireframe iteration against a live roadmap instance in a client KB repo converged on a validated multi-page design (wireframes retained outside this repo — they carry client content). This change productizes that design as a repeatable render path from any `gold-experiment-roadmap` artifact.

## Current State

- hypothesis-generator (v1.5.0, dual-mode) writes a single markdown roadmap: legacy `.claude/deliverables/experiment-roadmap.md` or KB-mode `{kb_root}/deliverables/{scope}-experiment-roadmap.md` with gold frontmatter. No rendering path beyond markdown exists.
- experiment-mockup produces standalone HTML mockup artifacts per hypothesis (capture of control state + injected variant), but nothing consumes them downstream.
- render-default-deliverables renders positioning deliverables (separate concern; precedent for a dedicated render skill).
- The markdown roadmap is analytically complete but presents nine experiments of dense rigor (scores, baselines, self-critique, inconclusive protocols) as a wall of prose — wrong altitude for stakeholder pitch review.

## Approach

Render the markdown roadmap into a self-contained static site with a hub-and-spoke structure. Design decisions validated in the 2026-06-10 wireframe session:

- **Hub (overview page):** hero with stat row and the roadmap's measurement-constraint callout; tier-grouped experiment index cards (one-line hypothesis, compact ICE, mockup-status indicator, thumbnail strip once mockups exist — the hub doubles as a mockup-progress tracker); sequencing wave diagram with experiment pills linking to spokes; "what's not here" exclusions; a "What We Need From {Client}" asks section (Provide / Confirm / Approve columns, each ask tagged with the experiments it unblocks).
- **Spoke (one page per experiment):** title/tier/page-chips/hypothesis header with deliberately quiet inline ICE; centerpiece control-vs-proposed mockup comparison with per-image change annotations and variation tabs (tabs collapse for single-variation experiments; mobile-scoped experiments render phone-width frames); why-this-should-work; win/loss panels; self-critique (kept — preempting objections is persuasive); per-experiment before-launch asks; breadcrumb + prev/next pager.
- **Pitch-focus principle:** the HTML curates, the markdown remains the analytical record. Measurement design (target metric/guardrail/threshold cells), inconclusive protocols, and bundled-elements disclosures stay markdown-only.
- **Visual system:** FunnelEnvy design language per the prior single-page deliverable pattern — IBM Plex Sans, CSS-variable palette, color-coded tier badges and callouts, browser-chrome mockup frames with lightbox zoom, sticky scroll-spy nav.
- **Inputs:** the gold roadmap markdown (sole content source) plus optional mockup artifacts (Open Issue 2). Re-render is a complete projection of the current markdown, mirroring hypothesis-generator's `Re-render Behavior` — no diffing.
- **Humanizer pass (user requirement, 2026-06-10):** because the output is a client-facing deliverable, render-authored copy (condensed card hypotheses, mockup annotations, section leads — anywhere the renderer phrases rather than quotes) runs through the `humanizer` skill as a final pipeline step before write. Passages lifted verbatim from the gold markdown are already deliverable-grade and may be exempted; the pass targets prose the renderer writes.
- **Reference implementation:** a hand-built instance of the full design now exists in the consuming client KB repo (PR-reviewed), giving Design a concrete template for the page anatomy, shared stylesheet, and JS behaviors rather than a from-scratch spec.

Structural placement (flag vs. skill), the mockup contract, output placement, deploy, and the humanizer dependency are open — see `## Open Issues`.

## Requirements

Stub — filled during Design.

## Verification Design

### Validation

Stub — filled during Design. Must include: a render pass against a real gold-experiment-roadmap artifact producing the hub plus one spoke per experiment with working relative navigation; placeholder behavior verified for experiments without mockups; mockup-present behavior verified for at least one experiment with experiment-mockup output; no client content committed to this repo.

## Verification Results

### Validation Outcomes

Pending — populated during QA.

## Changelog

| Version | Changes |
|---------|---------|
| 0.2.0 | Humanizer pass added to Approach as a user requirement (render-authored copy only; verbatim gold-markdown passages exempt); OQ 5 seeded for the humanizer dependency (device-level skill — detect-and-degrade vs embedded style rules); reference-implementation note added (hand-built instance now exists in the consuming client KB repo). |
| 0.1.0 | Initial backlog change document — multi-page roadmap presentation render from gold-experiment-roadmap markdown, design validated via wireframe session; four approach OQs seeded (flag vs. skill, mockup contract, output placement, deploy). |
