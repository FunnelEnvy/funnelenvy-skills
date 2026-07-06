# Phase 2 -- Independent Re-derivation

Goal: for each scored item, re-argue from the cited evidence what the verdict should be, before reading the item's own `Self-critique`. This is where independence is mechanically enforced: a separate skeptic, prompted to refute, re-derives the verdict cold. Unscored Measurement Foundation entries are not re-derived here (they are prerequisites, not experiments); they are handled by the one Foundation check in Phase 3.

## The skeptic subagent

Spawn skeptic subagents via the Task tool with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`, `model: "opus"`. Every skeptic is given `agent-header.md` verbatim, plus the cited evidence base (or the paths to read), plus the specific item under test. The skeptic is prompted to REFUTE the item from the evidence and to default to "unsupported" when evidence is thin.

Each skeptic returns, for its item:

- **Independent verdict** -- what the evidence supports (sound / sound-but-weaker-than-claimed / unsupported / wrong-target), with cited source lines.
- **Strongest failure mode** -- the single most likely way this item fails or reads misleadingly.
- **Evidence for and against** -- the specific source lines that support or undercut the item.

## Tier-gated depth (OQ2 resolution)

The expensive part is cold mechanism re-derivation and perspective-diverse skeptics. Point them where they pay off:

- **Quick Win and Strategic Bet tactical items, and all strategic bets:** full treatment.
  - **Cold mechanism re-derivation.** Before the skeptic is shown the item's chosen mechanism, it independently derives the candidate mechanisms that could move the item's named metric from the source data, and identifies the best-evidenced one. Only then compare against the mechanism the roadmap chose. This is what catches a competing-mechanism error (the roadmap targeting a weaker-evidenced mechanism than the data points to). Feeds CC8 in Phase 3.
  - **Perspective-diverse skeptics.** Run three skeptics with distinct lenses -- mechanism, measurability, population -- rather than three identical refuters. A finding survives only if the skeptics cannot defend the item against it.
- **Explorations (and any lower-tier item):** the lighter pass. One skeptic, bracket-the-self-critique re-derivation (re-derive the verdict from evidence without reading the `Self-critique`, but you may read the item's stated mechanism). No forced cold mechanism derivation, single lens.

Tier is read from the roadmap item's own tier label (Quick Win / Strategic Bet / Exploration for tactical; the strategic roadmap's bet tiering for strategic). If an item carries no tier, treat it as the higher tier (full treatment) -- err toward rigor.

## Boundary with Phase 3

Phase 2 produces per-item verdicts. Phase 3 runs the cross-cutting checklist across ALL items (including cross-item patterns a single-item skeptic cannot see: portfolio-wide guardrail readability, contradicts-prior-result, bundle interpretability). Do not duplicate the checklist here; Phase 2 is per-item re-derivation, Phase 3 is the structured cross-cutting sweep. The Phase 2 verdicts are inputs to the Phase 3 competing-mechanism check (CC8) and to the Phase 5 disposition.

## Output of this phase (held in-session)

Per scored item: independent verdict, strongest failure mode, cited for/against evidence, and (for full-treatment items) the cold-derived best-evidenced mechanism vs the roadmap's chosen mechanism.
