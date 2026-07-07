# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### 2026-07-07 audit sweep

#### Fixed
- **render-program-site** (0.5.2): the documented legacy lane actually works now -- `render_site.py` loads frontmatter-less legacy roadmaps as body-only files and gate check 7 skips the sidecar version lock per-file with an explicit reported note (KB gold lane unchanged; mixed pairs still fail closed). Plus four SKILL.md text fixes (dead anchor, override wording, `$PY` full-path command, nonexistent label-to-region map). 8 new unit tests.
- **hypothesis-generator** (1.14.1): unsatisfiable per-page device trigger rewritten to the site-level Mobile vs Desktop Gap producers actually emit; trigger count stated once authoritatively (22); Read-side Mapping basenames corrected to positioning-framework's real type-derived defaults; Operating Modes no longer claims reads resolve via the output artifact's `depends_on`; Phase 1 hard guard extended to copy-craft.md and slugify.md; strategic gold pre-write registration check added; copy-craft module closes its four open pre-merge items (on-page-but-unregistered back-fill path with a new construct.md Step 4b verification step, pronoun-neutral Rule 12 example, Rule 4 scope-match, new Rule 23 for non-terminal buttons).
- **positioning-framework** (1.1.3): inline-schema defects fixed (`voice_source` added to messaging frontmatter; Brand Narrative Tensions status conflict resolved as REQUIRED-with-empty-marker; VOC Integration checklist block added; scorecard one-liner sources from audience-messaging.md; `re-rated by` marker standardized); reference checklists synced both directions.
- **landing-page-generator** (2.0.2): four phantom context reads in `phases/copy.md` corrected to fields producers actually write; `device_split.mobile_pct` references in section-taxonomy and the section catalog corrected to `device_mobile_pct`.
- **aa-audit** (1.1.1): honest schema stamp ("2.1", the highest version whose full required field set it emits, instead of "2.3" without the mandatory AI-referrer fields); Producer Variance documented in the shared schema; page-association limitation documented.
- **live-capture** (0.2.2): browser-mode contract canonicalized (see below); `phases/select.md` documents that the 0.15 device-gap leverage term contributes 0 with current producers.
- **experiment-mockup** (1.4.2): WAF/enterprise-bot-management guidance and the headless pre-flight probe back-ported from live-capture (the duplicated detection contract had drifted).
- **Docs**: repo CLAUDE.md re-synced (dual-mode skill count, ga4-audit direct-API description + `ga4_client.py` in the tree, workflow order gains `/cro-roadmap-red-team`, deliverables table gains program-site / red-team / control-screenshot rows, experiment-mockup three-mode phase annotations, cro-roadmap-red-team cross-layer exception bullet, render-default-deliverables consumption claims for performance-profile/brand-voice removed to match the skill). README re-synced (22 triggers, experiment-mockup three modes, output tables, recommended order gains live-capture / red-team / render-program-site, How It Works paragraphs for landing-page-generator / live-capture / cro-roadmap-red-team, Playwright prerequisites).

#### Added
- **modules/browser-mode.md**: canonical browser-mode detection contract (exact-tool-name DevTools test, configured-but-broken = STOP, Playwright secondary, static last resort, WAF guidance, headless pre-flight probe) on the kb-mode.md pattern; experiment-mockup and live-capture keep runtime-self-contained inline copies, with a new drift canary in `scripts/registry_check.py` (4 new unit tests).
- **CI**: `scripts/validate-hypothesis-generator.sh` (91 content checks) now runs in the workflow; content regressions in the largest skill fail the PR instead of shipping silently.

### New skill

