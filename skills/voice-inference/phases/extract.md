# Phase: Extract

**Covers:** Page discovery, content-type classification, page selection, and web extraction for voice analysis.

**Produces:** `.claude/context/_voice-extractions.md` (operational file, overwritten on each run)

**Reads:** `modules/web-extract.md` (extraction pipeline), optional `.claude/context/company-identity.md` (known product URLs)

**Shared Agent Rules:** Read `agent-header.md` first. This file second.

---

## Required Inputs

- **URL:** The target company's primary website URL. Provided in the agent launch prompt.
- **web-extract module:** The three-tier extraction pipeline. Follow its tier fallback rules exactly.

## Optional Inputs

- **company-identity.md:** If available, read the Services/Capabilities section for known product page URLs. Add them to the candidate list with category `product` and priority 3.
- **Known product URLs from orchestrator:** The orchestrator may pass additional URLs from company-identity.md. Add them to the candidate list.

---

## Step 1: Page Discovery

Run all discovery methods. Merge and deduplicate results by normalized URL (strip trailing slashes, fragments, common query params like `utm_*`).

### 1a. Sitemap Crawl

```bash
curl -s --max-time 10 "[base_url]/sitemap.xml"
```

If sitemap exists: parse `<loc>` entries. If `sitemap_index.xml`, follow up to 3 child sitemaps. Extract all URLs under the target domain.

If sitemap returns 404/403/empty: skip. This is not an error.

### 1b. Wayback CDX API

```bash
curl -s --max-time 15 "https://web.archive.org/cdx/search/cdx?url=[domain]/*&output=json&fl=original,timestamp,statuscode&collapse=urlkey&limit=200&filter=statuscode:200"
```

Parse JSON response. Deduplicate by URL key. Sort by most recent timestamp. This catches:
- Pages removed from the live site but still cached
- Pages behind WAF/bot protection (403 on live, available via Wayback)
- Historical pages showing voice evolution

### 1c. Homepage Navigation Crawl

Extract the homepage using the `web-extract.md` pipeline. Parse all internal links from the extracted content. These represent actively promoted pages. Mark them as high-priority candidates.

### 1d. Optional: company-identity.md URLs

If `.claude/context/company-identity.md` exists, scan for URLs in the Services, Capabilities, and Products sections. Add each as a candidate with its likely category.

---

## Step 2: Classify Candidates

For each discovered URL, classify by content type using URL patterns:

| URL Pattern | Category | Base Priority |
|------------|----------|---------------|
| `/` or `/en` (root) | landing | 1 (always include) |
| `/solutions/*`, `/products/*`, `/platform/*`, `/features/*` | product | 3 |
| `/campaigns/*`, `/landing/*`, `/lp/*` | landing | 2 |
| `/blog/*`, `/news/*`, `/insights/*`, `/research/*`, `/resources/*` | thought_leadership | 5 |
| `/case-study/*`, `/case-studies/*`, `/customers/*`, `/success-stories/*` | case_study | 4 |
| `/about/*`, `/company/*`, `/who-we-are/*`, `/info/about*` | company | 3 |
| `/careers/*`, `/jobs/*` | other | 6 |
| `/pricing/*` | product | 3 |
| Everything else | other | 6 |

Priority 1 = must include, 6 = include only if filling gaps.

If URL patterns are ambiguous (e.g., `/en/solutions/credit-risk-solutions` could be product or landing), prefer the more specific category. When in doubt, classify as the category with fewer candidates to improve diversity.

---

## Step 3: Select Pages

**Target: 12-15 pages.** Content-type diversity is the primary selection criterion.

### Category Targets

| Category | Target | Min | Max |
|----------|--------|-----|-----|
| landing | 3-4 | 2 | 5 |
| product | 3-4 | 2 | 5 |
| thought_leadership | 2-3 | 1 | 4 |
| case_study | 1-2 | 0 | 3 |
| company | 1-2 | 0 | 2 |
| blog | 1-2 | 0 | 2 |
| other | 0-1 | 0 | 1 |

### Selection Algorithm

1. **Always include the homepage** (landing, priority 1).
2. **Fill each category to its minimum** from highest-priority candidates within that category.
3. **Fill remaining slots** (up to 15 total) by round-robin across categories that haven't hit their max. Within each category, prefer higher-priority candidates.
4. **If a category has 0 candidates:** Skip it. Redistribute its target slots to categories with candidates above their minimum.
5. **Prefer URL diversity within a category.** Don't extract 4 product pages that are all sub-pages of the same parent. Spread across different product areas.
6. **If total candidates < 12:** Extract all candidates. Note the limited corpus in the frontmatter notes field.

---

## Step 4: Extract Pages

For each selected page, run the `web-extract.md` three-tier pipeline.

### Extraction Order

1. Try markdown.new first (Tier 0).
2. If markdown.new returns < 100 words or fails: try curl + HTMLParser (Tier 1).
3. If Tier 1 returns < 100 words: try WebFetch (Tier 2).
4. If all tiers fail: log the page as skipped with reason.

### Wayback Machine Fallback

When live site extraction returns empty/blocked content for a URL:
1. Check CDX API results for cached versions of that URL.
2. If cached version exists with timestamp within the last 2 years:
   ```bash
   curl -s --max-time 10 "https://markdown.new/https://web.archive.org/web/[timestamp]/[url]"
   ```
