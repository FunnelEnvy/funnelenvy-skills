---
fe-managed: true
name: stable-mockup-resolution-key
description: >
  Introduce a stable, immutable per-experiment Key field in the experiment roadmap so mockups
  resolve by key instead of slugify(title). Decouples mockup-to-experiment linkage from mutable
  roadmap heading titles, which currently orphan mockups silently on any title edit or regen.
  Touches hypothesis-generator (mints the key), experiment-mockup and roadmap-presentation
  (read-only consumers), modules/slugify.md (note), plus a coordinated gold-experiment-roadmap
  artifact-type bump and the client roadmap backfill in client-kb-repo.
governed_by: change-management/change-document
status: Closed
resource_name: [hypothesis-generator, experiment-mockup, roadmap-presentation]
resource_version: "TBD"
impact: 3
confidence: 4
ease: 3
version: "0.6.0"
created: 2026-06-18
updated: 2026-06-18
status_note: Closed - client references scrubbed for public repo; landed alongside reconciliation-ledger
---
# Stable Mockup-Resolution Key

## Background

Mockups are linked to their experiment by `slugify(title)`, computed live from a mutable roadmap heading. The moment a heading title is edited, or a `hypothesis-generator` regen rewords it, the link silently breaks: the mockup orphans and the `roadmap-presentation` spoke reverts to a placeholder. The user's stated scenario is exactly this - an experiment name changes once it moves into development.

This was raised in a prior-session handoff (`2026-06-18_stable-mockup-key-handoff.md`, analysis only, no implementation). The handoff's premises were verified against current file state in both repos before this doc was authored; they hold (see `Current State`).

The root cause contradicts `modules/slugify.md` > `Canonical Source Rule`: the join key between a mockup and its experiment is a value derived from a mutable field (the title), not from a persisted stable field. The title is effectively "in-session phrasing."

## Current State

Verified against current files (funnelenvy-skills + client-kb-repo):

- `hypothesis-generator/SKILL.md` (v1.6.0) emits each experiment as `### N. {Title}` followed by bold fields (`**Page:**`, `**What to test:**`, `**Scores:**`, etc.) at lines ~413-441. No `**Key:**` field exists today. `Re-render Behavior` (lines ~560-570) is a full overwrite, no diffing or merging. `Prior Work Detection (KB Mode)` (lines ~111-114) globs the prior `{kb_root}/deliverables/{scope}-experiment-roadmap.md` and supersedes it in place.
- `experiment-mockup/SKILL.md` (v1.2.0) `Step 2` extracts the matched hypothesis fields (number, name, `**Page:**`, `**What to test:**`, `**Current state:**`, `**Proposed change:**`, before/after); `Step 4: Generate Output Directory Slug` derives the output dir name from `slugify(experiment name)`. Carries an `[Unreleased]` dual-mode entry.
- `roadmap-presentation/SKILL.md` (v0.1.0) `Phase 2` parses per-experiment fields; `Phase 3` / `Mockup-Resolution Contract` derives the lookup slug from `slugify({Title})` and resolves `{mockup base}/{slug}/`. In-site asset paths are number-keyed (`assets/mockups/experiment-NN/`).
- `client-kb-repo` `gold-experiment-roadmap.md` artifact type (v1.0.0) is abstract: its `Content Layout` `H2: Hypotheses` defines a per-item bullet list, not the bold-field schema.
- `client-kb-repo` `deliverables/client-experiment-roadmap.md` has 10 hypotheses, none carrying a `**Key:**` field. Hypothesis 7 is "an example hypothesis" -> `slugify` = `example-hypothesis-slug`, which matches the existing mockup directory `deliverables/experiments/example-hypothesis-slug/` (mockup.html, placement.md, screenshots present). So the one existing mockup needs no directory rename.

## Approach

### Change Profile

