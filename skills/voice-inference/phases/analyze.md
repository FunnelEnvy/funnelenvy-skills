# Phase: Analyze

**Covers:** Voice analysis from extracted page content. Produces scored tone dimensions, vocabulary patterns, example library, cross-channel consistency assessment, and actionable voice rules.

**Produces:** `.claude/context/brand-voice.md` (L1 context file)

**Reads:**
- `.claude/context/_voice-extractions.md` (REQUIRED -- hard precondition)
- `.claude/context/competitive-landscape.md` (OPTIONAL -- enriches Avoided Vocabulary)
- Brand docs (OPTIONAL -- passed by orchestrator as `BRAND_DOCS` in launch prompt if compare mode)

**Shared Agent Rules:** Read `agent-header.md` first. This file second.

---

## Required Inputs

### _voice-extractions.md (HARD REQUIREMENT)

This file must exist with valid frontmatter and at least 5 usable pages (tagged `[FULL]` or `[PARTIAL]`).

**Validation procedure:**
1. Check for valid YAML frontmatter with `schema: voice-extractions` and `total_pages_extracted` field.
2. Read the Page Inventory table. Count pages tagged `[FULL]` or `[PARTIAL]`. This is the usable page count.
3. If usable pages < 5: proceed with analysis but cap confidence at 2. Note in frontmatter `notes` field.
4. Classify usable pages by category from the inventory table. Count distinct categories.

### Brand Docs (CONDITIONAL -- compare mode only)

If the orchestrator passes `BRAND_DOCS` in the launch prompt, this is compare mode. The brand docs are pre-extracted text content from customer-provided documents (PDFs, Google Docs, markdown, pasted content).

**Brand doc consumption:**
1. Read each brand doc entry: `{ source, format, content }`.
2. Identify voice-relevant sections. Look for:
   - Tone/voice guidelines (formality, personality, register)
   - Do/don't word lists (approved vocabulary, banned terms)
   - Writing style rules (sentence length, structure, punctuation)
   - Example copy (approved samples, template language)
   - Brand personality attributes
