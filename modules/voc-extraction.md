# VOC Extraction Module

Structured Voice of Customer extraction protocol for review sites, forums, Reddit, community posts, and client-provided first-party research assets. Consumed by agents processing VOC sources during research and competitive analysis phases.

**Required Reads:** `modules/web-extract.md` (all URL fetches in this module MUST use the three-tier web-extract pipeline: markdown.new -> curl+HTMLParser -> WebFetch. Do NOT use WebFetch directly -- it will fail on the most valuable VOC sources.)

---

## Source Category Map

Not all companies have the same VOC surface area. Identify the company type first, then follow the matching source priority.

### SaaS / Software Products
Primary VOC sources exist on product review platforms.

| Priority | Source | Signal Type |
|----------|--------|-------------|
| 1 | G2, Capterra, TrustRadius | Direct buyer reviews (structured fields) |
| 2 | Reddit (subreddits for the product category) | Unfiltered practitioner discussion |
| 3 | App store reviews (if applicable) | End-user sentiment |
| 4 | Company website testimonials | Curated client voice |
| 5 | Glassdoor/Indeed/Fishbowl | Employee-proxy for client experience |

### Professional Services (Consulting, Agencies, Advisory)
No G2/Capterra profiles. Employer review sites are the primary independent source because employee reviews reveal client experience indirectly (engagement quality, staffing practices, expertise signals).

| Priority | Source | Signal Type |
|----------|--------|-------------|
| 1 | Glassdoor reviews (paginated) | Employee perspective on client work, culture, staffing |
| 2 | Fishbowl posts | Raw professional discussion, comp data, culture skepticism |
| 3 | Indeed reviews | Employee satisfaction, client-facing role descriptions |
| 4 | Reddit (industry subreddits, e.g. r/Accounting, r/consulting) | Unfiltered practitioner opinion |
| 5 | Company website testimonials | Curated client voice |
| 6 | LinkedIn post comments | Semi-public engagement signals |

### Hardware / Physical Products
| Priority | Source | Signal Type |
|----------|--------|-------------|
| 1 | Amazon/retailer reviews | Direct buyer reviews |
| 2 | Reddit (product-specific subreddits) | Unfiltered user discussion |
| 3 | YouTube comments | Engaged viewer reactions |
| 4 | Company website testimonials | Curated client voice |

### Mixed (SaaS + Services)
Use the SaaS priority for the product, Professional Services priority for the services arm. Tag each extraction with which arm it relates to.

---

## Review Reading Order

When processing review sources (G2, Capterra, TrustRadius, app stores), read in this priority order:

1. **3-star reviews first.** Most honest. Buyers who liked it but something's missing. These surface real gaps and trade-offs.
2. **1-star reviews.** Failure modes, deal-breakers, churn causes. Watch for emotional language indicating high-intensity pain.
3. **5-star reviews.** Proof points, success stories, "what sold me" narratives. Mine for trigger events and desired outcomes.
4. **4-star reviews.** "Only wish..." buried in praise. These are the friction points even satisfied customers notice.

### Paginated Review Sources

Review platforms (Glassdoor, Indeed, G2) show a limited number of reviews per page. Budget and prioritize:

| Depth | Pages per Source | Total VOC Fetches (across all sources) |
|-------|-----------------|---------------------------------------|
| Quick | 1 | 2-3 |
| Standard | 3 | 6-10 |
| Deep | 5 | 10-15 |

**Page selection strategy:** Do not read pages sequentially. Most platforms default to "most recent" sort. After page 1, switch to sort-by-rating if available:
1. Page 1: default sort (most recent -- captures sentiment drift)
2. Page 2: 3-star reviews (most honest, per reading order below)
3. Page 3: 1-star reviews (failure modes, deal-breakers)
4. Pages 4-5 (deep only): 5-star and 4-star

If the platform doesn't support sort-by-rating, read pages sequentially.

**URL pattern for pagination (common platforms):**
- Glassdoor: append `_P2.htm`, `_P3.htm` to the review URL
- G2: append `?page=2`, `?page=3`
- Indeed: append `?start=20`, `?start=40` (20 per page)

### Review Text Truncation

Some platforms truncate review text behind "Show more" or "Sign in" walls. markdown.new's headless browser rendering often gets more text than WebFetch, but may still hit login walls.

**Rules:**
- Extract what's visible. Do not fabricate the truncated portion.
- If a review is clearly truncated (ends with "...Show more" or similar), tag it `[TRUNCATED]` in the extraction.
- Truncated reviews still count for lens extraction -- partial data is better than no data.
- If >50% of reviews on a page are truncated to a single sentence, note `[SOURCE: LOGIN-GATED]` and deprioritize that source for money quote extraction (truncated quotes are unreliable).

