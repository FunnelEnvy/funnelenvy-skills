# FunnelEnvy Skills

AI-powered marketing and CRO skills for Claude Code. Built for practitioners who run real experiments, not just theorize about them.

## Repo Structure

```
funnelenvy-skills/
├── schemas/
│   ├── company-identity.md       # L0 schema
│   ├── competitive-landscape.md  # L1 schema (merged: market + competitors + battle cards)
│   ├── audience-messaging.md     # L1 schema (merged: personas + messaging + voice)
│   ├── positioning-scorecard.md  # L1 schema (includes quick reference)
│   ├── performance-profile.md    # L1 schema (GA4 analytics snapshot)
│   ├── _fetch-registry.md        # Operational metadata schema (not L0/L1)
│   └── _research-extractions.md  # Raw page extractions schema (operational)
├── modules/
│   ├── reddit-research.md        # Shared Reddit API integration (all skills)
│   ├── web-extract.md            # Three-tier web extractor (markdown.new -> curl+HTMLParser -> WebFetch)
│   ├── business-brief.md         # Pre-flight intake template + protocol
│   ├── slugify.md                # Deterministic name-to-slug rules for filenames
│   ├── competitive-assessment.md # Claim assessment, similarity, overlap scoring (Agent 2)
│   ├── experiment-patterns.md    # 23 CRO patterns across 9 categories (hypothesis-generator)
│   └── ice-scoring.md            # ICE calibration anchors and scoring rules (hypothesis-generator)
├── skills/
│   ├── positioning-framework/
│   │   ├── SKILL.md              # Orchestration hub v1 (~840 lines, depth-gated)
│   │   ├── agent-header.md       # Shared agent rules (deduped from phase files)
│   │   └── phases/               # Phase-specific instruction modules
│   │       ├── research.md       # Tier 0-3 research instructions (depth-gated)
│   │       ├── company.md        # L0 construction + inline schema
│   │       ├── competitive.md    # Competitive analysis + inline schema (depth-gated)
│   │       ├── messaging.md      # Personas + messaging + voice + inline schema
│   │       └── scoring.md        # Scorecard + QA + inline schema (depth-gated)
│   ├── ga4-audit/
│   │   └── SKILL.md              # GA4 analytics audit v2.0 (~single agent, analytics-mcp)
│   ├── hypothesis-generator/
│   │   ├── SKILL.md              # CRO hypothesis engine v1.1 (~single agent, reads L0+L1)
│   │   └── phases/               # Phase-specific instruction modules
│   │       ├── detect.md         # Pattern-based opportunity detection
│   │       ├── detect-contextual.md # Context-derived opportunity detection (Phase 2b)
│   │       ├── construct.md      # Hypothesis construction from matched patterns
│   │       └── score.md          # ICE scoring and prioritization
│   └── render-default-deliverables/
│       └── SKILL.md              # L2 rendering skill v1.0 (~single agent, no research)
├── examples/                     # Public examples
├── CLAUDE.md
├── LICENSE
└── README.md
```

## Three-Layer Architecture

```
L2: RENDERING (human-readable deliverables)
    Consumes L0 + L1. Produces polished documents for people.
    No new research. No new analysis. Pure synthesis and formatting.
    Owned by: render-default-deliverables skill
    Location: .claude/deliverables/
    ---------------------------------------------------------------
L1: ANALYSIS (machine-readable context files)
    Consumes L0. Produces structured analytical context.
    competitive-landscape.md | audience-messaging.md |
    positioning-scorecard.md | performance-profile.md
    Owned by: positioning-framework (Agents 2-4), ga4-audit
    Location: .claude/context/
    ---------------------------------------------------------------
L0: COMPANY IDENTITY (machine-readable foundation)
    Raw facts. No analysis, no opinions.
    company-identity.md
    Owned by: positioning-framework Agent 1
    Location: .claude/context/
```

### Layer Rules

**L0 Rules:**
- Contains only verifiable facts about the company
- No competitive comparisons, no analysis, no recommendations
- Single producing skill: positioning-framework Agent 1 (or L0 bootstrap for stubs)

