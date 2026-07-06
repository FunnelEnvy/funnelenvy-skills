# Changelog

## [0.1.0] - 2026-07-05

### Added
- Initial `cro-roadmap-red-team` skill: an independent red team for produced CRO roadmaps (both altitudes -- the tactical experiment roadmap and the strategic roadmap). Exists because a generator that grades its own work rubber-stamps it; independence lives in a separate evaluator, not inside `hypothesis-generator`.
- Six-phase pipeline: (1) scope and cold load with dual-mode source resolution and schema tolerance; (2) independent re-derivation via adversarial skeptic subagents with tier-gated cold mechanism re-derivation (full cold-mechanism + perspective-diverse skeptics for Quick Win / Strategic Bet / strategic bets; lighter single-skeptic pass for Explorations); (3) the cross-cutting checklist; (4) self-critique grading (rebut vs deflect); (5) dispositions + routed research backlog; (6) render.
- Cross-cutting checklist (CC1-CC11 + CC-MF + a non-skippable completeness step), authored altitude-aware (tactical A/B form + non-A/B strategic analog), with a gate-verdict-audit vs full-re-derivation split calibrated against hypothesis-generator's Phase 3.5 `validation_gates`.
- Enforced phase order (checklist before self-critique grading) and a negative-control property (a sound item can reach a `keep` disposition with no change).
- Dual-mode consumer I/O (legacy `.claude/deliverables/` + `.claude/context/`; KB mode reads the scope's gold roadmaps and their `depends_on`), writing a standalone critique (no `kb_layer`, never a KB artifact, never edits the target).
- Grounded boundary with `experiment-measurement-audit` (guardrail readability owned here; surviving experiments route to the audit downstream).
- `agent-header.md` shared skeptic posture; phase files `resolve.md`, `rederive.md`, `checklist.md`, `grade.md`, `disposition.md`.