3. Organize findings into a mental model of the "stated voice" for comparison against observed voice.
4. If brand docs contain no voice-relevant content: note this in the Tensions section and proceed as observe mode (confidence still capped at 4 since the guide didn't validate anything).

---

## Optional Inputs

### competitive-landscape.md

If `.claude/context/competitive-landscape.md` exists, read:
- Competitor names and positioning statements (for Avoided Vocabulary mapping)
- Competitor taglines and signature phrases
- Competitor voice descriptors (if available from competitor profiles)

If absent: Avoided Vocabulary section gets `[INCOMPLETE - no competitive data. Run /positioning-framework first or provide competitive-landscape.md]`.

---

## Analysis Pipeline

Execute these steps in order. Each step reads from `_voice-extractions.md` and builds a section of `brand-voice.md`.

### Step 1: Corpus Assessment

Read the full `_voice-extractions.md`. For each usable page:
- Note its category, word count, and content density
- Identify pages with only navigation chrome (mark as unusable even if tagged PARTIAL)
- Count actual usable pages and distinct content types

Set `pages_analyzed` = usable pages after chrome-only exclusions.

Record which pages belong to which categories. You'll need this for the Consistency Map.

### Step 2: Tone Spectrum

Analyze all usable page content across the five dimensions. For each dimension:

**Formality (1-10):** 1 = casual/conversational, 10 = institutional/formal
- Look for: contractions (casual) vs. none (formal), slang vs. industry terminology, sentence complexity, register indicators

**Confidence (1-10):** 1 = tentative/hedging, 10 = assertive/absolute claims
- Look for: superlatives ("unrivaled," "best"), absolute claims ("the definitive"), hedging ("may help," "could support"), qualifier frequency

**Warmth (1-10):** 1 = cool/analytical, 10 = empathetic/emotional
- Look for: emotional language, empathy phrases ("we understand"), outcome vs. feature focus, "you" address frequency, storytelling

**Complexity (1-10):** 1 = plain language, 10 = technical/jargon-dense
- Look for: unexplained acronyms, industry terminology, multi-clause sentences, assumed domain knowledge

**Energy (1-10):** 1 = calm/measured, 10 = urgent/high-energy
- Look for: imperative verbs, exclamation marks, urgency language ("now," "today," "don't miss"), action-oriented CTAs, sentence punch

For each dimension:
1. Sample evidence from across content types (not just one page or section)
2. Score 1-10 with a descriptive label (e.g., "7.5/10 (Formal-leaning)")
3. Write 1-2 sentence narrative explaining the score
4. Select 3 verbatim examples with source URLs that best illustrate the score

### Step 3: Person and Perspective

Scan all usable pages for pronoun patterns:

- **First person plural** ("we," "our," "us"): company-centric framing
- **Second person** ("you," "your"): direct address, consultative
- **Third person** ("they," "the company," "clients"): analytical, distanced
- **Mixed**: shifts between modes by content type

Determine:
- **Dominant grammatical person** with examples
- **Point of view** -- how the company positions itself relative to the reader (e.g., "enabler of outcomes," "trusted advisor," "thought leader")
- **Direct address frequency** -- how often "you/your" appears. High (every section), Medium (occasionally), Low (rare)

### Step 4: Sentence Architecture

Sample at least 30 sentences across all content types. Select sentences that represent the range (shortest, longest, typical).

Compute:
- **Average sentence length** in words
- **Range** -- shortest and longest sentences with examples
- **Complexity classification** -- simple, compound, complex, multi-clause with embedded qualifiers
- **Opening patterns** -- identify 3+ recurring sentence opening patterns with examples (e.g., "Imperative verb openers on campaigns," "Declarative 'We' openers on product pages")
- **Paragraph length** -- by content type (e.g., "2-4 sentences on marketing pages, 5-8 in research")

Assign the overall bucket: `short (8-14)`, `medium (14-19)`, `long (19-25)`, or `very_long (25+)`.

### Step 5: Persuasion Mode

For each usable page, identify which persuasion mode is dominant:

| Mode | Indicators |
|------|-----------|
| **Authority** | Expertise claims, superlatives, institutional credibility, "leading," "trusted" |
| **Logic** | Benefit-feature structures, systematic capability descriptions, numbered lists, data proof |
| **Social proof** | Testimonials, customer logos, award lists, usage statistics, case study references |
| **Empathy** | Pain point acknowledgment, "we understand," emotional language, customer-centric framing |
| **Urgency** | Time pressure, imperative commands, "now," "today," limited offers, FOMO language |

Build a frequency table: Mode | N/pages_analyzed | Pages Where Dominant.

Identify the primary mode (most frequent) and secondary mode. Write 2-3 sentence narrative for each.

### Step 6: Vocabulary Fingerprint

#### High-Frequency Terms

Scan all usable pages for recurring terms. Focus on terms that appear:
- Across multiple pages (not just one page)
- In prominent positions (headlines, CTAs, opening sentences)
- As part of the brand's identity vocabulary (not generic English)

Target: 12-15 terms. For each term:
- **Term:** the word or short phrase
- **Count:** approximate occurrence count with "+" qualifier (e.g., "15+")
- **Category:** `core` | `product` | `domain` | `brand` | `positioning` | `outcome` | `scale`
- **Example Usage:** one verbatim usage with source URL

#### Signature Constructions

Look for recurring syntactic patterns (not just words, but structural patterns in how sentences are built). These are the company's fingerprint constructions.

Examples of what to look for:
- Triple-verb patterns ("measure, monitor, and manage")
- Capability-to-outcome bridges ("so you can [outcome]")
- Fragment series for proof points ("30+ years. 35M+ reports.")
- Branded phrase anchors ("Essential Intelligence for...")
- Adjective-stacking patterns ("powerful analytics, robust data, unparalleled insights")

Target: 4-6 patterns. For each:
- Pattern name (descriptive, e.g., "Triple-verb imperative")
- Occurrence count
- 3+ verbatim examples with source URLs

#### Avoided Vocabulary

**Requires competitive-landscape.md.** If available:

1. Read competitor positioning statements, taglines, and signature phrases from competitive-landscape.md.
2. Cross-reference against the target company's content. Identify terms the target company conspicuously avoids that competitors own.
3. Build table: Avoided Term | Competitor Owner | Notes (why avoided or what the company uses instead).

Target: 4-8 entries.

If competitive-landscape.md is unavailable: `[INCOMPLETE - no competitive data. Run /positioning-framework first or provide competitive-landscape.md]`

#### Jargon Tolerance

Classify as Low, Medium, or High based on:
- **Low:** All terminology explained, plain language focus, accessible to general audience
- **Medium:** Some industry terms used without definition, but core concepts explained
- **High:** Industry terminology used freely without definition, acronyms unexpanded, assumed domain expertise

Write an evidence paragraph with specific examples of unexplained (or explained) terminology.

### Step 7: Example Library

Build five categorized tables of verbatim examples from the extraction corpus.

**Selection criteria for all examples:**
- Must be verbatim from extracted content (never paraphrase or invent)
- Must include source URL
- Must include content type classification
- Must include "Why Included" rationale (what voice pattern this example demonstrates)
- Prefer diversity across content types and pages
- Prefer examples that demonstrate the scored tone dimensions or signature constructions

**Subsection targets:**

| Subsection | What to Include | Minimum | Target |
|------------|----------------|---------|--------|
| Headlines | H1s, section headers, campaign taglines | 6 | 8+ |
| Body Passages | Representative paragraphs showing voice patterns | 6 | 8+ |
| CTAs | Button text, form CTAs, action prompts | 4 | 5+ |
| Proof Language | Statistics, awards, testimonials, coverage claims | 4 | 6+ |
| Transitional Phrases | Section bridges, navigation cues, framing devices | 4 | 6+ |

**Table format for each subsection:**

```markdown
### [Subsection] ([count])

| # | Quote | Source URL | Content Type | Why Included |
|---|-------|-----------|-------------|-------------|
| 1 | "[verbatim quote]" | url | [type] | [rationale] |
```

### Step 8: Consistency Map

Group usable pages by content type. For each content type with usable pages:

1. **Voice summary:** 2-3 sentences characterizing how the voice manifests in this content type. What's distinctive about the voice here?
2. **Comparison to overall:** 2-3 sentences comparing this content type's voice to the overall voice DNA. Where does it align? Where does it diverge?
3. **Classification:**
   - **Consistent:** Voice aligns with overall DNA on person, tone, vocabulary, and energy.
   - **Partial:** 1-2 dimensions shift (e.g., person changes from "we" to third person, or energy increases significantly).
   - **Divergent:** 3+ dimensions shift, or the voice is fundamentally different from other content types.

Content types with 0 usable pages: `[NOT ASSESSED - no [type] pages available in extraction corpus]`

**Overall Consistency Rating:**

Count Partial and Divergent classifications:
- **high:** 0-1 Partial, 0 Divergent
- **moderate:** 2-3 Partial, or 1 Divergent
- **low:** 4+ Partial, or 2+ Divergent

Write a narrative paragraph explaining the rating. Be specific about what's consistent and what diverges.

In compare mode, add a "vs. Brand Guide" assessment for each content type: how well does the observed voice in this content type match the stated brand guidelines?

### Step 9: Voice Rules

Synthesize all analysis into actionable rules. Each rule must be:

1. **Testable:** A reviewer can read a piece of copy and determine compliance.
2. **Company-specific:** Not generic writing advice. Grounded in THIS company's patterns.
3. **Evidence-based:** Supported by at least one verbatim example from the corpus.

**Rule format:**

```markdown
**N. [Rule name]**
Category: [structural | vocabulary | tone | proof | channel_override]
Instruction: [1-3 actionable sentences]
Example: "[verbatim quote]" (url)
```

**Category distribution target:**
- **structural** (2-4): sentence length defaults, paragraph structure, heading patterns, list formats
- **vocabulary** (3-5): approved superlatives, avoided terms, signature constructions to use, branded phrases
- **tone** (2-3): confidence level, warmth register, formality baseline, hedging rules
- **proof** (1-2): numeric formatting ("N+" pattern), social proof presentation, data citation style
- **channel_override** (1-2): register shifts for thought leadership, campaign energy levels, research vs. marketing tone

**Target: 10-15 rules. Minimum: 6.**

In compare mode: include rules from the brand guide that are supported by observed patterns. Flag rules from the guide that are NOT supported by observed behavior (these become Tensions).

### Step 10: Tensions

**Observe mode:**
- Scan for intra-site contradictions. Examples:
  - Homepage claims "We simplify complexity" but product pages use impenetrable jargon
  - One page uses first person, another uses third person without clear content-type justification
  - Brand claims "customer-first" but copy is entirely product-centric
- If no contradictions found: `*No tensions identified in observe mode. This section will be populated during guide comparison or A/B testing phases.*`
- If contradictions found: table with Tension | Where It Appears | Severity | Notes

**Compare mode (REQUIRED):**
For each brand doc directive, compare against observed content:

```markdown
| Tension | Brand Guide Says | Site Shows | Severity | Recommendation |
|---------|-----------------|------------|----------|---------------|
| [description] | "[guide directive]" | "[observed behavior with URL]" | high/moderate/low | [specific recommendation] |
```

Severity:
- **high:** Directly contradicts a stated guideline (guide says "never use superlatives," site uses them extensively)
- **moderate:** Drifts from guideline without outright contradicting it (guide says "warm tone," site is cool but not cold)
- **low:** Minor inconsistency (guide says "Oxford comma always," site is inconsistent)

### Step 11: Confidence Reconciliation

Set `voice_confidence` based on:

| Factor | Impact |
|--------|--------|
| Usable pages < 5 | Cap at 2 |
| Usable pages 5-8 | Cap at 3 (unless 3+ content types) |
| Usable pages 9-11 with 3+ content types | Can reach 3 |
| Usable pages 12-15 with 4+ content types | Can reach 4 |
| Compare mode with brand docs validating patterns | Can reach 5 |
| Example Library has significant gaps (< 24 total) | Reduce by 1 |
| Only 1-2 content types regardless of page count | Cap at 2 |

In compare mode: if brand docs contain voice guidelines and observed patterns consistently match them, add +1 (up to max 5). If brand docs contradict observed patterns on 3+ dimensions, do not add the bonus.

### Step 12: Write brand-voice.md

Assemble the complete file with YAML frontmatter and all sections.

**Frontmatter fields to compute from analysis:**

```yaml
schema: brand-voice
schema_version: "1.0"
generated_by: "voice-inference/analyze"
last_updated: "[today's date]"
last_updated_by: "voice-inference/analyze"
company: "[from extractions]"
url: "[from extractions]"
source_mode: "[observe|compare]"
guide_provided: [true|false]
guide_sources: [list from BRAND_DOCS or empty]
pages_analyzed: [usable page count after exclusions]
pages_extracted: [from extractions frontmatter]
page_categories: [counts by category]
voice_confidence: [from Step 11]
consistency_rating: "[from Step 8]"
primary_tone: [top 3-5 tone adjectives from Step 2]
rhetorical_mode: "[primary persuasion mode from Step 5]"
sentence_length_avg: "[bucket from Step 4]"
person: "[dominant person from Step 3]"
jargon_tolerance: "[from Step 6]"
example_count: [total examples in Example Library]
rule_count: [total rules in Voice Rules]
tension_count: [total tensions, 0 if none]
competitive_landscape_available: [true|false]
company_identity_available: [true|false]
notes: |
  [Any limitations, excluded pages, corpus notes]
```

**Body section order:**
1. Voice DNA (Tone Spectrum, Person and Perspective, Sentence Architecture, Persuasion Mode)
2. Vocabulary Fingerprint (High-Frequency Terms, Signature Constructions, Avoided Vocabulary, Jargon Tolerance)
3. Example Library (Headlines, Body Passages, CTAs, Proof Language, Transitional Phrases)
4. Consistency Map (per content type + Overall Rating)
5. Voice Rules (grouped by category)
6. Tensions (conditional)

---

## Prior Work Extension

If extending an existing `brand-voice.md`:

1. Read existing file completely.
2. Identify sections where new extraction data adds value (new content types, more examples, pattern confirmation).
3. Extend sections with new data. Add `<!-- extended by voice-inference [date] -->` comment at top of modified sections.
4. Preserve existing examples unless contradicted by new evidence.
5. Re-run confidence reconciliation with the combined corpus.
6. Update `last_updated` and `last_updated_by` in frontmatter. Preserve `generated_by`.

---

## Quality Checks

Before writing the final file, verify:

- [ ] YAML frontmatter has all required fields
- [ ] `pages_analyzed` matches actual usable page count (after chrome-only exclusions)
- [ ] `example_count` matches actual total examples in Example Library
- [ ] `rule_count` matches actual total rules in Voice Rules
- [ ] All 5 REQUIRED sections present (Voice DNA, Vocabulary Fingerprint, Example Library, Consistency Map, Voice Rules)
- [ ] Tone Spectrum has exactly 5 dimensions, each scored 1-10 with 3 sourced examples
- [ ] Every example in Example Library has a source URL from the extraction corpus
- [ ] No examples are paraphrased (all verbatim from extractions)
- [ ] Voice Rules >= 6 count
- [ ] Voice Rules span at least 3 categories
- [ ] In compare mode: Tensions section is populated
- [ ] Consistency rating aligns with Partial/Divergent count (see criteria)
- [ ] Confidence score follows the scale criteria
- [ ] No system internals in body (no file paths like `.claude/`, no agent names, no skill references)
- [ ] `primary_tone` in frontmatter accurately reflects Tone Spectrum scores

---

## Completion Summary

After writing `brand-voice.md`, return to the orchestrator:

```
Voice analysis complete.

Mode: [observe|compare]
Pages analyzed: [N] usable across [N] content types
Voice confidence: [N]/5
Consistency: [rating]
Primary tone: [adjectives]
Rhetorical mode: [mode]
Examples: [N] across 5 categories
Rules: [N] across [N] categories
[If compare mode: Tensions: [N] identified]
[If competitive data used: Avoided vocabulary mapped against [N] competitors]

brand-voice.md written to .claude/context/
```
