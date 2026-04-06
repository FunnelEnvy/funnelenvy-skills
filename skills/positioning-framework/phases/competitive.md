# Phase: Competitive Analysis

**Purpose:** Research competitors, map the competitive landscape, and produce `.claude/context/competitive-landscape.md`. This file contains everything an agent needs to execute the competitive analysis phase and build the merged output.

**Produces:** `.claude/context/competitive-landscape.md` (replaces the old split of `market-landscape.md` + `competitor-profiles.md`)

---

## Shared Agent Rules

**Shared agent rules** (Proof Point Protocol, Content Integrity Check, Confidence Rules) are in `agent-header.md`. Read that file first.

---

## Required Inputs

Before starting competitive analysis, verify these preconditions:

1. `.claude/context/company-identity.md` exists
2. L0 frontmatter `confidence` >= 3
3. L0 body sections populated (not `[NEEDS CLIENT INPUT]`):
   - Company Overview
   - Services & Capabilities
   - Target Segments
   - Stated Differentiators

If any precondition fails:
- STOP. Do not proceed with competitive analysis.
- Report to orchestrator: "[PRECONDITION FAILED] Agent 2 requires L0 confidence >= 3 with populated Company Overview, Services, Target Segments, and Differentiators. Current state: confidence={X}, missing sections: {list}."
- The orchestrator decides whether to re-run Agent 1 at deeper depth or proceed with user-supplied context.

### Required Reads

Load before beginning Step 5 (Competitive Attributes Matrix) and Step 7 (Claim Overlap Map):

- `modules/competitive-assessment.md` -- Claim Assessment Framework, Claim Similarity
  Assessment, and Overlap Score Calculation. These are the authoritative analytical
  methods for Steps 5 and 7. Do not improvise alternative assessment approaches.

Load before any web fetch:

- `modules/web-extract.md` -- Three-tier extraction pipeline (markdown.new -> curl+HTMLParser
  -> WebFetch). Defines quality tags, word count thresholds, and the step-by-step extraction
  flow. Follow this pipeline for all URL fetches in this phase.

- `modules/voc-extraction.md` -- structured VOC extraction protocol. Apply to competitor review sources.

---

## Graceful Degradation

If you cannot complete all sections (too many competitors, context limits, fetch failures):

1. **Prioritize REQUIRED sections** (Market Overview, Buyer Alternatives, JTBD Taxonomy, Per-Competitor Profiles for top 3, Claim Overlap Map, Competitive White Space). Write these first.
2. **Always write output to disk.** Partial competitive data is better than none. Agent 3 needs something to read.
3. **Mark incomplete sections with `[INCOMPLETE - reason]`.** E.g., `[INCOMPLETE - only 2 of 5 competitors deep-extracted before reaching context limits]`.
4. **Set confidence accordingly.** Fewer than 3 competitors profiled = confidence 2. No buyer alternatives = confidence 1.
5. **Never fail silently.** Your completion summary must list competitors identified, competitors profiled, and what was skipped.

---

## Output Length Targets
- Quick: N/A (skipped at quick depth)
- Standard: 2,500-4,000 words
- Deep: 4,000-6,000 words

These are targets, not hard limits. Prefer concise, evidence-dense output over padding. If a section has thin data, make it shorter, not fluffier.

---

## Depth Behavior

The orchestrator passes `depth` and `competitive-depth` parameters when launching Agent 2.

- **Quick depth:** This phase is **SKIPPED entirely**. No Agent 2 at quick depth. The orchestrator does not launch this agent. If launched anyway: produce a stub competitive-landscape.md with confidence: 1 and a single section noting "Quick depth does not include competitive analysis. Run at standard or deep depth."
- **Standard depth:** Current behavior. 10-15 web fetches. 3-5 competitors deep-extracted. Tier 1 sources plus basic Tier 2 (automated sources attempted). Targets ~120K tokens for competitive phase.
  This budget is for Agent 2 only and is independent of Agent 1's research phase budget.
- **Deep depth:** Extended behavior. 20+ web fetches. 6+ competitors deep-extracted. All Tier 2 sources (automated + manual follow-up tasks generated). Tier 3 sources attempted. No token cap.
  This budget is for Agent 2 only and is independent of Agent 1's research phase budget.

### Competitive-Depth Override

The `--competitive-depth` flag overrides the competitive analysis depth independently of the overall depth:

- `--competitive-depth deep`: Agent 2 runs at deep depth regardless of overall depth. Use when the user wants full competitive analysis but doesn't need the full positioning stack at deep depth.
- `--competitive-depth none`: Agent 2 is skipped entirely, even at standard or deep overall depth. Use when competitive data already exists and the user wants to focus on messaging/scoring.
- `--competitive-depth standard`: Explicit standard competitive depth (same as default at standard overall depth).

When not specified, competitive depth inherits from overall depth. At deep overall depth, competitive depth defaults to deep.

### Competitive-Focus Mode

When `--competitive-focus "[Competitor Name]"` is passed:

- Agent 2 runs focused on a **single competitor** at deep depth.
- Reads the existing `.claude/context/competitive-landscape.md` and extends it.
- Only produces/updates the profile for the named competitor. Does not touch other profiles.
- Adds the competitor to frontmatter `competitor_names` and `top_competitors` if not already present.
- Updates `competitors_analyzed` count.
- Runs the full deep extraction pipeline (all tiers) for that single competitor.
- Marks changes with `<!-- extended by positioning-framework/competitive-focus [date] -->`.

---

## Source Tiers by Depth

### Standard Depth Sources
- Company websites (homepage, features, pricing, about)
- LinkedIn company pages
- G2, Capterra, TrustRadius (review sites)
- Reddit (public JSON endpoints, see `modules/reddit-research.md`)
- Google Trends (category term validation)
- Competitor comparison pages

