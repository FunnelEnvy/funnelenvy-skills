# Phase 5 -- Disposition and Research Routing

Goal: turn the Phase 2-4 findings into two actionable outputs: a per-item disposition, and a prioritized research backlog that routes each gap to the skill that owns it. This skill surfaces research needs; it never conducts research.

## Per-item disposition

For each scored item, recommend exactly one disposition, driven by the findings (cite which):

- **Keep** -- sound as-is; no material finding changes it. (A genuinely sound item MUST be able to reach this outcome; a red team that never keeps anything is as broken as a self-critique that never concedes. This is the negative-control property in SKILL.md `Quality Rules`.)
- **Reframe** -- keep the item but change how it is positioned or read (e.g., reframe a recovery play as a diagnostic probe; add a pre-registered threshold; downgrade an Impact score pending a sizing input).
- **Demote** -- move to a lower tier, or out of scored experiments entirely into a context-verification / research item (e.g., a hypothesis whose population is undefined and might be near zero is a research question wearing an experiment's clothes).
- **Park behind dependencies** -- keep, but explicitly gate on named blocking dependencies that must clear before the item can read at all (dead telemetry, un-built instrumentation, un-shipped fixes).
- **Drop** -- the evidence contradicts the premise, or a settled prior result already resolved it.

Unscored Measurement Foundation entries get a disposition only if CC-MF found them misfiled (recommend: re-file as a scored intervention). Otherwise they are left as prerequisites.

Produce a disposition-change table: item | roadmap tier/ICE | red-team recommendation | driver (which findings).

## Prioritized research backlog

Emit a single ranked backlog, cheapest and most-blocking first. Each row: research item | what it unblocks | rough cost | why now | **routed-to**. Route each item to the skill or instrument that owns it:

- Analytics re-cuts, event/binding verification, bot/synthetic correction, segment sizing → `ga4-audit` or `aa-audit` (whichever produced the profile).
- Live structural/copy or production-vs-fixture confirmation → `live-capture`.
- Pre-launch measurement-plan validation for a surviving experiment (baseline existence, downfunnel completeness, denominator, power, confounds) → `experiment-measurement-audit` (the downstream per-experiment gate).
- Buyer-voice / qualitative comprehension reads → survey instruments (named, not built here).
- Desk-work items (pre-register thresholds, tag guardrails readable-today vs later) → no skill; a documented analyst task.

Ranking rule: a trivial verification that unblocks multiple items or silently zeroes a KPI (e.g., confirming a conversion event is not a dead binding) ranks above expensive single-item research.

## Output of this phase (held in-session)

The disposition-change table and the ranked, routed research backlog. Both feed the rendered critique (Phase 6, in SKILL.md `Output Format`).