#### Added
- **cro-roadmap-red-team** (0.1.0): an independent red team for a produced CRO roadmap, at both altitudes (the tactical `gold-experiment-roadmap` and the strategic `gold-strategic-roadmap`). Exists because a generator that grades its own work rubber-stamps it: roadmaps carry per-hypothesis self-critique blocks written by the same reasoning that built them, so they reliably end in a confident rebuttal and rarely concede. Independence cannot live inside `hypothesis-generator`, so it lives in a separate evaluator. Six-phase pipeline (scope + cold load; independent re-derivation via adversarial skeptic subagents, tier-gated so Quick Win / Strategic Bet / strategic bets get full cold-mechanism re-derivation plus perspective-diverse skeptics while Explorations get a lighter pass; a cross-cutting structural checklist CC1-CC11 + CC-MF + a non-skippable completeness step, altitude-aware with a gate-verdict-audit-vs-full-re-derivation split calibrated against hypothesis-generator's Phase 3.5 validation gates; self-critique grading rebut-vs-deflect; per-item dispositions plus a routed research backlog; render). Enforced phase order (checklist before grading) and a negative-control property (a sound item can reach `keep` with no change). Read-only and analysis-only: no web research, no edits to the target, no generated hypotheses. Dual-mode consumer I/O (legacy `.claude/deliverables/`; KB mode reads the scope's gold roadmaps and their `depends_on`), writing a standalone dated critique that is never a KB artifact. Boundary with `experiment-measurement-audit` grounded and complementary (that skill audits one finalized experiment pre-launch and checks guardrail definition; this skill red-teams a portfolio pre-spec and owns guardrail readability; survivors route to the audit). Registered as a package deal; `modules/kb-mode.md` now lists six dual-mode skills.

### Repo tooling

#### Fixed
- **client_ref_guard.py**: the corporate-suffix detector now catches the comma legal-name form ("Acme, Inc." / "Acme Traders, LLC"), the dominant US style, via an optional trailing comma on each capitalized token; new comma-form unit tests. The tightened detector also surfaced real company names used as fixture examples in `modules/slugify.md`, `modules/reddit-research.md`, and `skills/positioning-framework/phases/competitive.md`; all replaced with fictional placeholders per the public-repo rule.
- **CI**: the client-ref-guard workflow now also runs the `_tests/` unit suite, so guard regressions fail the PR instead of shipping silently.
- **Hygiene**: `.gitignore` gains key/credential-file patterns (`*.pem`, `*.key`, `*credentials*.json`, `*service-account*.json`); the stale "denylist" comment in `hooks/pre-commit` now describes the actual shape-based detector; the dead `skills/roadmap-presentation/` leftover directory was removed; local `test-runs/` engagement outputs were relocated outside the public working tree.
- **Docs**: repo CLAUDE.md re-synced with the filesystem (aa-audit registered in the structure tree, Available Skills, workflow order, and context-file table; all stale version pins updated; missing modules/phases/schemas/templates added to the tree; `examples/` removed; ga4-audit corrected to 11-15 reports / v2.3 profile; experiment-mockup corrected to three browser modes). README gains the missing `/render-default-deliverables` invocation example.

#### Added
- **scripts/registry_check.py** + CI step: mechanical enforcement of the "skill registration is a package deal" rule. Verifies SKILL.md frontmatter versions against the README skills table, CLAUDE.md Available Skills headers, marketplace.json coverage and skill count, and each skill's changelog top entry; flags dead skill directories and registry rows pointing at nonexistent skills. Includes a KB-mode drift canary (below). 10 unit tests. The CLAUDE.md structure tree no longer carries version pins (versions live in frontmatter and the checked registries only), removing one whole drift surface.
- **modules/kb-mode.md**: the canonical dual-mode (KB/legacy) contract. The five dual-mode skills (positioning-framework, hypothesis-generator, live-capture, experiment-mockup, render-program-site) keep runtime-self-contained inline copies but now point at the module as the single editing source; `registry_check.py` verifies each copy still carries the canonical section header, module pointer, and invariant sentences (scope HARD STOP, no `--kb` force flag, do-not-guess).
- **CONTRIBUTING.md**: SKILL.md scaffold (full template with required frontmatter, Preconditions shape, model table, quality checks) plus the registration package-deal checklist and the changelog convention, so new skills start contract-complete.

### Skill patch sweep (repo audit 2026-07-05)