**L1 Rules:**
- Contains analysis and interpretation of L0 in market context
- Machine-readable: YAML frontmatter with structured summaries, confidence scores, depth indicators
- Each file has a single producing skill (may have multiple extending skills)
- Frontmatter designed for token-efficient consumption (~200 tokens vs. full body)

**L2 Rules:**
- Contains NO analysis that isn't already in an L0 or L1 file
- If a deliverable says something that can't be traced to a context file, it's a bug
- Human-readable: no YAML frontmatter, no confidence scores inline, no `[NEEDS CONFIRMATION]` inline (footnotes only), no references to agents, skills, context files, frontmatter, or any system internals
- Designed to be forwarded, pasted into decks, printed, shared with stakeholders
- Single owner: the render-default-deliverables skill
- Can be re-rendered any time L0 or L1 changes without re-running research

### Cross-Layer Contracts

- L1 skills NEVER produce files in `.claude/deliverables/`
- L2 skill NEVER produces files in `.claude/context/`
- L2 skill NEVER performs web research, API calls, or data collection
- L2 deliverables include a footer noting which context files were consumed (provenance)

### Context Files (L0 + L1)

| File | Layer | Produced By | Consumed By |
|------|-------|------------|-------------|
| `.claude/context/company-identity.md` | L0 | positioning-framework (all depths) | All L1 skills, render-default-deliverables |
| `.claude/context/competitive-landscape.md` | L1 | positioning-framework (standard/deep) | render-default-deliverables, website-audit, content strategy, hypothesis roadmap |
| `.claude/context/audience-messaging.md` | L1 | positioning-framework (standard/deep) | render-default-deliverables, website-audit, content strategy |
| `.claude/context/positioning-scorecard.md` | L1 | positioning-framework (all depths, minimal at quick) | render-default-deliverables, website-audit, hypothesis roadmap |
| `.claude/context/performance-profile.md` | L1 | ga4-audit | hypothesis-generator (ICE calibration + performance-driven hypotheses), render-default-deliverables (opportunity sizing) |
| `.claude/context/_fetch-registry.md` | Operational | positioning-framework Agent 1 (appended by Agent 2) | Agent 2 (duplicate fetch prevention) |
| `.claude/context/_research-extractions.md` | Internal/Operational | positioning-framework Agent 1 | Agents 2, 3, 4 (selectively). Ephemeral, overwritten on each run. Not prior work. |

### Deliverable Files (L2)

| File | Description | Produced By |
|------|-------------|-------------|
| `.claude/deliverables/manifest.md` | Index of all deliverables | render-default-deliverables |
| `.claude/deliverables/executive-summary.md` | Tier 1 | render-default-deliverables |
| `.claude/deliverables/messaging-guide.md` | Tier 2 | render-default-deliverables |
| `.claude/deliverables/experiment-roadmap.md` | Standalone | hypothesis-generator |
| `.claude/deliverables/competitive-comparison-matrix.md` | Tier 3 | render-default-deliverables |
| `.claude/deliverables/battle-cards/[competitor-slug].md` | Tier 3 | render-default-deliverables |

**Note:** The `.claude/deliverables/` directory is empty until render-default-deliverables runs. positioning-framework does not produce deliverables.

**Migration notes:**
- Prior to v1.0, competitive and messaging data lived in separate files (`market-landscape.md` + `competitor-profiles.md`, `audience-personas.md` + `messaging-framework.md` + `brand-voice.md`). These were merged into `competitive-landscape.md` and `audience-messaging.md`. Deprecated schema files have been removed.
- Prior to v1.0, positioning-quick and competitive-research were separate skills. These were consolidated into positioning-framework with the `--depth` flag. Legacy split files are auto-migrated to the merged format on first run.

### Schema Definitions

Context file schemas live in `/schemas/`. Each schema defines:
- YAML frontmatter fields (metadata + structured summary for fast downstream consumption)
- Markdown body sections (REQUIRED vs OPTIONAL)
- What each section is used for by downstream skills
- Completeness checklist
- Versioning rules for extending skills