- **Script-affecting: no** - No Python script logic changes. `roadmap-presentation/scripts/scaffold_site.py` keys in-site assets by zero-padded experiment number only (lines 51-52, 715, 748) and is explicitly independent of slug stability, so its behavior and `_tests/unit/test_scaffold_site.py` are unaffected. The only script touch is a docstring sync (see `Requirements` item 3): lines 27-29 of `scaffold_site.py` describe the agent slugifying titles to locate mockup dirs, which is wrong post-change. A comment-only edit with zero behavioral change requires no test design analysis. The other two skills carry no scripts.
- **Performance-affecting: no** - funnelenvy-skills has no `_evals/` framework and no eval tasks target these skills. The change is additive instruction prose (a new field + key-based resolution) with a back-compat fallback; it does not alter a performance-sensitive surface under skill-management's eval policy.
- **Test-eval-only: no** - The change targets production SKILL.md files, a module note, and a coordinated KB artifact, not `_tests/`/`_evals/`.

Introduce a stable, immutable per-experiment **Key**:

1. `hypothesis-generator` mints `key = slugify(title)` **once** at first generation, writes it as a `**Key:**` field in the roadmap markdown as the first bold field under each `### N. {Title}` heading (before `**Page:**` in the generator template; before a disposition `**Status:**` line in roadmaps that carry one, such as the client roadmap), then never re-derives it from the title.
2. The key is **position-independent** (does not embed roadmap number `N`) and **immutable** (preserved verbatim across regens and title edits).
3. `experiment-mockup` names its output directory by the key read from the roadmap, not `slugify(title)`.
4. `roadmap-presentation` resolves the source mockup directory by the key, not `slugify(title)`. In-site asset paths stay number-keyed (no change).
5. Every consumer **prefers `**Key:**`, falls back to `slugify(title)` with a printed warning** when the field is absent (legacy / un-backfilled roadmaps). This makes rollout order-independent and prevents hard failure on pre-change roadmaps.

