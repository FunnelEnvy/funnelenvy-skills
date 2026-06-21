# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

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
