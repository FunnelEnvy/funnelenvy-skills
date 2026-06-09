---
fe-managed: true
name: hypothesis-generator-structural-consumption
description: >
  Make hypothesis-generator consume the silver-structural-observation artifact (Phase C of the
  observation-artifact integration). Phase A made the structural body load into detect's context;
  this change makes the correct patterns use it: a Step 1 extraction stanza, a gated Step 1e
  field-keyed trigger table with tri-state semantics and a no-double-count boundary, construct-side
  mobile defect-vs-layout routing and site-wide scope correction, and soft-dependency wiring with
  explicit no-confidence-penalty absence semantics.
governed_by: change-management/change-document
status: Build
resource_name: hypothesis-generator
resource_version: "TBD"
impact: 4
confidence: 4
ease: 3
initiative: cro-kb-path-b
status_note: Build complete, committed c0858a4 on dj_live-capture-skill (PR 10, supersedes PR 9); pending KB-repo chain validation
version: "0.2.0"
created: 2026-06-09
updated: 2026-06-09
---

# hypothesis-generator Structural Observation Consumption (Phase C)

## Background

Phase A added the optional `silver-structural-observation` row to the KB Read-side Mapping
(commit `aeaf19f`), so `reference/cro-{scope}/live-structure.md` loads into detect's context in KB
mode. Phase B built the producer (live-capture). But loading is not consumption:
`phases/detect.md` Step 1 signal extraction is file-keyed (one stanza per named context file) and
has no stanza for the structural artifact, so its fields never become signals. The Tier 2
reframing gates (mobile defect-vs-layout, site-wide scope correction) do not exist at all. This
change closes the gap so structural facts actually drive and reframe hypotheses.

## Current State

- Read-side row + note exist ([SKILL.md](../../skills/hypothesis-generator/SKILL.md) lines 91, 97); the body loads but no extraction path consumes it.
- [detect.md](../../skills/hypothesis-generator/phases/detect.md) Step 1 enumerates extraction stanzas for five named files; none for the structural artifact. Step 1c performance triggers are presence-gated; no structural analog.
- [construct.md](../../skills/hypothesis-generator/phases/construct.md) has no mobile defect-vs-layout routing on direct render observation and no site-wide scope generalization.
- CTR-14 (Device/OS Defect Misattribution) detection signals are performance-profile-only.
- Producer artifact verified real (schema 1.1, tri-state convention, per-page digest); every consumption-map pattern ID exists in the pattern library.

## Approach

Five-file markdown edit, no new files, zero validator churn (phase count 4, pattern count 32,
CTR count 14 all unchanged). Design decisions:

1. **Mobile gate extends CTR-14** rather than adding CTR-15: `mobile_render_clean: false` is a new
   detection signal for the existing defect-misattribution trigger; `true` is exactly the "error
   family ruled out" observation its gate condition waits for.
2. **Both an extraction stanza and a gated Step 1e trigger table**: the stanza feeds Step 2 generic
   matching (copy skeleton, PS-04, HM-02); Step 1e carries what generic matching cannot express:
   tri-state semantics (present fires, absent suppresses or fires absence patterns, not_checked
   does neither) and the no-double-count boundary (structure supplies targets, performance
   supplies firing counts for engagement patterns).
3. **Site-wide scope correction in construct.md Step 1** (target identification, not bundling).
4. **Absence is never penalized**: missing artifact skips Step 1e with no confidence penalty or
   global cap (absence means structure was not assessed).
5. Out of scope by design: PE-01/02 (needs cross-session variance), NX-03 (needs behavior),
   NX-05 (optional, deferred), PS-02 (page height feeds it as an ordinary signal).

### Evals

No matched eval tasks (`_evals/` does not exist in this repo). Validation is via the skill's own
validator script plus a functional chain run against a real artifact in the bound KB repo.

### Tests

No scripts added, modified, or removed. Not script-affecting.

## Requirements

1. `skills/hypothesis-generator/phases/detect.md`: Required Inputs bullet; graceful-degradation
   row (skip Step 1e, no confidence penalty); Step 1 extraction stanza (site-level + per-page
   fields, tri-state never coerced, missing field = not_checked, trust qualifiers downgrade to
   partial); new Step 1e gated trigger table per the consumption map.
2. `skills/hypothesis-generator/phases/construct.md`: red-flag mobile branch on
   `mobile_render_clean` (false routes fix-and-monitor, true proceeds as layout/content test);
   Step 1 site-wide scope check (`form_recurs_sitewide`, `sitewide_primary_cta_label`) plus EE
   element-targeting sentence; Step 2 observed current-state citation plus baseline boundary echo.
3. `modules/contrarian-triggers.md` CTR-14: structural detection signal (false) and gate-clearing
   observation (true). Heading and `Trigger count: 14` line untouched.
4. `skills/hypothesis-generator/SKILL.md`: rewrite the read-side note (the "no per-trigger
   handling" claim becomes false); KB-mode precondition bullet with no-penalty absence semantics
   and a /live-capture prerequisite suggestion; purity-list additions (`live-structure.md`,
   "structural observation", raw field names).
5. `skills/hypothesis-generator/CHANGELOG.md`: one dense Added bullet under [Unreleased]. No
   version bump.

## Validation

1. `bash scripts/validate-hypothesis-generator.sh`: all PASS, counts unchanged.
2. Purity greps empty: em dashes over edited files; client strings (none enter the public repo).
3. Functional chain run in the bound KB repo against the real structural artifact: structural
   trigger fires AND lands in the roadmap; mobile gate both directions; site-wide form
   generalization; tri-state honored (not_checked neither fires nor suppresses); absence
   regression completes with no confidence penalty; roadmap body purity (no field names, pattern
   IDs, or artifact references).

Cross-repo dependency: the functional run executes in the bound KB repo (private). No client data
enters this repo.

## Changelog

| Version | Changes |
|---|---|
| 0.2.0 | Build complete: all five file edits applied, validator 24/24 PASS, purity greps clean. Note: the working tree was switched to dj_live-capture-skill by a parallel session mid-build; Phase A's two SKILL.md lines and CHANGELOG bullet (commit aeaf19f, unmerged branch dj_hypgen-structural-observation-readside) were re-applied in the working tree so content is complete regardless of branch. Branch reconciliation required at commit time. |
| 0.1.0 | Initial change document (Backlog), created from approved plan; building in-session. |