### Deep Depth Sources (all standard sources PLUS)
- **Careers/jobs pages** - What roles are they hiring? Reveals product roadmap and strategic direction. Hiring AI engineers = building AI features. Hiring enterprise sales = moving upmarket. How they describe themselves in job posts is often more honest than marketing copy.
- **Product changelogs / release notes** - Recent feature launches and pricing changes signal strategic direction. Fetch `/changelog`, `/whats-new`, `/blog/category/updates`.
- **Product Hunt profiles and launch discussions** - Search "[competitor] site:producthunt.com". Launch comments are often candid about competitive alternatives.
- **Pricing pages with drift detection** - Compare current pricing against what's documented in third-party pricing reviews (Capterra, GetApp, SaaSworthy). Mismatches reveal recent model changes.
- **Crunchbase / funding data** - Funding stage and amount for each competitor. Well-funded competitors can price aggressively. PE rollups change competitive dynamics entirely.
- **Podcast / conference transcripts** - Executives say things on podcasts they'd never put on the website. More candid about competitive landscape and strategy. Search: "[competitor CEO name] podcast" or "[competitor name] podcast interview".
- **SEC filings** (public competitors) - 10-K risk factors are legally required competitive threat disclosure. Earnings call transcripts reveal strategy. Investor presentations contain competitive positioning maps never shown publicly.
- **Customer case studies / press releases** - "[company name] press release" or "[company name] partnership announcement". The customer's version of the partnership describes value differently.

### Auto-Escalation

If competitor identification at standard depth reveals an unusually crowded market (8+ direct competitors), the agent should notify the orchestrator and recommend escalating to deep competitive depth. The orchestrator can auto-escalate or ask the user.

---

## Mode-Specific Competitive Behavior

### Autonomous (Mode 1)
Default. Agent identifies, validates, and researches competitors autonomously. Single checkpoint with user for competitor validation.

### Guided (Mode 2)
User provides the competitor list manually. Agent validates the list with search-based cross-referencing: run "[company] vs" and "[company] alternative" searches to check for competitors the user may have missed. Present any additions with `[NEEDS CONFIRMATION]`. Research each provided competitor. Do not skip user-provided competitors even if they seem minor.

### Update (Mode 3)
Refresh an existing competitive analysis. Read existing competitive-landscape.md. Run fresh research against documented competitors. Flag what changed: new competitors entering the space, shifted positioning, new claims, pricing changes, acquisitions. Search for new competitors not in the existing file: "[company] vs" and "[company] alternative" with current date filters where possible. Update only what changed. Preserve stable analysis. Update `last_updated` and `last_updated_by` in frontmatter.

---

## Prior Work Check

Before starting, glob `.claude/context/competitive-landscape.md`. If it exists:
- Read frontmatter. If `confidence >= 3` and `last_updated` is within 90 days, consume it and skip competitive research entirely. Use existing data for framework sections.
- If `depth` is "standard" and current depth is "deep": extend to deep. Raise confidence where evidence supports it. Add competitors, enrich battle cards, deepen white space analysis. Do NOT overwrite category framing, existing competitor profiles, or existing white space entries.
- If `depth` is "deep" and current depth is also "deep": treat as update. Diff against fresh research, flag changes. Only add net-new insights.
- If stale or low confidence, re-run competitive research.

Also check for legacy split files (`market-landscape.md` + `competitor-profiles.md`). If both exist and no `competitive-landscape.md` exists: migrate content into the merged format. Move old files to `.claude/context/_deprecated/` (preserving rollback path). Log migration in frontmatter changelog. Then proceed with research as if extending from `depth: "standard"`.

---

## Extractions Pre-Check

Before checking `_fetch-registry.md`, run the Extractions Validation check on `_research-extractions.md`:

1. **Frontmatter check:** File has valid YAML frontmatter with `schema: research-extractions` and `total_pages` field.
   - If frontmatter exists and is valid: use the Index table for selective reads.
   - If frontmatter is missing (streaming crash before index was written): scan for `## N. [Page Type]` headers to discover available entries. Proceed with what exists.
   - If file is entirely absent or empty: treat as absent. Proceed to Fetch Registry Check with current behavior.
2. **Entry body spot-check:** For each entry you want to read, verify the corresponding `## N. [Page Type]` section exists in the file body. If missing: skip that entry, note in research log: "Extraction entry #N missing body, skipping."

If valid, read the Index table. For any page you would re-fetch for subject company data (buyer scenarios, objection language, feature detail, pricing framing), check whether the extraction entry contains the specific data you need.
- If the extraction contains the data: use it. Do not re-fetch. Note in research log: "Using Agent 1 extraction for [URL] -- [specific data found]."
- If the extraction exists but lacks the specific data: re-fetch is allowed. Note: "Re-fetching [URL] -- extraction does not contain [specific data needed]."
- If no extraction exists for the URL: fetch normally.

### Extractions Fallback Rules

When the extractions file exists but has issues:
- **Index/body mismatch** (index lists an entry but `## N.` section is missing in body): use body entries only. Log: "Extraction index references entry #N but body section missing, using body entries only."
- **Truncated entry** (section header exists but content is cut off mid-sentence or abnormally short): use what exists, tag data as `[PARTIAL]` in your research log. Do not discard partial data.
- **Duplicate URLs** (same URL appears in multiple entries): use the later entry. Agent 1's streaming write pattern means the later entry is from the final rewrite pass and more likely to be complete/corrected.

---

## Fetch Registry Check

Before fetching any URL, read `.claude/context/_fetch-registry.md` if it exists.

**For review sites (G2, Capterra, TrustRadius):**
- If Agent 1 already fetched the review page with tag [FULL] or [PARTIAL]: read the Proof Point Registry in company-identity.md for review data instead of re-fetching. The reviews are already extracted there.
- If you need data NOT in the Proof Point Registry (e.g., competitor alternatives listed on the review page, pricing comparison data): re-fetch is allowed. Note in your research log: "Re-fetching [URL] for [specific data not in L0]."

**For target company website pages (deep depth only):**
- If Agent 1 already fetched the page: read the relevant section of company-identity.md first. Only re-fetch if the L0 section is tagged [NOT EXTRACTED], [PARTIAL], or doesn't contain the specific data you need (buyer scenarios, objection language, etc.).
- If re-fetching: note in your research log: "Re-fetching [URL] -- L0 does not contain [specific data needed]."

**For Reddit threads:**
- If Agent 1 already searched the same subreddit for the company name: check whether the threads found are relevant to competitive analysis. If they contain competitor mentions or market comparisons, use the existing data. Only run new Reddit searches with different query terms (e.g., "[competitor] vs" instead of "[company name]").

**For all other URLs:** Fetch normally. The registry is informational, not blocking.

**If no registry exists:** Proceed normally. The registry is an optimization, not a precondition.

## Fetch Registry Write-Back

After completing all web fetches in this phase, append your fetches to `.claude/context/_fetch-registry.md`.

