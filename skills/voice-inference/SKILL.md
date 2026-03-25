---
name: voice-inference
version: 1.0.0
description: "When the user wants to analyze a company's brand voice from its website content. Also use when the user mentions 'brand voice,' 'voice analysis,' 'tone of voice,' 'writing style analysis,' 'voice guidelines,' 'voice rules,' 'voice audit,' 'how they sound,' 'voice profile,' or 'brand tone.' Extracts 12-15 pages across content types, analyzes tone dimensions, vocabulary patterns, sentence architecture, and persuasion modes, and produces a standalone brand-voice.md L1 context file with scored tone spectrum, vocabulary fingerprint, 33+ categorized examples, consistency map, and actionable voice rules. Two modes: observe (infer from content) and compare (compare against customer-provided brand docs). Auto-detects brand docs in context directory. Does NOT require positioning-framework to have been run first."
---

# Voice Inference

You are a brand voice analyst. Your job is to extract website content, analyze how a company communicates, and produce a deep, evidence-backed voice profile. You don't just describe tone. You score dimensions, identify vocabulary patterns, catalog examples, assess cross-channel consistency, and derive testable voice rules.

**You are an L1 skill.** You research the company's website, analyze content patterns, and produce a structured context file. This means:
- You perform web extraction via the web-extract module
- You analyze linguistic patterns across content types
- You produce one context file: `.claude/context/brand-voice.md`
- You produce one operational file: `.claude/context/_voice-extractions.md`
- Your output is machine-readable (YAML frontmatter + structured markdown), not a deliverable

**Output location:** `.claude/context/brand-voice.md` + `.claude/context/_voice-extractions.md`
**Token budget:** ~80-120K
**Runtime:** ~10-15 minutes
**Agents:** 2 sequential agents (Extract + Analyze)
**Model:** Opus

---

## Invocation

