# FunnelEnvy Skills

AI-powered marketing and CRO skills for Claude Code. Built for practitioners who run real experiments, not just theorize about them.

## Public Repo: No Client References (HARD RULE)

This repository is **public**. Never write a real company or client name, engagement codename, or account identifier into any file or commit message here. Use a generic placeholder (`Acme`, `Example Corp`, `the client`, `a private consumer engagement`) or omit it entirely. This binds everyone, including AI agents editing the repo, and it is applied by inference: if you recognize a string as a real company name, do not write it.

- Do not maintain or rely on a list of names. The rule is categorical: no real company names, ever.
- A self-contained guard backstops it: `hooks/pre-commit` and `hooks/commit-msg` (installed via `scripts/install-hooks.sh`) plus a CI job run `scripts/client_ref_guard.py`, which flags the shape of client data (a capitalized entity run followed by a corporate legal suffix) and blocks the commit. It reports locations only, never the matched text.
- The guard is a backstop, not the control. It cannot recognize a bare codename or an unsuffixed name; the rule and review are what actually prevent those. Author clean in the first place.
- `_dev/` and other dev surfaces are gitignored, but treat the rule as applying everywhere regardless.

## Repo Structure

```
funnelenvy-skills/
├── schemas/                      # Human-readable reference copies (phase-file inline schemas are authoritative)
│   ├── company-identity.md       # L0 schema
│   ├── competitive-landscape.md  # L1 schema (merged: market + competitors + battle cards)
│   ├── audience-messaging.md     # L1 schema (merged: personas + messaging + voice)
│   ├── positioning-scorecard.md  # L1 schema (includes quick reference)
│   ├── performance-profile.md    # L1 schema (GA4/AA analytics snapshot)
│   ├── brand-voice.md            # L1 schema (voice analysis: tone, vocabulary, examples, rules)
│   ├── live-observation.md       # L0 schema (live-capture page structure)
│   ├── live-copy.md              # L0 schema (live-capture verbatim copy)
│   ├── campaign-brief.md         # Campaign brief + companion schemas (landing-page-generator)
│   ├── _fetch-registry.md        # Operational metadata schema (not L0/L1)
│   └── _research-extractions.md  # Raw page extractions schema (operational)
├── modules/
│   ├── reddit-research.md        # Shared Reddit API integration (all skills)
│   ├── web-extract.md            # Three-tier web extractor (markdown.new -> curl+HTMLParser -> WebFetch)
│   ├── business-brief.md         # Pre-flight intake template + protocol
│   ├── slugify.md                # Deterministic name-to-slug rules for filenames
│   ├── competitive-assessment.md # Claim assessment, similarity, overlap scoring (Agent 2)
│   ├── kb-mode.md                # Canonical KB-mode dual-mode contract (all 5 dual-mode skills)
│   ├── voc-extraction.md         # Voice-of-customer extraction (positioning-framework)
│   ├── experiment-patterns.md    # 32 CRO patterns across 10 categories (hypothesis-generator)
│   ├── patterns-procurement.md   # Procurement archetype patterns (hypothesis-generator)
│   ├── contrarian-triggers.md    # 14 contrarian triggers (hypothesis-generator)
│   ├── hypothesis-interactions.md # AND/OR/XOR interaction gates + empirical effects (hypothesis-generator)
│   ├── ice-scoring.md            # ICE calibration anchors and scoring rules (hypothesis-generator)
│   ├── conversion-playbook.md    # Paid LP structural rules, CTA, form, benchmarks (landing-page-generator)
│   ├── campaign-brief-template.md # Campaign brief template structure (landing-page-generator)
│   ├── lp-audit-taxonomy.md      # 10-dimension LP audit taxonomy (landing-page-generator)
│   └── section-taxonomy.md       # Composable LP section taxonomy (landing-page-generator)
├── skills/
│   ├── positioning-framework/
│   │   ├── SKILL.md              # Orchestration hub (depth-gated)
│   │   ├── agent-header.md       # Shared agent rules (deduped from phase files)
│   │   └── phases/               # Phase-specific instruction modules
│   │       ├── research.md       # Tier 0-3 research instructions (depth-gated)
│   │       ├── company.md        # L0 construction + inline schema
│   │       ├── competitive.md    # Competitive analysis + inline schema (depth-gated)
│   │       ├── messaging.md      # Personas + messaging + voice + inline schema
│   │       ├── scoring.md        # Scorecard + QA + inline schema (depth-gated)
│   │       └── quick-readout.md  # Quick-depth readout template + context-file spec (orchestrator-inline)
│   ├── positioning-update/
│   │   └── SKILL.md              # Client feedback amendment skill (single agent)
│   ├── ga4-audit/
│   │   └── SKILL.md              # GA4 analytics audit (single agent, analytics-mcp)
│   ├── aa-audit/
│   │   ├── SKILL.md              # Adobe Analytics audit (single agent, AA 2.0 Reporting API)
│   │   ├── aa_audit.py           # Reporting API query script
│   │   └── aa-config.example.json # Client config template
│   ├── hypothesis-generator/
│   │   ├── SKILL.md              # CRO hypothesis engine (single agent, reads L0+L1)
│   │   └── phases/               # Phase-specific instruction modules
│   │       ├── detect.md         # Pattern-based opportunity detection
│   │       ├── detect-contextual.md # Context-derived opportunity detection (Phase 2b)
│   │       ├── detect-strategic.md # Strategic-lever detection (Phase 2c)
│   │       ├── construct.md      # Hypothesis construction from matched patterns
│   │       ├── validate.md       # Premise & measurement validation (Phase 3.5)
│   │       └── score.md          # ICE scoring and prioritization
│   ├── landing-page-generator/
│   │   ├── SKILL.md              # Orchestrator (4 phase agents, review gates)
│   │   ├── agent-header.md       # Shared agent rules (all phases)
│   │   ├── phases/               # Phase-specific instruction modules
│   │   │   ├── brief.md          # Phase 1: campaign brief builder
│   │   │   ├── copy.md           # Phase 2: landing page copy generation
│   │   │   ├── design.md         # Phase 3: HTML page builder
│   │   │   └── qa.md             # Phase 4: QA validation
│   │   └── templates/
│   │       ├── section-catalog.html      # Composable section visual reference (design phase)
│   │       └── wireframe-demo-legacy.jsx # Legacy React wireframe (reference only)
│   ├── voice-inference/
│   │   ├── SKILL.md              # Orchestrator (2 sequential agents, observe/compare modes)
│   │   ├── agent-header.md       # Shared agent rules (both agents)
│   │   └── phases/               # Phase-specific instruction modules
│   │       ├── extract.md        # Phase 1: page discovery + extraction
│   │       └── analyze.md        # Phase 2: voice analysis + rule derivation
│   ├── live-capture/
│   │   ├── SKILL.md              # Orchestrator (flags, I/O + browser mode resolution, routing)
│   │   ├── agent-header.md       # Shared agent rules (factual-not-interpretive, tri-state, position encoding)
│   │   ├── phases/               # select (Section 8), capture (passive DOM), static-capture, write (inline schema)
│   │   └── scripts/              # page_select.py (leverage ranking), content_hash.py (recapture-diff)
│   ├── experiment-mockup/
│   │   ├── SKILL.md              # Orchestrator (parses flags, detects mode, routes phases)
│   │   ├── agent-header.md       # Shared agent rules (all phases)
│   │   └── phases/               # Phase-specific instruction modules
│   │       ├── inspect.md        # Phase 1 (live): navigate, locate section, extract styles
│   │       ├── inject.md         # Phase 2 (live): build + inject content, iterate with user
│   │       ├── capture.md        # Phase 3 (live): screenshot, extract HTML, write mockup.html
│   │       ├── annotate.md       # Phase 4 (both): CRO placement rationale
│   │       └── static-build.md   # Fallback: combined extract + build (no DevTools)
│   ├── render-program-site/
│   │   ├── SKILL.md              # Orchestrator (phased: gate+emit, curate prose, humanize, write)
│   │   ├── edge-contract.md      # Validated object + 7-check gate + source schemas + type-label map
│   │   ├── scripts/             # render_site.py (deterministic: parse->gate->derive->emit)
│   │   ├── templates/           # base/hub/spoke-strategic/spoke-tactical/spoke-account.html + styles.css + site.js
│   │   └── references/          # ai-writing-signs.md (embedded humanizer rules)
│   └── render-default-deliverables/
│       └── SKILL.md              # L2 rendering skill (single agent, no research)
├── scripts/                      # client_ref_guard.py (public-repo guard), install-hooks.sh, validators
├── hooks/                        # pre-commit + commit-msg (invoke the guard; installed via core.hooksPath)
├── .github/workflows/            # client-ref-guard.yml (CI: tree scan + unit tests)
├── .claude-plugin/               # marketplace.json (plugin manifest)
├── _tests/                       # Unit tests (guard, render_site)
├── CLAUDE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── README.md
```

