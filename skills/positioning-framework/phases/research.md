# Research Phase

Instructions for the research agent. This file covers all research tiers for the positioning-framework skill. Read `agent-header.md` (shared agent rules) first, then this file plus your other phase file(s).

---

## Shared Agent Rules

**Shared agent rules** (Proof Point Protocol, Content Integrity Check, Confidence Rules) are in `agent-header.md`. Read that file first.

---

## Graceful Degradation

If you cannot complete all sections (context limits, repeated fetch failures, insufficient data):

1. **Prioritize REQUIRED sections.** Write them first. OPTIONAL sections can be omitted.
2. **Always write output to disk.** Partial output on disk is better than no output. Write what you have to `.claude/context/company-identity.md` even if incomplete.
3. **Mark incomplete sections with `[INCOMPLETE - reason]`.** E.g., `[INCOMPLETE - all review site fetches returned blocked/empty responses]`.
4. **Set confidence accordingly.** Incomplete sections should lower the overall confidence score.
5. **Never fail silently.** Your completion summary must list what was attempted, what succeeded, and what failed.

---

## CRITICAL: Content Extraction Integrity

NEVER invent, guess, or reconstruct page content that you could not directly extract from a WebFetch response. NEVER misattribute content from one page section (navigation, footer, sidebar) as content from another (hero, main content). Both fabrication AND misattribution cascade catastrophically through downstream agents and deliverables. This includes:
- Headlines, subheads, and hero copy
- CTA button text
- Pricing figures
- Testimonial quotes
- Feature descriptions
- Any text presented as "what the website currently says"

### Website Content Extraction Flow

For each URL, follow the three-tier extraction pipeline defined in `modules/web-extract.md`. The pipeline is:

1. **markdown.new (primary).** `curl -s --max-time 10 "https://markdown.new/$URL"`. Returns clean markdown. Handles SPAs natively.
2. **curl + HTMLParser (Fallback Tier 1).** The Python extractor in `modules/web-extract.md`. Falls through from markdown.new if <100 words or request failed.
3. **WebFetch (Fallback Tier 2, last resort).** Falls through from curl+HTMLParser if <100 words. Filter CSS noise before assessing word count.

Word count thresholds and quality tags are defined in `modules/web-extract.md`. The tags encode both the quality AND the extraction source:

| Tag | Source | Words |
|-----|--------|-------|
| `[FULL]` | markdown.new | 500+ |
| `[PARTIAL]` | markdown.new | 100-499 |
| `[FULL:CURL]` | curl + HTMLParser | 500+ |
| `[PARTIAL:CURL]` | curl + HTMLParser | 100-499 |
| `[PARTIAL:TOOL]` | WebFetch | 100+ |
| `[EMPTY:SPA]` | All failed | SPA detected |
| `[EMPTY:BLOCKED]` | All failed | Bot protection |

In ALL cases where extraction fails across all three tiers:
1. Note the URL in the Gaps section of company-identity.md
2. Do NOT fill in plausible-sounding copy as a substitute
3. Move on to the next page

The downstream impact of fabricated copy is catastrophic: experiments designed against non-existent baselines, executive summaries quoting copy the client has never seen, and total loss of credibility. A gap is always better than a fabrication.

---

## CRITICAL: Website Content Extraction Rules

The curl extractor returns plain text with `#`-`######` heading markers. WebFetch (fallback) returns page content as markdown. In both formats, navigation menus, dropdowns, and footer content appear BEFORE the main page content in the output. You must distinguish between navigation chrome and actual page content.

- `modules/voc-extraction.md` -- structured VOC extraction protocol. Apply to all Tier 1C and Tier 2 VOC sources.

### Document Structure Priority

1. **SKIP** all content that is clearly navigation: link-heavy sections at the top of the document, mega-menu dropdowns (lists of links with short taglines), header bars, footer sections, cookie banners.
2. **START** meaningful extraction from the main content area. Indicators of main content start:
   - A "Skip to content" link (content begins after it)
   - The first H1 that is NOT embedded in a dense list of navigation links
   - A clear transition from link-heavy text (nav) to prose-heavy text (content)
   - Content after breadcrumbs
