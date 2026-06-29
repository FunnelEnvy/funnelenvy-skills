# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### render-program-site

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
- **experiment-mockup** (1.3.1): repair malformed YAML frontmatter introduced in v1.3.0 — the `description` folded scalar had no indented body and a truncated `modes:` fragment was left as a stray key, so `description` parsed empty. An empty/invalid skill description aborted skill enumeration for the entire `funnelenvy-skills` plugin, making all 11 skills (not just experiment-mockup) fail to load. Restored the full description body; no behavioral change.

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
- **experiment-mockup**: dual-mode I/O (KB / legacy) — reads the scope's gold roadmap and writes mockups under the bound knowledge base; new `--scope` and `--no-kb` flags (v1.3.0)

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