Skill CHANGELOG.md files and per-skill dev artifacts are omitted from the tree for brevity. The tree carries no version pins; versions live in SKILL.md frontmatter (source of truth), mirrored only in the Available Skills headers below, README.md, and each changelog -- all enforced by `scripts/registry_check.py` in CI.

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
    positioning-scorecard.md | performance-profile.md |
    brand-voice.md
    Owned by: positioning-framework (Agents 2-4), ga4-audit, voice-inference
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
- **Exception:** hypothesis-generator reads L0 + L1 context and produces new analytical output in `.claude/deliverables/`: the tactical `experiment-roadmap.md` (page-element experiments) and, when a business-level lever qualifies, a separate `strategic-roadmap.md` (program/offer/motion/asset-level experiments with non-A/B measurement designs; KB mode emits it as a `gold-strategic-roadmap` artifact). It is not L2 (it produces new analysis, not just synthesis). It does not perform web research or write to `.claude/context/`.
- **Exception:** experiment-mockup reads the experiment roadmap (legacy `.claude/deliverables/experiment-roadmap.md` or KB-mode `{kb_root}/deliverables/{scope}-experiment-roadmap.md`) and makes web requests (DevTools navigation or curl extraction) to build visual mockups in the deliverables tree (`.claude/deliverables/experiments/` in legacy mode, `{kb_root}/deliverables/experiments/` in KB mode). It is not a pure L2 skill (it makes web requests, violating the "L2 never makes web requests" invariant). The violation is contained and documented, following the same pattern as hypothesis-generator.