Use the same format as Agent 1's entries: URL, your agent name (Agent 2), extraction quality tag, word count, key content summary. Append rows to the existing table. Do not overwrite or re-create the file.

After appending rows, update frontmatter: set `last_updated_by` to `"positioning-framework/competitive"`, `last_updated` to the current date, and `total_fetches` to the new total row count.

If the registry file does not exist (e.g., Agent 1 did not create one), create it using the standard format, then write your entries.

---

## Web Extraction

For all web fetches in this phase (competitor homepages, pricing pages, review sites, Reddit threads, etc.), follow the three-tier extraction pipeline defined in `modules/web-extract.md`.

**Pipeline summary:**
1. **markdown.new** (primary) -- `curl -s --max-time 10 "https://markdown.new/$URL"`. Clean markdown output. Handles SPAs.
2. **curl + HTMLParser** (Fallback Tier 1) -- Python extractor. Falls through if markdown.new returns <100 words.
3. **WebFetch** (Fallback Tier 2) -- Last resort. Filter CSS noise before counting words.

Tag every fetch with the quality tag from `web-extract.md` (`[FULL]`, `[PARTIAL]`, `[FULL:CURL]`, `[PARTIAL:CURL]`, `[PARTIAL:TOOL]`, `[EMPTY:SPA]`, `[EMPTY:BLOCKED]`). Use these tags in the Fetch Registry Write-Back above.

If all three tiers fail for a URL, note it as a gap and move on. Do not fabricate content.

---

## Step 1: Buyer Alternatives (Before Any Vendor)

Before mapping competitors, capture how buyers currently solve the problem without hiring anyone. This is often the real competition.

| Alternative Behavior | Why They Do It | What It Costs Them | When They Outgrow It |
|---------------------|---------------|-------------------|---------------------|
| | | | |

Probe for:
- Internal resources pulled off their day jobs
- Hiring a full-time employee (slow, expensive, single point of failure)
- Cobbling together freelancers or individual contractors
- Status quo (compounds problems long-term)
- Cheaper/simpler tool that doesn't fully solve it

Write in buyer language, not analyst language. "We just had our controller handle it" not "Internal resource reallocation."

### Discovery Sources

Check these sources in order before inventing alternatives from general knowledge:

1. **L0's Buyer Alternatives** (if populated from pre-flight intake). Client-provided alternatives are highest confidence.
2. **`_research-extractions.md` case study entries.** Scan for "before" states: what was the customer doing before they hired the company? Case studies often open with the prior approach.
3. **Review site "switching from" data.** G2/Capterra comparison pages and reviews frequently mention what buyers used previously. Check `_fetch-registry.md` for already-fetched review pages before re-fetching.
4. **Reddit threads.** Search for "what do you use for [JTBD]" or "how do you handle [problem]" in relevant subreddits. These surface DIY and workaround approaches that vendor-centric research misses.
5. **Company FAQ pages.** "Do I need [service]?" and "When should I hire [type of provider]?" questions reveal the alternatives buyers are weighing.

Alternatives sourced from steps 1-5 get cited in the Source column. Alternatives that don't trace to any of these sources are `[INFERRED]`.

### Source Requirements

Use this expanded table format with a Source column:

| Alternative Behavior | Why They Do It | What It Costs Them | When They Outgrow It | Source |
|---------------------|---------------|-------------------|---------------------|--------|

Each alternative must cite at least one source (review site complaint, Reddit thread, case study, job posting), or be marked `[INFERRED]` if sourced from positioning logic rather than direct evidence.

If fewer than 2 alternatives have source citations after research, mark the entire section `[LOW EVIDENCE]` and add a buyer-alternatives question to the Post-Research Questionnaire.

---

## Step 2: Competitor Identification

**Source hierarchy** (priority order):
1. **Client-provided list** (highest weight) - firms they lose deals to
2. **"[Company] vs" searches** - buyer-generated comparisons
3. **"[Company] alternative" searches**
4. **Review site comparisons** (G2 alternatives, Capterra)
5. **Industry analyst reports and market maps**
6. **Company's own website** (comparison pages, "why us", competitive displacement mentions)
7. **Aggregator sites** (Owler, ZoomInfo, Tracxn) - USE WITH CAUTION, firmographic matching not competitive matching

### Maturity Detection

If "[company] vs" and "[company] alternative" searches return zero results about the target company, the company has low market presence. Switch to category-based identification ("[category] alternative", "[category] comparison") and note that competitor list confidence is LOW since it's inferred from category, not from buyer-generated comparisons about this specific company.

### Competitor Sizing

For each identified competitor, assess scale using available signals (LinkedIn headcount, team page, careers page, funding data, web traffic indicators). Classify into tiers using this decision tree:

**Major** (full profile + battle card):
- 100+ employees on LinkedIn, OR
- $10M+ confirmed funding, OR
- Appears in "[company] vs [competitor]" search results (buyer-generated comparison), OR
- Listed in L0's Named Competitors with `origin: client` (client-provided always gets full profile)

**Emerging** (full profile, flagged "watch"):
- <100 employees AND at least one of: recent funding ($1M+ in last 18 months), 20%+ headcount growth signal, or founded <3 years ago with notable traction (press, awards, growing customer list)

**Minor** (JTBD table row only, no profile, no battle card):
- <50 employees, no recent funding, does not appear in "[company] vs" results, not client-provided

**Default when data is insufficient:** Classify as Emerging. This triggers a profile (better to over-research than miss a threat) but flags uncertainty in the Competitor Confidence Ratings table.

### Depth-Specific Competitor Counts

- **Standard:** 3-5 competitors deep-extracted. If the market is crowded and you're on standard, prioritize the competitors most likely to show up in the same deals (direct competitors with the closest positioning overlap).
- **Deep:** 6+ competitors deep-extracted. Minor competitors still get a JTBD table row only.

**Validation checkpoint:** After identification, validate the list against at least 2 buyer-perspective sources. Client-provided competitors always take priority. Flag any competitor sourced only from aggregators as LOW confidence.

---

## Step 3: JTBD Taxonomy

Categorize every competitor by relationship to the customer's Job To Be Done.

**Direct Competitors** - Same JTBD, same type of solution.
**Secondary Competitors** - Same JTBD, different type of solution.
**Indirect Competitors** - Different JTBD, conflicting solution that prevents adoption.

For each tier, fill:

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |
|-----------|------------------|---------------------|--------------------------|--------------------------|

