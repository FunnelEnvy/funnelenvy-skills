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
status_note: QA round 1 folded in (blocked-page tri-state fix + 2 schema declarations + objection_faq_present default); pending user QA approval
version: "0.2.0"
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

## QA Findings and Resolution

The first full KB-mode chain run (live-capture -> silver structural artifact -> hypothesis-generator) surfaced one bug and two schema-completeness gaps. All three are producer-side and folded into this change during QA.

**Finding 1 (bug): content-blocked pages asserted tri-state absence.** A page hard-blocked by the site's WAF (HTTP 403, zero content rendered) was recorded with a non-clean `page_block_status` AND a proof tri-state field set to `absent`. That is a false assertion: the proof-detection pass never saw a rendered page, so it observed nothing. `absent` means "looked and confirmed not there"; the correct value for a pass that never ran against rendered content is `not_checked`. This is the exact false-assertion class the tri-state design exists to prevent (the same reason v1.1 promoted the proof fields from bool to tri-state for below-fold lazy content). The downstream consumer survived it only because its trust qualifiers downgrade non-clean-page signals and the relevant firing condition happened not to hold; the producer must not rely on consumer compensation.

Resolution: a content-blocked-pages rule added to `agent-header.md` (Tri-State Existence Discipline), `phases/capture.md` (per-page WAF-block flow), `phases/write.md` (authoritative schema constraint), and `phases/static-capture.md` (static block-status path). On any content-blocked page (`page_block_status: akamai-403` / `challenge` / zero-content), every pass-dependent tri-state field is `not_checked` and pass-dependent counts are `null`, never `absent` / `0`. `partial` pages (rendered but not fully settled) are explicitly unaffected: their real observations stand and are not blanked.

**Finding 2 (schema gap): two emitted-but-undeclared fields.** The capture emits `sitewide_form_field_count` (site-level, sibling of the already-declared required-count) and per-page `name` (human-readable page label alongside `path`), neither declared in the authoritative schema. Resolution: both declared in `phases/write.md`, mirrored in `schemas/live-observation.md`. Emission unchanged.

**Finding 3 (decision): `objection_faq_present` declared but never emitted.** The schema declares this tri-state but no detection pass populates it. Resolution: kept the field and emit it explicitly as `not_checked` until a detection pass exists (schema-complete and honest, zero capture-logic work now). One line added to the capture flow; `phases/write.md` schema annotated. The field is NOT dropped: hypothesis-generator Step 1e keys TC-02 on it, so removal would orphan a consumer trigger.

**Consumer (hypothesis-generator) untouched, by design.** Step 1e's tri-state rule (`not_checked` neither fires nor suppresses) and its missing-field-equals-`not_checked` convention already handle the corrected output. No consumer change is needed; touching it would duplicate the contract the producer now satisfies.

## Changelog

| Version | Changes |
|---|---|
| 0.2.0 | QA round 1: folded in producer-side fixes from the first KB-mode chain run. Content-blocked pages now write pass-dependent tri-states as `not_checked` (not `absent`); declared `sitewide_form_field_count` and per-page `name`; `objection_faq_present` emitted explicitly as `not_checked` until a detection pass exists. Consumer untouched. |
| 0.1.0 | Backlog: live-capture skill scoped from the approved Phase B plan and the v1.1 observation schema. |