### Competitor Review Adjustment

For **competitor reviews** specifically: prioritize 4-star reviews. These are customers who like the competitor's product but still have complaints. More credible than 1-star detractors who may have misused the product.

### G2 Structured Fields

For **G2 specifically**, exploit the structured fields:
- "What do you like best?" -- competitor strengths (battlecard intel)
- "What do you dislike?" -- competitor weaknesses (your opportunities)
- "What problems are you solving?" -- Jobs to Be Done in customer language

---

## Six-Lens VOC Extraction Framework

For every VOC source (review, forum post, Reddit thread, interview transcript, support ticket, NPS verbatim), extract through all 6 lenses. Not every source will yield data for every lens. Skip empty lenses rather than forcing output.

### Lens 1: Jobs to Be Done

- Functional jobs (what they're trying to accomplish)
- Emotional jobs (how they want to feel)
- Social jobs (how they want to be perceived)

### Lens 2: Pain Points

- Prioritize by: (a) unprompted mentions and (b) emotional language intensity
- Tag intensity: HIGH (strong emotional language, deal-breaker framing, "I can't," "we had to switch"), MEDIUM (frustration but workable, "it would be nice if"), LOW (mild preference, "I wish")

### Lens 3: Trigger Events

What changed that made them seek a solution? Common triggers:
- Team growth or reorganization
- New hire (especially new leader/VP)
- Missed target or embarrassing incident
- Competitor doing something new
- Budget cycle / end of fiscal year
- Regulatory change
- Tool sunset, acquisition, or price increase
- Internal process breakdown at scale

### Lens 4: Desired Outcomes

Success criteria in the customer's own words. What does "working" look like to them? Capture the specific metrics or states they describe, not your interpretation.

### Lens 5: Language and Vocabulary

Exact phrases customers use to describe their problems, solutions, and outcomes. These are gold for downstream copy. Capture verbatim with quotation marks. Note the source type and approximate date.

### Lens 6: Alternatives Considered

What else did they evaluate? Categories:
- Named competitors
- DIY / internal build
- Hiring (agency, consultant, employee)
- Do nothing / status quo
- Adjacent tools repurposed

---

## Source Reliability Weighting

Tag every VOC extraction with a source reliability rating from this table:

| Source | Signal Strength | Bias to Note |
|--------|----------------|--------------|
| Customer interviews (unprompted) | Very High | Small sample; selection bias toward engaged customers |
| Win/loss interviews | High | Recent memory only; rationalization common |
| App store / G2 reviews | High | Skews toward strong opinions (love or hate) |
| Reddit / community posts | Medium-High | Skews technical, skeptical, vocal minorities |
| Support tickets | Medium | Skews toward problems; silent majority not represented |
| Survey (open-ended) | Medium | Primed by question framing |
| Survey (multiple choice) | Low-Medium | Artifacts of the options provided |
| NPS verbatims | Medium | Correlates with score; prompted by survey moment |
| YouTube / forum comments | Medium | Skews toward engaged viewers; social performance |
| Job postings | Low-Medium | Aspirational, not necessarily reflective of current pain |

When conflicting signals emerge across sources, higher-reliability sources override lower-reliability ones on the same topic.

---

## Segment Tagging

Tag every extracted insight with segment signals visible in the source:
- **Role/title** (if stated or inferable)
- **Company size** (if stated or inferable from context: startup language, enterprise complexity, team size mentions)
- **Industry** (if stated or inferable)
- **Use case** (specific workflow or problem described)

When segment cannot be inferred, tag as `[SEGMENT: inferred-unknown]`. Do NOT exclude these from extraction. Include them in cross-segment analysis only.

### Inference Heuristics

- Subreddit name often signals segment (e.g., r/startups vs r/sysadmin vs r/marketing)
- Language sophistication and problem complexity signal seniority
- Mention of team sizes, budget ranges, or tool stacks signals company size
- Specific workflow descriptions signal use case even without explicit labels

---

## VOC Extraction Entry Format

Write VOC extractions to _research-extractions.md under a ## VOC Extractions section, separate from page content extractions. Use this entry format per source:

```markdown
### [SOURCE_URL_OR_IDENTIFIER]
- **Source Type:** [G2 review | Reddit post | Forum thread | Interview transcript | Support ticket | etc.]
- **Reliability:** [Very High | High | Medium-High | Medium | Low-Medium]
- **Segment Signals:** [Role: X | Size: Y | Industry: Z | Use Case: W] or [SEGMENT: inferred-unknown]
- **Date:** [approximate date if available]

**Jobs to Be Done:**
- [functional/emotional/social jobs observed]

**Pain Points:**
- [HIGH] "verbatim quote or close paraphrase" -- [context]
- [MEDIUM] "verbatim quote or close paraphrase" -- [context]

**Trigger Events:**
- [trigger observed]

**Desired Outcomes:**
- [outcome in customer's words]

**Language/Vocabulary:**
- "exact phrase" -- [context of usage]
- "exact phrase" -- [context of usage]

**Alternatives Considered:**
- [competitor/DIY/hire/status quo mentioned]
```

### Minimum Viable Extraction

Not every lens will yield data from every source. Write the lenses that have data. Skip empty lenses. Do NOT fabricate data to fill lenses.

### Money Quotes

When you encounter a verbatim quote that is vivid, specific, and directly usable in copy, marketing, or sales materials, mark it with a source-differentiated tag:

- `[MONEY QUOTE:INDEPENDENT]` -- from review sites, forums, Reddit, or other sources the company does not control. These are high-value: raw, emotionally honest, and credible for downstream copy.
- `[MONEY QUOTE:CURATED]` -- from company website testimonials, case studies, or marketing materials. These are polished and sanitized. Usable but lower credibility for objection handling and pain point messaging.

Aim for 2-3 money quotes per VOC source when available. Downstream skills should prefer INDEPENDENT quotes for pain point copy and objection handling, CURATED quotes for proof point reinforcement.

### Employee Reviews as Client VOC Proxy

For professional services companies, employee review platforms (Glassdoor, Indeed, Fishbowl) are often the richest independent source. Employee reviews contain client-relevant signals:

- How consultants describe client work quality and engagement success/failure
- Staffing practices that affect client experience (bench time, placement speed, skill matching)
- Culture indicators that translate to client outcomes (engagement, retention, expertise depth)
- Compensation structures that affect talent quality (what caliber of consultant the client gets)

Tag extractions from employee review sources with `[EMPLOYEE-PROXY]` after the Source Type field. This tells downstream skills the insight is indirect -- valuable for understanding the company's delivery capability, but not direct client voice.

**Do NOT mix employee-proxy data with direct client VOC** in the same extraction entry. Write separate entries even if they come from the same platform page.

---

## VOC Adequacy Assessment

After completing all VOC extractions, assess the quality of the data collected. This determines downstream confidence caps.

### Adequacy Tiers

| Tier | Criteria | Downstream Impact |
|------|----------|-------------------|
| **Adequate** | 3+ independent sources extracted, 5+ money quotes (any tag), 3+ lenses populated across sources | No confidence cap. Full downstream synthesis. |
| **Thin** | 1-2 independent sources OR <5 money quotes OR <3 lenses populated | Flag `[VOC: THIN]` in _research-extractions.md frontmatter. Downstream confidence capped at 3 for VOC-derived sections (value themes, persona pain points, language bank). |
| **Curated-Only** | Zero independent sources. All VOC from company website. | Flag `[VOC: CURATED-ONLY]` in _research-extractions.md frontmatter. Downstream confidence capped at 2 for VOC-derived sections. Money quotes tagged `[HYPOTHESIZED - NOT VERIFIED]` unless corroborated by non-testimonial evidence. |
| **None** | No VOC sources accessible or extracted. | Flag `[VOC: NONE]` in _research-extractions.md frontmatter. Downstream skills skip VOC-dependent synthesis. Add prerequisite: "Interview data recommended for VOC-dependent sections." |

### Adequacy Reporting

At the end of the `## VOC Extractions` section in `_research-extractions.md`, write a brief adequacy summary:

```markdown
### VOC Adequacy
- **Tier:** [Adequate | Thin | Curated-Only | None]
- **Independent sources:** [count] ([list source types])
- **Curated sources:** [count]
- **Money quotes:** [count independent] / [count curated]
- **Lenses with data:** [list populated lenses]
- **Gaps:** [lenses with no data, source types that were inaccessible]
```

---

## Cross-References

- **Required dependency:** `modules/web-extract.md` (all URL fetches MUST use the three-tier pipeline)
- **Required dependency:** `modules/reddit-research.md` (Reddit VOC sources use old.reddit.com JSON endpoints)
- Consumed by: `skills/positioning-framework/phases/research.md` (Tier 1C + Tier 2 VOC sources)
- Consumed by: `skills/positioning-framework/phases/competitive.md` (competitor review sources)
- Entry format writes to: `_research-extractions.md` under `## VOC Extractions` section
- Source reliability table referenced by: `skills/positioning-framework/phases/messaging.md` (conflict resolution), `skills/positioning-framework/phases/scoring.md` (confidence scoring)
- VOC adequacy tier consumed by: `skills/positioning-framework/phases/messaging.md` (confidence caps on VOC-derived sections)