3. **The homepage H1 is the first `#` (H1) heading in the main content area**, not the first H1-like text in the document. Navigation taglines, dropdown descriptions, and menu item subtitles are NOT the homepage headline, even if they sound like positioning statements.
4. **If the page has multiple H1s in the main content** (carousel, slider, rotating hero), extract ALL of them and note the format (e.g., "Carousel with 3 slides").

### Structured Extraction Template

For each page fetched, extract content using this structure. Do NOT freestyle-interpret the page.

**For the homepage:**

```
HERO SECTION (inside main content area, below navigation):
  H1: [exact text of first H1 in main content]
  Additional H1s: [if carousel/slider, list all]
  Subhead: [text immediately following the hero H1]
  CTA(s): [button/link text in hero area]
  Format: [Static / Carousel (N slides) / Video background / etc.]

NAV TAGLINES (inside navigation/menus -- for reference only, NOT hero copy):
  [list any taglines found in navigation dropdowns]

META:
  title: [contents of <title> tag]
  meta description: [contents of meta description]
```

**For other pages:**

```
PAGE: [URL]
  H1: [first H1 in main content]
  Key content: [summary of main sections]
```

### Cross-Check: H1 vs. Meta Title

After extracting the homepage H1, compare it against the page's `<title>` tag and meta description. If the extracted H1 has zero semantic overlap with the meta title but a nav tagline does, you likely grabbed nav text instead of the actual headline. Re-scan the page for the correct H1 in the main content area.

Example of a mismatch that signals wrong extraction:
- Extracted "H1": "Turn complex problems into clear solutions" (actually a nav dropdown tagline)
- Meta title: "Financial Consulting and Advisory Firm | Acme"
- These share no semantic overlap. The real H1 is probably further down in the document.

### Common Traps

- **Mega-menu taglines**: Navigation dropdowns often contain H3-level taglines that sound like positioning statements. These describe nav sections, not the page.
- **Sticky headers with slogans**: Some sites put a tagline in the sticky header bar. This is branding chrome, not the hero headline.
- **"Above the fold" assumption**: In extracted output (both curl and WebFetch), navigation content is literally above the hero content. Don't assume the first positioning-sounding text is the headline.

---

## Content Extraction Quality Tags

After every page fetch, tag the extraction using the quality tags defined in `modules/web-extract.md`. The tags encode extraction source and word count. Reference that file for the complete tag vocabulary and thresholds.

### Quick Reference

- `[FULL]` / `[FULL:CURL]` -- 500+ words. High confidence. Use content directly.
- `[PARTIAL]` / `[PARTIAL:CURL]` -- 100-499 words. Reduced confidence. Cross-reference with other sources.
- `[PARTIAL:TOOL]` -- 100+ words via WebFetch (last resort). Treat as `[PARTIAL]`.
- `[EMPTY:SPA]` -- JS-rendered SPA, no content extracted by any method.
- `[EMPTY:BLOCKED]` -- Bot protection blocked all extraction methods.
- `[EMPTY]` -- Content genuinely absent or all tools failed.

### [CACHED] - Possible stale content

This tag is research-specific (not part of the extraction pipeline). Apply it when:
- Page content contradicts other recent sources about the same company
- OR: Copyright date or "last updated" timestamp is 2+ years old
- OR: Content references products/features that other sources indicate have been deprecated

Treat as [PARTIAL]. Flag for user verification at checkpoint.

### Usage

Tag every page fetch in research notes:
"Fetched https://example.com/pricing [FULL] - 1,200 words, pricing tiers and feature comparison extracted."
"Fetched https://example.com/about [PARTIAL:CURL] - 340 words via curl fallback, team overview only."

Tags are internal to research. They do NOT appear in context files or deliverables. They inform how confidently the agent treats each source when building L0 sections.

