# Schema: live-observation.md

> **Reference copy.** The authoritative schema is inlined in `skills/live-capture/phases/write.md`.
> This file is a human-readable reference for contributor orientation. If the two diverge, the
> phase file wins.

`live-observation.md` is a factual capture of a site's live page structure, produced by the
`live-capture` skill. Legacy mode writes it to `.claude/context/` as an L0 context file; KB mode
writes it as a `bronze-note-capture` and enriches the silver `silver-structural-observation`
artifact at `reference/cro-{scope}/live-structure.md`.

Facts and two permitted mechanical derivations only (`mobile_render_clean`, `nav_persona_segmented`).
No judgments. The consuming skills (hypothesis-generator detect, experiment-mockup) compute the
interpretation.

## Frontmatter (digest)

Site-level fast-path fields plus a per-page `pages:` digest so a consumer can decide whether a
pattern fires on a page without loading the body:

- Site level: `schema`, `schema_version`, `company`, `url`, `capture_date`, `capture_method`,
  `pages_captured`, `viewports`, `confidence` (coverage-weighted aggregate, not a min),
  `form_recurs_sitewide`, `sitewide_form_field_count`, `sitewide_form_required_field_count`,
  `sitewide_primary_cta_label`,
  `comparison_page_exists` / `roi_tool_exists` / `pricing_page_exists` (tri-state),
  `nav_persona_segmented` (derived).
- Per page (`pages[]`): `path`, `name` (human-readable page name), form fields (`form_present`, `form_field_count`,
  `form_required_field_count`, `form_embed`), CTA (`primary_cta_label`, `cta_count`), login
  (`login_present`, `login_above_fold`, `login_nav_rank`), proof (`named_client_proof_present`
  and `team_credibility_present`, both tri-state since they depend on below-fold lazy content;
  `proof_element_count`), sequential UI (`sequential_ui_present`,
  `sequential_ui_items`), `objection_faq_present` / `chatbot_present` (tri-state),
  `mobile_render_clean` (derived), `content_hash`, `page_block_status`, `page_confidence`.

## Body

Site-level section, then per-page blocks A-I + K plus a fixed `viewport_divergence` block. See
`skills/live-capture/phases/write.md` for the full block definitions and the confidence rubric.

## Tri-state and provenance

- Pass-dependent existence fields use `present | absent | not_checked`, never a bare `false`.
- On a content-blocked page (`page_block_status: akamai-403` or `challenge`, no content rendered), every pass-dependent tri-state field is `not_checked` by definition and the pass-dependent counts are `null`: a pass that never rendered content cannot assert `absent`.
- `capture_method` (capture fidelity) is distinct from KB `data_provenance` (buyer validation).
- Position encoding is `fold + ordinal + region`, never absolute pixels.