#### Fixed
- **ga4-audit** (2.4.0 -> 2.4.1): Quality Checks section moved to the end of the file per the quality-checks-last convention (pure reorder, no content change). The single-agent SKILL.md is deliberately NOT split: the agent consumes the whole file at runtime, so extraction saves no tokens and adds a read failure mode, and the inline schema is authoritative by design.
- **positioning-framework** (within 1.1.2): quick-depth readout template, tips, quality rules, and context-file spec (~148 lines) extracted verbatim to new `phases/quick-readout.md`, read by the orchestrator only on quick runs; Orchestrator Quality Checks moved to the end of SKILL.md. 1056 -> ~915 lines, no wording changes.
- **hypothesis-generator** (within 1.13.3): Quality Rules moved after Module Dependencies (quality-checks-last convention; pure reorder).
- **render-default-deliverables** (within 1.0.2): Preconditions now state the KB-mode position (no KB read path; positioning-framework skips the auto-run in KB mode; `--no-kb` is the legacy workaround).
- **positioning-framework** (1.1.1 -> 1.1.2): Homepage Messaging declared as inline-schema section #15 (REQUIRED) + completeness-checklist item in `phases/company.md`; reference schema's orphan "Top Landing Pages" table removed; `schemas/competitive-landscape.md` gains the missing #13 Post-Research Questionnaire its own checklist required; real-name example sanitization.
- **hypothesis-generator** (1.13.2 -> 1.13.3): Module Dependencies tree marks `patterns-b2b-saas.md` as planned/not-on-disk; contrarian trigger count corrected 13 -> 14 (tree + `phases/construct.md`).
- **render-program-site** (0.5.0 -> 0.5.1): mode-resolution contradiction resolved (binding detection selects KB mode; `--scope` never does); section renamed `KB Mode (Dual-Mode Output)`; Model declaration added.
- **landing-page-generator** (2.0.0 -> 2.0.1): Quality Checks section, per-agent model table, changelog, `updated` field added.
- **experiment-mockup** (1.4.0 -> 1.4.1): Quality Checks section added.
- **live-capture** (0.2.0 -> 0.2.1): Preconditions section added (hard/soft deps, reads/writes, concurrency).
- **voice-inference** (1.0.0 -> 1.0.1): per-agent model table, changelog, `updated` field added.
- **positioning-update** (1.0.0 -> 1.0.1): dangling `agent-header.md` references now point to `skills/positioning-framework/agent-header.md`; changelog + `updated` field added.
- **render-default-deliverables** (1.0.1 -> 1.0.2): Model declaration added.

## [1.8.0] - 2026-07-02

### hypothesis-generator

#### Added
- **hypothesis-generator** (1.11.1 -> 1.12.0): Catch-All Leg in Phase 2c. After the six lever families, a licensed family-agnostic full-body read detects business-level levers the loaded context affirmatively names that fit no family, so the six families stop being the strategic lane's recall boundary (field evidence: the lane's best-grounded production bet fit no family). A catch-all candidate must derive from signals in two independent loaded artifacts, passes the identical 7-criterion quality gate, and takes one additional -1 raw-Confidence soft modifier beyond the de-novo -1. Family precedence means the leg only adds, never re-routes, and it is byte-inert when it finds nothing.
- **hypothesis-generator** (1.13.0): three strategic-lane additions. R5 active soft-input elicitation: an engagement-context reference artifact in the bound KB is a first-class soft-input source that MUST be read, and an interactive run with no soft input present asks one consolidated pre-flight question (at most once, never blocking, penalty-free when unanswered). R6 cross-deliverable scheduling note: when the same idea stands at both measurement altitudes, each deliverable carries one natural-language scheduling-constraint line so the page-level test and the strategic read window are reconciled. R7 archetype strategic-family extension point, shipped inert: an archetype pattern module defining strategic lever families loads them additively as families 7+ under the same gate and record shape.