### Impact on Confidence Scores
- Section built primarily from [FULL] or [FULL:CURL] sources: confidence 4-5
- Section built from mix of [FULL]/[FULL:CURL] and [PARTIAL]/[PARTIAL:CURL]: confidence 3-4
- Section built primarily from [PARTIAL]/[PARTIAL:CURL]/[PARTIAL:TOOL] sources: confidence 2-3
- Section dependent on [EMPTY] or [CACHED] sources: confidence 1-2, mark section as `[NEEDS CLIENT INPUT]`

---

## Fetch Registry

After completing all web fetches, write a fetch registry to `.claude/context/_fetch-registry.md`.

For each URL fetched during this phase:
1. Record the URL, your agent name (Agent 1), the extraction quality tag, word count, and a 1-2 sentence summary of key content extracted.
2. Include ALL fetches, including failed ones ([EMPTY] tags). Downstream agents need to know a URL was attempted and failed, not just what succeeded.
3. Write the registry BEFORE writing company-identity.md (consistent with write-before-checkpoint pattern).
4. If page is tagged [FULL] or [PARTIAL]: strip rendering artifacts and append extraction entry to `_research-extractions.md` (see Research Extractions Output above). Release raw content from working memory.

**Registry format:**

```markdown
# Fetch Registry
<!-- Auto-generated by positioning-framework. Do not edit manually. -->

## Fetches

| URL | Agent | Tag | Words | Key Content |
|-----|-------|-----|-------|-------------|
```

Each row: full URL, agent name, extraction quality tag ([FULL], [PARTIAL], [EMPTY]), approximate word count of extracted content, and 1-2 sentence summary of what was extracted.

**If a fetch registry already exists from a prior run:** Read it first during prior work detection. Extend rather than overwrite, consistent with context file prior work pattern.

### _fetch-registry.md Format

Write this file to `.claude/context/_fetch-registry.md` with the following structure:

**Frontmatter:**
```yaml
schema: fetch-registry
schema_version: "1.0"
generated_by: "positioning-framework/research"
last_updated: [current ISO date]
last_updated_by: "positioning-framework/research"
total_fetches: [row count]
```

**Body:** Markdown table with columns: URL, Agent, Tag, Words, Key Content.

**Tag values:** `[FULL]` (markdown.new, 500+ words), `[PARTIAL]` (markdown.new, 100-499 words), `[FULL:CURL]` (curl fallback, 500+ words), `[PARTIAL:CURL]` (curl fallback, 100-499 words), `[PARTIAL:TOOL]` (WebFetch fallback, 100+ words), `[EMPTY:SPA]` (JS-rendered), `[EMPTY:BLOCKED]` (bot protection).

Update `total_fetches` in frontmatter to match the actual row count before writing.

After all pages are fetched: read back extraction entries, build index, and rewrite `_research-extractions.md` with frontmatter + index + all entries (see Research Extractions Output above). Then proceed to L0 construction.

---

## Research Extractions Output

Write raw page extractions to `.claude/context/_research-extractions.md` using a streaming pattern. This preserves content that would otherwise be lost between extraction and L0 schema construction. Downstream agents read this file selectively.

Schema reference: `schemas/_research-extractions.md`

### Streaming Write Pattern

Write each extraction entry to disk immediately after extracting it. Do NOT batch-write after all fetches.

**Per-page (inside the fetch loop), for each page tagged [FULL] or [PARTIAL]:**

1. Strip rendering artifacts from extracted content (see Artifact Stripping below)
2. Append page entry to `_research-extractions.md` in this format:

        ## N. [Page Type]: [URL]
        <!-- tag: [TAG] | words: NNN | fetched_by: Agent 1 -->

        ### Structured Extraction
        (Homepage only. Use the existing Structured Extraction Template:
        HERO SECTION, NAV TAGLINES, META.)

        ### Key Content Sections
        [Main body content organized by page sections. Preserve heading
        hierarchy and content structure.]

3. Release raw content from working memory. The entry is on disk.

**After all pages are fetched:**

