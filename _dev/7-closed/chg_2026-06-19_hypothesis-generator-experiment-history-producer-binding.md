---
fe-managed: true
name: hypothesis-generator-experiment-history-producer-binding
description: >
  Make hypothesis-generator's experiment-history input actually bind. The closed experiment-history
  consumption change authored a Read-side Mapping row that points at the wrong artifact (the roadmap
  the skill OUTPUTS, not the producer KB's gold index) and added no mechanism to discover the producer
  KB. As a result a KB-mode run never reads a bound completed-experiment KB: no completed-experiment
  evidence, no Step 1g triggers, no Step 4 replication modifier, no Step 7 winner-replication sequencing
  -- silently, because absence is penalty-free by design. Correct the table cell and add producer-KB
  discovery to the Mode Resolution Procedure.
governed_by: change-management/change-document
status: Closed
resource_name: hypothesis-generator
resource_version: "TBD"
initiative: cro-kb-path-b
impact: 4
confidence: 4
ease: 3
version: "0.8.0"
created: 2026-06-19
updated: 2026-06-19
related:
  - hypothesis-generator-kb-silver-input-basenames
  - hypothesis-generator-experiment-history-consumption
---
# hypothesis-generator: Experiment-History Producer-KB Binding

## Background

The experiment-history consumption feature (`chg_2026-06-14_hypothesis-generator-experiment-history-consumption`, shipped in skill **v1.7.0** on 2026-06-18 -- see `CHANGELOG.md` `[1.7.0]`) wired `hypothesis-generator` to read a completed-experiment knowledge base so a measured winner can drive a replication-grade Quick Win, the `Evidence From Completed Experiments` section, the Step 1g detect leg, the Step 4 replication Confidence/Ease modifier, and the Step 7 winner-replication sequencing. That change carried an explicit release gate -- a bound-KB functional regression in a consumer repo -- but shipped in v1.7.0 without the gate ever running, because no consumer had a completed-experiment KB bound at the time. The broken binding therefore shipped in a release; these are defects in released code, not in an unreleased change.

A consumer repo has now bound such a KB, exposing the defect. That repo declares two knowledge bases: a primary strategy KB at repo root (which defines the OUTPUT type `gold-experiment-roadmap`), and a second, separate completed-experiment KB whose gold `index.md` is typed `gold-experiment-index` -- the completed-experiment rollup and the KB's designated outbound reader surface. Its records carry one measured winner (`outcome: winner`) and two inconclusive interim reads (`outcome: inconclusive`). On a KB-mode regen (`/hypothesis-generator --scope <scope>`), none of it is read. The binding is dead, and because absence is designed to be silent and penalty-free, the run looks normal -- it behaves as if no experiment has ever read out.

This is why that scope's roadmap had to be hand-edited to ingest the read-outs rather than regenerated: a regen would have ignored the experiments KB entirely and clobbered the hand-finalized reconciliation. A correct binding lets a future regen pick up the measured winner natively.

## Current State

Two defects in [SKILL.md](../../skills/hypothesis-generator/SKILL.md), both originating in the closed experiment-history change's Requirement 1:

**1. The Read-side Mapping cell describes the wrong artifact.** Line 94:

```
| (none -- KB-native) | `gold-experiment-roadmap` (producer KB) + the silver insight records it links | `deliverables/{scope}-experiment-roadmap.md` (producer KB root) + linked silver insight paths | optional |
```

`deliverables/{scope}-experiment-roadmap.md` is the artifact the skill **outputs** (the `Output Mapping`, line 105, writes exactly this path). The prose everywhere else correctly calls the input the producer KB's **gold index plus the silver insight records it links**: line 101 ("read from the producer KB's gold index plus the silver insight records that index links"), line 184, [detect.md](../../skills/hypothesis-generator/phases/detect.md) lines 12 and 255, [score.md](../../skills/hypothesis-generator/phases/score.md) line 186, and the skill `CHANGELOG.md` `[1.7.0]` entry. The table cell is internally inconsistent with its own prose -- it conflated the output type (`gold-experiment-roadmap`, defined by the strategy KB) with the input type (`gold-experiment-index`, defined by the experiments KB).

**2. There is no producer-KB discovery mechanism.** The `Mode Resolution Procedure` (lines 69-76) resolves only the **output** KB -- the one defining `gold-experiment-roadmap`, `silver-strategy-context`, `bronze-company-facts`. Nothing discovers a **second** KB acting as the experiment-history producer, nor locates its gold index. So even with the prose intent, the skill has no way to find the producer's `index.md`. In the consumer repo the producer's gold index (`gold-experiment-index`) lives at the experiments-KB root, the shape the feature was modeled on. Nothing in the skill maps to that shape, so the input is treated as absent.

`roadmap-presentation` was checked: it reads only its own `gold-experiment-roadmap` as source (`SKILL.md` line 53) and consumes no experiment-history input, so it carries no equivalent self-referential producer assumption. No fix needed there.

## Discovery

### How does output-KB resolution work today, and what is the analogous producer key?

The `Mode Resolution Procedure` step 3 confirms KB mode by verifying the bound type skill's `artifacts/` directory defines three **exact artifact-type names**: `gold-experiment-roadmap`, `silver-strategy-context`, `bronze-company-facts`. These are not client-specific identifiers -- they are the skill's own contract type names, shared across every consumer that binds this skill. Keying on them is the established, client-agnostic pattern.

The producer is symmetric. A completed-experiment KB's outbound surface is a gold index typed `gold-experiment-index`. That type name is a cross-consumer convention (independent consumer experiments KBs use the same name for the same role), exactly like `gold-experiment-roadmap` -- so keying producer discovery on it is no more client-specific than the output-KB keys already are.

**Decision (OQ1):** key producer discovery on the artifact-type name `gold-experiment-index`. Discovery scans declared KBs for a second KB (distinct from the output KB) whose type skill's `artifacts/` directory defines `gold-experiment-index`, and resolves that KB's root + gold index path from the declaration. This mirrors output-KB resolution one-for-one. A capability/marker-based scheme was considered and rejected as over-engineering: it would invent a second discovery convention when the skill already keys on exact type names everywhere else, and there is no second producer-type name in evidence to generalize over.

### How are multiple KBs declared, and how does discovery walk them?

A repo's `## Knowledge Bases` section may declare the primary KB in the section body and a second KB in a `###` subsection, each naming its type skill (`.claude/skills/{kb-type}/`) and root. Discovery must not assume a fixed heading.

**Decision (OQ2):** after resolving the output KB, enumerate every KB declared in the `## Knowledge Bases` section (body and all subsections), resolve each one's type skill and root, and select the producer as the declared KB -- other than the output KB -- whose type skill's `artifacts/` defines `gold-experiment-index`. If none: no producer bound (penalty-free absence, unchanged behavior). If more than one defines it: prefer the producer whose gold index contains records matching the run `--scope`; if still ambiguous, use the first declared and log the choice in the run output. In practice a repo declares one experiments KB; the tie-break is a documented safeguard, not an expected path.

### Scope filtering and graceful absence

**Decision (OQ3, revised by OQ5):** discovery resolves the producer's gold index path only; downstream scope mapping (see OQ5) governs which records are read. A resolved producer whose index holds no records for the run scope degrades to "no matching records" -- identical to the penalty-free absent case -- never an error. A producer declared but unresolvable (type skill missing, index file absent) likewise degrades to absent and is logged, never fatal: per line 184 the experiment-history input is explicitly NOT a mode-resolution requirement, so a broken producer binding must not flip the run to legacy or hard-stop the way a broken OUTPUT binding does.

### roadmap-presentation re-confirmation (OQ4)

Re-confirmed: `roadmap-presentation/SKILL.md` line 53 resolves only its own `gold-experiment-roadmap` source artifact and has no experiment-history read. No other current or in-flight consumer of the experiment-history input exists. No change needed outside `hypothesis-generator`.

### Scope-vocabulary mapping (OQ5 -- surfaced by the QA bound-producer regression)

The first build (Requirements 1-3, 5, 6) fixed discovery and the cell, and the bound-producer regression confirmed the producer binds and the records are shaped correctly (one measured winner whose insight carries a `next_experiments: [type: rollout]` on its target page; two inconclusive interim reads). But the winner still did **not** surface, because the producer carries **no run-scope vocabulary anywhere** -- its records are addressed by experiment id / program tag, and its `index.md` has no scope field. The inherited Read-side contract ("filtered to the run's `--scope` by default") filtered the index to the literal run-scope string, matching zero records. The two KBs use disjoint scope vocabularies: the run `--scope` is the strategy program; the producer is the same program addressed by experiment id. The experiments KB's own contract already designates its index as "the outbound surface the strategy KB reads" -- i.e. read whole, not scope-filtered.

**Decision (OQ5):** scope-map the producer index by vocabulary. If the producer's records carry the run scope's vocabulary (a producer shared across strategy scopes tags each record with the consuming scope), filter to the run `--scope`. If the producer carries no record matching the run scope's vocabulary (a dedicated experiments KB whose program is 1:1 with the consuming strategy scope), read the **whole index** as the run's experiment history -- making the contract's "cross-scope reads allowed" clause the default for a disjoint-vocabulary producer instead of a footnote. A producer serving multiple disjoint strategy scopes in one KB should tag records with the consuming scope to re-enable filtering (documented, avoids cross-scope leakage). Alternatives -- requiring the consumer KB to add run-scope tags (pushes a skill defect into client data) and a separate change doc (leaves the binding unable to surface the winner) -- were rejected in favor of fixing the scope semantics in the skill where the defect lives.

## Approach

### Change Profile

- **Script-affecting: no.** No Python scripts in a skill `## Scripts` table are added, modified, or removed. The repo-level bash validator [validate-hypothesis-generator.sh](../../scripts/validate-hypothesis-generator.sh) gains an updated presence check for the corrected Read-side Mapping cell, but it is a test harness, not a registered Python script; no `_tests/` layer applies.
- **Performance-affecting: yes.** The change activates a previously-dead input path: a bound completed-experiment KB now feeds the `Evidence From Completed Experiments` section, the Step 1g detect leg, the Step 4 replication modifier, and the Step 7 sequencing. `_evals/` does not exist in this repo, so verification is the validator script plus a bound-KB functional regression against a consumer repo, not the eval framework. This is the same regression the closed experiment-history change deferred as its release gate -- this change is what makes that regression runnable.
- **Test-eval-only: no.**

### Approach narrative

Two coordinated edits to [SKILL.md](../../skills/hypothesis-generator/SKILL.md) (plus the scope-mapping clause forced out by OQ5), keeping the input strictly optional and penalty-free (the tri-state-safe degradation already in `Preconditions` and `detect.md` is correct and unchanged). No phase-file logic changes: `detect.md` Step 1g, `score.md` Step 4/Step 7, and the `Output Format` evidence section already consume the input correctly once it is actually resolved and loaded -- the defect is purely in resolution, scope mapping, and the table's description of the input.

**Edit 1 -- Correct the Read-side Mapping cell (line 94).** Rewrite the row so the input is the producer KB's **gold index** (a `gold-experiment-index`-class artifact at the **producer KB root**) plus the silver insight records that index links -- not a `gold-experiment-roadmap` at the output path. Generic type label and KB-root-relative placeholder; no client KB type name and no client path, consistent with every other row. The cell aligns with the prose at line 101 after the edit.

**Edit 2 -- Add producer-KB discovery to the Mode Resolution Procedure.** Add a step, after output-KB resolution, that enumerates the declared KBs in the repo `CLAUDE.md` `## Knowledge Bases` section (body + subsections), resolves each one's type skill and root, and binds as the experiment-history producer the declared KB (other than the output KB) whose type skill's `artifacts/` defines `gold-experiment-index`. Resolve its KB root + gold index path from the declaration. Strictly optional and penalty-free: no producer (or an unresolvable/empty one) leaves the run unchanged and never flips it to legacy or hard-stops -- preserving the line 184 guarantee that the experiment-history input is NOT a mode-resolution requirement. Multiple-producer tie-break per the Discovery OQ2 decision. No hardcoded KB type name (other than the convention type `gold-experiment-index`, keyed exactly as output types are) and no hardcoded path.

**Edit 3 -- Scope mapping (OQ5).** Replace the bare "filtered to the run's `--scope` by default" clause with the vocabulary-aware rule so a disjoint-vocabulary producer is read whole rather than filtered to an empty set. Plus a short read-side note making the resolution rule discoverable from the prose, not only the procedure.

### Alternatives Considered

- **Capability/marker-based producer discovery** (instead of keying on the `gold-experiment-index` type name). Rejected. The skill already keys output-KB resolution on exact artifact-type names; introducing a separate marker convention for the producer would be a second, inconsistent discovery scheme with no second producer-type in evidence to justify the generalization. Keying on `gold-experiment-index` is symmetric with the existing output keys and equally client-agnostic.
- **Hardcode the producer KB type name and path.** Rejected for the same reason the closed experiment-history change rejected it for the input generally: the producer lives in a consumer repo, not this public skill; hardcoding a client type or path breaks the moment a second consumer binds a differently-named experiments KB. Resolution is declaration-driven.
- **Treat a missing/broken producer binding as a mode-resolution failure** (fall back to legacy or hard-stop, as a broken OUTPUT binding does). Rejected. The experiment-history input is optional by contract (line 184); a degraded producer must degrade to penalty-free absence, never alter the run's mode or stop it.
- **Require the consumer KB to tag records with the run scope** (instead of the whole-index read in OQ5). Rejected as the default: it pushes a skill resolution defect into client KB data and leaves the skill unable to surface evidence for a dedicated experiments KB out of the box. Tagging is documented only as the path to re-enable filtering for a producer that genuinely serves multiple disjoint scopes.

## Requirements

All edits are KB-mode-only behavior wired through the existing binding-resolved read path; legacy mode is untouched. No phase-file logic changes (`detect.md` Step 1g, `score.md` Step 4/Step 7, and the `Output Format` evidence section already consume the input correctly once it resolves). Numbered continuously across files.

### `skills/hypothesis-generator/SKILL.md`

1. **`Read-side Mapping` experiment-history row.** Rewrite the cell so the input is the producer KB's `gold-experiment-index` (producer KB) plus the silver insight records it links, and the path is the producer KB root `index.md` resolved by discovery. Final row:

   ```
   | (none -- KB-native) | `gold-experiment-index` (producer KB) + the silver insight records it links | producer KB root `index.md` (resolved by discovery, see `Mode Resolution Procedure` step 5) + linked silver insight paths | optional |
   ```

   Generic type label and KB-root-relative placeholder; no client KB type name and no client path. The cell now agrees with the read-side prose.

2. **`Mode Resolution Procedure` new step 5 (producer discovery).** After step 4 (KB mode confirmed), add a step that: enumerates every KB declared in the `Knowledge Bases` section (body + `###` subsections); resolves each one's type skill and KB root; binds as the experiment-history producer the declared KB *other than the output KB* whose type skill's `artifacts/` defines `gold-experiment-index`; resolves that KB's root and gold index (`{producer-kb-root}/index.md`). Keyed on the `gold-experiment-index` type name exactly as step 3 keys the output KB on `gold-experiment-roadmap` (no hardcoded client type or path). Tie-break: none defining it -> no producer; more than one -> prefer the producer whose index carries records for the run `--scope`, else first declared with a logged note. Degradation: a declared-but-unresolvable/empty producer degrades to penalty-free absence; it is NOT a mode-resolution requirement, so it never flips the run to legacy and never hard-stops (one-line run-output note only). The `--kb`-force-flag paragraph is amended to scope the loud legacy fallback to the *output* KB and to state step 5 as the optional exception.

3. **Read-side prose note (experiment-history bullet).** Append a sentence stating the producer KB is resolved by Mode Resolution step 5 as the declared KB whose type defines `gold-experiment-index`, distinct from the output KB (`gold-experiment-roadmap`), and that the gold index referenced is the producer's `gold-experiment-index`, never this skill's own output.

4. **Read-side scope-mapping clause (experiment-history bullet, OQ5).** Replace the bare "filtered to the run's `--scope` by default" sentence with the vocabulary-aware rule: filter to `--scope` only when the producer's records carry the run scope's vocabulary; otherwise (a dedicated experiments KB with a disjoint vocabulary, records addressed by experiment id) read the whole index as the run's experiment history, with the multi-scope-producer tagging caveat. This is what makes a bound producer actually surface evidence for a strategy scope it does not literally tag.

### `scripts/validate-hypothesis-generator.sh`

5. **`[13]` Read-side Mapping presence check.** Update the grep target and label from `gold-experiment-roadmap. (producer KB)` to `gold-experiment-index. (producer KB)` so the check guards the corrected cell. No count changes ([3] phases 4, [4] patterns 32, [12] CTR 14 untouched).

### `skills/hypothesis-generator/CHANGELOG.md`

6. **`[Unreleased]` Fixed entry.** One entry describing the corrected cell, the new producer discovery step, and the scope-mapping rule, noting the v1.7.0 origin and the optional/penalty-free contract.

## Verification Design

### Validation

1. **Static / validator clean.** `bash scripts/validate-hypothesis-generator.sh` reports all PASS, counts unchanged (phases 4, patterns 32, CTR 14); `[13]` now guards `gold-experiment-index. (producer KB)`. No em-dashes in edited files. `gold-experiment-roadmap` references remain only on the output side.
2. **Bound-producer regression (consumer repo).** A KB-mode run with a completed-experiment KB bound reports binding the producer at its `index.md`, reads the linked silver insight records, surfaces the measured winner as a replication opportunity (winner + rollout next-experiment whose target page is in the run scope), and correctly does NOT surface the inconclusive interim reads.
3. **Absent/broken-producer degradation.** A run in a repo with no experiments KB declared (or `--no-kb`) completes unchanged: no evidence section, Step 1g/Step 4/Step 7 inert, no Confidence penalty and no global cap. A declared-but-unresolvable producer degrades identically with a one-line note, never flipping mode or hard-stopping.

### Evals

`_evals/` does not exist in this repo; the eval framework does not apply. Performance-affecting verification is the validator (Validation 1) plus the bound-producer functional regression (Validation 2) against a consumer repo -- the same regression the closed experiment-history change deferred as its release gate. This change is what makes that regression runnable.

## Verification Results

### Validation Outcomes

- **Validation 1 (static/validator):** CONFIRMED. `bash scripts/validate-hypothesis-generator.sh` = 31 PASS / 0 FAIL / 0 WARN; counts unchanged. `[13]` updated and passing against the corrected `gold-experiment-index. (producer KB)` cell. Zero em-dashes in `SKILL.md`. `gold-experiment-roadmap` occurrences (8) are all output-side.
- **Validation 2 (bound-producer regression):** CONFIRMED at runtime. A clobber-safe full skill run (`--scope <scope> --max 5`, backup + restore, run against a consumer repo with a completed-experiment KB bound) passed all six checks: (a) the run discovered the second KB and bound its gold index as the experiment-history producer, reading the whole index (records keyed by experiment id, no run-scope vocabulary -> the dedicated-KB whole-index default from OQ5) plus the three linked silver insight records; (b) an `Evidence From Completed Experiments` section rendered, citing the measured winner in natural language; (c) the winner surfaced as the top-ranked Quick Win and the evidence section named the replication connection to a roadmap hypothesis; (d) the two inconclusive interim reads appeared only as explicitly directional running tests, never as wins or Quick Wins; (e) Confidence was not globally capped at 4 (it varied), proving the competitive/audience/performance silver inputs were read -- a cross-confirmation of the sibling `hypothesis-generator-kb-silver-input-basenames` fix; (f) body purity held (the only system surface was the gold frontmatter `governed_by`; zero internal field names, experiment codes, or pattern IDs in the body). The earlier read-only trace reached the same conclusion. The run superseded the consumer's roadmap in place and was then restored from backup: post-run `git status` equaled the pre-run state and the restored file's sha256 matched the backup, so the hand-finalized deliverable was preserved. `kb_type_validate.py` passed on the generated artifact (exit 0).
- **Validation 3 (absent/broken degradation):** CONFIRMED statically. Step 5 specifies penalty-free absence and the explicit non-mode-resolution-requirement guarantee; the read-side bullet and `Preconditions` (line 184) carry the no-penalty/no-cap semantics. Runtime portion confirmable in the same consumer-repo session.

## Changelog

| Version | Changes |
|---|---|
| 0.8.0 | Closed. All verification green (validator 31/0/0, runtime bound-producer regression passed all six checks, body purity + sanitization clean). Moved to `_dev/7-closed/`; `resource_version` stays TBD (resolved at release); skill `CHANGELOG.md` `[Unreleased]` entry already present. Both this fix and the sibling silver-basenames fix target released v1.7.0, so the next release cuts a patch/minor on top of it. ICE unchanged (4/4/3). |
| 0.7.0 | QA bound-producer regression CONFIRMED at runtime via a clobber-safe full skill run (`--max 5`, backup + restore) against a consumer repo with a completed-experiment KB bound. All six checks passed (producer discovered + whole-index read + 3 silver records; Evidence section cites the winner; winner is the top Quick Win with the replication connection named; inconclusive reads stay directional-only; Confidence not capped at 4 -> cross-confirms the sibling silver-basenames fix; body purity clean, `kb_type_validate.py` exit 0). Restore verified: post-run `git status` == pre-run state, restored sha256 == backup, hand-finalized deliverable preserved. Verification Results > Validation 2 upgraded from by-trace to runtime-confirmed. ICE unchanged (4/4/3). Ready to close. |
| 0.6.0 | Sanitized for the public repo: removed client/consumer identifiers (repo name, KB type names, scope name, experiment codes, target-page slugs, customer names) throughout, matching the generic norm of the existing tracked `_dev/` change docs. Technical substance and SKILL.md line citations unchanged. ICE unchanged (4/4/3). |
| 0.5.0 | QA bound-producer regression (read-only) surfaced a third defect: discovery + the corrected cell bind the producer and read the records, but literal run-scope filtering matched zero records (the producer carries no run-scope vocabulary), so the winner still did not surface. Reopened to Discovery, resolved as OQ5 (whole-index read for a disjoint-vocabulary producer; documented multi-scope-producer tagging caveat); rejected the consumer-KB-retag and separate-doc alternatives. Added Requirement 4 (SKILL.md read-side scope-mapping clause; existing validator/CHANGELOG reqs renumbered 5/6) and rebuilt: SKILL.md read-side bullet now maps the producer index by vocabulary. Validator 31/0/0, no em-dashes; CHANGELOG `[Unreleased]` entry extended with the scope-mapping rule. Re-ran the regression: the measured winner now satisfies the Step 1g replication condition by trace; inconclusive reads correctly excluded. Full clobber-safe write run left as an optional release-gate confirmation. Back at QA. ICE unchanged (4/4/3). |
| 0.4.0 | Approach approved. Phase 2 Requirements (5, numbered across SKILL.md / validator / CHANGELOG) + Verification Design authored. Build applied: SKILL.md Read-side cell corrected to `gold-experiment-index` (producer KB) at producer KB root `index.md`; new Mode Resolution Procedure step 5 (declared-KB enumeration, `gold-experiment-index` keying, tie-break, penalty-free degradation, output-vs-producer fallback scoping); read-side prose note; `--kb`-flag paragraph scoped to the output KB. Validator `[13]` retargeted to `gold-experiment-index. (producer KB)`. `bash scripts/validate-hypothesis-generator.sh` = 31/0/0, counts unchanged, no em-dashes. Skill `CHANGELOG.md` `[Unreleased]` Fixed entry added. Verification Results: Validation 1 + 3 confirmed static; Validation 2 (bound-producer runtime regression) deferred to a consumer-repo run. Moved to `_dev/6-qa/`, status QA. ICE unchanged (4/4/3). Awaiting QA approval. |
| 0.3.0 | document-management review pass (validators clean; all line-number citations verified accurate). Corrected stale release-state framing: the prior experiment-history change is NOT unreleased -- it shipped in skill **v1.7.0** (2026-06-18); Background and Current State now reflect that the broken binding shipped in a release with its bound-KB regression gate never run, and the CHANGELOG reference is `[1.7.0]` not `[Unreleased]`. Aligned the deferred verification skeleton to the current sibling convention (`## Requirements` + `## Verification Design` with Validation/Evals subsections + `## Verification Results`) in place of a bare `## Validation`. `## Discovery` retained (template-sanctioned optional H2). ICE unchanged (4/4/3). Awaiting Approach approval. |
| 0.2.0 | Moved to `_dev/2-discovery/`, status Discovery. Resolved the initial open questions into the Approach (OQ1: key producer discovery on the `gold-experiment-index` artifact-type name, symmetric with output-KB resolution; OQ2: enumerate declared KBs in `## Knowledge Bases` body + subsections, select the non-output KB whose type defines `gold-experiment-index`, documented tie-break; OQ3: scope handling; OQ4: roadmap-presentation re-confirmed clean). Added Change Profile, Alternatives Considered, and Discovery section. Requirements/Verification deferred to Phase 2 per lifecycle. ICE unchanged (4/4/3). |
| 0.1.0 | Backlog. Identified both defects (line-94 wrong-artifact cell + missing producer-KB discovery), grounded against a consumer repo with a completed-experiment KB bound (producer gold `gold-experiment-index` at the experiments-KB root; one winner record, two inconclusive). ICE 4/4/3. |