Also capture:
- **Anti-persona:** Who is NOT a good fit? Who is better served by a competitor? (Routes to company-identity.md > Anti-Personas)
- **Switching triggers:** What event or frustration starts the search? (Routes to company-identity.md > Buying Triggers)

---

## Step 4: Per-Competitor Deep Dives

For each Major or Emerging competitor (top 2-3 per JTBD tier at standard, more at deep), extract:

- Homepage H1 (verbatim), subheadline, hero CTA
- Category they claim
- Primary differentiator
- Social proof (logos, testimonials, case study count, named customers)
- Pricing model (mark `[NEEDS CONFIRMATION]` if inferred)
- Tone/voice (formal/casual, technical/accessible)
- Recent strategic signals (new content, hires, acquisitions, repositioning)
- One specific competitive tactic (a page, form, pricing trick, dark pattern, sales behavior - URL if available)

### Competitor VOC Extraction

For competitor reviews, apply `modules/voc-extraction.md` with these competitive-specific adjustments:
- Prioritize 4-star reviews (customers who like the competitor but have complaints -- these are the most credible switching signals)
- For G2 specifically, extract all three structured fields: "What do you like best?" (their strengths = your battlecard intel), "What do you dislike?" (their weaknesses = your opportunities), "What problems are you solving?" (the JTBD)
- Focus extraction on: Pain Points (their unresolved issues), Alternatives Considered (who else they evaluated), and Language/Vocabulary (how their customers describe the problem space)
- Tag all competitor VOC extractions with the competitor name for downstream routing to battle cards
- Write to `_research-extractions.md` `## VOC Extractions` section, clearly labeled with competitor name in the entry header (e.g., `### [Competitor Name] -- G2 Reviews`)

### Deep Depth Extensions (per competitor)

At deep depth, also extract for each Major and Emerging competitor:

- **Careers page:** Fetch the competitor's careers/jobs page. What roles are they hiring? This reveals product roadmap and strategic direction. Hiring 5 ML engineers = building AI features. Hiring 3 enterprise sales reps = moving upmarket. How they describe themselves in job posts is often more honest than marketing copy.
- **Changelog / what's-new page:** Fetch product update pages (`/changelog`, `/whats-new`, `/blog/category/updates`). Recent feature launches and pricing changes signal strategic direction.
- **Product Hunt:** Search "[competitor] site:producthunt.com". Launch comments are often candid about competitive alternatives and positioning.
- **Pricing drift detection:** Compare current pricing against what's documented in third-party pricing reviews (Capterra, GetApp, SaaSworthy). If third-party sites show older pricing, the competitor has changed their model. Also compare the competitor's current homepage H1 against how Capterra/G2/SaaSworthy describe them - mismatches reveal recent repositioning.
- **Competitor comparison pages:** Many competitors publish their own comparison pages (e.g., `fillout.com/form-builder-comparison`). These reveal how competitors frame the market and where they think they win. Fetch these directly.

### Deep Depth: Target Company Deep Extraction

At deep depth, beyond what L0 provides, extract the following from the target company's own website. These are inputs the client would normally provide in a workshop, but autonomous research should attempt to surface them from public content.

**Extractions-first for target company deep extraction:**

Read `_research-extractions.md` entries for the target company first. Extract buyer scenarios, objections, ICP signals, and glossary terms from the raw content. Only fetch additional pages if the extractions don't cover the specific content needed (e.g., a "Who We Serve" page that Agent 1 didn't fetch).

**Buyer Scenarios:** Search the target company's website for signals of how they segment their own buyers:
- "Who we serve" / "Who is this for" pages
- Case study customer profiles (what stage was the customer at when they bought?)
- Form intake questions (these reveal buyer segmentation the company uses internally)
- Landing page variants targeting different personas
- Blog content targeting specific buyer situations

Output: 3-5 specific buyer scenarios in this format: "[Type of buyer] who is [situation/trigger]." Example: "Growth company upgrading from Gusto after hitting 200 employees."

**Objection Mining:** Search for common objections buyers raise about the company or its business model. Prioritize sources that are actually accessible to automated research:
- Company FAQ page (fetch directly)
- "How it works" / "How we make money" pages (fetch directly)
- Competitor comparison pages that attack the company (fetch directly - these are often the richest source)
- G2/Capterra reviews of the target company (search "[company] reviews G2" or "[company] reviews Capterra" - review summaries often appear in search results even if the full page blocks scraping)
- Reddit/forum threads (generate specific search queries as manual follow-up tasks if automated access fails)

Output: List of objections with the **specific source URL or page** and any existing rebuttal the company provides. Vague source attribution ("price-sensitive buyers") is not acceptable. Every objection must cite the page or search result it came from, or be flagged as `[INFERRED]`.

**ICP Triangulation:** Pull ICP signals from at least 3 sources (website copy, founder interviews/podcasts, case study customer sizes, job posting language, pricing page). If sources conflict, surface ALL of them with source attribution and a `[CONFLICTING DATA]` flag. Do not pick a winner without client confirmation.

**Glossary Terms:** Extract industry-specific terms, acronyms, and category labels that appear repeatedly on the target company's website. Define each briefly. This is especially important when the industry has overlapping or confusing terminology (e.g., HRIS vs. HCM vs. HRMS).

### Phase 1 Exit Gate (Standard and Deep Depth)

Before moving to analysis, verify you have:
- [ ] Glossary terms extracted from target company website
- [ ] ICP signals from 3+ sources (with `[CONFLICTING DATA]` flags if sources disagree)
- [ ] At least 3 buyer scenarios identified (or flagged as `[GAP]`)
- [ ] Objections from at least one public source (FAQ, reviews, competitor comparison pages) or flagged as `[GAP]`

If any are missing, make one more targeted attempt before proceeding.

**Battle card data** (inline with each competitor profile):
- **Strengths:** What they're genuinely good at. Be honest.
- **Weaknesses:** Where they fall short for your target customer.
- **When we win:** Scenarios, customer types, or use cases where you beat them.
- **When we lose:** When they're the better choice. If this is empty, the analysis isn't honest.
- **Killer question:** A question that exposes their weakness without trash-talking.
- **Proof to deploy:** Reference proof point IDs from L0's Proof Point Registry (P1, P3, etc.)

**Battle card rules:**
- "When We Lose" is mandatory. If every battle card says "we always win," the analysis isn't honest.
- Only produce profiles + battle cards for Major and Emerging competitors. Minor competitors get a JTBD Taxonomy table row only.
- Proof points must reference P_ IDs that resolve to entries in L0's Proof Point Registry.
- Verbatim competitor quotes (H1, key claims) make battle cards actionable. Sales reps need to know exactly what the competitor says.