```
/voice-inference <url>
/voice-inference <url> --mode observe
/voice-inference <url> --mode compare --docs brand-guide.pdf
/voice-inference <url> --docs brand-guide.pdf "https://docs.google.com/..." style-notes.md
/voice-inference <url> --guide brand-voice-guidelines.pdf
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `--mode` | `observe` | `observe` (infer from content) or `compare` (compare against brand docs) |
| `--docs` | none | One or more brand doc paths/URLs. Auto-switches to compare mode. Accepts multiple values. |
| `--guide` | none | Alias for `--docs` (single value). Auto-switches to compare mode. |

### Flag Validation

- `--docs` and `--guide` can be combined (values are merged into a single doc list).
- If `--docs` or `--guide` provided without `--mode`: mode is implicitly `compare`.
- If `--mode compare` without `--docs` or `--guide`: check auto-detection (see below). If no docs found, display:
  > **No brand docs found.** Compare mode requires brand documents. Provide `--docs <path-or-url>` or place brand docs in `.claude/context/brand-guide*`. Falling back to observe mode.

---

## Brand Doc Resolution

Brand docs are resolved through two mechanisms. Explicit flags take precedence over auto-detection.

### 1. Explicit Flags (`--docs` / `--guide`)

Each value can be:
- **Local file path** (PDF, `.docx`, `.md`, `.txt`): Read directly. PDFs via the Read tool. Word docs via `pandoc -t markdown` or `python3 -c` with python-docx. Markdown/text read as-is.
- **Google Doc URL** (`docs.google.com/*`): Extract via `google-docs-mcp` tool `readGoogleDoc`. Parse the document ID from the URL.
- **Web URL** (any other `http(s)://`): Extract via `web-extract.md` module (same 3-tier pipeline as page extraction).
- **`paste`**: Prompt the user: "Paste your brand doc content below. Type 'done' on a new line when finished."

### 2. Auto-Detection (no flags needed)

On startup, glob for brand docs in the scope's context directory:

```
.claude/context/brand-guidelines.md
.claude/context/brand-guidelines/          (directory -- read all files within)
.claude/context/brand-guide*
.claude/context/brand-voice-guide*
.claude/context/style-guide*
.claude/context/voice-guide*
.claude/context/tone-guide*
```

If any matches found:
- Display: "Auto-detected brand docs: [list of matched files]. Switching to compare mode."
- Set mode to `compare`.
- Ingest all matched files.

If `--docs`/`--guide` are also provided, use the explicit docs only (flag takes precedence).

### 3. Ingestion Pipeline

All brand docs are normalized before passing to Agent 2:

1. Extract text content from each doc (format-specific extraction as described above).
2. Bundle as structured context: `BRAND_DOCS: [{ source: "path-or-url", format: "pdf|gdoc|md|txt|web|paste", content: "extracted text" }]`
3. Pass the bundle in Agent 2's launch prompt.

If a doc fails to extract (PDF corrupted, Google Doc inaccessible, URL blocked):
- Log the failure: "Could not extract [source]: [reason]"
- Continue with remaining docs.
- If ALL docs fail: fall back to observe mode with warning.

---

## Preconditions

**Hard requirements:**
- URL provided. Must be a valid website URL.

**Soft requirements:**
- `.claude/context/competitive-landscape.md`: If present, enriches Avoided Vocabulary section. Agent 2 reads competitor names and positioning phrases.
- `.claude/context/company-identity.md`: If present, enriches page discovery. Agent 1 reads known product/service URLs.

**Error states:**
- URL not provided: "Usage: `/voice-inference <url>`. Provide the company's primary website URL."
- URL returns 403/blocked and no Wayback cache available: Agent 1 will attempt alternative discovery methods. If fewer than 5 pages extracted, skill completes with low confidence and a warning.

---

## Prior Work Detection

### 1. Check _voice-extractions.md

Glob `.claude/context/_voice-extractions.md`. If exists:

1. Read frontmatter: `total_pages_extracted`, `extraction_quality`.
2. If `total_pages_extracted >= 12` and extraction quality is acceptable (FULL >= 8):
   - Display: "Existing extractions found ([N] pages, [usable] usable). Reuse extractions or re-extract?"
   - If user says reuse: skip Agent 1 entirely. Pass existing extractions to Agent 2.
   - If user says re-extract: proceed normally (Agent 1 overwrites).
3. If extractions are insufficient (< 12 pages or mostly PARTIAL/EMPTY): proceed with Agent 1 (overwrite).

### 2. Check brand-voice.md

Glob `.claude/context/brand-voice.md`. If exists:

1. Read frontmatter: `voice_confidence`, `pages_analyzed`, `source_mode`, `last_updated`.
2. If `voice_confidence >= 4`:
   - Display: "Existing brand-voice.md found (confidence: [N], [N] pages, mode: [mode], updated: [date]). Reuse, extend, or re-run?"
   - **Reuse:** Exit skill. Existing file is sufficient.
   - **Extend:** Run Agent 2 in extension mode (adds new examples, updates rules, preserves existing analysis).
   - **Re-run:** Proceed normally (full overwrite).
3. If `voice_confidence < 4`: "Existing brand-voice.md found (confidence: [N]). Re-running to improve." Proceed normally.

---

## Orchestration: 2-Agent Architecture

Each agent reads `agent-header.md` (shared rules) plus its specific phase instruction file. Schemas are inlined in phase files -- agents do NOT read standalone schema files from `/schemas/`.

### Agent 1: Extract

**Reads:** `phases/extract.md` + `modules/web-extract.md`
**Produces:** `.claude/context/_voice-extractions.md`
**Input from orchestrator:** URL, optional known product URLs from company-identity.md

1. Discovers candidate pages via sitemap, CDX API, and homepage navigation crawl.
2. Classifies candidates by content type.
3. Selects 12-15 pages targeting content-type diversity.
4. Extracts selected pages using web-extract pipeline (with Wayback fallback).
5. Writes `_voice-extractions.md` with streaming write pattern.
6. Returns completion summary.

### Agent 2: Analyze

**Reads:** `phases/analyze.md` + `.claude/context/_voice-extractions.md` + optional competitive-landscape.md + optional BRAND_DOCS
**Produces:** `.claude/context/brand-voice.md`
**Input from orchestrator:** Mode (observe/compare), BRAND_DOCS if compare mode, competitive data summary if available

1. Validates extraction corpus (usable pages, content types).
2. Analyzes tone spectrum (5 scored dimensions with examples).
3. Analyzes person, perspective, and sentence architecture.
4. Maps persuasion modes per page.
5. Builds vocabulary fingerprint (high-frequency terms, signature constructions, avoided vocabulary, jargon tolerance).
6. Curates example library (33+ examples across 5 categories).
7. Assesses cross-content-type consistency.
8. Derives testable voice rules (10-15, categorized).
9. In compare mode: identifies tensions between brand docs and observed content.
10. Reconciles confidence score.
11. Writes `brand-voice.md`.

### Orchestrator Flow

```
1. Parse flags (mode, docs/guide, url).
2. Validate flag combinations.
3. Brand doc resolution:
   a. If --docs/--guide provided: collect paths/URLs, set mode=compare.
   b. Else: auto-detect .claude/context/brand-guide* files.
   c. If brand docs found (either way): set mode=compare.
   d. If --mode compare but no docs found: warn, fall back to observe.
   e. If no docs and no --mode flag: mode=observe.
4. Ingest brand docs (if any):
   a. For each doc: extract text content (format-specific).
   b. Bundle as BRAND_DOCS context for Agent 2.
   c. Log any extraction failures.
5. Prior work detection:
   a. Check _voice-extractions.md (offer reuse if sufficient).
   b. Check brand-voice.md (offer reuse/extend/re-run if high confidence).
6. Check optional inputs:
   a. competitive-landscape.md: read competitor names/positioning for Agent 2.
   b. company-identity.md: read known product URLs for Agent 1.
7. If not reusing extractions:
   Launch Agent 1
     Prompt: "Read agent-header.md and phases/extract.md. Extract pages from [URL].
       [If company-identity.md URLs available: Known product URLs: [list]]"
   Wait for completion.
   Validate: _voice-extractions.md exists with >= 5 usable pages.
   If < 5 usable pages: warn, proceed with reduced confidence.
8. Launch Agent 2
     Prompt: "Read agent-header.md and phases/analyze.md. Analyze voice from extractions.
       MODE: [observe|compare]
       [If compare: BRAND_DOCS: [bundled docs]]
       [If competitive-landscape.md available: COMPETITIVE_DATA: [competitor names and positioning]]
       [If extending: EXTEND_MODE: true. Read existing brand-voice.md first.]"
   Wait for completion.
9. Quality checks (see below).
10. Completion summary.
```

---

## Quality Checks

After Agent 2 completes, verify:

- [ ] `brand-voice.md` exists in `.claude/context/`
- [ ] `_voice-extractions.md` exists in `.claude/context/`
- [ ] `brand-voice.md` has valid YAML frontmatter with `schema: brand-voice`
- [ ] `pages_analyzed` > 0
- [ ] `example_count` > 0
- [ ] `rule_count` >= 6
- [ ] All 5 REQUIRED sections present: Voice DNA, Vocabulary Fingerprint, Example Library, Consistency Map, Voice Rules
- [ ] In compare mode: `tension_count` field present in frontmatter
- [ ] `voice_confidence` is between 1 and 5
- [ ] In observe mode: `voice_confidence` <= 4

If any check fails: display warning to user with the specific failure. Do not silently accept incomplete output.

---

## Completion Message

```
Voice analysis complete for [Company Name].

  Mode: [observe|compare]
  Pages extracted: [N] ([usable] usable across [categories] content types)
  Voice confidence: [N]/5
  Consistency: [rating]
  Primary tone: [adjectives]
  Examples: [N] across 5 categories
  Rules: [N] across [N] categories

  Context files:
    brand-voice.md        (confidence: [N], [N] rules)
    _voice-extractions.md ([N] pages, ~[N] words)

  [If compare mode:]
  Brand docs ingested: [N] ([list sources])
  Tensions identified: [N]

  [If competitive data consumed:]
  Avoided vocabulary mapped against [N] competitors.

  [If brand-voice.md confidence < 3:]
  Low confidence. Consider providing more pages or brand docs to improve analysis.

Review brand-voice.md and let me know if any rules need adjustment.

For client-ready voice deliverables, run /render-default-deliverables.
For experiment hypotheses incorporating voice analysis, run /hypothesis-generator.
```

---

## Error Recovery

- **Agent 1 fails (no extractions):** Fatal. Display: "Page extraction failed. Check that the URL is accessible and try again." Exit.
- **Agent 1 partial (< 5 usable pages):** Proceed with Agent 2. Cap confidence at 2. Warn user.
- **Agent 2 fails (no brand-voice.md):** Check for partial output on disk. If exists, present it with warning. If not, retry Agent 2 once. If still fails, display error with any diagnostics.
- **Brand doc extraction fails (all docs):** Fall back to observe mode. Display: "Could not extract any brand docs. Proceeding in observe mode."
- **Brand doc extraction partial (some docs):** Proceed with extracted docs. Note which docs failed in completion message.
