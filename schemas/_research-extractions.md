---
type: schema-reference
artifact: _research-extractions.md
layer: operational
written_by: Agent 1 (research phase)
consumed_by: Agents 2, 3, 4 (selectively)
---

# Research Extractions Schema

<!-- v1.1: Added ## VOC Extractions section with 6-lens extraction framework, source reliability tags, segment signals -->

Raw page extractions from Agent 1's research phase. Operational artifact (underscore-prefixed). Overwritten on each run. NOT considered prior work for depth evaluation.

Authoritative spec: `skills/positioning-framework/phases/research.md`

## Frontmatter

| Field | Type | Description |
|-------|------|-------------|
| schema | string | Always `research-extractions` |
| schema_version | string | `"1.1"` |
| generated_by | string | `"positioning-framework/research"` |
| last_updated | date | ISO date of generation |
| company | string | Company name |
| url | string | Primary company URL |
| depth | string | `quick`, `standard`, or `deep` |
| total_pages | integer | Number of extraction entries in file body |
| total_words | integer | Approximate total word count across all entries |

## Index Table

Immediately after frontmatter. One row per extraction entry.

| Column | Description |
|--------|-------------|
| # | Entry number (matches `## N.` section header) |
| Page Type | Homepage, Features, Pricing, About, Case Study, FAQ, Blog, Competitor, Reddit, etc. |
| URL | Full URL fetched |
| Tag | Extraction quality tag: [FULL], [PARTIAL] |
| Words | Approximate word count for this entry |
| Key Content | Brief summary of what's in the entry (one line) |

Only pages tagged [FULL] or [PARTIAL] get entries. Pages tagged [EMPTY], [EMPTY:SPA], or [EMPTY:BLOCKED] are logged in `_fetch-registry.md` only.

## Per-Page Entry Structure

Each entry is a level-2 heading:

    ## N. [Page Type]: [URL]
    <!-- tag: [TAG] | words: NNN | fetched_by: Agent 1 -->

    ### Structured Extraction
    (Homepage only. Uses the Structured Extraction Template from research.md:
    HERO SECTION with H1, Subhead, CTA(s), Format; NAV TAGLINES; META with
    title and meta description.)

    ### Key Content Sections
    Main body content organized by page sections. Preserves headings, bullet
    lists, and content hierarchy. Rendering artifacts stripped.

## VOC Extractions Entry Structure

A separate `## VOC Extractions` section follows page content entries. Each entry follows this structure:

### [SOURCE_URL_OR_IDENTIFIER]
- **Source Type:** G2 review | Reddit post | Forum thread | Interview transcript | Support ticket | etc.
- **Reliability:** Very High | High | Medium-High | Medium | Low-Medium (per `modules/voc-extraction.md` Source Reliability table)
- **Segment Signals:** Role, Size, Industry, Use Case -- or `[SEGMENT: inferred-unknown]`
- **Date:** approximate date if available

**Six-Lens Extraction (include populated lenses only):**
- Jobs to Be Done (functional/emotional/social)
- Pain Points (tagged HIGH/MEDIUM/LOW intensity)
- Trigger Events
- Desired Outcomes
- Language/Vocabulary (verbatim with quotation marks)
- Alternatives Considered

**Money Quotes:** Vivid verbatim quotes marked with `[MONEY QUOTE]` tag.

VOC entries are written by Agent 1 (Tier 1C review sites, Tier 2 Reddit/forums) and Agent 2 (competitor review sources). Entry format defined in `modules/voc-extraction.md`.

## Content Rules

### Always strip (rendering artifacts, not content):
- Nav/header/footer chrome (identical across pages, zero positioning signal)
- Animated counter widget artifacts (JS counter digit sequences like "0 1 2 3 4 5 6 7 8 9 . , + % b $"). Preserve only the final displayed value if identifiable. Otherwise note "[animated stat]" as placeholder.
- Duplicate carousel/slider content (keep first occurrence, remove duplicates)
- Boilerplate (newsletter signup, cookie consent, social links)

### Always deduplicate across pages:
- Same testimonial/content block on multiple pages: include once (first occurrence), write "See entry #[N]" in subsequent pages.

### Always preserve verbatim (never paraphrase, summarize, or truncate):
- H1, subheads, CTAs, testimonial quotes
- Pricing tier names, feature gate labels
- FAQ questions and answers
- Case study metrics and before/after statements

### No word budget
No per-page or per-file word limits. File size is bounded by page-count limits, not content trimming. Downstream agents read selectively by page type.

## Page-Count Limits

| Depth | Max Extraction Entries |
|-------|----------------------|
| Quick | 7 |
| Standard | 18 |
| Deep | 30 |

Pages beyond the cap are logged in `_fetch-registry.md` but do not get extraction entries.

## Sanity-Check Ceilings (warning, not trimming trigger)

| Depth | Warning Ceiling |
|-------|----------------|
| Quick | 8K words |
| Standard | 20K words |
| Deep | 35K words |

If exceeded, orchestrator logs warning. Agent 1 does NOT trim content.

## Extractions Validation Check

Every agent consuming this file runs this check before reading content:

1. **Frontmatter check:** File has valid YAML frontmatter with `schema: research-extractions` and `total_pages` field.
   - If frontmatter exists and is valid: use the Index table for selective reads.
   - If frontmatter is missing (streaming crash before index was written): scan for `## N. [Page Type]` headers to discover available entries. Proceed with what exists.
   - If file is entirely absent or empty: treat as absent.
2. **Entry body spot-check:** For each entry the agent wants to read, verify the corresponding `## N. [Page Type]` section exists in the file body. If missing: skip that entry, note in research log: "Extraction entry #N missing body, skipping."

## Write Pattern

Streaming (not batch). See `phases/research.md` for authoritative write sequence.

**Per-page (inside fetch loop):**
1. Fetch page, tag extraction quality
2. Append URL to `_fetch-registry.md`
3. Strip rendering artifacts from extracted content
4. Append page entry to `_research-extractions.md`
5. Release raw content from working memory

**After all pages:**
6. Read back all entries, build index from what exists, rewrite complete file (frontmatter + index + all entries)
7. Build `company-identity.md` (L0)

## Graceful Degradation

- Truncated file (crash mid-stream): entries on disk are complete. Consuming agents use what exists, skip what's missing, log what they skipped.
- File with entries but no index (crash after entries, before rewrite): consuming agents scan `## N.` headers instead of reading index.
- Absent file: all consuming agents proceed without it (current behavior).

## Cross-Reference

- Fetch index: `_fetch-registry.md` (records all fetches; extractions file only records entries up to page-count cap)
- Structured output: `company-identity.md` (L0, built from these extractions)
