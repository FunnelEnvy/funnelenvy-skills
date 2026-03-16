# FunnelEnvy Skills

AI-powered positioning and competitive research skills for [Claude Code](https://claude.ai/claude-code). Built by [FunnelEnvy](https://funnelenvy.com).

Works standalone. Works better with FunnelEnvy's private data layer.

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| [positioning-framework](skills/positioning-framework/SKILL.md) | 1.0.0 | Autonomous positioning and messaging framework from web research |
| [ga4-audit](skills/ga4-audit/SKILL.md) | 2.1.0 | GA4 analytics audit with page grouping, opportunity sizing, element interactions, and trend analysis |
| [hypothesis-generator](skills/hypothesis-generator/SKILL.md) | 1.2.0 | CRO experiment engine with 28 patterns, ICE scoring, test feasibility, and causal reasoning |
| [landing-page-generator](skills/landing-page-generator/SKILL.md) | 1.0.0 | B2B paid landing page generator with brief, copy, design, and QA phases |
| [render-default-deliverables](skills/render-default-deliverables/SKILL.md) | 1.0.0 | Generates client-ready deliverables from positioning context |

## Quick Start

Clone the repo and work from inside it. Claude Code discovers skills automatically.

```bash
git clone https://github.com/FunnelEnvy/funnelenvy-skills.git
cd funnelenvy-skills
```

Run a skill:

```
/positioning-framework https://example.com
/ga4-audit properties/123456789
/hypothesis-generator
/landing-page-generator example-co campaign-slug --stage all
```

Research output goes to `.claude/context/`. Deliverables go to `.claude/deliverables/`.

## Depth Levels

| Depth | What It Does | Time | Tokens |
|-------|-------------|------|--------|
| `--depth quick` | Fast triage. Company identity + inline health check. | ~5-8 min | ~70-90K |
| `--depth standard` (default) | Full framework. Competitive analysis, messaging, scorecard, deliverables. | ~30-35 min | ~450-500K |
| `--depth deep` | Extended competitive. 6+ competitors, deeper sources, deliverables. | ~40-50 min | ~550-650K |

Each depth builds on prior work. Running quick then standard then deep is incremental, not redundant.

Examples:

```
/positioning-framework https://example.com --depth quick
/positioning-framework https://example.com --depth deep
/positioning-framework https://example.com --competitive-focus "Acme Corp"
/positioning-framework https://example.com --property properties/123456789
```

## Output Files

### Context (`.claude/context/`)

| File | Description |
|------|-------------|
| company-identity.md | Company facts, services, differentiators, proof points, constraints |
| competitive-landscape.md | Market overview, competitor profiles, claim overlap, white space |
| audience-messaging.md | Personas, messaging hierarchy, language bank, voice rules |
| positioning-scorecard.md | Positioning health check, messaging gaps, confidence scores |
| performance-profile.md | Page performance, conversion funnels, channel/device breakdown, data quality |
| _fetch-registry.md | Internal coordination file logging all URLs fetched by each agent |

### Deliverables (`.claude/deliverables/`)

| File | Description |
|------|-------------|
| executive-summary.md | Positioning assessment for executives |
| messaging-guide.md | Persona-by-persona messaging with voice rules |
| experiment-roadmap.md | Prioritized experiment plan (produced by hypothesis-generator) |
| competitive-comparison-matrix.md | Structured comparison grid across competitors |
| battle-cards/[competitor].md | One-page competitor reference cards |

## How It Works

Skills build on each other. Each one reads from and writes to `.claude/context/`, creating a shared knowledge layer that downstream skills consume.

**positioning-framework** researches a company and its competitors, then produces structured context files with evidence-backed analysis. It runs autonomous web research across multiple source tiers (website, reviews, Reddit, SEC filings, job postings) depending on depth level. At standard and deep depth, render-default-deliverables runs automatically after it completes.

**ga4-audit** pulls 10-15 reports from a GA4 property via the analytics-mcp server. Classifies conversion events, groups pages by type, sizes opportunities, discovers element-level interactions (CTA clicks, link text, custom parameters), and detects failure modes. Produces `performance-profile.md`. Standalone -- works with or without positioning context, though it can optionally enrich its output with product-line mappings from `company-identity.md` if one exists.

**hypothesis-generator** reads everything the other skills produced and generates a prioritized experiment roadmap. Without GA4 data, it works from positioning gaps alone (confidence capped at 4/5). With GA4 data, it unlocks 19 performance-driven triggers, calibrates ICE scores using real traffic numbers, adds baseline metrics and test feasibility estimates to each hypothesis, and routes infeasible experiments (insufficient traffic) to "What's Not Here" with alternative approaches.

**render-default-deliverables** converts context files into polished, shareable documents. No research, no analysis. Pure synthesis and formatting. Run it manually with `/render-default-deliverables` any time after editing context files.

### Recommended Order

```
# 1. Build positioning context (who you are, your market, your competitors)
# Add --property to use GA4 data for page selection (optional)
/positioning-framework https://example.com --property properties/123456789

# 2. Pull analytics data (what's actually happening on your site)
/ga4-audit properties/123456789

# 3. Generate data-informed experiment ideas
/hypothesis-generator

# 4. Re-render deliverables any time context changes
/render-default-deliverables
```

Each step is optional and independent, but they compound. Positioning context makes GA4 audit smarter (product-line page grouping). GA4 data makes hypothesis-generator smarter (traffic-calibrated scores, performance-driven triggers). Run what you have access to.

## Vision

The research layer (L0 company identity + L1 analysis) is the foundation. Once those context files exist, any number of skills can consume them to produce different outputs.

Today the pipeline covers positioning research, GA4 analytics, experiment planning, and polished deliverables. That's the starting point, not the ceiling.

The goal is a library of composable skills that read from the same structured context: website audits that score pages against the messaging framework, content strategies built on proven value themes, ad copy generators that pull from the language bank. Each skill does one thing well, and none of them need to re-run the research.

Build the context once. Run whatever analysis or deliverable you need on top of it.

## License

MIT