**"When We Lose" specificity requirements:**

Each "when we lose" entry must include at least one of:
- A specific buyer scenario: who they are, what they need, why the competitor fits better. Not "large companies" but "enterprise teams with 500+ employees needing dedicated account management and SLA guarantees."
- A specific capability gap with detail: not "they're better at X" but "their platform handles [specific workflow] natively while ours requires [workaround]."
- A specific proof gap: what evidence they have that we don't. "They can cite [specific metric/case study] while our best proof for this claim is [weaker evidence or none]."

Generic contextual facts are not actionable intelligence. Example of what to avoid vs. what to write:
- BAD: "When the buyer is backed by PE." (This is a fact about the buyer, not a competitive insight.)
- GOOD: "When the buyer is backed by PE and under mandate to cut vendor costs 30% within 12 months -- [Competitor] offers a lower-cost self-service tier we can't match without margin compression."

---

## Step 5: Competitive Attributes Matrix

For each Stated Differentiator from L0's company-identity.md, build a row in the matrix.

**Assessment method:** Apply the Claim Assessment Framework from `modules/competitive-assessment.md`.
Assess each differentiator against each competitor type (Direct, Secondary, Indirect) using the
three-dimension evaluation: Claim Status, Proof Status, Replicability.

Write each matrix cell in the module's prescribed format:
`[Claim] | [Proof] | [Replicability] -- [one sentence summary]`

**Differentiator qualification:** Per the module, only attributes where competitors face
STRUCTURAL replicability barriers qualify as true differentiators. Flag any L0 Stated
Differentiator that scores EASY replicability across all competitor types -- this is a
positioning vulnerability, not a strength.

| Stated Differentiator | vs. Direct | vs. Secondary | vs. Indirect | True Differentiator? |
|----------------------|-----------|--------------|-------------|---------------------|
| [from L0] | [Claim]\|[Proof]\|[Repl] -- summary | ... | ... | YES if any STRUCTURAL |

**Moat depth** summary row: Derive from per-cell Replicability ratings above. For each differentiator, summarize as `commodity` (all competitors rated EASY), `investment` (any competitor rated HARD, none STRUCTURAL), or `structural` (any competitor rated STRUCTURAL). Only `structural` attributes qualify as true differentiators in downstream messaging. `commodity` attributes are table stakes and should never lead positioning.

**Depth behavior:**
- **Standard:** Assess top 3-5 direct competitors individually. Group secondary/indirect.
- **Deep:** Assess all profiled competitors individually across all types.

---

## Step 6: Competitive Pricing

| Dimension | Your Company | Competitor A | Competitor B | Competitor C |
|-----------|-------------|-------------|-------------|-------------|
| Pricing model (hourly / project / retainer / outcome-based) | | | | |
| Relative positioning (premium / mid-market / value) | | | | |
| Engagement model (staff aug / project / retainer / managed) | | | | |
| Minimum engagement size | | | | |
| Contract structure (month-to-month / annual / multi-year) | | | | |

Company pricing pulled from L0's Pricing Model. Do not re-research.

**Revenue estimation discipline:** Only estimate competitor revenue when you have concrete signals (public funding rounds, published revenue figures, Growjo/ZoomInfo data, or SEC filings). Otherwise write "Unknown" rather than speculating from headcount or vibes. Unfounded estimates undermine the document's credibility.

If pricing is unknown, document what's inferrable from positioning language. "Premium without the premium" implies mid-tier pricing. "Enterprise-grade" implies premium. "Accessible" implies value positioning.

---

## Step 7: Claim Overlap Map

**Critical distinction:** Positioning vs. Campaigns. Campaign taglines like "Consulting is Dead" are marketing tactics, not positioning elements. If a campaign reveals positioning intent, note the underlying thesis, not the tagline. Campaign taglines should NOT appear in the Claim Overlap Map.

Map every claim from the target company against claims from all profiled competitors.

**Similarity assessment:** Apply the Claim Similarity Assessment from
`modules/competitive-assessment.md`. Use the three-category system:

| Unique? | Meaning |
|---------|---------|
| UNIQUE | No competitor makes a substantially similar promise |
| PARTIAL | Surface overlap but differs on mechanism, audience, or proof. Add note explaining the difference. |
| SHARED | A buyer would perceive these as interchangeable promises |

| Claim | Us | Comp A | Comp B | Comp C | Unique? | Use As |
|-------|-----|--------|--------|--------|---------|--------|
| [claim] | x | x | x | - | SHARED | Qualifier (body copy) |
| [claim] | x | - | - | - | UNIQUE | Headline / lead |
| [claim] | x | x | - | - | PARTIAL -- Overlaps on [X] but differs on [Y] | Headline IF differentiator explicit |

**Rules:**
- Company claims sourced from L0's Stated Differentiators.
- Campaign taglines are NOT claims. Only durable positioning statements.
- Downstream skills: never lead with a SHARED claim. PARTIAL claims can lead IF the differentiating mechanism is made explicit in copy.
- **When all competitors use similar language, document the sameness explicitly.** That IS the finding. A Claim Overlap Map where every claim is marked SHARED tells the company it has a differentiation problem. Do not treat unanimous similarity as a failure of the analysis.

**Score calculation:** After completing the map, calculate `claim_overlap_score` using
the formula from `modules/competitive-assessment.md`:
`claim_overlap_score = (SHARED count + 0.5 * PARTIAL count) / total claims mapped`
Write to frontmatter as a float (2 decimal places).

**Origin-aware rules for Claim Overlap analysis:**
When reading L0's Stated Differentiators and competitors, check the `Origin` column. `client`-origin competitors from L0 are **confirmed targets** -- do not question whether they're actually competitors; research them directly. `research`-origin competitors are **candidates** -- use judgment on relevance and deprioritize or exclude if evidence is thin. `client`-origin differentiators are **real market claims the company makes in deals** -- treat them as validated starting points, not hypotheses to test. `research`-origin differentiators may be aspirational website copy; validate them more skeptically before mapping overlap. When a `client`-origin differentiator has no competitive overlap, that is a **stronger white space signal** than a `research`-origin one with no overlap, because the client has confirmed the claim matters in actual sales conversations.

---

## Step 8: Competitive White Space