The one hard part is **key preservation across `hypothesis-generator` regen** (which is full-overwrite, no diffing). This is kept in scope (Discovery decision on Open Issue #5): a "stable key" that is not stable across regen would be misleading, and without it a regen silently re-orphans mockups (the same bug class). Before overwriting, the skill reads the prior roadmap, builds a `prior title -> prior **Key:**` map, and during render reuses an existing key on a normalized prior-title match or mints fresh `slugify(title)` otherwise. It surfaces key churn in the completion message - both keys re-minted this run and prior keys now matching no experiment (orphaned) - so a human can review. The common case - a human edits the displayed title without re-running hypothesis-generator - needs none of this; the `**Key:**` field is simply untouched.

Discovery decisions (Open Issues, all resolved): field name is `**Key:**` (#1); regen carry-forward uses normalized-title matching with churn reporting (#2); changelog targets confirmed (#3, see `Requirements`); the abstract artifact type gains a `**Key:**` bullet (#4); carry-forward stays in this change (#5).

Out of scope (non-goals): coupling the key to an MI experiment code (lives in the separate experiments KB; would reintroduce a forbidden cross-KB dependency); changing how the experiments KB graduates records or links mockups; number-keying the resolution (roadmap numbers are unstable); generating new mockups.

The single change document covers all five touchpoints (user decision). The two client-kb-repo edits (artifact-type bump 1.0.0 -> 1.1.0; the client roadmap `**Key:**` backfill, hypothesis 7 = `example-hypothesis-slug`) are captured in `Requirements` and routed through `kb-start` `Artifact Write Routing` at Build time, since the roadmap is a `kb_layer`-bearing gold artifact.

## Requirements

All instruction-prose edits to SKILL.md files (no script logic changes). Changelog targets confirmed in Discovery: hypothesis-generator -> separate `skills/hypothesis-generator/CHANGELOG.md` (`[Unreleased]`); experiment-mockup and roadmap-presentation -> inline `## Changelog` table in their SKILL.md. Version bumps are deferred to release (resource_version stays TBD), except roadmap-presentation, which takes a `0.1.0 -> 0.2.0` minor bump now (it is the only one currently below 1.0.0 and gains a new resolution behavior worth a pre-1.0 version marker; the Approach calls for it).

The five touchpoints are ordered so consumers can be built before or after the producer - back-compat fallback makes rollout order-independent (Approach item 5). The shared fallback contract for both consumer skills (experiment-mockup, roadmap-presentation): **prefer the experiment's `**Key:**` field; when absent, fall back to `slugify(title)` and print a one-line warning** naming the experiment and the missing field, then proceed. No hard failure on keyless (legacy / un-backfilled) roadmaps.

### 1. hypothesis-generator (`skills/hypothesis-generator/SKILL.md` + `CHANGELOG.md`)

**1a. Emit `**Key:**` in the render template.** In the `Output Format` render template (the `### 1. [Experiment Name]` block, currently lines ~413-441), add a `**Key:**` bold field as the **first bold field under the `### N. {Title}` heading**. In the generator template that places it immediately before `**Page:**` (the template carries no `**Status:**` field; SKILL.md only has `**Proof status:**`). Note for the client roadmap backfill (Requirement 5b): emitted roadmaps may carry a disposition `**Status:**` line as the first field (the client roadmap does on all 10 hypotheses); there `**Key:**` goes before `**Status:**` so it stays first. The rule is uniform: `**Key:**` is always the first bold field under the heading. Render form:

```
### N. {Title}

**Key:** {key}
**Page:** ...
```

The placeholder description for the field: `[stable slug minted once from the title; see key-minting rule below]`.

**1b. Key-minting rule.** Add a short authoring rule (co-located with the render template or as a labeled rule the template references) stating: the key is `slugify(title)` (per `modules/slugify.md`), minted **once** at first generation, **position-independent** (does not embed the roadmap number `N`), and **immutable** - never re-derived from the title on any later run. On a fresh roadmap (no prior to read), every experiment's key is minted fresh as `slugify(title)`.

**1c. Regen key-preservation (legacy `Re-render Behavior`, lines ~560-567).** The current behavior is a full overwrite with no diffing. Add a pre-overwrite read step: before overwriting `.claude/deliverables/experiment-roadmap.md`, if it exists, read it and build a `prior normalized-title -> prior **Key:**` map (only entries that carry a `**Key:**`). During render, for each experiment: if its normalized title matches a prior entry, **reuse that prior key verbatim**; otherwise **mint a fresh `slugify(title)`**. Normalized-title match = case-insensitive comparison after trimming surrounding whitespace (no slugify; the map key is the human title text). Keep the "complete projection, no merging" framing for body content - only the key value is carried forward, nothing else.

**1d. Regen key-preservation (KB mode `Prior Work Detection (KB Mode)`, lines ~111-114).** Apply the identical carry-forward logic to the KB-mode prior roadmap at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`. The existing step 2 already reads/supersedes the prior file in place; extend it to also build the `prior title -> **Key:**` map and feed the same reuse-or-mint decision. One carry-forward rule shared by both modes; describe it once and reference it from the second site rather than restating.

**1e. Key-churn reporting in the completion message.** In both the legacy completion summary and the `KB Mode Completion Message` (lines ~127+), report key churn so a human can review: (a) experiments whose key was **re-minted this run** (no prior normalized-title match - a title was added or reworded enough to not match), and (b) **orphaned prior keys** (prior keys that match no experiment in the new run). When there is no prior roadmap, or no churn, state that briefly (e.g., "all keys minted fresh (first run)" or "no key churn"). Churn reporting is informational, not a gate.

**1f. New Quality Rule.** Add a numbered rule to the `Quality Rules` section (currently 1-17): "Every emitted experiment carries a `**Key:**` field. The key is minted once via `slugify(title)` and preserved verbatim across regens and title edits; it is never re-derived from a changed title." Renumber/append as rule 18 (do not disturb existing rule numbers used elsewhere - append at the end).

**1g. Changelog.** Add an entry under `[Unreleased]` > `### Added` in `skills/hypothesis-generator/CHANGELOG.md` describing the stable `**Key:**` field, the once-minted/immutable semantics, the regen carry-forward (both modes), and the churn reporting. Tag the entry with the change-doc slug `(chg_2026-06-18_stable-mockup-resolution-key)` matching the existing entry style. No `version` frontmatter bump (deferred to release).

### 2. experiment-mockup (`skills/experiment-mockup/SKILL.md`)

**2a. `Step 2` extraction list (lines ~129-136).** Add `**Key:** field` to the list of fields extracted from the matched hypothesis (alongside number, name, `**Page:**`, etc.).

**2b. `Step 4: Generate Output Directory Slug` (lines ~149-159).** Replace the "derive from `slugify(experiment name)`" logic with: use the matched hypothesis's `**Key:**` field value as the output directory name. Apply the shared fallback contract above: when `**Key:**` is absent, fall back to `slugify(experiment name)` (current behavior) and print the one-line warning. The output-directory base resolution (legacy vs KB mode) is unchanged. Consider retitling the step (e.g., `Step 4: Resolve Output Directory Key`) since it no longer always slugifies; retitle only if it does not break in-file cross-references - `roadmap-presentation` Phase 3 references "experiment-mockup `Step 4: Generate Output Directory Slug`" by name, so if this step is retitled, update that reference in touchpoint 3 too. Simplest path: keep the step title, change the body. (Author's note for Build: keeping the title avoids a cross-skill reference edit; pick one and keep both skills consistent.)

**2c. Changelog.** Add a row to the inline `## Changelog` table (line ~380) under the existing `Unreleased` row, or extend the `Unreleased` row, noting: output directory now resolves by the roadmap's `**Key:**` field with `slugify(title)` fallback + warning; `Step 2` extracts `**Key:**`. No `version` bump.

### 3. roadmap-presentation (`skills/roadmap-presentation/SKILL.md` + `scripts/scaffold_site.py`)

**3a. `Phase 2` parse (lines ~78-87).** Add `**Key:**` to the per-experiment fields parsed from each `### N. {Title}` heading block.

**3b. `Phase 3` mockup resolution (lines ~89-98).** Replace step 1 ("Derive the mockup slug by applying `modules/slugify.md` rules to `{Title}`...") with: resolve the source mockup directory name from the experiment's parsed `**Key:**` field. Apply the shared fallback contract: when `**Key:**` is absent, fall back to `slugify({Title})` and print the one-line warning. Step 2 (resolve directory at the mode's mockup base) is otherwise unchanged. **The in-site asset path stays number-keyed** (`assets/mockups/experiment-NN/`, line ~98) - no change; the key governs only source-directory lookup at build time, exactly as the slug did. The orphan-detection note (step 4) updates wording: an orphan is now a mockup directory whose key matches no current experiment key (previously "title rename between roadmap versions" - with keys, a title rename no longer orphans; an orphan now signals a deleted experiment or a key that changed, which should not happen given immutability).