3. Tag the extraction method as `wayback` in the per-page metadata.
4. Note in the extraction_note: "Wayback Machine used as fallback for blocked pages."

### Content Preservation Rules (Voice-Specific)

These rules differ from `_research-extractions.md`. Voice analysis has different needs than positioning research.

**Always preserve verbatim:**
- All body copy (headlines, subheads, body paragraphs)
- CTAs, button text, form labels, microcopy
- Repeated marketing blocks across pages (template discipline is a voice signal)
- Testimonial quotes and proof language
- Error messages, empty states, helper text (if visible)

**Always strip:**
- Nav menus, header navigation, breadcrumbs
- Footer links (but preserve footer marketing copy if present)
- Cookie banners, consent dialogs
- Social media icon links, share buttons
- Script/style blocks, SVG, JSON-LD, schema.org markup
- Search bars, login/logout widgets

**Critical difference from _research-extractions.md:**
- Do NOT deduplicate cross-page repeated content. If "You're one step closer to unlocking our suite..." appears on 4 pages, preserve all 4 occurrences. Repetition patterns are voice evidence.
- Do NOT use the Structured Extraction Template (that's positioning-framework specific). Extract all pages as raw content with heading hierarchy preserved.

### Quality Tagging

Tag each page extraction:
- `[FULL]` -- 100+ words of body content extracted
- `[PARTIAL]` -- 30-99 words, or content appears truncated
- `[CHROME-ONLY]` -- Only navigation/footer chrome extracted, no body content. Mark as unusable.
- `[EMPTY]` -- No content extracted. Mark as unusable.

After extraction, count usable pages (FULL + PARTIAL). If fewer than 5 usable pages, note this in frontmatter. The orchestrator will cap confidence at 2.

---

## Step 5: Write Output

### Write Pattern

Streaming write (same pattern as `_research-extractions.md`):

**Per-page (during extraction loop):**
1. Extract page content
2. Tag extraction quality
3. Append page entry to `_voice-extractions.md`

**After all pages:**
4. Read back all entries
5. Build frontmatter + index table
6. Rewrite complete file (frontmatter + index + all entries)

### Output Structure

```markdown
---
schema: voice-extractions
schema_version: "1.0"
generated_by: "voice-inference/extract"
last_updated: "[ISO date]"
company: "[Company Name]"
url: "[base URL]"

total_pages_discovered: [N]
total_pages_extracted: [N]
categories:
  landing: [N]
  product: [N]
  thought_leadership: [N]
  case_study: [N]
  company: [N]
  blog: [N]
  other: [N]

discovery_sources:
  - sitemap              # only if sitemap was found
  - cdx_api              # only if CDX API returned results
  - homepage_navigation  # always (homepage is always extracted)
  - company_identity     # only if company-identity.md was consumed

skipped_pages:
  - url: "https://example.com/page"
    reason: "Returns 403; no Wayback cache available"

extraction_quality:
  FULL: [N]
  PARTIAL: [N]
  CHROME_ONLY: [N]
  EMPTY: [N]
extraction_method: "[primary method, fallback notes]"
extraction_note: "[any limitations, e.g., 'Navigation chrome stripped. Content verbatim.']"
---

# [Company Name]: Voice Extractions

Extracted: [N] pages, ~[N] words of body content.
Source: [primary extraction method] [fallback notes].

## Page Inventory

| # | URL | Category | Priority | Extracted | Tag | Words | Method |
|---|-----|----------|----------|-----------|-----|-------|--------|
| 1 | https://... | landing | 1 | Yes | [FULL] | 1510 | markdown.new |
| 2 | https://... | product | 3 | Yes | [FULL] | 890 | wayback |
...
| 40 | https://... | other | 6 | No | - | - | - |

## Extracted Pages

---

## Page 1: [URL]

**Category:** [category]
**Extraction:** [FULL|PARTIAL]
**Word Count:** [N]
**Method:** [markdown.new | wayback | curl | webfetch]

[Verbatim extracted content follows -- preserve markdown heading hierarchy]

---

## Page 2: [URL]
...
```

### Page Inventory Table

Include ALL discovered pages (extracted and not extracted). This gives Agent 2 visibility into what was available vs. what was selected. Pages not extracted have `-` in Tag/Words/Method columns.

---

## Graceful Degradation

- **Sitemap unavailable:** Proceed with CDX API + homepage navigation only. Note in discovery_sources.
- **CDX API unavailable:** Proceed with sitemap + homepage navigation only.
- **Live site blocks all automated access (403/Cloudflare):** Use Wayback Machine as primary extraction method. Note in extraction_method and extraction_note.
- **Fewer than 12 pages available:** Extract all available. Note limited corpus in frontmatter notes.
- **Fewer than 5 usable pages:** Complete extraction but note "LOW CORPUS WARNING" in extraction_note. Orchestrator will cap confidence at 2.
- **Single content type available:** Extract all pages of that type. Note in frontmatter. Consistency Map in brand-voice.md will be limited.

---

## Completion Summary

After writing `_voice-extractions.md`, return to the orchestrator:

```
Extraction complete.

Pages discovered: [N]
Pages extracted: [N] ([usable] usable)
Content types: [list of categories with counts]
Extraction method: [primary method]
[Any warnings about limited corpus, blocked access, etc.]

_voice-extractions.md written to .claude/context/
```
