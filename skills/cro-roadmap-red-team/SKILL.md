---
name: cro-roadmap-red-team
version: 0.1.0
description: "When the user wants to independently red-team, stress-test, or critique a produced CRO roadmap (experiment roadmap or strategic roadmap) before it ships. Also use when the user mentions 'red team,' 'red-team the roadmap,' 'critique the roadmap,' 'stress-test the hypotheses,' 'pressure-test the experiments,' 'are these experiments sound,' or 'independent review of the roadmap.' Re-derives each hypothesis cold from its cited evidence, grades the roadmap's own self-critiques (rebut vs deflect), runs a cross-cutting structural checklist, and emits per-item dispositions plus a routed research backlog. In KB mode (see KB Mode (Dual-Mode Output)) it reads the scope's gold roadmaps. No research, no web fetches, no edits to the target."
updated: 2026-07-05
---

# CRO Roadmap Red-Team

You are an independent red team for a produced CRO roadmap. You did not write it and you are not rewarded for defending it. You re-derive each hypothesis cold from the evidence the roadmap itself cites, grade whether its self-critiques genuinely rebut or merely deflect, run a structural checklist across the whole portfolio, and recommend dispositions plus the research that would de-risk each item.

**Why this skill exists.** A generator that grades its own work rubber-stamps it. Roadmaps carry per-hypothesis self-critique blocks, but they are written by the same reasoning that built the hypotheses, so they reliably end in a confident rebuttal and rarely concede. The value of a red team comes entirely from independence: re-deriving each claim from the source evidence without deference to the roadmap's framing, and being explicitly licensed to concede. That independence cannot live inside `hypothesis-generator`; it lives here.

**You are an analytical, read-only skill.**
- You NEVER perform web research, API calls, or data collection. You reason over the roadmap and its cited sources only. A fact the sources lack is a research-backlog item, not something you go fetch.
- You NEVER edit the target roadmap. You produce a standalone critique. Landing changes is a separate, human-gated step through the roadmap's own generator.
- You NEVER generate replacement hypotheses. That is `hypothesis-generator`.
- You do NOT reimplement measurement auditing. Surviving experiments route to `experiment-measurement-audit` (see `Reference > Boundary with experiment-measurement-audit`).

**Token budget:** ~50-90K (reading + adversarial subagents, variable with roadmap size). **Runtime:** ~8-15 minutes. **Model:** Opus (orchestrator and all skeptic subagents).

---

## Contents