Skills producing context files MUST follow the schema. Skills consuming context files can rely on REQUIRED sections being present.

**Downstream consumption pattern:** Read frontmatter of the relevant context file first. If the frontmatter structured summary contains sufficient data for your needs, use it. If you need the full analytical narrative, read the body. This saves tokens when a skill only needs top-line data (e.g., top 3 competitors and white spaces) rather than the full analysis.

## Prior Work Detection

Before researching, producing skills MUST glob `.claude/context/` and read the frontmatter of relevant existing files. Skills that produce context files already produced by other skills MUST extend prior work rather than overwriting it.

**Rules:**
- If prior work exists at a shallower depth, extend it. Do not re-fetch data already present.
- If prior work exists at the same or deeper depth, skip re-analysis and only add net-new content.
- Extending skills update `last_updated` and `last_updated_by` but preserve `generated_by`.
- Extending skills can only RAISE confidence scores, never lower them (exception: positioning-scorecard scores can go up or down on re-assessment).
- Mark extended sections with `<!-- extended by [skill-name] [date] -->` comments.

## L0 Bootstrap Protocol

When a consuming skill (render-default-deliverables, future L2 skills) needs `company-identity.md` and none exists, it runs this protocol transparently instead of stopping the user or asking them to run a different skill.

**Any skill can invoke this protocol. The canonical definition lives here so it's not duplicated across SKILL.md files.**

### Steps

1. **Detect.** Glob `.claude/context/company-identity.md`.
   - If it exists with `confidence >= 2`: read frontmatter and continue with the consuming skill.
   - If it exists with `confidence < 2`: treat as missing and proceed to step 2.
   - If missing: proceed to step 2.

2. **Research.** Fetch up to 3 pages from the company's website (homepage, pricing or about page, one differentiator or case study page). No background agents. Same budget as positioning-quick's required research.

3. **Build.** Generate a stub `company-identity.md` following the schema in `/schemas/company-identity.md`. Populate what's possible from the 3 fetches:
   - YAML frontmatter (company, category, target_market)
   - Company Overview
   - Services & Capabilities
   - Stated Differentiators
   - Proof Point Registry (whatever proof is visible on the site)
   - Pricing Model (if visible)
   - Category Gap (if detectable)

   Mark unpopulated REQUIRED sections with `[NEEDS CLIENT INPUT]`. Set frontmatter: `confidence: 2`, `generated_by: "{consuming-skill-name}/bootstrap"`.

4. **Write to disk.** Save to `.claude/context/company-identity.md` immediately. Writing before the checkpoint means the user can edit the file directly, and no state is lost if the session drops.

5. **Single checkpoint.** Present a combined summary of L0 findings plus any skill-specific pre-flight questions. One interruption, not three. Format:

   ```
   ## Company Identity (auto-generated, confidence: 2)

   **Company:** [name]
   **Category:** [primary] (buyers search: [buyer terms])
   **Key services:** [bullet list]
   **Stated differentiators:** [numbered list]
   **Proof strength:** [summary]
   **Gaps:** [what couldn't be determined from public data]

   Saved to `.claude/context/company-identity.md`. Edit the file directly if anything's wrong.

   ## [Skill-specific pre-flight questions here]

   Reply with edits, answers, or just "go" to proceed.
   ```

6. **Continue.** After the user responds (or says "go"), proceed with the consuming skill's next phase. The stub is good enough to start. For a complete L0 with full proof point registry and all REQUIRED sections, run positioning-framework.

### Design Decisions

- **Write before checkpoint.** File is on disk before the user sees the summary. Session crash = no lost work.
- **Single checkpoint.** L0 review and skill-specific questions are combined into one prompt. The user answers once, not three times.
- **confidence: 2.** Explicitly signals "bootstrap stub, not a full L0." positioning-framework sees this and knows to extend, not skip.
- **Not a full L0 build.** The bootstrap is intentionally shallow (3 fetches, no competitor research, no review mining). The full L0 comes from positioning-framework.
- **Minimal extractions file.** Bootstrap should also write a minimal `_research-extractions.md` with those 3 pages (following the same streaming write pattern and artifact stripping rules as the full research phase).