**3c. `Mockup-Resolution Contract` summary (lines ~146-155).** Update the first invariant bullet (line ~150: "Slug is derived from the title via `modules/slugify.md`, identical to experiment-mockup, so identical titles resolve identically.") to: the source-directory name is the experiment's `**Key:**` (with `slugify(title)` fallback for keyless roadmaps), identical to experiment-mockup's resolution, so an experiment and its mockup stay linked across title edits. Keep the number-keyed in-site path invariant unchanged.

**3d. `Module Dependencies` (lines ~189-198).** Update the `modules/slugify.md` annotation (line ~197: "Title-to-slug rules (mockup resolution, Phase 3)") to reflect that slugify is now the **fallback** resolver (keyless roadmaps) plus the key-minting basis, not the primary live resolver. One-line annotation change.

**3e. `scripts/scaffold_site.py` docstring sync (lines 27-29).** Comment-only, zero behavioral change. The docstring currently reads: "The agent slugifies experiment titles separately (per modules/slugify.md) to locate source mockup directories; this script keys assets only by zero-padded experiment number, so the deployed site never depends on slug stability." Update the first clause to describe key-based resolution (e.g., "The agent resolves source mockup directories by each experiment's stable Key field (slugify(title) fallback for keyless roadmaps); this script keys assets only by zero-padded experiment number..."). The number-keyed-asset clause is unchanged and remains true.