### Context Files (L0 + L1)

| File | Layer | Produced By | Consumed By |
|------|-------|------------|-------------|
| `.claude/context/company-identity.md` | L0 | positioning-framework (all depths) | All L1 skills, render-default-deliverables |
| `.claude/context/competitive-landscape.md` | L1 | positioning-framework (standard/deep) | render-default-deliverables, website-audit, content strategy, hypothesis roadmap |
| `.claude/context/audience-messaging.md` | L1 | positioning-framework (standard/deep) | render-default-deliverables, website-audit, content strategy |
| `.claude/context/positioning-scorecard.md` | L1 | positioning-framework (all depths, minimal at quick) | render-default-deliverables, website-audit, hypothesis roadmap |
| `.claude/context/performance-profile.md` | L1 | ga4-audit (GA4 properties) or aa-audit (Adobe Analytics properties) | hypothesis-generator (ICE calibration + performance-driven hypotheses), live-capture (page selection), render-default-deliverables (executive summary enrichment) |
| `.claude/context/brand-voice.md` | L1 | voice-inference | positioning-framework Agent 3 (voice baseline), landing-page-generator (voice calibration), render-default-deliverables (messaging guide enrichment), hypothesis-generator (voice-aware hypothesis framing) |
| `.claude/context/live-observation.md` | L0 | live-capture (legacy mode) | hypothesis-generator, experiment-mockup |
| `.claude/context/live-copy.md` | L0 | live-capture (legacy mode) | hypothesis-generator, experiment-mockup |
| `.claude/context/_fetch-registry.md` | Operational | positioning-framework Agent 1 (appended by Agent 2) | Agent 2 (duplicate fetch prevention) |
| `.claude/context/_voice-extractions.md` | Internal/Operational | voice-inference Agent 1 | Agent 2. Ephemeral, overwritten on each run. Not prior work. |
| `.claude/context/_research-extractions.md` | Internal/Operational | positioning-framework Agent 1 | Agents 2, 3, 4 (selectively). Ephemeral, overwritten on each run. Not prior work. |

### Deliverable Files (L2)

