> **Reference copy.** The authoritative schema is inlined in `skills/voice-inference/phases/analyze.md`.
> This file is a human-readable reference for contributor orientation. If the two diverge, analyze.md wins.

---

# Brand Voice Schema (Layer 1)

**Version:** 1.0.0
**Output path:** `.claude/context/brand-voice.md`
**Produced by:** `voice-inference`
**Consumed by:** positioning-framework Agent 3 (voice baseline), landing-page-generator (voice calibration), render-default-deliverables (messaging guide enrichment), hypothesis-generator (voice-aware hypothesis framing)

---

## Purpose

Deep brand voice analysis derived from observed website content. Contains tone dimensions, vocabulary patterns, example library, cross-channel consistency assessment, and actionable voice rules. Unlike the voice subsection in `audience-messaging.md`, this is a standalone deep-dive with 5x the depth: scored tone dimensions, sentence architecture, persuasion mode mapping, signature constructions, and 33+ categorized examples.

**Boundary rule:** This file contains voice analysis (HOW the company communicates). It does not contain persona profiles (WHO the company talks to -- that's `audience-messaging.md`), competitive positioning (that's `competitive-landscape.md`), or company facts (that's `company-identity.md`). The Avoided Vocabulary subsection references competitor names but does not profile them.

**Two modes:**
- `observe`: Voice inferred from website content only. No brand guide. Confidence caps at 4.
- `compare`: Observed voice compared against customer-provided brand docs. Produces Tensions section. Can reach confidence 5.

---

## Schema Definition

### YAML Frontmatter

```yaml
---
schema: brand-voice
schema_version: "1.0"
generated_by: "voice-inference/analyze"       # Immutable after creation
last_updated: "2026-03-25"                    # ISO date
last_updated_by: "voice-inference/analyze"    # Updated on each run

company: "Company Name"
url: "https://example.com"

# Mode
source_mode: "observe"                        # observe | compare
guide_provided: false                         # true if brand docs were supplied
guide_sources: []                             # list of { path_or_url, format, voice_sections_found }

# Extraction summary
pages_analyzed: 12                            # Count of usable pages (after chrome-only exclusions)
pages_extracted: 15                           # Total pages extracted (before exclusions)
page_categories:
  landing: 5
  product: 4
  thought_leadership: 3
  case_study: 1
  company: 1
  blog: 1
  other: 0

# Voice summary (machine-readable for downstream consumption)
voice_confidence: 4                           # 1-5
consistency_rating: "moderate"                # high | moderate | low
primary_tone:                                 # 3-5 adjectives
  - authoritative
  - institutional
  - solution-oriented
rhetorical_mode: "authority"                  # authority | logic | social_proof | empathy | urgency
sentence_length_avg: "long (19-25)"           # short (8-14) | medium (14-19) | long (19-25) | very_long (25+)
person: "first_plural"                        # first_plural | third_person | second_person | mixed
jargon_tolerance: "high"                      # low | medium | high
example_count: 33                             # Total examples across Example Library
rule_count: 15                                # Total voice rules
tension_count: 0                              # 0 in observe mode unless intra-site contradictions found

# Soft dependency status
competitive_landscape_available: false        # true if competitive-landscape.md was consumed
company_identity_available: false             # true if company-identity.md was consumed

notes: |
  Optional. Free-text notes about extraction limitations, excluded pages, etc.
---
```

**Downstream consumption pattern:** Read frontmatter first. If the structured summary has sufficient data for your needs (primary_tone, person, consistency_rating, rhetorical_mode), use it. Read the full body only when you need the analytical narrative, specific examples, or voice rules.

### Confidence Scoring

| Score | Criteria |
|-------|----------|
| 1 | Fewer than 5 usable pages, single content type, minimal examples |
| 2 | 5-8 usable pages, 2 content types, example library has significant gaps |
| 3 | 9-11 usable pages, 3 content types, all REQUIRED sections populated |
| 4 | 12-15 usable pages, 4+ content types, rich example library, clear patterns |
| 5 | Compare mode only. 12+ pages, 4+ types, brand docs validate observed patterns |

Observe mode caps at 4. Without a brand guide to validate against, you cannot confirm whether observed patterns are intentional voice choices or accidental drift.

---

## Body Sections

### 1. Voice DNA (REQUIRED)

```markdown
## Voice DNA

### Tone Spectrum

**Formality: N/10 (Label)**
[1-2 sentence narrative]

- "[verbatim quote]" (source_url)
- "[verbatim quote]" (source_url)
- "[verbatim quote]" (source_url)

**Confidence: N/10 (Label)**
[repeat pattern]

**Warmth: N/10 (Label)**
**Complexity: N/10 (Label)**
**Energy: N/10 (Label)**

### Person and Perspective

**Grammatical person:** [description with examples]
**Point of view:** [description]
**Direct address frequency:** High | Medium | Low [with evidence]

### Sentence Architecture

**Average sentence length:** N words (sampled across 30+ sentences)
**Range:** N words (shortest example) to N words (longest example)
**Complexity:** [classification with examples]
**Opening patterns:**
- [pattern name]: "[example]"
- [pattern name]: "[example]"
**Paragraph length:** [by content type]
**Overall bucket:** "[short|medium|long|very_long] (N-N)"

### Persuasion Mode

| Mode | Frequency | Pages Where Dominant |
|------|-----------|---------------------|
| Authority | N/pages_analyzed | [page list] |
| Logic | N/pages_analyzed | [page list] |
| Social proof | N/pages_analyzed | [page list] |
| Empathy | N/pages_analyzed | [page list] |
| Urgency | N/pages_analyzed | [page list] |

**Primary mode: [Mode].** [2-3 sentence narrative]
**Secondary mode: [Mode].** [1-2 sentence narrative]
```

**Five tone dimensions (always these five, always 1-10):**
- **Formality:** 1 = casual/conversational, 10 = institutional/formal
- **Confidence:** 1 = tentative/hedging, 10 = assertive/absolute claims
- **Warmth:** 1 = cool/analytical, 10 = empathetic/emotional
- **Complexity:** 1 = plain language/accessible, 10 = technical/jargon-dense
- **Energy:** 1 = calm/measured, 10 = urgent/high-energy

Each dimension requires exactly 3 verbatim examples with source URLs.

### 2. Vocabulary Fingerprint (REQUIRED)

```markdown
## Vocabulary Fingerprint

### High-Frequency Terms

| Term | Count | Category | Example Usage (URL) |
|------|-------|----------|-------------------|
| [term] | N+ | core | "[usage]" (url) |

### Signature Constructions

**1. [Pattern name] (N+ occurrences)**
[Description]
- "[example]" (url)
- "[example]" (url)
- "[example]" (url)

### Avoided Vocabulary

| Avoided Term | Competitor Owner | Notes |
|-------------|-----------------|-------|
| [term] | [competitor] | [why avoided] |

### Jargon Tolerance

**Classification: [Low | Medium | High]**
[Evidence paragraph with examples]
```

**Targets:**
- High-Frequency Terms: 12-15 entries
- Signature Constructions: 4-6 patterns, each with 3+ examples
- Avoided Vocabulary: 4-8 entries (requires `competitive-landscape.md`; degrades to `[INCOMPLETE - no competitive data]` without it)
- Jargon Tolerance: always populated

**Category values for High-Frequency Terms:** `core` (brand-defining), `product` (product/feature language), `domain` (industry terminology), `brand` (trademarked/branded phrases), `positioning` (differentiation language), `outcome` (customer outcome language), `scale` (scale/coverage claims)

### 3. Example Library (REQUIRED)

Five subsection tables, each with columns: # | Quote | Source URL | Content Type | Why Included

```markdown
## Example Library

### Headlines (N)

| # | Quote | Source URL | Content Type | Why Included |
|---|-------|-----------|-------------|-------------|
| 1 | "[verbatim]" | url | [type] | [rationale] |

### Body Passages (N)
### CTAs (N)
### Proof Language (N)
### Transitional Phrases (N)
```

**Minimum counts:**

| Subsection | Minimum | Target |
|------------|---------|--------|
| Headlines | 6 | 8+ |
| Body Passages | 6 | 8+ |
| CTAs | 4 | 5+ |
| Proof Language | 4 | 6+ |
| Transitional Phrases | 4 | 6+ |

**Total target: 33+ examples.** Every example must be verbatim from extracted content with source attribution. No paraphrasing, no invented examples.

### 4. Consistency Map (REQUIRED)

```markdown
## Consistency Map

### [Content Type] ([N] usable: [page list])

**Voice summary:** [2-3 sentences]
**Comparison to overall:** [2-3 sentences]
**Classification: [Consistent | Partial | Divergent]**

### Overall Consistency Rating: **[high | moderate | low]**

[Narrative paragraph explaining the rating]
```

One subsection per content type that had usable pages. Content types with 0 usable pages get: `[NOT ASSESSED - no [type] pages available in extraction corpus]`

**Consistency rating criteria (same as audience-messaging.md Voice Consistency Rating):**
- **high:** Same person + same tone adjectives + consistent vocabulary across all content types + 0-1 Partial classifications
- **moderate:** Person or tone shifts on 1-2 content types OR 2-3 Partial classifications OR branded pages consistent but secondary pages differ
- **low:** Person shifts on 3+ content types OR no common tone adjectives OR 4+ Partial/Divergent classifications

### 5. Voice Rules (REQUIRED)

```markdown
## Voice Rules

### [Category] Rules

**N. [Rule name]**
Category: [structural | vocabulary | tone | proof | channel_override]
Instruction: [1-3 actionable sentences]
Example: "[verbatim quote]" (url)
```

**Targets:** 10-15 rules (minimum 6).

**Category distribution target:**
- structural: 2-4 (sentence length, paragraph structure, heading patterns)
- vocabulary: 3-5 (approved terms, avoided terms, signature constructions)
- tone: 2-3 (confidence level, warmth register, formality)
- proof: 1-2 (numeric formatting, social proof patterns)
- channel_override: 1-2 (thought leadership register shifts, campaign energy)

**Rule quality requirements:**
- **Testable:** A reviewer can read a piece of copy and determine if it follows or breaks the rule.
- **Company-specific:** Not generic writing advice. "Use active voice" fails. "Use triple-verb imperative constructions for capability statements" passes.
- **Evidence-grounded:** Every rule has at least one verbatim example from the extraction corpus.

### 6. Tensions (CONDITIONAL)

```markdown
## Tensions

### In observe mode:
*No tensions identified in observe mode.*
OR
| Tension | Where It Appears | Severity | Notes |

### In compare mode (REQUIRED):
| Tension | Brand Guide Says | Site Shows | Severity | Recommendation |
|---------|-----------------|------------|----------|---------------|
```

- **Observe mode:** Only populated if the agent finds contradictions within the site itself (e.g., homepage claims "We simplify complexity" while product pages use impenetrable jargon).
- **Compare mode:** REQUIRED. Every mismatch between brand guide directives and observed content. Severity: `high` (directly contradicts guide), `moderate` (drifts from guide), `low` (minor inconsistency).

---

## Quality Checklist

Before writing the final file, verify:

- [ ] YAML frontmatter has all required fields
- [ ] `pages_analyzed` matches actual usable page count
- [ ] `example_count` matches actual example count in Example Library
- [ ] `rule_count` matches actual rule count in Voice Rules
- [ ] All 5 REQUIRED sections present (Voice DNA, Vocabulary Fingerprint, Example Library, Consistency Map, Voice Rules)
- [ ] Tone Spectrum has exactly 5 dimensions, each scored 1-10 with 3 examples
- [ ] Every example in Example Library has a source URL that appears in `_voice-extractions.md`
- [ ] No example is paraphrased (all verbatim from extractions)
- [ ] Voice Rules >= 6 count
- [ ] Voice Rules span at least 3 categories
- [ ] In compare mode: Tensions section populated with at least 1 entry (or explicit "no tensions found" with rationale)
- [ ] Consistency rating matches the criteria (high/moderate/low aligned with Partial/Divergent count)
- [ ] No system internals in output (no file paths, no agent references, no skill names in body text)
- [ ] `confidence` score follows the confidence scale criteria

---

## Relationship to audience-messaging.md

When `brand-voice.md` exists with `voice_confidence >= 3`, the positioning-framework's messaging phase (Agent 3) defers to it:

- Writes abbreviated Voice Profile (Section 12) referencing brand-voice.md
- Copies Voice Rules (Section 18) verbatim from brand-voice.md
- Builds Language Bank (Section 15) from Vocabulary Fingerprint
- Skips Channel Consistency Audit (Section 13) and Competitor Voice Comparison (Section 14)
- Sets `voice_source: "brand-voice.md"` in audience-messaging.md frontmatter

When `brand-voice.md` is absent or `voice_confidence < 3`, the messaging phase performs its own voice analysis (current behavior, unchanged).
