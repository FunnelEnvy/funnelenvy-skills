# KB Mode: Canonical Dual-Mode Contract

**This module is the canonical editing source for KB-mode semantics.** Nine skills carry an
inline copy of the mode-resolution procedure so their runtime read is self-contained (the same
inline-authority pattern the schemas use). When KB-mode semantics change, edit THIS file first,
then re-sync every skill listed below in the same change. A drift canary in
`scripts/registry_check.py` verifies the invariant sentences below exist in every dual-mode
SKILL.md.

## Dual-mode skills

| Skill | Section | Resolution point | KB-mode gate (artifact types the type skill must define) |
|---|---|---|---|
| positioning-framework | KB Mode (Dual-Mode Output) | pre-flight, step 2.5 | all 7 CRO types (3 bronze + 4 silver); also HARD STOPs on `--depth quick` |
| hypothesis-generator | KB Mode (Dual-Mode Output) | Phase 1, step 0 | `gold-experiment-roadmap` + `silver-strategy-context` + `bronze-company-facts`; optional producer-KB discovery (step 5) keyed on `gold-experiment-index`, with an in-output-KB `schema: experiment-history` fallback tried only when no external producer binds |
| live-capture | KB Mode (Dual-Mode Output) | Phase 0 | `silver-structural-observation` (gate) + the two bronze capture types, via two-level lookup (repo-local `artifacts/` first, then the `kb-start` base) |
| experiment-mockup | KB Mode (Dual-Mode Output) | orchestrator, Step 1b | `gold-experiment-roadmap` (consumer check; writes no KB artifacts) |
| render-program-site | KB Mode (Dual-Mode Output) | input resolution, phase 1 | `gold-experiment-roadmap` (consumer check; writes no KB artifacts) |
| cro-roadmap-red-team | KB Mode (Dual-Mode Output) | Phase 1 (resolve) | `gold-experiment-roadmap` (consumer check; reads gold roadmaps + their `depends_on`; writes a standalone critique, no KB artifacts) |
| ga4-audit | KB Mode (Dual-Mode Output) | Step 0 (before Step 1) | `silver-performance-analysis` (write output; single-agent write-side, no read-side mapping) |
| aa-audit | KB Mode (Dual-Mode Output) | Step 0 (before Step 1) | `silver-performance-analysis` (write output; single-agent write-side, no read-side mapping) |
| render-default-deliverables | KB Mode (Dual-Mode Output) | startup, before Context Discovery | `gold-strategy-deliverable` + `gold-battle-card` (write outputs) + `silver-strategy-context` + `bronze-company-facts` (L0-equivalent read precondition) |

All nine sections use the exact header `KB Mode (Dual-Mode Output)` -- skills cross-reference
each other's sections by that name.

## Canonical Mode Resolution Procedure

Resolved ONCE at the skill's resolution point and held in-session. Only read/write targets (and,
where a skill says so, output document shape) differ between modes; all analysis, phase logic,
and quality rules are identical in both.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy
   mode, and note it in the run output ("No `Knowledge Bases` section in CLAUDE.md; using
   legacy output." / "... using legacy I/O." per the skill's I/O surface).
3. Parse the KB root path and KB type skill name from that section. Verify the type skill
   exists at `.claude/skills/{kb-type}/` and defines this skill's gate artifact types (per the
   table above). If any check fails: legacy mode, and report which check failed. Never write
   typed artifacts into a half-configured KB.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the
   type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and
   ask the user to re-run with `--scope`. Do not guess a scope.
5. (Skill-specific extra gates run here, e.g., positioning-framework's quick-depth HARD STOP or
   hypothesis-generator's optional producer-KB discovery.)

## Invariants (must hold verbatim in spirit in every dual-mode skill)

- **Binding detection selects the mode.** `--scope` never selects KB mode; it only names the
  scope once KB mode is confirmed.
- **There is deliberately no `--kb` force flag.** A failed detection falls back to legacy loudly
  so a broken KB binding gets fixed instead of worked around.
- **`--scope` in KB mode:** required; missing or invalid is a HARD STOP listing valid scopes.
  Do not guess a scope.
- **`--scope` in legacy mode:** warn-and-ignore.
- **In-session state:** once KB mode is confirmed, hold `kb_root`, `kb_type`, `scope` (plus any
  skill-specific type-def paths) for the read/write steps. No skill hardcodes a KB type skill
  name or a client-specific path.
- **Type defs are the write-side authority** in KB mode (output path, frontmatter contract,
  section layout); phase files remain the authority for analytical content.

## Optional-input exception

Optional inputs (soft dependencies, producer-KB discovery) are never mode-resolution
requirements: a missing or broken optional binding degrades penalty-free with a one-line note,
never flips the run to legacy, and never hard-stops. Only the OUTPUT KB's binding failures
trigger the loud legacy fallback.
