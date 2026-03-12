# Campaign Brief Schema Reference

> **Schema:** campaign-brief
> **Version:** 1.1
> **Authoritative source:** Inline schema in `skills/landing-page-generator/phases/brief.md` Step 6
> **This file:** Human-readable reference copy only. If this file diverges from the phase file, the phase file wins.

---

## Frontmatter Fields

```yaml
schema: campaign-brief              # Fixed value
schema_version: "1.1"               # Semver string
client: str                          # Company name from company-identity.md
campaign: str                        # Kebab-case campaign slug
service_line: str                    # Service or offer name
target_persona: str                  # Persona title + qualifier
target_keywords: [str]               # Search terms driving traffic
traffic_awareness_stage: str         # unaware | problem_aware | solution_aware | product_aware | most_aware
traffic_source: str                  # paid_search | paid_social_cold | paid_social_retargeting | email | organic | referral | direct
offer_type: str                      # demo | consultation | content | quote
form_strategy:
  fields: int                        # Number of form fields
  type: str                          # lightbox | embedded | multi-step
  enrichment_tool: bool              # Whether client uses ZoomInfo/Clearbit/etc.
post_submit: str                     # calendar | asset | thankyou
proof_points_count: int              # Total proof points in the brief
gaps: [str]                          # Unresolved IMPORTANT gaps
depth: str                           # standard | deep
generated_by: str                    # "landing-page-generator/brief"
last_updated: str                    # ISO-8601 date
```

## Companion Schemas (output by other phases)

### campaign-copy (Phase 2 output)

```yaml
schema: campaign-copy
schema_version: "1.0"
client: str
campaign: str
headline_approach: str               # pain | keyword | proof | all-three
recommended_headline: str            # A | B | C
cta_text: str                        # Exact CTA button text
sections_with_proof: int             # Count of sections containing proof points
gaps_carried_forward: [str]
word_count: int
generated_by: str                    # "landing-page-generator/copy"
last_updated: str
```

### qa-report (Phase 4 output)

```yaml
schema: qa-report
schema_version: "1.0"
client: str
campaign: str
files_checked: [str]                 # Which files were QA'd
copy_checks: str                     # "X/Y" pass count
design_checks: str                   # "X/Y" pass count
cross_checks: str                    # "X/Y" pass count
overall: str                         # PASS | FAIL
generated_by: str                    # "landing-page-generator/qa"
last_updated: str
```

### page.html (Phase 3 output)

No YAML frontmatter (HTML file). Metadata stored in an HTML comment block at the top of the file. See phases/design.md Step 7 for format.

---

## Consumption Patterns

| Consumer | Reads | Uses frontmatter for |
|----------|-------|---------------------|
| phases/copy.md (Phase 2) | brief.md | Validates preconditions, extracts target_keywords, cta_text, form_strategy, gaps |
| phases/design.md (Phase 3) | copy.md | Not read (stage isolation). Reads copy.md body only. |
| phases/qa.md (Phase 4) | brief.md, copy.md, page.html | Cross-references keywords, CTA text, banned terms, field count |

---

*Schema reference v1.1 | Last updated March 2026*
