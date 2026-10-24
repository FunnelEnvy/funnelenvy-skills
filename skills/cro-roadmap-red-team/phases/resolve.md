# Phase 1 -- Scope and Cold Load

Goal: identify the target roadmap(s) and every source they cite, then load everything with the sources as primary truth and the roadmap as a claim. Order is load-bearing: read sources before forming any opinion about the roadmap's conclusions.

## Step 1.1 -- Resolve mode and inputs

Run the `Mode Resolution Procedure` from the SKILL.md `KB Mode (Dual-Mode Output)` section. This sets legacy vs KB and, in KB mode, the in-session `kb_root` / `kb_type` / `scope`.

Resolve the target roadmap path(s) per the I/O contract and `--altitude`:

- `--altitude both` (default): resolve both the tactical and strategic roadmap. If only one exists, red-team it and note the other's absence in the critique header. Never fail because an altitude is missing.
- `--altitude tactical` / `strategic`: resolve only that altitude. If the requested roadmap is absent, report it and stop (nothing to red-team).
- Explicit positional paths override the mode-resolved inputs.

Hard precondition: at least one target roadmap resolves and is readable. If none resolve, STOP and tell the user the resolved path(s) and to run `/hypothesis-generator` first (with `--scope <slug>` in KB mode).

## Step 1.2 -- Resolve cited sources

For each resolved roadmap, resolve its evidence base:

- **KB mode:** read the roadmap's `depends_on` frontmatter and resolve each listed artifact to its body path in the bound KB. These silver/bronze artifacts are the evidence base. Also resolve the external experiment-history producer, which has no `depends_on` edge because the generator cites it by attribution only: the KB the working repo's `Knowledge Bases` section declares, other than the output KB, whose type skill defines `gold-experiment-index`. Its gold index and the silver insight records it links join the evidence base.
- **Legacy mode:** the evidence base is the `.claude/context/` L0 + L1 files (company-identity, competitive-landscape, audience-messaging, positioning-scorecard, performance-profile, brand-voice, live-observation/live-copy) that exist, plus the experiment history when present: `.claude/context/experiment-history.md`, only when its frontmatter declares `schema: experiment-history` (a file that does not is noted and not read as history), and every `.claude/deliverables/experiments/*/insight.md` record.

Record which sources resolved and which did not. An unresolvable cited source is itself a finding (it means the roadmap leaned on evidence you cannot verify) and belongs in the critique.

## Step 1.3 -- Cold load

Read every resolved source in full first, except the experiment history (below). Only then read the roadmap. Read the roadmap's structure (hypotheses/levers, tiers, ICE, `Self-critique` blocks, `validation_gates` records if present, `What's Not Here`, sequencing, Measurement Foundation for strategic). Do NOT read the `Self-critique` blocks as settled truth; you will grade them in Phase 4, and Phase 2 must run before you internalize them.

**History exception.** The experiment history is the one source not read in full, because a full history file can exceed this skill's whole token budget. From the legacy `experiment-history.md` or the in-KB `schema: experiment-history` artifact, read the frontmatter; the cross-experiment patterns, discovered mechanisms, and coverage gaps sections; the full entry for every experiment on a surface the roadmap targets (find them by each entry's page field); and, for every other entry, its Next Steps field or, where it has none, its final Learning sentences, since that is where a prose next test is named. Read every insight record's `next_experiments` block in full. Parse all of it yourself, by section and by surface. Never run the generator's history script (`history_backlog.py`) or read its output as a substitute: a parser bug must not be able to pass both skills.

## Step 1.4 -- Schema tolerance (degrade, do not fail)

- **No `Self-critique` blocks** (pre-v1.5.0 roadmap output): skip Phase 4 (self-critique grading) and note the omission in the critique header. All other phases run.
- **No `validation_gates` records** (pre-v1.9.x output): treat every checklist item as full re-derivation (no gate-verdict-audit shortcut is available). Note it.
- **Absent or partial `depends_on`** (KB) or missing context files (legacy): resolve what exists, record the unresolvable sources, and continue. Checks that depend on a missing source return "cannot assess -- source absent," which is itself a finding, not a silent pass.
- **Strategic roadmap present but no `## Measurement Foundation` section:** normal; the Foundation-specific check simply finds nothing to check.
- **No "Decision posture" line** (output from a generator before 1.18): CC2 audits against its fallback reference. Name the posture audited in the critique header.

## Output of this phase (held in-session)

- Resolved mode, roadmap path(s), altitude(s) in scope.
- The evidence base (resolved source paths) and the unresolved-source list.
- The parsed roadmap item inventory: per item its title, altitude, tier, ICE, chosen mechanism, named metric, named guardrail(s), stopping rule, `validation_gates` verdicts (if present), and whether it is a scored item or an unscored Measurement Foundation entry.
- The declared decision posture: the roadmap's rendered "Decision posture" line (confidence and sidedness, power, relative MDE, directional band) and the Quick Win ceiling its tier definitions state; or "none declared" when the line is absent, which sends CC2 to its fallback reference.
- The history backlog: every `recommended_lead` or `high` item, typed or prose, with each prose priority derived from the record text by CC13's rubric, each with its parent record, surface, and priority; medium and low items listed separately as considered, never as gaps; or "no history source" when none resolved. CC13 audits the roadmap against this list.
