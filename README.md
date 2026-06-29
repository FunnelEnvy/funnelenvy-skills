# FunnelEnvy Skills

AI-powered positioning and competitive research skills for [Claude Code](https://claude.ai/claude-code). Built by [FunnelEnvy](https://funnelenvy.com).

Works standalone. Works better with FunnelEnvy's private data layer.

## Skills

| Skill | Version | Description |
|-------|---------|-------------|
| [positioning-framework](skills/positioning-framework/SKILL.md) | 1.1.1 | Autonomous positioning and messaging framework from web research. Dual-mode output: legacy `.claude/context/` files, or KB-native artifacts when a CRO knowledge base binding is detected |
| [ga4-audit](skills/ga4-audit/SKILL.md) | 2.4.0 | GA4 analytics audit with page grouping, opportunity sizing, element interactions, trend analysis, and AI-referrer (LLM) traffic segmentation |
| [aa-audit](skills/aa-audit/SKILL.md) | 1.1.0 | Adobe Analytics audit with the same output schema as ga4-audit |
| [hypothesis-generator](skills/hypothesis-generator/SKILL.md) | 1.10.2 | CRO experiment engine with 32 patterns, ICE scoring, test feasibility, contrarian filtering, and LIFT sequencing. When business-level levers qualify, also produces a separate strategic roadmap deliverable (program/offer/motion/asset-level experiments with non-A/B measurement designs like holdout, pre/post, and operational tracking, each with its own scoring and exclusions) alongside the tactical page-element roadmap. Dual-mode I/O: legacy `.claude/context/` files, or KB-native (reads the scope's silver artifacts, writes a typed gold experiment roadmap) when a CRO knowledge base binding is detected. In KB mode with a completed-experiment knowledge base bound, generates net-new iteration experiments from prior test outcomes |
| [landing-page-generator](skills/landing-page-generator/SKILL.md) | 2.0.0 | B2B paid landing page generator with brief, copy, design, and QA phases |
| [positioning-update](skills/positioning-update/SKILL.md) | 1.0.0 | Apply client feedback and corrections to positioning context files |
| [voice-inference](skills/voice-inference/SKILL.md) | 1.0.0 | Brand voice analysis from website content with scored tone spectrum, vocabulary fingerprint, and actionable voice rules |
| [live-capture](skills/live-capture/SKILL.md) | 0.2.0 | Live-page structural and copy capture. Navigates selected pages, passively reads the rendered DOM across viewports, and writes two factual artifacts (structure + verbatim copy). Dual-mode: legacy `.claude/context/` files, or KB-native bronze plus a silver structural artifact (in active development) |
| [experiment-mockup](skills/experiment-mockup/SKILL.md) | 1.3.2 | Visual mockup generator for experiment hypotheses. Dual-mode (legacy / KB); resolves mockups by a stable per-experiment Key |
| [render-program-site](skills/render-program-site/SKILL.md) | 0.1.0 | Renders a unified two-altitude program site (hub plus one spoke per strategic bet and one per page test) from a strategic experiment layer and a tactical roadmap, with the cross-altitude edge contract enforced as a hard build gate. Deterministic generator for the gate, the Impact-by-Ease map, and all structure; a scoped LLM pass curates spoke prose. Dual-mode: legacy `.claude/deliverables/` or KB-native |
| [render-default-deliverables](skills/render-default-deliverables/SKILL.md) | 1.0.1 | Generates client-ready deliverables from positioning context |

## Quick Start

Clone the repo and work from inside it. Claude Code discovers skills automatically.

```bash
git clone https://github.com/FunnelEnvy/funnelenvy-skills.git
cd funnelenvy-skills
```

Run a skill:

```
/positioning-framework https://example.com
/positioning-update
/ga4-audit properties/123456789
/aa-audit --config path/to/config.json
/hypothesis-generator
/landing-page-generator example-co campaign-slug --stage all
/landing-page-generator example-co campaign-slug --stage brief
/voice-inference https://example.com
/voice-inference https://example.com --mode compare
/live-capture https://example.com
/live-capture https://example.com --scope b2c
/experiment-mockup 1
/render-program-site
/render-program-site --scope b2c
```

The `--stage` flag on landing-page-generator controls which phases run: `brief`, `copy`, `design`, `qa`, or `all` (default).

Research output goes to `.claude/context/`. Deliverables go to `.claude/deliverables/`.

## Positioning Framework Depth Levels

The `positioning-framework` skill supports three depth levels. Other skills do not use the `--depth` flag.

| Depth | What It Does | Time | Tokens |
|-------|-------------|------|--------|
| `--depth quick` | Fast triage. Company identity + inline health check. | ~5-8 min | ~70-90K |
| `--depth standard` (default) | Full framework. Competitive analysis, messaging, scorecard, deliverables. | ~30-35 min | ~450-500K |
| `--depth deep` | Extended competitive. 6+ competitors, deeper sources, deliverables. | ~40-50 min | ~550-650K |

Each depth builds on prior work. Running quick then standard then deep is incremental, not redundant.

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
| performance-profile.md | Page performance, conversion funnels, channel/device breakdown, AI-referrer traffic, data quality |
| brand-voice.md | Scored tone spectrum, vocabulary fingerprint, categorized examples, voice rules |
| _fetch-registry.md | Internal coordination file logging all URLs fetched by each agent |

### Deliverables (`.claude/deliverables/`)

| File | Description |
|------|-------------|
| executive-summary.md | Positioning assessment for executives |
| messaging-guide.md | Persona-by-persona messaging with voice rules |
| experiment-roadmap.md | Prioritized page-element experiment plan (produced by hypothesis-generator) |
| strategic-roadmap.md | Separate program/offer/motion/asset-level experiment plan with non-A/B measurement designs (produced by hypothesis-generator when business-level levers qualify) |
| competitive-comparison-matrix.md | Structured comparison grid across competitors |
| battle-cards/[competitor].md | One-page competitor reference cards |
| campaigns/[slug]/brief.md | Campaign brief for a landing page |
| campaigns/[slug]/copy.md | Section-by-section landing page copy |
| campaigns/[slug]/page.html | Single-file HTML landing page |
| campaigns/[slug]/qa-report.md | QA validation report |
| experiments/[slug]/mockup.html | Standalone HTML mockup of proposed experiment change |
| experiments/[slug]/placement.md | CRO placement rationale and implementation notes |

## How It Works

Skills build on each other. Each one reads from and writes to `.claude/context/`, creating a shared knowledge layer that downstream skills consume.

**positioning-framework** researches a company and its competitors, then produces structured context files with evidence-backed analysis. It runs autonomous web research across multiple source tiers (website, reviews, Reddit, SEC filings, job postings) depending on depth level. At standard and deep depth, render-default-deliverables runs automatically after it completes.

**ga4-audit** pulls 11-15 reports from a GA4 property via direct API (preferred) or analytics-mcp fallback. Classifies conversion events, groups pages by type, sizes opportunities, discovers element-level interactions (CTA clicks, link text, custom parameters), segments AI-referrer traffic (ChatGPT, Perplexity, Claude, Gemini, Copilot, etc.) with source normalization and trajectory analysis, and detects failure modes. Produces `performance-profile.md`. Standalone -- works with or without positioning context, though it can optionally enrich its output with product-line mappings from `company-identity.md` if one exists. Requires GA4 credentials (see `skills/ga4-audit/.env.example`) or [analytics-mcp](https://github.com/nicholasgriffintn/analytics-mcp) as fallback.

**aa-audit** is the Adobe Analytics equivalent of ga4-audit. Runs a Python script against the AA 2.0 Reporting API and produces the same `performance-profile.md` schema, so all downstream skills (hypothesis-generator, render-default-deliverables) work identically regardless of analytics platform. Requires Python 3 with `requests`, Adobe Analytics API credentials (env vars), and a client config JSON file.

**hypothesis-generator** reads everything the other skills produced and generates a prioritized experiment roadmap. Without GA4 data, it works from positioning gaps alone (confidence capped at 4/5). With GA4 data, it unlocks 19 performance-driven triggers, calibrates ICE scores using real traffic numbers, adds baseline metrics and test feasibility estimates to each hypothesis, and routes infeasible experiments (insufficient traffic) to "What's Not Here" with alternative approaches. In KB mode it reads the scope's silver CRO artifacts from a bound knowledge base instead of `.claude/context/` and writes the roadmap as a typed gold artifact, with schema-tolerant performance trigger evaluation for profiles that lack `schema_version`.

**voice-inference** analyzes how a company communicates by extracting 12-15 pages across content types (homepage, product, blog, case studies, about) and building an evidence-backed voice profile. Scores tone dimensions, identifies vocabulary patterns and sentence architecture, catalogs 33+ categorized examples, and derives actionable voice rules. Two modes: observe (infer from content alone) and compare (compare inferred voice against customer-provided brand docs). Does not require positioning-framework to have been run first. Produces `brand-voice.md`.

**experiment-mockup** (in active development) takes a hypothesis from the experiment roadmap and builds a visual mockup showing the proposed change in the context of the real target page. In live mode (requires Chrome DevTools MCP), it injects the change into the user's browser, matches the site's design system using computed styles, and iterates on placement and styling in real time. In static mode (automatic fallback), it extracts page HTML and builds a standalone mockup file. Both modes produce a CRO placement rationale explaining why the element is positioned where it is, what visual hierarchy strategy it uses, and how the dev team should implement it.

**render-program-site** (in active development) renders a unified two-altitude program site from two markdown inputs: a strategic experiment layer (program-level bets) and a tactical experiment roadmap (page-level tests). It produces a hub page plus one spoke per bet and one per test, with the cross-altitude edge contract (mechanism compatibility, dangling targets, version lock) enforced as a hard build gate that fails closed. A deterministic Python generator owns the gate, the Impact-by-Ease portfolio map, and all structure and chrome, so the strategic layer cannot drift; a scoped LLM pass then curates the spoke prose and runs a humanizer pass. Per-test mockups from experiment-mockup feed the tactical spokes' proposed-change comparison. Dual-mode: legacy `.claude/deliverables/` or KB-native.

**positioning-update** applies client feedback, stakeholder corrections, and new intelligence to existing context files. Paste an email, Slack thread, or meeting notes and it classifies each piece of information, shows you a structured change plan, and executes surgical edits after approval. No web research. Triggers deliverable re-render automatically.

**render-default-deliverables** converts context files into polished, shareable documents. No research, no analysis. Pure synthesis and formatting. Run it manually with `/render-default-deliverables` any time after editing context files.

### Recommended Order

```
# 1. Build positioning context (who you are, your market, your competitors)
# Add --property to use GA4 data for page selection (optional)
/positioning-framework https://example.com --property properties/123456789

# 2. Apply client feedback to correct and enrich context (optional)
/positioning-update

# 3. Pull analytics data (what's actually happening on your site)
/ga4-audit properties/123456789

# 4. Generate data-informed experiment ideas
/hypothesis-generator

# 5. Analyze brand voice (standalone, works without positioning context)
/voice-inference https://example.com

# 6. Visualize specific experiment changes as mockups
/experiment-mockup 1

# 7. Re-render deliverables any time context changes
/render-default-deliverables
```

Each step is optional and independent, but they compound. Positioning context makes the analytics audit smarter (product-line page grouping). Analytics data makes hypothesis-generator smarter (traffic-calibrated scores, performance-driven triggers). Run what you have access to.

## Prerequisites

Most skills are pure markdown with no external dependencies. These are the exceptions:

| Skill | Requirement | Why |
|-------|-------------|-----|
| ga4-audit | GA4 credentials (see `.env.example`) OR [analytics-mcp](https://github.com/nicholasgriffintn/analytics-mcp) | Queries GA4 via direct API (preferred) or MCP fallback. Python 3 + `requests` for direct API. |
| aa-audit | Python 3 + `requests` package, Adobe Analytics API credentials (env vars), client config JSON | Runs a Python script against the AA 2.0 Reporting API |
| experiment-mockup (live mode) | Chrome DevTools MCP | Injects changes into live browser DOM. Falls back to static mode without it. |

## License

MIT