| File | Description | Produced By |
|------|-------------|-------------|
| `.claude/deliverables/manifest.md` | Index of all deliverables | render-default-deliverables |
| `.claude/deliverables/executive-summary.md` | Tier 1 | render-default-deliverables |
| `.claude/deliverables/messaging-guide.md` | Tier 2 | render-default-deliverables |
| `.claude/deliverables/experiment-roadmap.md` | Analytical deliverable, page-element experiments (see Cross-Layer Contracts exception) | hypothesis-generator |
| `.claude/deliverables/strategic-roadmap.md` | Analytical deliverable, business-level levers with non-A/B measurement designs (conditional: produced only when a lever qualifies; see Cross-Layer Contracts exception). KB mode: `{kb_root}/deliverables/{scope}-strategic-roadmap.md` as a `gold-strategic-roadmap` artifact | hypothesis-generator |
| `.claude/deliverables/competitive-comparison-matrix.md` | Tier 3 | render-default-deliverables |
| `.claude/deliverables/battle-cards/[competitor-slug].md` | Tier 3 | render-default-deliverables |
| `.claude/deliverables/campaigns/[slug]/brief.md` | Campaign brief | landing-page-generator (Phase 1) |
| `.claude/deliverables/campaigns/[slug]/copy.md` | Landing page copy | landing-page-generator (Phase 2) |
| `.claude/deliverables/campaigns/[slug]/page.html` | HTML landing page | landing-page-generator (Phase 3) |
| `.claude/deliverables/campaigns/[slug]/qa-report.md` | QA validation report | landing-page-generator (Phase 4) |
| `.claude/deliverables/experiments/<slug>/mockup.html` | Standalone HTML mockup of proposed experiment change | experiment-mockup |
| `.claude/deliverables/experiments/<slug>/placement.md` | CRO placement rationale + implementation notes | experiment-mockup |
| `.claude/deliverables/experiments/<slug>/mockup-screenshot.png` | Browser screenshot of injected state (live mode only) | experiment-mockup |

**Note:** The `.claude/deliverables/` directory is empty until render-default-deliverables runs. positioning-framework does not produce deliverables.

**Note:** The experiment-mockup paths above are legacy mode. In KB mode, experiment-mockup writes these artifacts under `{kb_root}/deliverables/experiments/<slug>/` instead, co-located with the gold roadmap so render-program-site resolves them via each test's `mockup` block.

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
4. **`/positioning-update`** (optional, apply client feedback/corrections to context files, ~20-40K tokens)
5. **`/ga4-audit <property_id>`** (optional, produces performance-profile.md for traffic-driven hypotheses, ~5-8 min; for Adobe Analytics properties, run **`/aa-audit --config <path>`** instead, same output file)
6. **`/hypothesis-generator`** (produces experiment roadmap from L0 + L1 context + optional performance data)
7. **`/render-default-deliverables`** (produces human-readable deliverables from L0 + L1 context)
8. **`/landing-page-generator <company> <slug> --stage all`** (optional, produces campaign landing page from L0 + L1 context, ~260-400K tokens)
9. **`/voice-inference <url>`** (optional, standalone brand voice analysis, ~80-120K tokens, ~10-15 min)
10. **`/live-capture <url>`** (optional, captures live-page structure + copy as factual context; feeds hypothesis-generator and experiment-mockup. Browser-based, dual-mode)
11. **`/experiment-mockup <hypothesis-number>`** (optional, produces visual mockup + placement rationale for a specific hypothesis)
12. **`/render-program-site [<strategic-md> <tactical-md>] [--scope <slug>]`** (optional, renders a strategic experiment layer + tactical roadmap into a client-facing two-altitude HTML site with a hard edge-contract gate)

**Tip:** Add `--property <ga4_property_id>` to any positioning-framework invocation to use GA4 traffic data for page selection (e.g., `/positioning-framework https://example.com --property properties/123456789`). This runs a single lightweight query before research begins and saves the property ID to `company-identity.md` so downstream skills like ga4-audit can auto-detect it. The full ga4-audit still runs separately.

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
- **Operational files** use underscore prefix: `_fetch-registry.md`, `_research-extractions.md`, `_voice-extractions.md`. These are internal coordination artifacts. They are NOT considered "prior work" for depth evaluation and are overwritten (not extended) on each run.
- L2 deliverables output to `.claude/deliverables/`
- L1 skills never produce deliverables. L2 skill never performs research. All human-facing output goes through render-default-deliverables.
- Skills are standalone. No external dependencies required.
- Every skill should work in at least two modes: automated (agent does the research) and guided (user provides input manually)
- When a skill needs a context file that doesn't exist, it should either produce it (if capable) or instruct the user which skill to run first.

## Available Skills

