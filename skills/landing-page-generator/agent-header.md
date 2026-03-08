# Landing Page Generator: Shared Agent Rules

> Read by all phase agents. Do NOT read the full SKILL.md. This file contains everything you need.

---

## Accuracy Over Completeness

- Never fabricate proof points, metrics, case studies, or testimonials. Every claim must trace to a source in the context files or be confirmed by the human.
- If a proof point is missing for a section, flag it as `[GAP]` and explain what's needed. Do not substitute generic copy.
- Preserve exact numbers and attribution from context files. "96% reduction in reconciliation time" stays exactly that. Do not paraphrase metrics.
- If context files contain contradictions (e.g., different NPS figures across files), flag the contradiction and ask the human to confirm.

## Context Files Reference

| File | Layer | What It Contains | Frontmatter Key Fields |
|------|-------|-----------------|----------------------|
| company-identity.md | L0 | Company facts, target market, segments | company.name, company.url, target_market, confidence |
| audience-messaging.md | L1 | Personas, value themes, voice, proof points | persona_count, personas, tone, voice_consistency, confidence |
| competitive-landscape.md | L1 | Competitor analysis, white spaces, claim overlap | competitors_analyzed, top_competitors, white_spaces, confidence |
| positioning-scorecard.md | L1 | Dimension ratings, gaps, opportunities | ratings, top_gap, top_opportunity, confidence |
| performance-profile.md | L1 | GA4 data, traffic, conversions, channels | total_sessions, conversion_events, top_channels, traffic_adequacy, confidence |

**Reading protocol:** Always read frontmatter first (~200 tokens). Only load the full body when the phase instructions say to. This saves tokens and keeps the context window clean.

## Campaign Deliverables Directory

All outputs for a campaign go to:
```
.claude/deliverables/campaigns/<campaign-slug>/
```

Files in this directory:
| File | Produced By | Consumed By |
|------|------------|-------------|
| brief.md | Phase 1 (Brief) | Phase 2 (Copy) |
| copy.md | Phase 2 (Copy) | Phase 3 (Design) |
| page.html | Phase 3 (Design) | Phase 4 (QA) |
| qa-report.md | Phase 4 (QA) | Human review |

## Frontmatter Rules

Every output file must include YAML frontmatter. Minimum fields:

```yaml
schema: <file-type>
schema_version: "1.0"
client: <company-name>
campaign: <campaign-slug>
generated_by: "landing-page-generator/<phase-name>"
last_updated: <ISO-8601 date>
```

Additional fields are defined per phase. See the phase file for the complete schema.

## Content Integrity Rules

1. **One persona per campaign.** Never blend messaging from multiple personas in a single landing page. If the brief specifies "CFO (PE-Backed)," every section addresses that persona only.
2. **Proof before claim.** If a headline or card lacks a supporting proof point, it goes in body copy, not in a headline. Flag the gap.
3. **Message match.** The landing page headline must echo the target keywords or ad copy from the brief. If the ad says "interim CFO," the page says "interim CFO."
4. **Banned terms are absolute.** Check the language guidance from the context files before generating any copy. Violations are not acceptable.
5. **Stage isolation.** Each phase reads only its specified inputs. Phase 3 (Design) does not re-read positioning context. It reads copy.md only. If something is wrong with the copy, flag it but do not change it.

## Voice Rules (from context)

When `audience-messaging.md` is available, extract and follow:
- Brand voice description (Sounds Like / Doesn't Sound Like)
- Voice rules (numbered list)
- Language guidance (Use This / Not This)
- Required disclaimers

When voice context is unavailable, ask the human for:
- 3 adjectives describing brand voice
- Any terms to avoid
- Required legal disclaimers

## Em Dashes

Never use em dashes anywhere. Use colons, commas, or separate sentences instead.
