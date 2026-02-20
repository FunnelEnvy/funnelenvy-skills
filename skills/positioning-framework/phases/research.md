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

For each URL, follow this sequence:

1. **Run the curl extractor** using the command template from `modules/web-extract.md`.
2. **Count words** in the output.
3. **Assess curl output:**
   - **500+ words:** Tag `[FULL]`. Use the content. Done.
   - **100-499 words:** Tag `[PARTIAL]`. Use the content but note for cross-reference. Done.
   - **<100 words:** Curl failed to extract usable content. Continue to step 4.
4. **Try WebFetch** on the same URL.
5. **Filter CSS noise from WebFetch output:** Discard any `<style>` blocks, CSS class definitions, or inline styling rules. Focus on HTML semantic elements: headings, paragraphs, lists, links with visible text, and image alt text. Many CMS platforms embed hundreds of lines of inline CSS that swamp the markdown conversion -- the content is still there, extract it from between the noise. After filtering, assess by word count:
   - If usable content remains after filtering: tag `[FULL]` or `[PARTIAL]` by word count (same thresholds as step 3). Done.
   - If no usable content after filtering: continue to step 6.
6. **Failure triage** (both curl and WebFetch failed):
   a. **SPA indicators present?** `<div id="root">` or `<div id="app">` as sole body child, `__NEXT_DATA__`, `bundle.js`, `_next/`, React/Vue/Angular boot markers, `<noscript>` fallback content, empty `<body>` with only script tags. If yes: tag `[EMPTY:SPA]`. Write `[NOT EXTRACTED - JS-rendered SPA]` for unpopulated fields. Done.
   b. **Access blocked?** CAPTCHA/challenge page, 403/429, Cloudflare/WAF token, "Enable JavaScript" message with no body content. If yes: tag `[EMPTY:BLOCKED]`. Write `[NOT EXTRACTED - access blocked]`. Done.
   c. **Neither?** Content genuinely absent or tool failure. Tag `[PARTIAL:TOOL]` if some content was extracted, `[EMPTY]` if nothing. Write `[NOT EXTRACTED - tool parse failure]`. Done.

In ALL cases where extraction fails:
1. Note the URL in the Gaps section of company-identity.md
2. Do NOT fill in plausible-sounding copy as a substitute
3. Move on to the next page

The downstream impact of fabricated copy is catastrophic: experiments designed against non-existent baselines, executive summaries quoting copy the client has never seen, and total loss of credibility. A gap is always better than a fabrication.

---

## CRITICAL: Website Content Extraction Rules

The curl extractor returns plain text with `#`-`######` heading markers. WebFetch (fallback) returns page content as markdown. In both formats, navigation menus, dropdowns, and footer content appear BEFORE the main page content in the output. You must distinguish between navigation chrome and actual page content.

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

After every page fetch, assess the extraction quality and tag it:

### [FULL] - High confidence extraction
- Page returned 500+ words of body content
- H1 present and semantically related to page URL/title
- Multiple content sections visible (not just nav + footer)

### [PARTIAL] - Reduced confidence
- Page returned 100-500 words of body content
- OR: Content appears truncated (ends mid-sentence, missing sections visible in navigation but not in body)
- Treat findings from [PARTIAL] pages as provisional. Cross-reference with other sources before including in L0.

### [PARTIAL:TOOL] - Extraction incomplete
- Content exists on page but extraction was incomplete after CSS filtering
- Some usable content extracted, but clearly missing sections that should be present
- Treat as [PARTIAL]. Note extraction limitation in research notes.

### [EMPTY] - No usable content
- Page returned <100 words of body content
- OR: Content is entirely navigation/footer chrome
- OR: Both curl and WebFetch returned errors or empty responses
- Cause unknown. Do not use any content from this page.

### [EMPTY:BLOCKED] - Access denied
- CAPTCHA/challenge page, 403/429, Cloudflare/WAF interception, rate limit
- Do not use any content from this page. Generate a manual follow-up task.

### [EMPTY:SPA] - JS-rendered SPA
- Confirmed by framework indicators (React/Vue/Angular boot markers, `<div id="root">` as sole body child, `__NEXT_DATA__`, empty `<body>` with only script tags)
- Use the appropriate `[NOT EXTRACTED]` tag from the Website Content Extraction Flow above. Do not use any content from this page.

### [CACHED] - Possible stale content
- Page content contradicts other recent sources about the same company
- OR: Copyright date or "last updated" timestamp is 2+ years old
- OR: Content references products/features that other sources indicate have been deprecated
- Treat as [PARTIAL]. Flag for user verification at checkpoint.

### Usage
Tag every page fetch in research notes:
"Fetched https://example.com/pricing [FULL] - 1,200 words, pricing tiers and feature comparison extracted."

These tags are internal to research. They do NOT appear in context files or deliverables. They inform how confidently the agent treats each source when building L0 sections.

### Impact on Confidence Scores
- Section built primarily from [FULL] sources: confidence 4-5
- Section built from mix of [FULL] and [PARTIAL]: confidence 3-4
- Section built primarily from [PARTIAL] sources: confidence 2-3
- Section dependent on [EMPTY] or [CACHED] sources: confidence 1-2, mark section as `[NEEDS CLIENT INPUT]`

---

## Fetch Registry

After completing all web fetches, write a fetch registry to `.claude/context/_fetch-registry.md`.

For each URL fetched during this phase:
1. Record the URL, your agent name (Agent 1), the extraction quality tag, word count, and a 1-2 sentence summary of key content extracted.
2. Include ALL fetches, including failed ones ([EMPTY] tags). Downstream agents need to know a URL was attempted and failed, not just what succeeded.
3. Write the registry BEFORE writing company-identity.md (consistent with write-before-checkpoint pattern).

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

**Tag values:** `[FULL]` (500+ words), `[PARTIAL]` (100-499 words), `[PARTIAL:TOOL]` (WebFetch fallback, 100+ words), `[EMPTY:SPA]` (JS-rendered), `[EMPTY:BLOCKED]` (bot protection).

Update `total_fetches` in frontmatter to match the actual row count before writing.

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