### positioning-framework (v1.1.2)
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

**Dual-mode output:** When the working repo's CLAUDE.md declares a `Knowledge Bases` section whose type skill defines the 7 CRO artifact types, the skill writes KB-native bronze/silver artifacts into that KB instead of `.claude/context/` (KB mode, requires `--scope <slug>`; `--no-kb` forces legacy). Legacy behavior is unchanged when no KB binding is detected. See SKILL.md > KB Mode (Dual-Mode Output).

Four modes: Autonomous Research (default), Guided Interview, Audit & Update, Reconciliation (compare research against client's manual worksheet).

### render-default-deliverables (v1.0.2)
L2 rendering skill. Consumes L0 + L1 context files and produces human-readable deliverables. No research, no analysis. Pure synthesis and formatting.

Auto-invoked by positioning-framework at standard/deep depth. Also available standalone via `/render-default-deliverables` for re-rendering after context updates.

**Deliverable tiers:**
- Tier 1: Executive Summary (needs L0 + scorecard)
- Tier 2: Messaging Guide (needs L0 + audience-messaging)
- Tier 3: Competitive Comparison Matrix, Battle Cards (needs L0 + competitive-landscape)

**Output:** `.claude/deliverables/` with manifest

### ga4-audit (v2.4.1)
GA4 analytics audit. Pulls 11-15 targeted reports from a GA4 property via analytics-mcp, classifies conversion events, discovers element-level interactions (CTA clicks, link text, custom parameters), and produces a v2.3 `performance-profile.md` L1 context file with page grouping, opportunity sizing, trend analysis, element interaction data, and optional L0 enrichment. Single agent, no depth flag. Overwrites on each run (analytics snapshots, not incremental).

**Invocation:** `/ga4-audit [property_id] [--days 90] [--date-range "YYYY-MM-DD:YYYY-MM-DD"] [--no-compare]`

Property ID is optional. If omitted, auto-detects from `company-identity.md` frontmatter (`ga4_property` field, set by positioning-framework `--property` flag). Falls back to account summaries if not found.

**Outputs:**
- L1 context: performance-profile.md (page performance, conversion funnels, channel/device breakdown, element interactions, data quality assessment)

**Runtime:** ~5-8 minutes. ~50-80K tokens. Single interaction point (event classification confirmation).

### aa-audit (v1.1.0)
Adobe Analytics audit, the AA counterpart to ga4-audit for properties on Adobe. Runs `aa_audit.py` against the AA 2.0 Reporting API (client config JSON + `ADOBE_AA_*` env credentials), interprets the structured JSON output, and produces a `performance-profile.md` L1 context file consumable by the same downstream skills (hypothesis-generator, live-capture page selection, render-default-deliverables). Single agent, no depth flag. Overwrites on each run (analytics snapshots, not incremental).

**Invocation:** `/aa-audit [--config /path/to/config.json] [--days 90] [--no-compare]`

**Outputs:**
- L1 context: performance-profile.md (page performance, conversion funnels, channel/device breakdown, data quality assessment)

**Runtime:** ~5-8 minutes. ~50-80K tokens.

### hypothesis-generator (v1.13.3)
Standalone CRO hypothesis engine. Reads positioning context (L0 + L1) plus optional performance data, applies
32 experiment patterns across 10 categories plus performance-driven triggers, and produces a prioritized experiment
roadmap with ICE scoring, test feasibility estimation, contrarian filtering (14 triggers that reframe or suppress standard CRO advice in B2B and context-specific scenarios), interaction-effect modeling (AND/OR/XOR gates between same-page hypotheses, 7 empirical interaction effects), LIFT-model sequencing (Relevance > Clarity > Anxiety > Distraction > Urgency within tiers), empirical tiebreakers (winner replication, proximity-to-conversion ordering), and inconclusive test guidance per experiment including post-deployment causal impact validation and directional significance soft-coding. Premise and measurement validation (Phase 3.5) emits per-hypothesis tri-state gates consumed as hard Confidence ceilings, covering both lanes: six tactical gates, plus strategic gates (baseline reliability with a design-forcing branch, business-metric instrumentation, premise contradiction). When a business-level lever qualifies (Phase 2c, six lever families with a 7-criterion quality gate whose gap-is-still-open criterion is tri-state: documented-live discards, documented-absent mints a build, context-silence about a client-side system mints only confirm-first), also produces a separate strategic roadmap deliverable with non-A/B measurement designs and an unscored Measurement Foundation section for instrumentation prerequisites (never scored as experiments). When `performance-profile.md` is present, produces data-calibrated scores with empirical benchmarks and B2B SaaS calibration anchors, traffic-driven hypotheses, and per-experiment feasibility notes. Infeasible experiments (insufficient traffic) are routed to "What's Not Here" with alternative approaches. Dual-mode I/O: when the working repo declares a CRO knowledge base binding, reads the scope's silver artifacts from the KB and writes typed gold-experiment-roadmap / gold-strategic-roadmap artifacts (`--scope` required; `--no-kb` forces legacy), with schema-tolerant performance trigger evaluation for profiles lacking `schema_version`. Manually invoked: /hypothesis-generator

### landing-page-generator (v2.0.1)
B2B paid landing page generator. Four-phase pipeline: Brief Builder, Copy Agent, Design Agent, QA Validator. Consumes L0+L1 context files and produces campaign-specific landing page deliverables. Each phase produces a file consumed by the next phase. Human review gates between phases when running the full pipeline.

**Invocation:** `/landing-page-generator <company> <campaign-slug> [--stage brief|copy|design|qa|all] [--depth standard|deep]`

**Phases:**
- Phase 1 (Brief): Reads L0+L1 context, extracts into campaign brief template, resolves gaps interactively
- Phase 2 (Copy): Generates section-by-section landing page copy from brief + conversion playbook + LP audit taxonomy (construct mode: D1,D2,D3,D5,D7,D8,D10)
- Phase 3 (Design): Builds single-file HTML page from copy + wireframe reference + LP audit taxonomy (construct mode: D4,D6,D9) + brand design system (if available in context directory). Stage isolation exception: brand/design files are read from context directory.
- Phase 4 (QA): Validates copy and HTML against playbook checklist + LP audit taxonomy (10-dimension scoring). Runs inline, no subagent.

**Dependencies:**
- Hard: `company-identity.md` (confidence >= 3)
- Soft: `audience-messaging.md`, `competitive-landscape.md`, `positioning-scorecard.md`, `performance-profile.md`, rendered deliverables

**Outputs:** `.claude/deliverables/campaigns/<slug>/` (brief.md, copy.md, page.html, qa-report.md)

**Runtime:** ~270-410K tokens for full pipeline. Individual phases: Brief ~50-80K, Copy ~85-125K, Design ~105-155K, QA ~30-50K.

### positioning-update (v1.0.1)
Client feedback amendment skill. Parses freeform client feedback (emails, Slack messages, meeting notes), classifies each piece of intelligence, presents a structured change plan for approval, and executes surgical updates to L0+L1 context files. No web research. Triggers deliverable re-render after changes.

**Invocation:** `/positioning-update [--file path/to/feedback.md] [--dry-run] [--context-dir path/] [--skip-render]`

**Change classifications:** CORRECT (fix wrong data), ADD (net-new intelligence), REMOVE (no longer true), AMEND (modify nuance), CONSTRAINT (business guardrail), GAP (targets missing file/section).

**Dependencies:**
- Hard: at least one context file, `company-identity.md` confidence >= 2
- Soft: L1 files (feedback targeting missing L1 files flagged as research gap)

**Key behaviors:**
- Client data is highest authority (client > tier-0 > research)
- Corrections are upgrades (replacing wrong with right does not lower confidence)
- Proof point IDs are immutable (never reuse, never renumber)
- Fundamental wrongness detection: warns if 5+ corrections target core identity
- Surgical edits only (change affected lines, preserve everything else)

**Runtime:** ~20-40K tokens. ~3-8 minutes.

### voice-inference (v1.0.1)
Brand voice analysis from website content. Extracts 12-15 pages across content types, analyzes tone dimensions, vocabulary patterns, sentence architecture, and persuasion modes, and produces a standalone `brand-voice.md` L1 context file. Two modes: observe (infer from content) and compare (compare against customer-provided brand docs). Does not require positioning-framework to have been run first.

**Invocation:** `/voice-inference <url> [--mode observe|compare] [--docs <path-or-url>...] [--guide <path-or-url>]`

**Agents:** 2 sequential (Extract + Analyze). Both Opus.

**Dependencies:**
- Hard: URL provided
- Soft: `competitive-landscape.md` (enriches Avoided Vocabulary), `company-identity.md` (enriches page discovery)

**Outputs:**
- L1 context: brand-voice.md (tone spectrum, vocabulary fingerprint, example library, consistency map, voice rules)
- Operational: _voice-extractions.md (raw page extractions)

**Runtime:** ~80-120K tokens. ~10-15 minutes.

### live-capture (v0.2.1, in active development)
Live-page structural and copy capture. Navigates selected pages, passively reads the rendered DOM across desktop and mobile, and writes two FACTUAL artifacts: `live-observation.md` (page structure) and `live-copy.md` (verbatim copy). Facts and two permitted mechanical derivations only; no judgments (consumers compute the interpretation). Reuses experiment-mockup's browser stack (Chrome DevTools / Playwright / static fallback, with the configured-but-broken = STOP rule) and positioning-framework's dual-mode KB write contract.

**Invocation:** `/live-capture <url> [--scope <slug>] [--no-kb] [--static] [--urls <comma-list>] [--viewports desktop,mobile]`

**Page selection:** Section 8 leverage algorithm (`scripts/page_select.py`): traffic, conversion-gap-below-benchmark, bounce, device-gap weighted sum; two lanes (conversion by leverage, content by organic sessions); always-capture homepage + positive-control; no-profile nav-crawl fallback (confidence capped at 3).

**Dependencies:**
- Hard: URL provided, a browser MCP (or `--static`)
- Soft: `performance-profile.md` / `silver-performance-analysis` (page selection; nav-crawl fallback when absent)

**Outputs:**
- Legacy: L0 `live-observation.md` + `live-copy.md` in `.claude/context/`
- KB mode: bronze (`bronze-note-capture`, `bronze-research-extraction`) + silver enrichment `silver-structural-observation` at `reference/cro-{scope}/live-structure.md`

**Note:** KB-mode silver enrichment depends on the client type skill registering `silver-structural-observation` (Phase A Change B). Legacy mode is independent. Authoritative artifact schema inlined in `phases/write.md`; reference copies in `schemas/`.

### experiment-mockup (v1.4.1)
Visual mockup generator for proposed experiment changes. Takes a hypothesis from `experiment-roadmap.md`, navigates to the target page, injects the proposed change styled to match the site's design, iterates with the user in real time, then captures the approved state as a standalone HTML artifact with CRO placement rationale. Three browser modes: live (Chrome DevTools MCP, interactive, ~90% visual fidelity), playwright (Playwright MCP, screenshot-based iteration), and static (HTML extraction fallback, non-interactive, ~70% fidelity).

**Invocation:** `/experiment-mockup <hypothesis-number> [--url <override-url>] [--static] [--scope <slug>] [--no-kb]`

**Phases:**
- Phase 1 (Inspect, live only): Navigate to page, locate target section, extract computed styles via DevTools MCP
- Phase 2 (Inject, live only): Build content block, inject into live DOM, iterate with user on placement/styling/copy
- Phase 3 (Capture, live only): Screenshot viewport, extract section HTML, build standalone mockup.html
- Phase 4 (Annotate, both modes): Write placement.md with CRO rationale, attention strategy, implementation notes
- Static Build (fallback): Fetch page HTML via web-extract pipeline, parse CSS, build mockup.html

**Dependencies:**
- Hard: the experiment roadmap (produced by hypothesis-generator)
- Soft: Chrome DevTools MCP (degrades to static mode if unavailable)
- Does NOT read L0/L1 context files (hypothesis is the single source of truth)

**Dual-mode I/O:** mode resolution mirrors hypothesis-generator and render-program-site (`--scope` required in KB mode, `--no-kb` forces legacy, failed detection falls back to legacy loudly). Legacy mode reads `.claude/deliverables/experiment-roadmap.md` and writes under `.claude/deliverables/experiments/`. KB mode reads `{kb_root}/deliverables/{scope}-experiment-roadmap.md` and writes under `{kb_root}/deliverables/experiments/` (co-located so render-program-site resolves the mockups; not a KB artifact, no `kb_layer`).

**Outputs (dual-mode):** legacy `.claude/deliverables/experiments/<slug>/`; KB mode `{kb_root}/deliverables/experiments/<slug>/` (mockup.html, placement.md, mockup-screenshot.png)

**Runtime:** ~40-80K tokens (live, variable with iteration), ~30-50K tokens (static).

### render-program-site (v0.5.1)
Renders a unified two-altitude program site from hypothesis-generator's two gold roadmaps, read in place: the strategic roadmap (`gold-strategic-roadmap`, program-level bets) and the tactical roadmap (`gold-experiment-roadmap`, page-level tests). It derives each item's id, key, title, tier, ICE, and page from the gold structure and authors nothing into those artifacts; the one net-new input is a small render-owned sidecar (`{scope}-program-edges.md`) carrying the cross-altitude edge binding plus the gate-classification fields, keyed by gold `**Key:**`. Produces a hub page plus one spoke per bet (`sb-NN.html`) and one per test (`p-NN.html`), with the cross-altitude edge contract enforced as a hard build gate (mechanism compatibility, dangling targets, executor-status derivation, sidecar-vs-gold version lock, binding completeness) that fails closed with a non-zero exit. An optional third input, an account-program deliverable (`--account-program`), renders a distinct off-store altitude: account plays carry no ICE, no on-page mechanism, and no cross-altitude edge, so they bypass the edge gate and the portfolio map and are validated by a separate account-binding leg (>=1 play, unique ordinals, required labels); the hub gains an `#account-program` section and one `ap-NN.html` spoke per play. When no account program is supplied the render is byte-identical to a two-altitude site. The strategic roadmap's optional `## Measurement Foundation` section (hypothesis-generator's Strategic Roadmap Output Format) renders as an unscored `#measurement-foundation` hub section: keyless prerequisite entries with no ICE, no tier, no map presence, no cross-altitude edges, and no spokes; they need no sidecar entries and are excluded from every sidecar-related gate check (a sidecar edge that targets one fails as a dangling target), and a roadmap without the section renders byte-identically. Hybrid skill: a deterministic generator (`scripts/render_site.py`) owns the gate, the Impact-by-Ease portfolio map, edge typing, and all chrome and data-bound structure, so the strategic layer cannot drift; a scoped LLM pass then curates the spoke prose slots and runs a humanizer pass. Replaces the former roadmap-presentation skill. No web research, no `.claude/context/` writes.