4. Read back all entries from `_research-extractions.md`. Build the index table by scanning `## N.` headers. Count total words across entries.
5. Rewrite the complete file in one operation: YAML frontmatter (with `schema: research-extractions`, `schema_version: "1.0"`, `generated_by: "positioning-framework/research"`, `last_updated`, `company`, `url`, `depth`, `total_pages`, `total_words`) + index table + all entries. This is a full file rewrite, not a prepend. The entries survive a crash between per-page writes and this step.
6. Proceed to L0 construction. You can re-read specific extraction entries from disk during L0 construction if you need to revisit content.

Skip pages tagged [EMPTY], [EMPTY:SPA], or [EMPTY:BLOCKED]. These are logged in `_fetch-registry.md` only.

Skip pages beyond the page-count limit for the current depth. Log them in `_fetch-registry.md` normally, but do not write extraction entries.

### Artifact Stripping

Strip rendering artifacts (never real content):

- **Nav/header/footer chrome.** Identical on every page. Remove entirely.
- **Animated counter widget artifacts.** JS counter widgets render as repeated digit sequences (e.g., "0 1 2 3 4 5 6 7 8 9 . , + % b $"). Remove these sequences. Preserve only the final displayed value if identifiable (e.g., "5,000+ customers"). If not identifiable, write "[animated stat]" as placeholder.
- **Duplicate carousel/slider content.** Testimonial carousels and content sliders often render all slides in HTML. If the same testimonial or content block appears more than once in the extraction, keep the first occurrence and remove duplicates.
- **Boilerplate.** Newsletter signup, cookie consent, social links. Remove.

### Cross-Page Deduplication

Track a lightweight in-memory list of testimonials, CTAs, and content blocks already written. If the same content appears on a subsequent page, write "See entry #[N]" instead of duplicating it.

### Verbatim Preservation

Never paraphrase, summarize, or truncate these items:

- H1, subheads, CTAs, testimonial quotes
- Pricing tier names, feature gate labels
- FAQ questions and answers
- Case study metrics and before/after statements

These are baseline measurements for downstream analysis.

### Page-Count Limits

| Depth | Max Extraction Entries |
|-------|----------------------|
| Quick | 7 |
| Standard | 18 |
| Deep | 30 |

Pages beyond the cap are logged in `_fetch-registry.md` but do not get extraction entries. The caps are generous -- they only constrain sites with unusually high page counts.

### Sanity-Check Ceiling

| Depth | Warning Ceiling |
|-------|----------------|
| Quick | 8K words |
| Standard | 20K words |
| Deep | 35K words |

If the file exceeds the ceiling after the final rewrite, log a warning: "Extractions file is [N] words at [depth] depth. Verify artifact stripping is working correctly." Do NOT trim content to hit the ceiling.

### Graceful Degradation

If you hit context limits before completing all extractions:

1. Whatever entries are on disk are complete (streaming wrote them as they were extracted).
2. Write the frontmatter + index table covering only the entries that exist. `total_pages` reflects actual entries written, not pages fetched.
3. If you must choose between writing the index/frontmatter and completing L0, **L0 wins**. An extractions file with entries but no index is still usable -- consuming agents scan headers.

### VOC Extractions Section

After all page content extraction entries, create a `## VOC Extractions` section in `_research-extractions.md`. This section uses the entry format defined in `modules/voc-extraction.md` Section 5 (VOC Extraction Entry Format). VOC entries are separate from page content entries -- do not mix them.

Write VOC entries as they are extracted during Tier 1C and Tier 2 processing. Each entry follows the structured template with Source Type, Reliability, Segment Signals, and applicable lenses.

---

## Depth Budget

The orchestrator passes a `depth` parameter (quick, standard, or deep) when launching this agent. Research scope scales with depth.

### Quick Depth

**Page budget:** 4-7 fetches. Tier 1 only (company website + LinkedIn). No Reddit. No Tier 2 or Tier 3 sources. No competitor deep extraction (skip 1D, 1D-1, 1E entirely).

