# Changelog

All notable changes to this project will be documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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

#### Changed
- Inlined schema into SKILL.md, saving ~11-13K tokens per run

### positioning-framework

#### Added
- L0 provenance tracking with origin tags for source attribution
- Cross-agent content sharing via _research-extractions.md
- Competitive-assessment module (claim assessment, similarity scoring, overlap calculation)
- Buyer alternatives discovery process in competitive phase
- `--property` flag for GA4-guided page selection
- GA4 property ID persistence in company-identity.md for downstream skill auto-detection

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