**Invocation:** `/render-program-site [<strategic-md> <tactical-md>] [--edges <path>] [--account-program <path>] [--scope <slug>] [--no-kb] [--out <dir>]`.

**Phases:** (1) resolve three inputs + mode (HARD STOP on a missing sidecar); (2) run `render_site.py` to validate the gate and emit all structure/chrome with labeled prose slots; (3) LLM curation pass mapping gold body sections -> prose slots (drop-list applied); (4) humanizer pass over authored prose; (5) write site + completion message (mode, bet/test counts, per-test mockup status, gate result, deferred-hosting note).

**Dependencies:**
- Hard: the two gold roadmaps (strategic + tactical) read in place, plus the edge sidecar; the sidecar's `strategic_version`/`tactical_version` must match the live gold roadmaps' frontmatter `version`
- Soft: per-test mockup artifacts from experiment-mockup (placeholder frames when absent), referenced via each sidecar test's `mockup` block
- Does NOT read L0/L1 context files; the two gold roadmaps + the edge sidecar are the single source of truth

**Outputs (dual-mode):** legacy `.claude/deliverables/program-site/`; KB mode `{kb_root}/deliverables/{scope}-program-site/` (`styles.css`, `site.js`, `index.html`, `sb-NN.html`, `p-NN.html`, `ap-NN.html` when an account program is supplied, `mockups/<id>/`). No `kb_layer` frontmatter (derived view). Hosting/deploy deferred to a follow-up (v1 non-goal).

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

## README Sync Rule

When a skill is added, removed, or has its version changed in `skills/`, update `README.md` to match:

1. **Skills table:** Add or remove the skill row. Each skill name must link to its `SKILL.md` file using the format `[skill-name](skills/skill-name/SKILL.md)`. Include the version from the skill's YAML frontmatter and a one-line description.
2. **Skill count:** If the README mentions a skill count anywhere, update it to reflect the current number of skills in `skills/`.
3. **Invocation examples:** If the new skill has a user-facing invocation (e.g., `/landing-page-generator`), add it to the "Run a skill" examples in the Quick Start section.

This rule is mechanically enforced: `scripts/registry_check.py` runs in CI and fails the PR on any frontmatter/README/CLAUDE.md/marketplace/changelog mismatch. Run it locally before pushing.