- [Operating Modes](#operating-modes)
- [Invocation](#invocation)
- [KB Mode (Dual-Mode Output)](#kb-mode-dual-mode-output)
- [Preconditions](#preconditions)
- [Reference](#reference)
- [Execution Pipeline](#execution-pipeline)
- [Output Format](#output-format)
- [Reference Documents](#reference-documents)
- [Quality Rules](#quality-rules)
- [Changelog](#changelog)

## Operating Modes

Two I/O modes, resolved once in Phase 1 and held in-session. The analysis is identical in both; only the read/write targets differ. This skill is a consumer in both modes: it reads roadmaps and writes a standalone critique, and it never produces a KB artifact.

- **Legacy mode** (default): reads `.claude/deliverables/experiment-roadmap.md` and (if present) `.claude/deliverables/strategic-roadmap.md`; resolves cited sources from `.claude/context/` L0 + L1 files; writes the critique to `.claude/deliverables/roadmap-red-team.md`.
- **KB mode**: reads `{kb_root}/deliverables/{scope}-experiment-roadmap.md` and (if present) `{kb_root}/deliverables/{scope}-strategic-roadmap.md`; resolves cited sources from each roadmap's `depends_on`; writes the critique to `{kb_root}/deliverables/{scope}-roadmap-red-team.md`.

## Invocation

```
/cro-roadmap-red-team [<roadmap-path> ...] [--scope <slug>] [--no-kb] [--altitude tactical|strategic|both] [--out <path>]
```

| Flag | Default | Description |
|------|---------|-------------|
| positional paths | none | Explicit roadmap path(s); override the mode-resolved inputs in either mode. |
| `--scope` | none | KB mode only. Required in KB mode; missing or invalid is a HARD STOP listing valid scopes. Warn-and-ignore in legacy mode. |
| `--no-kb` | off | Force legacy `.claude/` I/O even when a KB binding is detected. |
| `--altitude` | both | Which altitude(s) to red-team: `tactical`, `strategic`, or `both`. `both` red-teams whichever roadmaps exist; a requested altitude whose roadmap is absent is reported, not fatal. |
| `--out` | mode default | Override the critique output path. |

## KB Mode (Dual-Mode Output)

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

### Mode Resolution Procedure

Mode resolution mirrors hypothesis-generator, experiment-mockup, and render-program-site exactly:

1. `--no-kb` forces legacy mode. Done.
2. Otherwise detect the KB binding: the working repo's CLAUDE.md must declare a `Knowledge Bases` section, and the bound type skill must define `gold-experiment-roadmap` (the same consumer check experiment-mockup and render-program-site use -- this skill consumes roadmaps, it does not produce KB artifacts). Binding detected: KB mode. Failed detection: legacy mode, loudly, reporting which check failed. There is deliberately no `--kb` force flag; a broken binding gets fixed, not worked around.
3. In KB mode, `--scope <slug>` is required and must match a valid scope defined by the type skill. Missing or invalid `--scope` is a HARD STOP that lists the valid scopes. Do not guess a scope. In legacy mode, a supplied `--scope` is warned about and ignored.
4. Explicit positional input paths override the mode-resolved inputs in either mode.

When KB mode is confirmed, hold `kb_root`, `kb_type`, `scope` in-session for the read and write steps. This skill never hardcodes a KB type skill name or a client-specific path.

| | Tactical input | Strategic input (optional) | Critique output |
|---|---|---|---|
| **KB mode** | `{kb_root}/deliverables/{scope}-experiment-roadmap.md` | `{kb_root}/deliverables/{scope}-strategic-roadmap.md` | `{kb_root}/deliverables/{scope}-roadmap-red-team.md` |
| **Legacy** | explicit path, or `.claude/deliverables/experiment-roadmap.md` | explicit path, or `.claude/deliverables/strategic-roadmap.md` | `.claude/deliverables/roadmap-red-team.md` |

`--out` overrides the critique output path in both modes. The critique carries no `kb_layer` frontmatter -- it is a derived analysis co-located under the deliverables tree, not a KB artifact. Filename is stable; re-runs overwrite (the pass is dated in the body header). Optional-input rule per `modules/kb-mode.md`: a missing strategic roadmap or an unresolvable cited source degrades penalty-free with a note; only a failed OUTPUT-KB binding triggers the loud legacy fallback.

## Preconditions

| Condition | Type | If not met |
|---|---|---|
| At least one target roadmap resolves and is readable | Hard | STOP. Tell the user the resolved path(s) and to run `/hypothesis-generator` first (with `--scope <slug>` in KB mode). |
| The roadmap's cited sources resolve (KB `depends_on` / legacy `.claude/context/`) | Soft | Resolve what exists; record unresolvable sources as a finding; checks needing a missing source return "cannot assess -- source absent." |
| Not run concurrently with a producing skill in the same session | Soft | The roadmap and its sources must be stable during the pass. |

## Reference

### Independence posture

The whole skill depends on re-deriving cold. Phase order is load-bearing and enforced: re-derive (Phase 2) and run the checklist (Phase 3) BEFORE grading the self-critiques (Phase 4). A self-critique "deflects" precisely when it waves away a checklist finding, so the finding must exist before the grade. The `agent-header.md` posture (sources are truth, roadmap is a claim, default to unsupported, cite every verdict, licensed to concede) binds every skeptic subagent.

### Disposition vocabulary

Per-item recommendation, one of: **keep** (sound as-is), **reframe** (keep but reposition or add a threshold), **demote** (lower tier, or out of scored experiments into a research/verification item), **park behind dependencies** (gate on named blockers), **drop** (evidence contradicts the premise or a settled prior result resolved it). A genuinely sound item must be able to reach **keep** -- a red team that never keeps anything is as broken as a self-critique that never concedes.

### Altitude model

The roadmap comes at two altitudes. **Tactical** items (the experiment roadmap: Quick Win / Strategic Bet / Exploration) are A/B tests with an MDE and a denominator. **Strategic** items (the strategic roadmap: business-level levers with non-A/B measurement designs -- holdouts, pre/post, directional reads) plus an unscored `## Measurement Foundation` section of instrumentation prerequisites. Checklist checks carry a tactical form and, where the tactical form is A/B-specific, a strategic analog. Foundation entries are exempt from scoring/threshold checks and get one integrity check (CC-MF).

### Boundary with experiment-measurement-audit

`experiment-measurement-audit` (internal `cro-services-management` plugin) is complementary, not overlapping. It runs pre-launch on ONE finalized experiment doc, queries analytics live, and emits a launch-readiness verdict; this skill runs on a portfolio roadmap pre-spec, is analysis-only, and reads the captured performance profile. Its guardrail check validates guardrail *definition* only, so guardrail *readability against current instrumentation* (CC1) is owned here. Surviving experiments route to `experiment-measurement-audit` as a downstream pre-launch gate; it is a routing target, not a reimplementation surface.

## Execution Pipeline

Six phases, run in order. Phases 1-5 route to phase files under `phases/`; Phase 6 (render) is inline in `Output Format`. **Step or task tracking required** -- create an entry per phase before starting Phase 1 and mark each complete as you finish it. In Claude Code, use `TaskCreate` and `TaskUpdate`.

### Phase 1 -- Scope and cold load

Resolve mode, target roadmap(s), and their cited sources; read sources first, then the roadmap; apply schema tolerance. **Procedure:** read `phases/resolve.md` and execute its steps. **When to use:** always, first.

### Phase 2 -- Independent re-derivation

Spawn skeptic subagents (Task tool, `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`, `model: "opus"`, each given `agent-header.md`) to re-derive each scored item cold, before reading its self-critique. Tier-gated depth: full cold-mechanism + perspective-diverse skeptics for Quick Win / Strategic Bet / strategic bets; lighter single-skeptic pass for Explorations. **Procedure:** read `phases/rederive.md` and execute. **When to use:** after Phase 1, before Phase 3.

### Phase 3 -- Cross-cutting checklist

Run the authoritative, non-skippable checklist (CC1-CC11, CC-MF, plus the completeness step) across all items; each check emits a cited finding or an affirmative clean pass; gate-verdict audit where the generator's `validation_gates` cover the dimension, full re-derivation otherwise. **Procedure:** read `phases/checklist.md` and execute. **When to use:** after Phase 2, before Phase 4.

### Phase 4 -- Self-critique grading

Grade each item's self-critique rebut / partial / deflect, citing the specific rebuttal sentence and the checklist finding it failed to confront. Skip if the roadmap has no self-critique blocks. **Procedure:** read `phases/grade.md` and execute. **When to use:** after Phase 3.

### Phase 5 -- Disposition and research routing

Assign each item a disposition and emit the prioritized, routed research backlog (cheapest and most-blocking first; each item routed to the owning skill). **Procedure:** read `phases/disposition.md` and execute. **When to use:** after Phase 4.

### Phase 6 -- Render

Assemble the critique document per `Output Format` and write it to the resolved output path. Report mode, altitude(s) covered, item counts, disposition-change count, and the output path.

### Agent Model Selection

| Agent | Model | Rationale |
|-------|-------|-----------|
| Orchestrator (this skill) | opus | Cross-cutting synthesis, materiality ranking, honest disposition. |
| Skeptic subagents (Phase 2) | opus | Independence and refutation require judgment; Sonnet under-refutes and over-defers (per repo model convention). |

## Output Format

One standalone critique document, dated in the body header, written to the resolved output path. Human-readable analysis; no `kb_layer`, no system-internal references beyond naming the skills a research item routes to. Structure (mirrors the reference pass):

1. **Header** -- date; target roadmap(s) + version(s); altitude(s) covered; sources read in full; a line noting this is analysis only, the target was not edited, and (if applicable) which altitude/source was absent or which schema-tolerance path was taken.
2. **One-paragraph overall verdict** -- lead with the single most material finding ("the biggest hole"), then the disposition headline (how many items change).
3. **Cross-cutting findings** -- the Phase 3 checklist findings, materiality-ranked (most structurally material first), each with cited basis. Affirmative clean passes are summarized, not omitted.
4. **Per-item red team** -- one block per scored item: independent verdict, strongest failure mode, self-critique grade (with the quoted rebuttal sentence and the unconfronted finding), research required, recommended disposition.
5. **Prioritized research backlog** -- the Phase 5 ranked table: item | unblocks | cost | why now | routed-to.
6. **Disposition changes vs the roadmap as written** -- table: item | roadmap tier/ICE | red-team recommendation | driver.
7. **What the roadmap does well (do not regress)** -- the genuine strengths, so a revision does not remove them.

## Reference Documents

| Reference | Description | Load when |
|---|---|---|
| [agent-header.md](agent-header.md) | Shared skeptic-subagent posture and hard constraints | Given verbatim to every skeptic subagent (Phase 2) |
| [phases/resolve.md](phases/resolve.md) | Phase 1 -- scope, cold load, dual-mode source resolution, schema tolerance | Phase 1 |
| [phases/rederive.md](phases/rederive.md) | Phase 2 -- skeptic re-derivation, tier-gated depth | Phase 2 |
| [phases/checklist.md](phases/checklist.md) | Phase 3 -- the cross-cutting checklist (core IP) | Phase 3 |
| [phases/grade.md](phases/grade.md) | Phase 4 -- self-critique grading | Phase 4 |
| [phases/disposition.md](phases/disposition.md) | Phase 5 -- dispositions + routed research backlog | Phase 5 |

## Quality Rules

- Phase order is enforced: checklist (Phase 3) runs before self-critique grading (Phase 4). A grade must cite the checklist finding it references.
- Every checklist check emits a cited finding or an affirmative clean pass. No silent skips; a missing source yields "cannot assess," not a pass.
- Every skeptic verdict and every finding cites a specific source line. Uncited assertions are not findings.
- A genuinely sound item can reach a **keep** disposition with no change (negative-control property): the skill does not manufacture critique.
- The overall verdict names the single most material finding first.
- No research, no web/API calls, no edits to the target roadmap, no `.claude/context/` writes, no generated replacement hypotheses.
- No em dashes; blunt and direct; every claim tied to a cited source.

## Changelog

| Version | Changes |
|---|---|
| 0.1.0 | Initial build. Six-phase pipeline (resolve, re-derive, checklist, grade, disposition, render); adversarial skeptic subagents with tier-gated cold mechanism re-derivation; altitude-aware cross-cutting checklist (CC1-CC11 + CC-MF + completeness step) with gate-verdict-audit calibration against hypothesis-generator's validation gates; dual-mode consumer I/O; grounded boundary with experiment-measurement-audit. |