## Workflow Order

### Recommended execution order

1. **`/positioning-framework <url> --depth quick`** (optional fast triage, ~5-8 min, ~70-90K tokens)
2. **`/positioning-framework <url>`** (standard depth, produces all L0 + L1 context + deliverables, ~450-500K tokens across subagents)
3. **`/positioning-framework <url> --depth deep`** (extends competitive context to deep, ~550-650K tokens across subagents)
4. **`/ga4-audit <property_id>`** (optional, produces performance-profile.md for traffic-driven hypotheses, ~5-8 min)
5. **`/hypothesis-generator`** (produces experiment roadmap from L0 + L1 context + optional performance data)
6. **`/render-default-deliverables`** (produces human-readable deliverables from L0 + L1 context)

**Tip:** Add `--property <ga4_property_id>` to any positioning-framework invocation to use GA4 traffic data for page selection (e.g., `/positioning-framework https://example.com --property properties/123456789`). This runs a single lightweight query before research begins. The full ga4-audit still runs separately.

Each depth level builds on prior work. Running quick then standard then deep is incremental, not redundant. The skill detects existing context and extends rather than overwrites. Deliverables can be re-rendered at any time after context files exist.

### Concurrency rule

Do NOT run two producing skills simultaneously in the same session. Context files have no locking mechanism.

## Skill Format

Each skill lives in its own folder under `skills/` and contains a `SKILL.md` file with:

- YAML frontmatter: `name`, `version`, `description` (used for trigger matching)
- Workflow sections defining how the agent should execute
- Output format specifications
- Context dependencies (which L0/L1 files it needs)
- Preconditions (what must exist before the skill runs, what must NOT be running concurrently)
- Quality checks

## Agent Model Selection

Skills that spawn subagents MUST specify the `model` parameter on the Task tool call.

**Current convention:** Opus for all agents. Sonnet was tested and produced worse output (hallucinated facts, wrong competitors, inflated scores) with marginal cost savings that didn't justify the quality hit.

Each skill's SKILL.md includes an Agent Model Selection table specifying the model per agent role.

## Architectural Decisions

### Schema Authority
Phase files contain inline schemas that agents read at execution time. These are the authoritative schema definitions. Standalone files in `/schemas/` are human-readable reference copies for contributor orientation only. If the two diverge, the phase file wins.

When updating a schema: update the phase file's inline schema first, then update the standalone schema file to match.

### Scoring: Categories, Not Numbers
Positioning dimensions use categorical ratings (Strong / Needs Work / Missing) instead of numerical scores. Numbers imply false precision from a single-pass LLM assessment. Categories are more consistent across runs, easier to calibrate, and just as effective at driving experiment prioritization. Most companies land at Needs Work on most dimensions. The Key Finding column provides the specific evidence that makes each rating meaningful.

## Conventions

- L0 + L1 context files output to `.claude/context/`
- **Operational files** use underscore prefix: `_fetch-registry.md`, `_research-extractions.md`. These are internal coordination artifacts. They are NOT considered "prior work" for depth evaluation and are overwritten (not extended) on each run.
- L2 deliverables output to `.claude/deliverables/`
- L1 skills never produce deliverables. L2 skill never performs research. All human-facing output goes through render-default-deliverables.
- Skills are standalone. No external dependencies required.
- Every skill should work in at least two modes: automated (agent does the research) and guided (user provides input manually)
- When a skill needs a context file that doesn't exist, it should either produce it (if capable) or instruct the user which skill to run first.

## Available Skills

### positioning-framework (v1.0.0)
Consolidated positioning, competitive research, and messaging framework. Feed it a company URL with a depth level and it researches, analyzes, and produces structured L0 + L1 context files.