**Required fetches (same as the old positioning-quick skill):**
1. **Homepage** - H1, subheadline, hero CTA, proof points, client logos. Verbatim.
2. **Features page** - Full feature list, integrations, capabilities. This is where unique capabilities hide. Look for features that competitors DON'T list. If no dedicated features page, use "Why us" or "How it works."
3. **Pricing page** (if it exists) - Capture ALL tiers including free, entry, and top tier. Note feature gates between tiers (what's locked at each level). Capture any add-ons or usage-based pricing separately. Skip if no public pricing.
4-6. **Three additional pages** - Pick from: integrations, docs landing, changelog, use-cases, solutions, or industry pages. Choose whichever are most likely to reveal capabilities, use cases, or buyer segments not on the homepage. **Never pick /about or /team** -- these are low-signal pages for positioning research.
   - **If the user provided priority pages in the intake:** Fetch ALL of them (no limit) AND still pick your three additional pages. User pages are additive, not a replacement.
   - **If GA4 Priority Pages data is in the launch prompt:** Use it to select the three additional pages instead of picking from the hardcoded list. See "GA4-Informed Page Selection" section above. User priority pages still come first if both are present.

**Optional fetches (only if the above leaves gaps):**
7. LinkedIn company page
8. One "[company name] vs" or "[company name] review" search for lightweight competitive context
9. One competitor homepage for contrast (the most similar/dangerous competitor)

**At quick depth: Do NOT prompt the user.** If running inside a project repo (Tier 0 data available), scan it silently for features, integrations, pricing logic, and templates/presets. Budget: 5 minutes max. This supplements website research, it does NOT replace it. If no Tier 0 data available, proceed with website-only research. Zero questions asked.

**DO NOT at quick depth:**
- Fetch more than 7 URLs total
- Launch background agents
- Search for Tier 2/3 sources (Glassdoor, Wayback Machine, podcasts, SEC filings)
- Extract case studies, blog posts, or careers pages
- Build a full competitive matrix across 6+ competitors
- Run Reddit research

### Standard Depth

**Page budget:** 15-20 fetches total (company + competitors + Tier 2 sources). Follow the full source tier hierarchy below.

**Tier 2 stop condition:** Max 5 attempted Tier 2 fetches beyond Tier 1. If 3 consecutive Tier 2 fetches fail (blocked, empty, or irrelevant content), stop Tier 2 attempts. Note skipped sources in Section Confidence.

### Deep Depth

**Page budget:** 25-35 fetches total. Deep competitive sources are handled by Agent 2 (competitive.md), so this budget covers the research phase only. Follow the full source tier hierarchy below with no restrictions.

**Tier 2/3 stop condition:** Max 10 attempted Tier 2/3 fetches beyond Tier 1. If a source is blocked, generate a manual follow-up task for the user and move on. Do not retry the same URL.

---

## Pre-Flight Intake Consumption

**Pre-Flight intake is handled by the orchestrator (SKILL.md step 5), not by this agent.** The orchestrator collects user input before launching agents and passes it in the launch prompt as a structured intake payload.

**At quick depth:** No intake payload provided. If `.claude/business-brief.md` exists on disk, it was already consumed by the orchestrator and relevant content is in your launch prompt. If neither exists, proceed autonomously. Flag unanswered items with `[NEEDS CONFIRMATION]` in the output.

**At standard/deep depth:** Read the Pre-Flight intake from your launch prompt and apply it:

1. **Named competitors:** Add to your required competitive research targets. Client-provided competitors are highest priority -- research them even if "[company] vs" searches don't surface them. Weight higher than any web-sourced list.
2. **Priority pages:** Fetch ALL user-provided pages (no limit). These are additive -- the agent still picks its own three additional pages (#4-6). Never select /about or /team as a research page unless the user explicitly listed it.
3. **Existing docs:** Treat as Tier 0 sources. Extract product facts, pricing, features, differentiators. Tier 0 overrides Tier 1 on factual matters.
4. **Language constraints:** Thread "must use" terms into L0 Glossary (Correct Usage column). Thread "must avoid" terms into L0 Glossary (Incorrect/Avoid column) AND L0 Constraints section.
5. **Additional context:** Thread into relevant L0 sections (Service Exclusions, Retired Positioning, Target Segments, etc.) as applicable.

**If no intake was provided (user said "go"):** Proceed autonomously with web research. Flag gaps with `[NEEDS CONFIRMATION]` in the output. Note in Section Confidence that no client input was available.

---

## GA4-Informed Page Selection

**When GA4 Priority Pages data is present in your launch prompt**, use it to replace heuristic discretionary page picks. This data comes from the orchestrator's Step 5.5 (a single GA4 query run before your launch).

**Rules:**

1. **Required pages stay required.** Homepage, features, and pricing are always fetched regardless of GA4 data. These are non-negotiable.
2. **Client priority pages still override everything.** If the user specified pages in intake, those come first, then GA4-informed picks, then heuristic fallback for any remaining slots.
3. **GA4 replaces the heuristic discretionary picks.** Instead of picking from the hardcoded list (integrations, docs landing, changelog, use-cases, solutions, industry pages), pick from GA4 priority pages ranked by signal:
   - First: `high-traffic-high-conversion` pages not already in the required list (messaging is working here -- study it)
   - Second: `high-traffic-low-conversion` pages (biggest opportunities -- messaging is failing)
   - Third: `low-traffic-high-conversion` pages (hidden gems -- potentially underexposed messaging)
   - Skip: `low-traffic-low-conversion` pages unless they match a required category
4. **Page budget is unchanged.** Quick: 4-7 fetches. Standard: 15-20. Deep: 25-35. GA4 data changes WHICH pages fill discretionary slots, not how many slots exist.
5. **GA4 data informs company page selection only.** Competitor pages, Tier 2 sources (LinkedIn, Reddit, reviews), and Tier 3 sources are selected by their own logic. GA4 data does not affect those picks.

**When GA4 Priority Pages data is NOT present** (no `--property` flag was used): Use the existing heuristic page selection. No change to current behavior.

---

## Source Tier Hierarchy

Research sources are organized in tiers. **Tier 0 is the primary source of truth when available.** Tier 1 is required for every run but subordinate to Tier 0 on factual matters (pricing, features, integrations, plan limits). Tier 2 should be attempted in every Mode 1 run. Tier 3 when available or when deeper analysis is needed.

**Critical: When Tier 0 and Tier 1 conflict, Tier 0 wins.** Public websites frequently lag behind the actual product. Feature pages show "Coming Soon" for shipped features. Pricing pages omit add-ons. WebFetch may return stale or pre-JS-rendered HTML. Never treat public website content as ground truth when codebase data is available.

---

## Tier 0: Local Project Data (PRIMARY SOURCE OF TRUTH)

Check if you're running inside the company's project repo or have access to local files. **Tier 0 is authoritative for all factual product data.** Overrides any conflicting Tier 1 information.

**What to look for:**
- **Config files** (pricing tiers, feature flags, plan limits): `pricing.ts`, `plans.json`, `config/`, `constants/`
- **README / docs**: Internal product descriptions, setup guides, architecture notes
- **Package manifests** (`package.json`, `pyproject.toml`): Dependencies reveal tech stack and integrations
- **Marketing copy source files**: `src/pages/`, `content/`, `copy/`
- **Analytics/tracking config**: Event names, conversion goals, tracked funnels
- **Integration configs**: What CRMs, MAPs, and third-party services are actually connected
- **Feature flags / enums**: What's shipped vs. gated vs. waitlisted. The single most important check.
- **Existing positioning docs**: `.claude/context/` files, brand guidelines, sales decks
- **Customer data references**: Testimonial databases, case study drafts, NPS data, support ticket categories

**Handling conflicts:** When Tier 0 contradicts Tier 1, document both. Add a "Tier 0 Corrections" section listing every discrepancy. This gives the client an actionable list of website updates.

**If no local project access:** Skip to Tier 1. Note in Section Confidence that internal data was unavailable and feature/pricing claims are based on public website data which may be stale. Flag as confidence-limiting across sections referencing specific features or pricing.

---

## Tier 1: Core Sources (REQUIRED)

### 1A: Company Website Extraction

Extract verbatim. Copy exact headlines, exact phrases. Don't paraphrase yet. **Follow the Website Content Extraction Rules above** to distinguish main content from navigation chrome.

- **Homepage**: H1, subheadline, hero CTA, proof points (logos, stats, testimonials). Use the Structured Extraction Template. The H1 comes from the main content area, NOT from navigation menus or dropdowns.
- **About page**: How they describe themselves, founding story, team positioning
- **Product/services pages**: Feature language, capability claims, pricing structure
- **Case studies** (2-3): Customer type, problem described, results claimed, customer quotes
- **Careers page**: How they pitch themselves to employees (reveals real culture vs. marketed culture)
- **Pricing page**: Tiers, feature breakdown, CTAs, anchoring or comparison language
- **Footer/boilerplate**: Tagline, legal entity description

**While extracting, note tone signals:** Formal or conversational? Technical or accessible? First person ("we") or third person? Humor or serious? Jargon-heavy or plain language? These feed Brand Voice in Phase 3.

### 1B: LinkedIn Extraction

- Company description (often differs from website, revealing inconsistency)
- Recent posts: topics and language
- Employee count and growth signals
- Specialties list (compare against website service language)

### 1C: Review Sites (G2, Capterra, TrustRadius, Glassdoor)

- Pull 5-10 customer reviews
- Extract: What do customers praise? Complain about? What comparisons do they make?
- This is where real voice-of-customer lives. Not from asking the client. From what customers actually wrote.
- Glassdoor employee reviews reveal internal culture vs. marketed culture. Look for complaint patterns.

**If review data is sparse:** Search company name + "review" or "vs" or "alternative" for comparison content, forum discussions, or Reddit threads.

#### VOC Extraction Protocol (Tier 1C)

For all review site sources, read and apply the extraction protocol in `modules/voc-extraction.md`:
- Follow the Review Reading Order (3-star first, then 1-star, 5-star, 4-star)
- Apply the Six-Lens VOC Extraction Framework to each substantive review
- Tag each extraction with Source Reliability and Segment Signals
- Write structured VOC entries to the `## VOC Extractions` section of `_research-extractions.md`
- Mark vivid, copy-ready verbatim quotes as `[MONEY QUOTE]`

### 1D/1D-1/1E: Competitor Identification, Validation & Market Research

**Competitor identification and deep extraction are handled by Agent 2 (see `competitive.md`).** This agent (Agent 1) does not perform competitive research at any depth.

- At quick depth: no competitive research at all.
- At standard/deep depth: Agent 2 handles competitor identification, validation, JTBD taxonomy, per-competitor profiles, and market category research.
- If client-provided competitors were included in the Pre-Flight intake, they are passed to Agent 2's launch prompt as required research targets.

---

## Tier 2: Extended Sources (Attempt in every Mode 1 run)

**Skip if depth is quick.** Quick depth uses Tier 1 only (company website + LinkedIn).

**Budget and stop conditions:** See Depth Budget section above. If a source is blocked or returns no useful data, note it as a gap and move on. Do not retry blocked URLs. Generate a manual follow-up task in the output's Gaps section instead.

### 1F: Unmoderated Voice of Customer

Go beyond curated review sites. Find how real users talk when not writing a formal review.

**Reddit (automated):** Follow the query instructions in `modules/reddit-research.md`. Run 3-5 Reddit searches (see positioning-framework query templates in the module). Read 2-3 full threads with the richest discussion (highest comment count + relevance). No API key required.

Reddit data feeds into: Switching Dynamics (push/pull from real switchers), Objection Handling (unmoderated complaints), Language Bank (exact buyer phrases), and Voice-of-Customer sentiment.

#### VOC Extraction Protocol (Tier 2)

For substantive VOC content found in Reddit threads, forums, and community posts, also apply `modules/voc-extraction.md`:
- Apply the Six-Lens Framework (particularly Pain Points, Trigger Events, Language/Vocabulary, and Alternatives Considered)
- Tag Reliability as Medium-High for Reddit/community sources
- Apply Segment Tagging using subreddit name, language sophistication, and problem complexity as inference signals
- Write structured VOC entries to `_research-extractions.md` `## VOC Extractions` section

**Other unmoderated sources:**
- **Hacker News**: Search for company mentions. Brutally candid on positioning, pricing, and alternatives.
- **Quora**: "[company] review" or "[company] vs [competitor]". Lower signal-to-noise but sometimes captures buyer language.
- **Twitter/X**: Company name + "love" OR "hate" OR "switched from" OR "switched to". Real-time sentiment.
- **Industry forums / Slack communities**: If they exist for the space. Often the most candid source.

The value is language. Capture exact words people use describing the problem, solution, and alternatives. These become the language bank.

### 1G: Financial & Investor Data (Public Companies)

If the company or major competitors are publicly traded:

- **SEC filings (10-K, 10-Q)**: Risk factors reveal actual competitive threats (legally required disclosure). Business description has precise market sizing and positioning language reviewed by lawyers for accuracy.
- **Earnings call transcripts**: CEO/CFO commentary on strategy, competitive dynamics, customer trends. More candid than any marketing page. Search Seeking Alpha, Motley Fool, or investor relations pages.
- **Investor presentations**: Slide decks distilling positioning for shareholders. Often contain competitive positioning maps never put on the website.

This data is gold because it's legally required to be honest in ways marketing copy is not.

### 1H: Company Job Postings

Search the company's careers page and job boards:

- **What roles are they hiring?** Reveals product roadmap and strategic priorities. Hiring 5 ML engineers = building AI features. Hiring 3 enterprise sales reps = moving upmarket.
- **How do they describe themselves in job posts?** The "About Us" in job listings is often written differently from the website. Compare the two.
- **What tools/technologies do they list?** Reveals tech stack, signals maturity and approach.
- **Competitor job postings**: Same analysis. What are competitors building? Where are they investing?

### 1I: Google Trends & Search Behavior

- Search Google Trends for category terms. Growing, flat, or declining?
- Compare multiple category framings: "financial consulting" vs "accounting advisory" vs "CFO consulting". Which has momentum?
- Check geographic distribution against target markets.
- Compare company name search volume against top competitors as a rough brand awareness proxy.

---

## Tier 3: Deep Sources (When Available or Needed)

**Skip if depth is quick.** Quick depth uses Tier 1 only.

### 1J: Wayback Machine / Positioning History

Check web.archive.org for the company's homepage over the past 2-3 years:

- How has the H1 headline changed? Frequent changes = positioning confusion. Consistency = conviction.
- Has the pricing page changed? Price increases = confidence. Price cuts/restructuring = market pressure.
- Have they added or removed services? Reveals strategic pivots.
- Do the same for top 1-2 competitors. Competitor positioning drift creates opportunities.

### 1K: Funding & Ownership Data

Search Crunchbase, PitchBook, or press releases:

- Funding stage and amount (changes how aggressively they can position)
- Investor names (PE-backed companies position differently than bootstrapped)
- Recent acquisitions (signals expansion direction)
- Acquirer identity for competitors (PE rollup vs. strategic acquisition changes competitive dynamics)

### 1L: Podcast / Conference Appearances

Search for founder/CEO appearances:

- Executives say things on podcasts they'd never put on the website. More candid about competitive landscape, challenges, and real strategy.
- Conference talks reveal what the company considers thought leadership vs. what the website says.
- Search: "[CEO name] podcast" or "[company name] podcast interview" or "[company name] conference talk"

### 1M: Customer Press Releases

Search for press releases FROM the company's customers mentioning the company:

- "[company name] press release" or "[company name] partnership announcement"
- The customer's version of the partnership often describes the value differently than the company's version. That gap is informative.
