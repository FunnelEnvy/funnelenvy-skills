---
fe-managed: true
name: live-capture-skill
description: >
  Build the live-capture skill (Phase B): a dual-mode public skill that navigates a site's pages,
  passively reads the rendered DOM, and writes two factual artifacts (live-observation.md page
  structure, live-copy.md verbatim copy). Reuses experiment-mockup's browser stack and
  positioning-framework's KB write contract. Legacy mode writes L0 to .claude/context/; KB mode
  writes bronze and enriches the silver-structural-observation type unblocked by Phase A.
governed_by: change-management/change-document
status: QA
resource_name: live-capture
resource_version: "TBD"
impact: 4
confidence: 4
ease: 2
initiative: cro-kb-path-b
status_note: Build complete, scripts tested (32 green); pending user QA + KB-mode validation in client repo
version: "0.1.0"
created: 2026-06-09
updated: 2026-06-09
---

# live-capture Skill (Phase B)

## Background

Phase A added a read-side row to hypothesis-generator for an optional `silver-structural-observation`
artifact, but nothing produces it. Phase B builds the producer: a new public skill that captures
live-page structure and copy. The canonical output schema (Observation Artifact Schema v1.1) was
supplied 2026-06-09 and is the authority for both artifacts' frontmatter, body, the page-selection
algorithm, and the confidence model. This completes the observation-artifact chain and is the
producer half of the Path B KB-native integration.

## Current State

- `hypothesis-generator/SKILL.md` reads `reference/cro-{scope}/live-structure.md` (optional, soft) in KB mode.
- No skill writes `live-observation.md`, `live-copy.md`, or the silver structural artifact.
- Reusable machinery exists and is mapped: experiment-mockup browser stack (mode detection +
  passive DOM/style extraction), positioning-framework KB write contract, `modules/web-extract.md`,
  `modules/slugify.md`, the bronze artifact types in client CRO type skills.

## Approach

New skill `skills/live-capture/` (slash `/live-capture`), Opus, single orchestrator + sequential
phases, mirroring experiment-mockup. Dual-mode I/O mirroring positioning-framework.

Invocation: `/live-capture <url> [--scope <slug>] [--no-kb] [--static] [--urls <list>] [--viewports desktop,mobile]`

- **I/O mode resolution** (reuse positioning-framework lines 113-191): `--no-kb` -> legacy; else
  read working CLAUDE.md `Knowledge Bases`, verify the type skill defines `bronze-note-capture`,
  `bronze-research-extraction`, and `silver-structural-observation`; missing -> loud legacy
  fallback; resolve `--scope` (HARD STOP if missing/invalid in KB mode). Never hardcode a client
  type-skill name or path.
- **Browser-mode detection** (reuse experiment-mockup Step 5): chrome-devtools -> playwright ->
  STOP-and-ask -> static. Configured-but-broken = STOP, never silent-degrade.
- **Page selection** (spec Section 8): leverage = `0.35*traffic_norm + 0.30*conversion_gap_norm +
  0.20*bounce_norm + 0.15*device_gap_norm` (conversion_gap = clamped distance below benchmark, not
  raw CVR); two lanes (conversion by leverage ~8, content by organic sessions 1-2); always-capture
  homepage + healthiest page; no-profile nav-crawl fallback caps confidence at 3.
- **Capture** (passive, no injection): per page per viewport, navigate + read rendered DOM, extract
  spec blocks A-I + K and the viewport_divergence block; block H render/technical from
  devtools/playwright; static fallback writes block H `[NOT AVAILABLE: static mode]`.
- **Assembly + output:** facts + the two permitted mechanical derivations only; coverage-weighted
  file confidence; `content_hash` per page. Legacy -> two L0 files in `.claude/context/`. KB ->
  bronze (`bronze-note-capture`, `bronze-research-extraction`) + enrich silver
  `reference/cro-{scope}/live-structure.md`; KB frontmatter contract + supersede + post-write
  `kb_type_validate.py`. Additive only; no third writer to `performance-profile.md`.

Authoritative artifact schema inlined in `phases/write.md`; human-reference copies in `schemas/`.

## Requirements

Files to create under `skills/live-capture/`:
- `SKILL.md` — orchestrator (frontmatter trigger description, invocation/flags, I/O + browser mode
  resolution, page-selection routing, capture-agent launch with KB param block, completion +
  validation gate, Scripts table, Module Dependencies).
- `agent-header.md` — shared rules: accuracy > capture fidelity > completeness; factual-not-
  interpretive; tri-state existence fields; fold/ordinal/region position encoding; capture-
  provenance vs KB data_provenance distinction; no em dashes; output file table.
- `phases/select.md` — Section 8 page selection (formula + lanes + always-capture + no-profile path).
- `phases/capture.md` — passive per-page/per-viewport DOM capture of blocks A-I/K + viewport_divergence.
- `phases/static-capture.md` — static fallback via web-extract + curl HTML/CSS parse.
- `phases/write.md` — assembly + dual-mode output + inline authoritative schema for both artifacts.
- `scripts/page_select.py` — deterministic leverage normalization + ranked two-lane selection from a
  per-page-metrics JSON; formula documented in select.md as authority.
- `scripts/content_hash.py` — deterministic hash of H1 + structural skeleton.
- `CHANGELOG.md` — skill changelog.

Repo-level (registration package deal):
- `schemas/live-observation.md`, `schemas/live-copy.md` — human-reference copies.
- `README.md` — skills table row + count + invocation example.
- `.claude-plugin/marketplace.json` — skill entry.
- inner `funnelenvy-skills/CLAUDE.md` + outer root `CLAUDE.md` — skill inventory.
- `_tests/` — unittest coverage for both scripts (per repo convention).

## Validation

1. Legacy live run `/live-capture <public-url> --no-kb` writes both L0 files validating against the
   v1.1 schema (blocks A-I/K, content_hash, coverage-weighted confidence, no interpretive fields).
2. `--static` produces artifacts with block H `[NOT AVAILABLE: static mode]`, confidence 2-3.
3. Configured-but-broken browser MCP -> skill STOPS (no silent static degrade).
4. `page_select.py` + `content_hash.py` unit tests green; profile-present run selects by leverage +
   always-captures homepage; no-profile run nav-crawls and caps confidence at 3.
5. KB-mode write path code-reviewed; full kb_type_validate proof deferred to the client repo after
   Change B registers the silver type (cross-repo dependency).
6. Registration complete (README/marketplace.json/both CLAUDE.md/SKILL+CHANGELOG); doc-management
   review clean.

## Changelog

| Version | Changes |
|---|---|
| 0.1.0 | Backlog: live-capture skill scoped from the approved Phase B plan and the v1.1 observation schema. |