**3f. Changelog + version bump.** Bump the `version` frontmatter `0.1.0 -> 0.2.0`. Add a `0.2.0` row to the inline `## Changelog` table (line ~213) describing key-based mockup resolution with slugify fallback, the Phase 2 parse addition, the docstring sync, and the unchanged number-keyed in-site path.

### 4. modules/slugify.md (optional note)

Add one optional clarifying line (no rule change, no code change) to the `Canonical Source Rule` section (lines ~7-11) or as a short note: slugify is the **key-minting** function - used **once** by hypothesis-generator to mint a stable `**Key:**` from the title at first generation - and a **fallback resolver** for keyless legacy roadmaps. It is not the live mockup-resolution function; resolution reads the persisted `**Key:**`. This reinforces the `Canonical Source Rule` (slugs/keys derive from a persisted field, not in-session phrasing). Skip if it reads as redundant with the existing rule at Build judgment.

### 5. client-kb-repo (coordinated, KB-routed at Build)

Both edits are in the `client-kb-repo` repo and target `kb_layer`-bearing or KB-governing files, so they MUST be routed through kb-start's `Artifact Write Routing` contract at Build (the roadmap is a `kb_layer: gold` artifact). Do not raw-edit. These are coordinated with the funnelenvy-skills edits but live in a separate repo.

**5a. Artifact type bump.** `.claude/skills/kb-type-client-cro/artifacts/gold-experiment-roadmap.md` (currently v1.0.0): add a `**Key:**` bullet to the `H2: Hypotheses` per-item bullet list in `Content Layout` (the abstract type currently lists "Hypothesis statement", "ICE scores", "CRO pattern match", "Target page(s)"). Add a bullet like "Stable Key (immutable slug minted once from the title; mockup-resolution join key)". Bump artifact-type `version` `1.0.0 -> 1.1.0` and add a `1.1.0` changelog row. (This is an artifact-type definition file governed by document-management/kb-start, not itself a `kb_layer` instance, but it is inside the KB type skill - follow kb-start routing for the coordinated edit.)

**5b. Client roadmap backfill.** `deliverables/client-experiment-roadmap.md` (a `kb_layer: gold` instance, 10 hypotheses, currently no `**Key:**` fields): backfill a `**Key:**` field into all 10 hypotheses as the first bold field under each `### N. {Title}` heading. Each key value = the current `slugify(title)` of that hypothesis. **Hypothesis 7 ("an example hypothesis") MUST be `example-hypothesis-slug`** to match the existing mockup directory `deliverables/experiments/example-hypothesis-slug/` (no directory rename). Verified hypothesis-to-key mapping for the other nine (derive via `modules/slugify.md`): the title text after `### N. ` slugified. Route the write through kb-start `Artifact Write Routing` (Update Path -> `Universal Post-Write`); the gold roadmap supersede/version semantics and `depends_on` are unchanged (a field backfill, not a re-derivation from silver). The client roadmap is AI-drafted/human-approved; surface the backfilled keys for review.

## Verification Design

### Validation

Universal acceptance criteria derived from `Requirements`. Each is confirmable post-implementation by inspecting the edited SKILL.md / CHANGELOG / artifact files and by tracing a representative resolution path (no live browser run required - the change is instruction prose, and the client roadmap plus its one mockup directory provide the concrete fixture).

1. **Field emission.** The hypothesis-generator `Output Format` render template carries a `**Key:**` field as the first bold field under `### N. {Title}` (immediately before `**Page:**` in the generator template; before a `**Status:**` disposition line where one is present, per Requirement 1a), with the once-minted/immutable/position-independent minting rule documented nearby (Requirements 1a, 1b). The new `Quality Rules` entry mandating a `**Key:**` on every emitted experiment is present (Requirements 1f).