#### Fixed
- **hypothesis-generator** (1.12.1): seven text-determinacy route-backs from the 1.12.0 release-gate regression (both consumer-repo legs PASSED all four gate assertions). Highlights: two-artifact independence is defined at the evidence-origin level, channel-scale programs (SEO, AI-search, paid-media strategy) join the catch-all anti-patterns, family precedence matches on a family's definition sentence with no consume-and-discard on near-misses, and criterion 7 names the built-but-disabled middle state (documented-live with an enablement gap, minting only the enablement shape). Content-only change to `phases/detect-strategic.md`.
- **hypothesis-generator** (1.13.0): ten strategic-lane text-determinacy clarifiers accumulated from the 1.11.0 release-gate regression and two production regenerations, pinning judgment calls the runs resolved defensibly but the text left open. Highlights: demotion-not-key-churn semantics for a scored bet regenerated as a Foundation entry, a primary-metric framing preference in Strategic Gate 2, a strategic Ease anchor clause in ice-scoring.md, blocked-pending-decision routing to "What's Not Here", and the two-stage read pattern blessed with a single `measurement_design` token.
- **hypothesis-generator** (1.13.1): three text pins from the 1.13.0 release-gate regression (all three gate assertions PASSED). The R6 case-2 pair predicate is now the explicit conjunction of same underlying idea AND shared read surface with a multiple-pair rule; a regeneration-only strategic run never writes the tactical deliverable (its side of a case-2 line lands on the tactical roadmap's next re-render); and the tactical template's "no strategic-lane lines" sentence is scoped so the one permitted case-2 scheduling cross-reference is not suppressed. Content-only.

### render-program-site

#### Added
- **render-program-site** (0.4.0 -> 0.5.0): Measurement Foundation rendering. `render_site.py` now parses the strategic gold roadmap's optional `## Measurement Foundation` section (hypothesis-generator SKILL.md > Strategic Roadmap Output Format) into a new item class: foundation entries, the unscored, keyless instrumentation prerequisites hypothesis-generator 1.11.0+ can emit (bold-labeled items; no ICE, no tier, no portfolio-map presence, no cross-altitude edges, no spokes). Previously the section was silently ignored, so the stand-up work the scored bets name as their dependency never appeared on the client-facing site. The hub gains a conditional `#measurement-foundation` section between the strategy cards and the experiment backlog (one card per entry: the bold label as the data-bound title, prose through `foundation-lead`/`foundation-<n>` curation slots, no score chips) plus a nav link; new `#measurement-foundation`/`.mf-grid`/`.mf` CSS. Foundation entries are excluded from every sidecar-related gate check (binding completeness, dangling targets, executor-status derivation, version-lock scope) and require no sidecar entries; a sidecar edge whose target names a foundation entry fails as a dangling target (check 2). Composes with the optional account-program altitude (both present, either alone, or neither). Output is byte-identical to 0.4.0 for any strategic roadmap without the section (empty `{{MEASUREMENT_FOUNDATION}}` reproduces the hub seam; no nav link). Also adds an edge-direction semantics note for `informs` to `edge-contract.md` (every edge is authored on the bet and points bet -> test; codifies what the type-label map already implied, no behavior change).

## [1.7.0] - 2026-07-02

### Repo tooling

#### Added
- **Client-reference guard**: a self-contained guard that keeps real company/client names out of this public repo. A categorical rule ("never write a real company name; use a placeholder or omit") is codified in `CLAUDE.md` and `CONTRIBUTING.md` as the primary control. A stdlib scanner (`scripts/client_ref_guard.py`) backstops it by flagging the shape of client data (a run of capitalized words followed by a corporate legal suffix), with leak-safe output (locations only, never the matched text). Installed as local `hooks/pre-commit` + `hooks/commit-msg` via `scripts/install-hooks.sh` (`core.hooksPath`) and enforced in CI (`.github/workflows/client-ref-guard.yml`, `scan-tree`). No list and no secret to maintain; money figures are deliberately not flagged (instructional content cites them constantly). Unit tests in `_tests/unit/test_client_ref_guard.py`.
- Also patched a pre-existing engagement-codename leak in `skills/hypothesis-generator/CHANGELOG.md` (genericized).

### experiment-mockup

#### Added
- **experiment-mockup** (1.3.2 -> 1.4.0): Before/After control screenshots in live mode. Phase 3 capture now restores the original section, shoots `control-screenshot.png`, re-injects the approved change, and shoots `mockup-screenshot.png` framed identically, so downstream renders can show a true control-vs-variant pair; inject.md hands off the injected element's selector and modified-original markup to make the restore deterministic. `control-screenshot.png` is added to the SKILL.md output files and agent-header; static mode writes no screenshots, unchanged.

### hypothesis-generator

#### Added
- **hypothesis-generator** (1.11.0): strategic rigor tranche. Phase 3.5 gains strategic-lane validation gates (an affirmatively disqualified comparison baseline forces re-finalization toward forward-only/randomized designs or caps Confidence at 2; strategic metric instrumentation with the live-elsewhere posture; unreconciled quantitative premise contradictions are an affirmative fail), consumed by scoring as a hard Confidence ceiling with the same tri-state semantics as the tactical lane. The strategic deliverable gains an unscored Measurement Foundation section separating instrumentation prerequisites from scored interventions, with an explicit guard that instrumentation stand-ups are never scored on an Impact anchor. Criterion 7 ("Gap is still open") becomes tri-state: documented-live discards, documented-absent mints a build, and context-silence about a client-side system the context could not observe mints only in confirm-first shape (existence check as step one, Confidence contingency), closing the third face of the already-solved-gap defect class.

#### Fixed
- **hypothesis-generator** (1.10.1): the Phase 2c strategic detector no longer mints already-closed gaps as experiments. A new quality-gate criterion 7 ("Gap is still open") discards a lever whose named intervention is documented as already implemented, live, or operating in the loaded context, routing it to "What's Not Here" as an existing capability; the objective-mismatch lever family gains a matching precondition to confirm down-funnel measurement is not already instrumented before minting. Content-only change to `phases/detect-strategic.md`.
- **hypothesis-generator** (1.10.2): tactical analog of 1.10.1. The instrumentation path no longer tells the client to stand up tracking that is already live in production: detect.md Step 1f gains a live-capability leg (a metric documented live in any loaded silver artifact, not only the performance profile, enters `instrumented_metrics` as `live-elsewhere`), validate.md Gate 2 passes live-elsewhere metrics with a per-surface confirmation note instead of an instrumentation-build prerequisite, and the Readiness output renders the case as verification rather than a stand-up. Genuinely dark metrics still route to Prerequisites with a Confidence cap.
- **hypothesis-generator** (1.11.1): five route-backs from the 1.11.0 bound-KB release-gate regression (all three named gate assertions passed). The ice-scoring Impact-anchor guard is lane-scoped to the strategic pass; a Foundation-entry-only strategic output now has a rendering path; Strategic Gate 1 evaluates the final (re-finalized) design; the strategic "What's Not Here" spec explicitly holds criterion-7 existing-capability notes; and criterion 7 gains a boundary clarifier (comprehensive-inventory silence on a surface the context does cover reads as documented absence, not context-silence). Content-only.

### render-program-site

#### Added
- **render-program-site** (0.3.0 -> 0.4.0): optional account-program altitude. A new `--account-program <path>` renders an off-store account layer alongside the two on-store altitudes. `load_account` parses the deliverable standalone (plays sliced from `## The Account-Level Plays`, cohorts from the `## The Account-Cohort Taxonomy` table; no `**Key:**`/`**Scores:**` required). Account plays are deliberately off-store: they carry no ICE, no on-page mechanism, and no cross-altitude edge, so they never enter the 7-check edge gate or the Impact-by-Ease map. A separate account-binding gate leg validates the plays (at least one play, unique `### N.` ordinals, required `Cohort`/`The play`/`How it is measured` labels). The hub gains a conditional `#account-program` section (cohort cards + one card per play) and nav link, and one `ap-NN.html` spoke is emitted per play. `extract_sections` id-prefix generalized to `{bet:sb, test:p, play:ap}`; new `templates/spoke-account.html` and `#account-program`/`.cohort`/`.x-tag.off` CSS. Output is byte-identical to 0.3.x for any program that supplies no account program (empty `{{ACCOUNT_PROGRAM}}` reproduces the hub seam; no nav link; no `ap-*.html`). Also corrects the stale `0.2.1` version pin in `README.md` and the in-repo `CLAUDE.md`.
- **render-program-site** (0.2.1 -> 0.3.0): Before/After mockup compare on tactical spokes. An optional `mockup.control_screenshot` field in the edge sidecar renders a labeled two-frame Before/After compare grid (new `.mockup-compare`/`.mockup-label` CSS, stacking below 760px); `copy_mockup_assets` copies the control asset alongside the after screenshot, and the gate rejects a non-string `control_screenshot`. An absent or unresolvable control degrades to output byte-identical to the prior after-only frame.

#### Changed
- **render-program-site** (0.1.0 -> 0.2.1): input contract reconciled with hypothesis-generator's actual output. The generator now reads the two prose gold roadmaps (`gold-experiment-roadmap`, `gold-strategic-roadmap`) in place and derives each item's id (from the `### N.` ordinal), key (from `**Key:**`), title, tier (from the enclosing tier H2), ICE (from `**Scores:**`), and page from the gold bodies. The cross-altitude edge binding plus the gate-classification fields (`delivery_surface`, `executor_status`, per-test `mechanism_class`, optional `status`/`run_tag`/`keystone`/`mockup`) move to a new render-owned sidecar `{scope}-program-edges.md` keyed by gold Key. The KB-mode strategic input is renamed `{scope}-strategic-experiment-layer.md` -> `{scope}-strategic-roadmap.md`, and the tactical-path collision is resolved by reading the gold artifact directly. Gate check 7 is redefined as a sidecar-vs-gold version lock, with new binding checks (every gold bet bound, every sidecar Key resolves, every live test carries a `mechanism_class`). `render_site.py` gains `--edges`; the map, edge typing, tier grouping, and chrome stay deterministic. Replaces the bespoke hand-authored `bets:`/`tests:`/`edges:` frontmatter that no deliverable ever carried. Also fixes the hub `keystone` prose-slot prefill, which hardcoded the client-specific claim `"%s converge on a shared asset."` (ungrammatical for a single keystone bet, and an unwarranted relationship assertion): it is now a neutral, count-correct seed naming only the keystone bet(s) (`"SB-2 is the keystone bet."` / `"SB-1 and SB-2 are the keystone bets."`). The slot stays a `<!--PROSE-->` curation slot, so the curated, shipped site is unaffected.

## [1.6.0] - 2026-06-24

### render-program-site

#### Added
- **render-program-site** (0.1.0): new skill replacing roadmap-presentation. A deterministic Python generator renders a unified two-altitude program site (a hub plus one spoke per strategic bet and one per page test) from two markdown inputs: a strategic experiment layer and a tactical roadmap. The cross-altitude edge contract (edge-type validity, dangling targets, mechanism compatibility, executor-status derivation, version lock) is enforced as a hard build gate that fails closed. The generator owns the gate, the Impact-by-Ease portfolio map, edge typing, and all chrome and data-bound structure; a scoped LLM pass curates the spoke prose and runs a humanizer pass. Per-test mockups from experiment-mockup feed the tactical spokes. Dual-mode I/O (legacy `.claude/deliverables/` or KB-native).

### roadmap-presentation

#### Removed
- **roadmap-presentation** (was 0.3.0): removed. Superseded by render-program-site, which renders the two-altitude program site (hub plus per-bet and per-test spokes) instead of a single-altitude per-experiment site.

### hypothesis-generator

#### Removed
- **hypothesis-generator** (1.10.0): retired the `--present` chaining flag, which invoked the now-removed roadmap-presentation skill. Auto-chaining is unsound for render-program-site (it needs two edge-contract-schema inputs a freshly-written roadmap does not yet carry); re-chaining is deferred to a follow-up that has hypothesis-generator emit those schemas.

### experiment-mockup

#### Changed
- **experiment-mockup** (1.3.2): reference rename roadmap-presentation to render-program-site in the KB-mode and mockup-output prose (the consumer skill was replaced). No behavioral change.

## [1.5.0] - 2026-06-24

### hypothesis-generator

#### Added
- **hypothesis-generator** (1.9.0): premise and measurement rigor made binding. A new validation phase (Phase 3.5) applies six tri-state gates (premise triangulation, instrumentation, baseline, control-stability, power, segmentation) as a hard Confidence ceiling, plus segmentation pre-registration, bundle interpretability, consequential self-critique, a data-hygiene discount for bot/synthetic traffic, and a forced-spread anti-clustering remedy. Absence is neutral (never penalizes); all checks are KB-internal with no new research.
- **hypothesis-generator** (1.9.0): strategic experiments as a separate, first-class deliverable. A business-level lever detection phase produces a standalone strategic roadmap (program/offer/audience-motion/asset levers with non-A/B measurement designs such as holdout, pre/post, geo split, and operational tracking, each with its own scoring and exclusions) alongside the tactical page-element roadmap, governed by a client-facing register. Context-gated: when no lever qualifies, output is byte-identical to the tactical-only roadmap.

## [1.4.1] - 2026-06-22

### experiment-mockup

#### Fixed
- **experiment-mockup** (1.3.1): repair malformed YAML frontmatter introduced in v1.3.0 -- the `description` folded scalar had no indented body and a truncated `modes:` fragment was left as a stray key, so `description` parsed empty. An empty/invalid skill description aborted skill enumeration for the entire `funnelenvy-skills` plugin, making all 11 skills (not just experiment-mockup) fail to load. Restored the full description body; no behavioral change.

## [1.4.0] - 2026-06-21

### hypothesis-generator

#### Added
- **hypothesis-generator** (1.8.0): all-outcome experiment-history iteration generation in KB mode (mint iteration hypotheses from completed-experiment next-steps across winners, losses, and flats; outcome-aware scoring posture; Experiment Program Continuity output; same-mechanism merge test). Plus two KB-mode input fixes (producer-KB binding resolution, silver-input basenames).

## [1.3.0] - 2026-06-18

### roadmap-presentation

#### Added
- **roadmap-presentation** (new skill, 0.3.0): renders an experiment roadmap into a self-contained multi-page HTML site (hub overview plus one spoke per experiment) with control-vs-proposed mockup comparisons. Deterministic `scaffold_site.py` chrome in a reconciliation-ledger design language (IBM Plex Mono data layer, disposition palette, hero run-order spine), version-agnostic section-mapping, humanizer pass. Dual-mode (legacy `.claude/deliverables/` or KB). Key-based mockup resolution; `--present` chaining from hypothesis-generator

### experiment-mockup

#### Added
- **experiment-mockup**: dual-mode I/O (KB / legacy) -- reads the scope's gold roadmap and writes mockups under the bound knowledge base; new `--scope` and `--no-kb` flags (v1.3.0)

#### Changed
- **experiment-mockup**: output directory now resolves by the roadmap's persisted `**Key:**` field (with `slugify(title)` fallback plus warning) instead of `slugify(title)`, decoupling mockups from mutable heading titles (v1.3.0)

### hypothesis-generator

#### Added
- **hypothesis-generator**: stable per-experiment `**Key:**` emission (immutable, dual-mode regen carry-forward, churn reporting); optional experiment-history consumption in KB mode (gold index plus silver insights, winner-replication sequencing, replication Confidence/Ease modifier); thin `--present` chaining flag to roadmap-presentation (v1.7.0)

## [1.2.0] - 2026-06-11

### aa-audit

#### Added
- **aa-audit**: Element-interaction and measurement-integrity capture by default: sub-property `scope` (segment or entry/page prefix), `interaction_dimensions` array, scoped element enumeration, event-liveness audit, and friction tagging; element-instrumentation and a new Measurement Integrity section promoted to REQUIRED (v1.1.0, performance-profile schema 2.3)

#### Fixed
- **aa-audit**: Comparison-period fetch crash on string/NaN cells (v1.1.0)

### ga4-audit

#### Added
- **ga4-audit**: Element-interaction and measurement-integrity capture by default: scope `dimensionFilter` flags, Step 3 event-liveness, Step 5b rework (no silent skip, autotrack enumeration, scoped page set), friction pass; element-instrumentation and Measurement Integrity promoted to REQUIRED (v2.4.0, performance-profile schema 2.3)

### hypothesis-generator

#### Added
- **hypothesis-generator**: Archetype architecture layer (resolver + loader) and procurement archetype pattern module; structural-observation consumption (Phase C); KB dual-mode I/O; engagement-context reasoning input; CTR-14 contrarian trigger; output quality blocks (v1.6.0)

#### Changed
- **hypothesis-generator**: Self-critique rendered on every hypothesis regardless of tier (v1.6.0)

#### Fixed
- **hypothesis-generator**: Module resolution hardening, validator realignment, cross-surface bundling reconciliation (v1.6.0)

### live-capture

#### Added
- **live-capture**: Initial skill (Phase B): Section 8 page selection (`page_select.py`), browser-mode detection, `content_hash.py` recapture-diff, dual-mode I/O, headless-WAF handling, coverage-weighted confidence; authoritative schema inlined in `phases/write.md` (v0.2.0)

#### Fixed
- **live-capture**: Content-blocked tri-state handling, KB-mode artifact-type resolution, schema completeness, explicit `not_checked` defaults (v0.2.0)

### positioning-framework

#### Fixed
- **positioning-framework**: Module resolution hardening for `modules/` references (v1.1.1)

### render-default-deliverables

#### Fixed
- **render-default-deliverables**: Module resolution hardening for the `modules/slugify.md` reference (v1.0.1)

## [1.1.0] - 2026-06-03

### hypothesis-generator

#### Added
- hypothesis-generator skill with 13 CRO experiment patterns and ICE scoring (v1.0.0)
- Phase 2b context-derived opportunity detection with quality gate
- Prerequisites and Data Gaps section in final deliverable
- Performance-profile v2 support: 19 performance-driven triggers, ICE modifiers, baseline metrics
- Element-level interaction triggers (EE-01 CTA Click-Through, EE-02 Element Engagement Drop-off)
- Test feasibility estimation with infeasible routing to "What's Not Here"
- 3 NX experiment patterns; enriched PZ-01 with Rule of 100

#### Changed
- Expanded from 13 to 28 patterns across 10 categories (v1.1.0, v1.2.0)
- ICE scoring scale changed from 1-10 to 1-5
- Confidence capped at 4 when no performance data available

### ga4-audit

#### Added
- ga4-audit skill with GA4 analytics via analytics-mcp (v1.0.0)
- Period-over-period comparison, data-driven page grouping, opportunity sizing (v2.0.0)
- Three-tier event classification (KEY EVENT / heuristic / L0-mapped)
- New/returning user analysis, source x page cross-tab, failure mode detection
- Element-level interaction discovery via custom dimensions and enhanced measurement (v2.1.0)
- Optional L0 enrichment with product-line page grouping
- AI-referrer (LLM) traffic segmentation with source normalization and trajectory analysis (v2.3.0)
- Step 6b: PARTIAL_REGEXP source filtering across 19 LLM referrers (ChatGPT, Perplexity, Claude, Gemini, Copilot, DeepSeek, Mistral, Meta AI, etc.), 3-query breakdown (sources, monthly trajectory, top landing pages), canonical source map collapsing provider variants (chatgpt.com/openai, perplexity/perplexity.ai, copilot.microsoft.com/copilot.cloud.microsoft, gemini.google.com/bard.google.com, chat.mistral.ai/mistral.ai)
- Frontmatter fields: `ai_sessions_count`, `ai_sessions_pct`, `ai_conversions_count`, `ai_conversion_rate`, `ai_traffic_trend`, `ai_not_set_landing_pct`, `top_ai_sources[]`
- Data quality flag for `(not set)` landing page share > 15% on AI-referrer traffic
- AI-Referrer Traffic body subsection with collapsed and raw source views; collapses to one-liner below 20 sessions

#### Changed
- Inlined schema into SKILL.md, saving ~11-13K tokens per run
- Performance-profile schema bumped to 2.2 (AI-traffic fields, additive-only change)

### positioning-framework

#### Added
- L0 provenance tracking with origin tags for source attribution
- Cross-agent content sharing via _research-extractions.md
- Competitive-assessment module (claim assessment, similarity scoring, overlap calculation)
- Buyer alternatives discovery process in competitive phase
- `--property` flag for GA4-guided page selection
- GA4 property ID persistence in company-identity.md for downstream skill auto-detection
- Dual-mode output (KB mode): typed bronze/silver artifacts into a client knowledge base when a KB binding is detected; --scope/--no-kb flags; per-agent post-write validation gate; legacy output unchanged

#### Changed
- Integrated markdown.new as primary web extractor with three-tier fallback
- Improved competitive phase: stricter market sizing, source requirements, PARTIAL overlap scoring
- Improved messaging phase (Agent 3): proof assessment, persona tiers, objection categories
- Fixed confidence reconciliation to use REQUIRED sections only

### render-default-deliverables

#### Removed
- Tier 4 Opportunity Sizing Report

## [1.0.0] - 2026-02-20

### Added
- positioning-framework skill with 3 depth levels (quick/standard/deep)
- render-default-deliverables skill for human-readable output from context files
- Three-layer architecture: L0 company identity, L1 analysis, L2 deliverables
- 4 shared modules: reddit-research, web-extract, business-brief, slugify
- 5 context file schemas with YAML frontmatter for token-efficient consumption
- Prior work detection for incremental depth runs (quick -> standard -> deep)
- L0 bootstrap protocol for automatic company identity generation
- Competitive analysis with battle cards, claim overlap detection, and white space mapping
- Audience personas, messaging hierarchy, language bank, and voice rules
- Positioning scorecard with categorical ratings (Strong / Needs Work / Missing)
