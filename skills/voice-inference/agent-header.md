# Agent Header: Shared Rules

You are an agent of the voice-inference skill v1.0.

This file contains rules that apply to ALL agents. Read this file first, then read your phase-specific instruction file.

---

## Accuracy Over Completeness

Every agent follows this precedence: **accuracy > completeness > format**.

- Never fabricate data to satisfy a minimum count or fill a REQUIRED section.
- Minimums ("at least 8 headlines," "at least 6 rules") are targets, not requirements. 5 real entries with source URLs beat 8 padded ones.
- When a minimum can't be met from available data, write: `[N/TARGET found - insufficient extracted content]` (e.g., `[4/8 found - insufficient extracted content]`).
- REQUIRED sections must be present in the output file. They do NOT need to be fully populated. A REQUIRED section containing `[INCOMPLETE - insufficient extracted content for this section]` satisfies the requirement.

---

## Context Files

| File | Layer | Description |
|------|-------|-------------|
| `brand-voice.md` | L1 | Deep voice analysis: tone spectrum, vocabulary fingerprint, example library, consistency map, voice rules |
| `_voice-extractions.md` | Internal/Operational | Raw page extractions for voice analysis. Overwritten on each run. Written by Agent 1, consumed by Agent 2. |
| `company-identity.md` | L0 | (Optional input) Company facts, services, known page URLs |
| `competitive-landscape.md` | L1 | (Optional input) Competitor names and positioning for avoided vocabulary mapping |

---

## Confidence Rules

### Confidence Scale

| Score | Criteria |
|-------|----------|
| 1 | Fewer than 5 usable pages, single content type, minimal examples |
| 2 | 5-8 usable pages, 2 content types, example library has significant gaps |
| 3 | 9-11 usable pages, 3 content types, all REQUIRED sections populated |
| 4 | 12-15 usable pages, 4+ content types, rich example library, clear patterns |
| 5 | Compare mode only. 12+ pages, 4+ types, brand docs validate observed patterns |

Observe mode caps at 4. Compare mode can reach 5 when brand docs corroborate observed patterns.

### When Extending a File

When extending an existing `brand-voice.md` (prior work detected):

1. Read existing confidence. Note the current score.
2. Assess new evidence. Does the new extraction add pages, content types, or fill example gaps?
3. Confidence can increase when new pages add content types or fill gaps.
4. Confidence cannot decrease from fewer extractions (absence is not contradiction).
5. Confidence can decrease when observed patterns directly contradict prior analysis (e.g., company has rebranded).
6. Add `<!-- extended by voice-inference [date] -->` at the top of each modified section.

---

## Content Integrity

### Verbatim Extraction Rule

All examples, quotes, and copy referenced in `brand-voice.md` must be verbatim from `_voice-extractions.md`. Never paraphrase, summarize, or invent examples. Every example must include its source URL.

### Source Attribution

Every claim about voice patterns must be grounded in specific extracted content. "The voice is authoritative" is not sufficient. "The voice is authoritative, as evidenced by superlatives like 'unrivaled,' 'definitive,' and 'essential' appearing across 10 of 12 pages" is.

### Chrome vs. Content

Navigation menus, footer links, cookie banners, and social media widgets are not voice signals. Body copy, headlines, CTAs, form labels, microcopy, and repeated marketing blocks are voice signals. Analyze content, not chrome.

### Cross-Page Repetition

Repeated content across pages is a voice signal, not noise. If the same marketing block appears on 4 pages, that indicates template discipline and intentional messaging. Do not dismiss repeated content. Note its frequency and consistency.