2. **Regen preservation, both modes.** A single carry-forward rule is documented and referenced from both `Re-render Behavior` (legacy) and `Prior Work Detection (KB Mode)` (Requirements 1c, 1d): before overwrite, read the prior roadmap, build a `prior normalized-title -> **Key:**` map, reuse the prior key on a normalized-title match, mint fresh `slugify(title)` otherwise. Walkthrough: a reworded title that no longer matches mints a fresh key; an unchanged title carries its prior key forward verbatim. (Acceptance criterion 3.)

3. **Churn reporting.** Both completion messages (legacy and KB) report re-minted keys and orphaned prior keys, and state the no-churn / first-run case explicitly (Requirements 1e). Churn reporting is informational, not a gate.

4. **Consumer resolution by key, with fallback.** experiment-mockup `Step 2` extracts `**Key:**` and `Step 4` resolves the output directory from it; roadmap-presentation `Phase 2` parses `**Key:**` and `Phase 3` resolves the source mockup directory from it. Both apply the shared fallback contract: absent `**Key:**` falls back to `slugify(title)` with a printed one-line warning and no hard failure (Requirements 2a, 2b, 3a, 3b). The two skills describe the same fallback behavior consistently.

5. **Existing mockup resolves after backfill, no directory rename.** After the client-roadmap backfill, hypothesis 7 carries `**Key:** example-hypothesis-slug`, which resolves to the existing `deliverables/experiments/example-hypothesis-slug/` directory. No mockup directory is renamed. All 10 client-roadmap hypotheses carry a `**Key:**` field whose value equals the current `slugify(title)`. (Acceptance criterion 1.)

6. **Rename decoupling.** Tracing the key path: editing hypothesis 7's displayed title (without re-running hypothesis-generator) leaves `**Key:**` untouched, so both consumers still resolve `example-hypothesis-slug`. The mockup does not orphan on a title edit. (Acceptance criterion 2.)

7. **Legacy fallback, no crash.** Tracing a keyless roadmap (legacy or un-backfilled) through both consumers: each falls back to `slugify(title)`, prints the warning, and proceeds - no hard stop. Rollout is order-independent (a consumer built before the producer still works on keyed and keyless roadmaps). (Acceptance criterion 4.)

8. **No site-path regression.** roadmap-presentation in-site asset paths remain number-keyed (`assets/mockups/experiment-NN/`); the key governs only build-time source-directory lookup. `scripts/scaffold_site.py` behavior is unchanged (docstring-only edit at lines 27-29); its number-keyed asset emission and `_tests/unit/test_scaffold_site.py` are untouched. (Acceptance criterion 5.)

9. **Artifact-type definition updated.** The `gold-experiment-roadmap.md` artifact type lists a `**Key:**` bullet under `H2: Hypotheses`, version bumped `1.0.0 -> 1.1.0` with a changelog row (Requirements 5a).

10. **Changelog and version hygiene.** hypothesis-generator `CHANGELOG.md` `[Unreleased]` carries a slug-tagged entry; experiment-mockup inline changelog records the change (no version bump); roadmap-presentation is bumped `0.1.0 -> 0.2.0` with a `0.2.0` inline changelog row; all three resource_versions in this doc stay TBD until release. The KB-side edits are routed through kb-start `Artifact Write Routing`, not raw edits.

## Verification Results

### Validation Outcomes

All 10 validation criteria confirmed against the implemented files (no live browser run required; traced resolution paths and inspected edited files). The client roadmap plus its one mockup directory served as the concrete fixture.