### White Space Identification Methodology

White space = positioning territory that buyers care about but no analyzed competitor claims.

**Step 1: Collect buyer signals.** From these sources (already gathered):
- Review site complaints and feature requests
- Reddit/forum discussions about unmet needs
- Job posting requirements that imply workflow gaps
- Buyer Alternatives section: what DIY/workaround approaches suggest about unmet needs

**Step 2: Map buyer signals against competitor claims.** For each buyer signal:
- Check: Does any competitor's positioning explicitly address this?
- Check: Does any competitor's proof points demonstrate solving this?
- If no competitor addresses it: candidate white space.

**Step 3: Validate candidates.** For each candidate white space:
- Is it real? (sourced from at least 1 buyer signal, not inferred)
- Is it addressable? (the target company could credibly claim this territory)
- Is it valuable? (relates to a buying trigger or JTBD, not a nice-to-have)

**Step 4: Write up.** Each white space entry must include:
- The territory (what's unclaimed)
- Buyer signal source (which review, forum post, or job posting surfaced this need)
- Why no competitor owns it (brief: "None of the [N] analyzed competitors mention X in their positioning or proof points")
- Addressability rating:
  - **Ready** = L0 shows existing capability in Services & Capabilities AND existing proof in the Proof Point Registry (cite P_ IDs)
  - **Credible** = L0 shows existing capability but no proof yet (default rating when unsure)
  - **Aspirational** = no existing capability in L0 (requires investment to claim this territory)

White spaces without a sourced buyer signal are speculation, not analysis. Mark any unsourced entry: `[SPECULATIVE - no buyer signal found]`.

---

## Step 9: Reddit Research

**Standard and deep depth.** Follow the query instructions in `modules/reddit-research.md`. Run 4-6 Reddit searches (see competitive query templates in the module). Read 3-4 full threads, prioritizing threads with 10+ comments. No API key required.

Reddit data feeds into: Battle Cards ("When We Lose" from real buyer complaints), Buyer Scenarios (purchase triggers from recommendation threads), Competitive White Space (unmet needs from complaint threads), and the Post-Research Questionnaire (specific Reddit-informed follow-up questions).

---

## Step 10: Deep Sources (Deep Depth Only)

**Skip at standard depth.** These sources are only researched at deep depth.

### SEC Filings & Earnings (Public Competitors)

If any competitor is publicly traded:

- **10-K Risk Factors:** Competitors are legally required to disclose competitive threats. This is where you find honest competitive assessment.
- **Earnings call transcripts:** CEO/CFO commentary on competitive dynamics, pricing pressure, market shifts. Search Seeking Alpha, Motley Fool, or investor relations pages.
- **Investor presentations:** Often contain competitive positioning maps companies would never put on their website.

This data is gold because it's legally required to be honest in ways marketing copy is not.

### Funding & M&A Activity

Search Crunchbase, press releases:

- **Funding stage and amount** for each competitor. Well-funded competitors can price aggressively.
- **Recent acquisitions** signal where competitors are expanding.
- **PE rollups** in the space change competitive dynamics entirely. A competitor that just got acquired by PE will likely cut costs and push for growth.
- **Competitor acquisitions of adjacent companies** signal strategic direction.

### Podcast / Conference Appearances

Search for competitor CEO/founder appearances:

- Executives say things on podcasts they'd never put on the website. More candid about competitive landscape and strategy.
- Search: "[competitor CEO name] podcast" or "[competitor name] podcast interview"
- Conference talks reveal what the company considers thought leadership vs. what the website says.

### Manual Follow-Up Tasks (Not Automated)

These sources contain high-value competitive intelligence but cannot be reliably accessed by automated tools. Generate specific follow-up tasks for the user in the Post-Research Questionnaire.

- **Hacker News:** Specific search queries for hn.algolia.com (e.g., "Search hn.algolia.com for '[competitor name]' sorted by date").
- **Wayback Machine:** Specific URLs to compare at web.archive.org (e.g., "Compare typeform.com snapshots from Jan 2024 vs Jan 2025 for H1 headline changes").
- **Industry forums / Slack communities:** Name the specific communities to search if they exist for the space.

---

## Step 11: Scratch File for Agent Handoff

**All depths.** Before writing the output file, save all raw research findings to `.claude/context/_research-notes.md`. This keeps the writing phase clean and provides a debugging artifact if output looks wrong. Delete the scratch file after `competitive-landscape.md` is written.

---

## Output: competitive-landscape.md

The output merges what was previously two files (market-landscape.md + competitor-profiles.md) into one. The structure eliminates the redundancy where market-landscape had a "Competitive Overview" table that duplicated competitor-profiles' JTBD Taxonomy.

Write the file to `.claude/context/competitive-landscape.md` following the inline schema below.

---

## Inline Schema: competitive-landscape.md

### YAML Frontmatter

```yaml
---
schema: competitive-landscape
schema_version: "1.0"
generated_by: positioning-framework  # skill that first created this file
depth: standard                      # "quick" | "standard" | "deep"
last_updated: 2026-02-16
last_updated_by: positioning-framework
confidence: 3                        # 1-5, lowest section confidence within this file
company: "Company Name"

# Market-level summary
category: "B2B conversion optimization"
category_buyer_term: "CRO agency"       # what buyers actually search for

# Competitive summary
competitors_analyzed: 3
top_competitors:
  - name: "Competitor A"
    positioning: "their H1 or core claim"
    threat_level: high                   # high | medium | low | emerging
  - name: "Competitor B"
    positioning: "their claim"
    threat_level: medium
  - name: "Competitor C"
    positioning: "their claim"
    threat_level: medium
competitor_names:
  - "Competitor A"
  - "Competitor B"
  - "Competitor C"
white_spaces:
  - "unclaimed territory 1"
  - "unclaimed territory 2"
overlap_zones:
  - "claim made by 2+ competitors"
claim_overlap_score: 0.72               # (SHARED + 0.5*PARTIAL) / total claims (0-1)
---
```

**Field notes:**
- `depth`: "standard" = standard depth, enough for messaging. "deep" = extended Tier 2/3 competitive sources, 6+ competitors. ("quick" depth skips Agent 2 entirely, so this file is not produced at quick depth.)
- `claim_overlap_score`: Higher = more generic positioning.
- `top_competitors`: Only the top 3 in frontmatter. Full list in body.
- `category_buyer_term`: What buyers search for, not what the company calls itself.
- `competitor_names`: Full list of all profiled competitors for downstream skill checks.

### Markdown Body Sections

#### 1. Market Overview (REQUIRED)

Category framing and buyer context. 2-3 sentences for someone unfamiliar with the space.

```markdown
## Market Overview

[Category] is the market for [what buyers are trying to do]. Buyers typically search for "[buyer terms]". [Company] positions as [how they frame themselves] within this space.
```

**Used by:** Website audit (category alignment), content strategy (keyword framing), ad copy (search terms).

#### 2. Buyer Alternatives (REQUIRED)

How buyers solve the problem without hiring any vendor. At least 3 alternatives.

```markdown
## Buyer Alternatives

| Alternative Behavior | Why They Do It | What It Costs Them | When They Outgrow It | Source |
|---------------------|---------------|-------------------|---------------------|--------|
| | | | | |
```

Write in buyer language, not analyst language. Each alternative must cite a source or be marked `[INFERRED]`.

**Used by:** Messaging framework (push/pull dynamics), copy briefs (problem-aware content), ad copy (objection handling).

#### 3. JTBD Taxonomy (REQUIRED)

Competitors categorized by relationship to the customer's Job To Be Done. All three tiers required with real competitor names.

```markdown
## JTBD Taxonomy

### Direct Competitors
Same JTBD, same type of solution.

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |
|-----------|------------------|---------------------|--------------------------|--------------------------|

### Secondary Competitors
Same JTBD, different type of solution.

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |

### Indirect Competitors
Different JTBD, conflicting solution that prevents adoption.

| Competitor | How They Position | Where They Fall Short | What It Costs the Customer | Customer Fear/Frustration |
```

**Used by:** Battle card generation (tier context), positioning framework, sales enablement.

#### 4. Per-Competitor Profiles (REQUIRED)

One subsection per Major and Emerging competitor. Minor competitors get a row in the JTBD Taxonomy table only. Battle card data is inlined here (not separate deliverables).

```markdown
## Competitor Profiles

### [Competitor Name]

**Size:** [Major/Emerging] | [headcount, funding, key scale metrics]
**Tier:** [Direct/Secondary/Indirect]

**Positioning:**
- H1: "[exact headline]"
- Category claim: [what shelf they put themselves on]
- Primary differentiator: [their #1 claim]

**Proof & Social Proof:**
- [Logos, testimonials, case study count, named customers]

**Pricing Model:**
- [Model, tiers, relative positioning. Mark [NEEDS CONFIRMATION] if inferred]

**Tone/Voice:**
- [Formal/casual, technical/accessible, personality notes]

**Recent Strategic Signals:**
- [New content, hires, acquisitions, repositioning. From Tier 2/3 if available]

**Specific Competitive Tactic:**
- [One concrete example with URL if available]

**Battle Card:**
- **Strengths:** [What they're genuinely good at]
- **Weaknesses:** [Where they fall short for your target customer]
- **When we win:** [Scenarios, customer types, use cases where you beat them]
- **When we lose:** [When they're the better choice]
- **Killer question:** [Question that exposes their weakness without trash-talking]
- **Proof to deploy:** [P_ IDs from L0 registry]

**Confidence:** [1-5 for this competitor's data quality]
```

**Used by:** Sales enablement (battle card data is inline), copy briefs (competitive context), positioning framework.

#### 5. Competitive Attributes Matrix (REQUIRED)

Per-differentiator matrix using three-dimension assessment from `modules/competitive-assessment.md` (Claim/Proof/Replicability). Rows are L0 Stated Differentiators, not generic categories.

```markdown
## Competitive Attributes Matrix

| Stated Differentiator | vs. Direct | vs. Secondary | vs. Indirect | True Differentiator? |
|----------------------|-----------|--------------|-------------|---------------------|
| [from L0] | [Claim]|[Proof]|[Repl] -- summary | ... | ... | YES if any STRUCTURAL |
| Moat depth | commodity/investment/structural | ... | ... | -- |
```

Each cell uses the module's `[Claim] | [Proof] | [Replicability] -- [summary]` format. Moat depth row derived from per-cell Replicability: EASY->commodity, HARD->investment, STRUCTURAL->structural.

**Used by:** Battle cards (win/lose scenarios), messaging framework (proof mapping).

#### 6. Competitive Pricing (REQUIRED)

```markdown
## Competitive Pricing

| Dimension | Target Company | Competitor A | Competitor B | Competitor C |
|-----------|---------------|-------------|-------------|-------------|
| Pricing model | | | | |
| Relative positioning | | | | |
| Engagement model | | | | |
| Minimum engagement | | | | |
| Contract structure | | | | |
```

Target company pricing pulled from L0's Pricing Model.

**Used by:** Battle cards (pricing objection handling), sales enablement.

#### 7. Claim Overlap Map (REQUIRED)

```markdown
## Claim Overlap Map

| Claim | Us | Comp A | Comp B | Comp C | Unique? | Use As |
|-------|-----|--------|--------|--------|---------|--------|
| [claim] | x | x | x | - | SHARED | Qualifier (body copy) |
| [claim] | x | - | - | - | UNIQUE | Headline / lead |
| [claim] | x | x | - | - | PARTIAL -- Overlaps on [X] but differs on [Y] | Headline IF differentiator explicit |
```

**Unique? column values:** `UNIQUE` / `PARTIAL` / `SHARED` (assessed per `modules/competitive-assessment.md`).
PARTIAL entries MUST include a note: "Overlaps on [X] but differs on [Y]."

**Score:** `claim_overlap_score = (SHARED + 0.5 * PARTIAL) / total claims` (written to frontmatter).

**Rules:**
- Company claims from L0's Stated Differentiators.
- Campaign taglines are NOT claims.
- SHARED claims are qualifiers only. PARTIAL can lead if differentiator is explicit. UNIQUE leads.

**Used by:** Copy briefs (headline selection), messaging framework (hierarchy), website audit.

#### 8. Competitive White Space (REQUIRED)

```markdown
## Competitive White Space

1. **[Territory name]** [Ready/Credible/Aspirational] - [Why it's unclaimed and why it matters to buyers]
2. **[Territory name]** [Credible] - [...]
```

At least 1 white space. Include where the market is over-indexed. Each entry includes an addressability rating: **Ready** (capability + proof in L0), **Credible** (capability, no proof; default), **Aspirational** (no capability).

**Used by:** Hypothesis roadmap, messaging framework, content strategy.

#### 9. Market Over-Indexing (OPTIONAL)

```markdown
## Market Over-Indexing

- **"[Overused claim]"** - [Who claims it and why it's now table stakes]
```

**Used by:** Copy briefs (what NOT to lead with), brand voice (tone differentiation).

#### 10. Buyer Scenarios & Objections (REQUIRED)

```markdown
## Buyer Scenarios

| Buyer Scenario | Trigger | What They Need | Where They Look First |
|---------------|---------|---------------|----------------------|

## Common Objections

| Objection | Source | Existing Rebuttal | Rebuttal Strength |
|-----------|--------|-------------------|-------------------|
```

**Used by:** Battle cards (win/lose maps to scenarios), objection handling in copy.

#### 11. Competitor Confidence Ratings (REQUIRED)

```markdown
## Competitor Confidence Ratings

| Competitor | Confidence | Validation Sources | Notes |
|-----------|-----------|-------------------|-------|
```

**Used by:** Skills deciding whether to trust competitor data or re-research.

#### 12. Founder/Leadership Intelligence (OPTIONAL)

```markdown
## Founder Intelligence

### [Name] ([Competitor])
- [Key strategic insights from interviews, podcasts, earnings calls]
```

**Used by:** Battle cards (strategic context), sales prep.

#### 13. Post-Research Questionnaire (REQUIRED)

**Always produce this.** This is NOT the Pre-Flight questionnaire. This is generated AFTER all research is complete, informed by specific gaps the research uncovered.

- **Standard depth:** 3-5 questions focused on competitor validation and objection discovery (the highest-value gaps).
- **Deep depth:** Full questionnaire (5-10 questions) across all categories below.

```markdown
## Post-Research Questionnaire

The following questions would most improve the confidence of this analysis. They are specific to gaps identified during research, not generic.

### Competitor Validation
- [Specific question, e.g., "Do you actually lose deals to People Managing People, or is that a content competitor only?"]
- [e.g., "Is Matchr (2-person company) a real competitive threat or can we ignore them?"]

### Internal Intelligence
- [e.g., "What does OutSail's pricing actually look like from the vendor side? Do you have data on their referral fees?"]
- [e.g., "Which competitors show up most in your sales conversations?"]

### Objections
- [e.g., "What objections do prospects raise most often? We found X and Y from public sources but likely missing the big ones."]

### ICP Clarification
- [e.g., "Your website suggests 100-1,000 employees but a podcast interview mentioned 0-3,000. Which is the actual target range?"]

### Manual Research Tasks
- [e.g., "Search hn.algolia.com for '[competitor name]' sorted by date"]
- [e.g., "Compare typeform.com snapshots from Jan 2024 vs Jan 2025 at web.archive.org for H1 headline changes"]
```

Each question should reference what triggered it (a specific research finding, a data conflict, a gap). No generic questions like "tell us about your competitors." Every question should be answerable in one sentence by someone who knows the business.

**Used by:** Client workshop prep, follow-up research, confidence improvement.

### Completeness Checklist

> A checklist item passes with either (a) populated content citing sources or (b) an explicit gap marker. Silent omission fails. Honest gaps pass.

A competitive-landscape.md file is **complete** when:

- [ ] YAML frontmatter has all required fields (schema, schema_version, generated_by, depth, last_updated, last_updated_by, confidence, company, category, top_competitors, competitors_analyzed, competitor_names, white_spaces, overlap_zones, claim_overlap_score)
- [ ] Market Overview defines the market in buyer language
- [ ] Buyer Alternatives has entries from verified sources (target: 3+ non-vendor alternatives; fewer is acceptable with gap marker)
- [ ] JTBD Taxonomy covers all three tiers with real competitor names
- [ ] Per-Competitor Profiles exist for every Major and Emerging competitor
- [ ] Each profile includes verbatim H1, category claim, at least one competitive tactic, and inline battle card data
- [ ] Battle card data includes "when we lose" for every profiled competitor
- [ ] Competitive Attributes Matrix maps L0 differentiators against competitor types
- [ ] Competitive Pricing populated (or flagged with confidence impact)
- [ ] Claim Overlap Map covers claims from L0 (target: 5+; fewer is acceptable with gap marker)
- [ ] Competitive White Space identifies unclaimed territory (target: 1+; mark `[NONE FOUND - no buyer signals available]` if none identified from available data)
- [ ] Buyer Scenarios has entries from verified sources (target: 3+; fewer is acceptable with gap marker)
- [ ] Competitor Confidence Ratings populated for every profiled competitor
- [ ] `confidence` value equals the lowest section confidence within this file
- [ ] Post-Research Questionnaire included (3-5 questions at standard, 5-10 at deep) with specific, research-informed questions (not generic)
- [ ] At deep depth: Tier 2 automated sources attempted (careers pages, changelogs, Product Hunt, comparison pages, pricing drift)
- [ ] At deep depth: Tier 3 sources attempted for public competitors (SEC filings, funding/M&A, podcasts)
- [ ] At deep depth: Target company deep extraction attempted (buyer scenarios, objections, ICP triangulation, glossary)
- [ ] At deep depth: Phase 1 exit gate passed (glossary, ICP, buyer scenarios, objections all captured or flagged)
- [ ] Reddit research attempted at standard and deep depth (public JSON endpoint, no auth needed)
- [ ] No speculative revenue estimates without concrete supporting signals (funding rounds, published figures, SEC filings)
- [ ] Competitors sized (Major/Minor/Emerging) with scale justification
- [ ] Minor competitors excluded from deep extraction and battle cards (JTBD table row only)

### Versioning Rules

When a skill extends this file (e.g., a deep-depth run extending a standard-depth analysis):

- Update `last_updated` and `last_updated_by` to the extending skill
- Preserve `generated_by` as the original producing skill
- Can only RAISE confidence scores, never lower them
- Preserve existing competitor profiles; do not overwrite unless the extending skill has strictly better data
- Append new competitors, extend existing profiles, add to white space
- Mark extended sections with `<!-- extended by [skill-name] [date] -->` comments
- Update `competitors_analyzed`, `competitor_names`, and `top_competitors` in frontmatter

```markdown
## Changelog

| Date | Change | By |
|------|--------|----|
| 2026-02-16 | Initial creation | positioning-framework |
| 2026-02-18 | Extended to 8 competitors, deeper white space | positioning-framework (deep) |
```
