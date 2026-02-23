# FunnelEnvy Skills

AI-powered positioning and competitive research skills for [Claude Code](https://claude.ai/claude-code). Built by [FunnelEnvy](https://funnelenvy.com).

Works standalone. Works better with FunnelEnvy's private data layer.

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| positioning-framework | 1.0.0 | Autonomous positioning and messaging framework from web research |
| render-default-deliverables | 1.0.0 | Generates client-ready deliverables from positioning context |
| hypothesis-generator | 1.1.0 | CRO experiment engine with 23 patterns, ICE scoring, and causal reasoning |

## Quick Start

Clone the repo and work from inside it. Claude Code discovers skills automatically.

```bash
git clone https://github.com/FunnelEnvy/funnelenvy-skills.git
cd funnelenvy-skills
```

Run the positioning framework:

```
/positioning-framework https://example.com
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
```

## Output Files

### Context (`.claude/context/`)

| File | Description |
|------|-------------|
| company-identity.md | Company facts, services, differentiators, proof points, constraints |
| competitive-landscape.md | Market overview, competitor profiles, claim overlap, white space |
| audience-messaging.md | Personas, messaging hierarchy, language bank, voice rules |
| positioning-scorecard.md | Positioning health check, messaging gaps, confidence scores |
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

**positioning-framework** researches a company and its competitors, then produces structured context files with evidence-backed analysis. It runs autonomous web research across multiple source tiers (website, reviews, Reddit, SEC filings, job postings) depending on depth level.

**render-default-deliverables** converts those context files into polished, shareable documents. No research, no analysis. Pure synthesis and formatting.

**hypothesis-generator** reads the same context files and produces a prioritized experiment roadmap. Run it with `/hypothesis-generator` after positioning context exists.

At standard and deep depth, render-default-deliverables runs automatically after positioning-framework completes. Run it manually with `/render-default-deliverables` any time after editing context files. hypothesis-generator is always manually invoked.

## Vision

The research layer (L0 company identity + L1 analysis) is the foundation. Once those context files exist, any number of skills can consume them to produce different outputs.

Today, render-default-deliverables produces executive summary, messaging guide, competitive matrix, and battle cards. hypothesis-generator adds experiment roadmaps with ICE-scored hypotheses. That's the starting point, not the ceiling.

The goal is a library of composable skills that read from the same structured context: website audits that score pages against the messaging framework, GA4 analysis that ties traffic data to positioning gaps, content strategies built on proven value themes, ad copy generators that pull from the language bank. Each skill does one thing well, and none of them need to re-run the research.

Build the context once. Run whatever analysis or deliverable you need on top of it.

## License

MIT
