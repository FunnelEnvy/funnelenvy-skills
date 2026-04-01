# Campaign Brief Schema Reference

> **Schema:** campaign-brief
> **Version:** 1.2
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
schema_version: "2.1"
client: str
campaign: str
headline_approach: str               # was: pain | keyword | proof | all-three
                                     # v2.0: matches hero variant slug: pain-lead | keyword-match | proof-lead
recommended_headline: str            # A | B | C
cta_text: str                        # Exact CTA button text
sections_with_proof: int             # Count of sections containing proof points
gaps_carried_forward: [str]
word_count: int
generated_by: str                    # "landing-page-generator/copy"
last_updated: str
# NEW in v2.0
sections: [{type: str, variant: str}]    # ordered section manifest
section_count: int                        # count of sections in manifest
objections_distributed_inline: int        # Pattern A objection count
objections_in_faq_block: int             # Pattern B objection count (0 if no FAQ section)
proof_points_used: [str]                 # P-IDs referenced in copy
# Brand component fields (present only when brand design system detected in Step 3.5)
component_degradations:           # omit entirely if no brand files detected
  - section: str
    original_variant: str
    resolved_variant: str
    component: str
    reason: str
    level: str                    # variant_degradation | section_removed | missing_component
component_degradation_count: int  # 0 if none, omit if no brand files
brand_design_system: str          # filename, omit if no brand files
brand_components_html: str        # filename, omit if no brand files
```

### qa-report (Phase 4 output)

```yaml
schema: qa-report
schema_version: "1.1"
client: str
campaign: str
files_checked: [str]                 # Which files were QA'd
copy_checks: str                     # "X/Y" pass count
design_checks: str                   # "X/Y" pass count
cross_checks: str                    # "X/Y" pass count
overall: str                         # PASS | FAIL
# Brand component fields (present only when brand design system detected)
brand_component_checks: str       # "X/Y" pass count, omit if no brand files
brand_component_violations: int   # BC- check failure count, omit if no brand files
brand_component_warnings: int     # BC-7 warning count, omit if no brand files
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

*Schema reference v1.2 | Last updated March 2026*