**Depth levels:**
- `--depth quick` (~5-8 min, ~70-90K tokens): Fast positioning triage. Agent 1 only + inline health check. Produces L0 + minimal scorecard.
- `--depth standard` (default, ~30-35 min, ~450-500K tokens across subagents): Full framework. All 4 agents + render-default-deliverables. Produces L0 + 3 L1 context files + deliverables.
- `--depth deep` (~40-50 min, ~550-650K tokens across subagents): Extended competitive analysis. 6+ competitors, Tier 2/3 sources, post-research questionnaire.

**Note:** Token totals for standard/deep include render-default-deliverables, which auto-runs. Usage is distributed across subagents -- the main context window never needs to auto-compact.

**Additional flags:**
- `--competitive-depth none|standard|deep`: Override competitive analysis depth independently.
- `--competitive-focus "Name"`: Deep-dive a single competitor, extending existing analysis.
- `--property <ga4_property_id>`: Use GA4 traffic data to guide Agent 1's page selection. Single lightweight query. Falls back to heuristic if auth fails.

**Outputs:**
- L0 context: company-identity.md (facts, differentiators, proof registry, constraints)
- L1 context: competitive-landscape.md (market overview, competitor profiles with inline battle card data, claim overlap, white space)
- L1 context: audience-messaging.md (personas, messaging hierarchy, language bank, voice rules)
- L1 context: positioning-scorecard.md (quick reference, health check with categorical ratings, gap analysis, confidence scores)

Runs up to 4 sequential agents depending on depth (Research+L0, Competitive, Messaging+Voice, Scorecard). Each depth builds on prior work incrementally.

Four modes: Autonomous Research (default), Guided Interview, Audit & Update, Reconciliation (compare research against client's manual worksheet).

### render-default-deliverables (v1.0.0)
L2 rendering skill. Consumes L0 + L1 context files and produces human-readable deliverables. No research, no analysis. Pure synthesis and formatting.

Auto-invoked by positioning-framework at standard/deep depth. Also available standalone via `/render-default-deliverables` for re-rendering after context updates.

**Deliverable tiers:**
- Tier 1: Executive Summary (needs L0 + scorecard)
- Tier 2: Messaging Guide (needs L0 + audience-messaging)
- Tier 3: Competitive Comparison Matrix, Battle Cards (needs L0 + competitive-landscape)
- Tier 4: Opportunity Sizing (deferred, needs performance-profile.md from ga4-audit)

**Output:** `.claude/deliverables/` with manifest

### ga4-audit (v2.0.0)
GA4 analytics audit. Pulls 10-13 targeted reports from a GA4 property via analytics-mcp, classifies conversion events, and produces a v2 `performance-profile.md` L1 context file with page grouping, opportunity sizing, trend analysis, and optional L0 enrichment. Single agent, no depth flag. Overwrites on each run (analytics snapshots, not incremental).

**Invocation:** `/ga4-audit <property_id> [--days 90] [--date-range "YYYY-MM-DD:YYYY-MM-DD"] [--no-compare]`

**Outputs:**
- L1 context: performance-profile.md (page performance, conversion funnels, channel/device breakdown, data quality assessment)

**Runtime:** ~5-8 minutes. ~50-75K tokens. Single interaction point (event classification confirmation).

### hypothesis-generator (v1.1.0)
Standalone CRO hypothesis engine. Reads positioning context (L0 + L1) plus optional performance data, applies
23 experiment patterns across 9 categories plus performance-driven triggers, and produces a prioritized experiment
roadmap with ICE scoring. When `performance-profile.md` is present, produces data-calibrated scores and traffic-driven hypotheses. Manually invoked: /hypothesis-generator

## Development

When creating or editing skills:

1. Follow the existing SKILL.md format (frontmatter + structured markdown)
2. Include quality checks at the end of every skill
3. Test against a real company URL before committing
4. Every claimed differentiator or value theme in a skill's output must require evidence. No unsubstantiated claims.
5. Define context dependencies: which L0/L1 files the skill reads and which it writes
6. Follow the schema definitions in `/schemas/` for any context files produced
7. Include a Preconditions section stating what must exist before the skill runs
8. Implement Prior Work Detection: check for existing context files before researching