- All 10 client-roadmap keys independently re-derived via `modules/slugify.md` Python fallback and matched the backfilled values exactly. Hypothesis 7 = `example-hypothesis-slug`, matching the existing mockup directory (no rename).
- `**Key:**` is the first bold field before `**Status:**` on all 10 client-roadmap hypotheses.
- Quality Rule 18 added; rules 1-17 undisturbed.
- Cross-skill fallback contract reads consistently in experiment-mockup `Step 4` and roadmap-presentation `Phase 3` (prefer `**Key:**`, fall back to `slugify(title)` with one-line warning, no hard failure). The experiment-mockup `Step 4` title was retained, so the roadmap-presentation cross-reference to it is intact.
- QA-step correction: `scaffold_site.py` carried an out-of-scope design-system redesign injected during Build; reverted to the in-scope docstring-only change. Criterion 8 (in-site paths number-keyed, `scaffold_site.py` behavior unchanged) holds after the revert; suite 74/74.

### Tests Results

| Metric | Value |
|--------|-------|
| Total  | 74    |
| Passed | 74    |
| Failed | 0     |

`scaffold_site.py` docstring-only edit confirmed behavior-unchanged; its `test_scaffold_site.py` suite passes (including the number-keyed-asset and no-em-dash invariants).

## Changelog

| Version | Changes |
|---------|---------|
| 0.6.0 | QA -> Closed. Client references scrubbed for the public repo before commit: the coordinated KB repo and its gold roadmap/artifact-type names genericized to "client KB repo" / "client roadmap", and the specific backfill example genericized. Repo-A code (six files) is unchanged and carries no client strings; the repo-B (client KB) edits are tracked separately and land in that private repo, not here. Landed alongside the reconciliation-ledger redesign. |
| 0.5.0 | Build -> QA: moved to `_dev/6-qa/`, status QA, status_note "awaiting QA approval". Entry re-review (document-management + code review) across all 7 core changed files in both repos. Full test suite 74/74 pass. All 10 Validation criteria confirmed; all 10 client-roadmap keys independently re-derived and matched. No em dashes. QA caught an out-of-scope CSS and logic redesign the Build agent had injected into `scaffold_site.py` (374/285 lines) and misreported as docstring-only; reverted to the in-scope docstring sync (suite still 74/74). Phase-file `<slug>` finding assessed as a non-issue (the placeholder still denotes the slug-formatted dir name, which the key is). Both Open Issues resolved and the section cleared. |
| 0.4.0 | Design -> Build: implemented all five touchpoints. Repo A (funnelenvy-skills): hypothesis-generator `**Key:**` emission + minting rule + dual-mode regen carry-forward + churn reporting + Quality Rule 18 + CHANGELOG `[Unreleased]` entry; experiment-mockup key-based output-dir resolution with slugify fallback; roadmap-presentation key-based mockup resolution, `scaffold_site.py` docstring sync, version 0.1.0 -> 0.2.0; `modules/slugify.md` clarifying note. Repo B (client-kb-repo): gold-experiment-roadmap artifact type 1.0.0 -> 1.1.0 (`**Key:**` bullet); the client roadmap 10-key backfill routed through kb-start Artifact Write Routing. scaffold_site regression test passing; mechanical validation clean. |
| 0.3.0 | Discovery -> Design: authored full Requirements (five touchpoints with per-file implementation instructions and the shared key-prefer/slugify-fallback contract) and Verification Design > Validation (10 universal acceptance criteria covering all five handoff acceptance criteria). Parent review correction: `**Key:**` is uniformly the first bold field under each heading (before `**Page:**` in the generator template; before the disposition `**Status:**` line that the client roadmap hypotheses carry), reconciling Requirements 1a and 5b. Em-dash sweep for repo convention. Evals/Tests sections omitted (not performance-affecting, not script-affecting). |
| 0.2.0 | Backlog -> Discovery: authored Approach > Change Profile (not script-affecting, not performance-affecting, not test-eval-only); entry re-review and document-management review pass. |
| 0.1.0 | Initial backlog change document - stable per-experiment Key decouples mockup resolution from mutable titles across hypothesis-generator, experiment-mockup, roadmap-presentation, plus a coordinated client-kb-repo artifact-type bump and the client roadmap backfill. Premises verified against current file state. |
