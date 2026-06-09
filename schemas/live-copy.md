# Schema: live-copy.md

> **Reference copy.** The authoritative schema is inlined in `skills/live-capture/phases/write.md`.
> This file is a human-readable reference for contributor orientation. If the two diverge, the
> phase file wins.

`live-copy.md` is a verbatim capture of a site's live page copy, produced by the `live-capture`
skill. Legacy mode writes it to `.claude/context/` as an L0 context file; KB mode writes it as a
`bronze-research-extraction`. It supersedes older snapshots (e.g. Wayback) for positioning: a
consumer trusts `live-copy.md` over any source dated before its `capture_date`.

## Frontmatter

- `schema`, `schema_version`, `company`, `url`, `capture_date`, `capture_method`,
  `supersedes_source`, `pages_captured`, `confidence`.
- Per page (`pages[]`): `path`, `h1`, `hero_subhead_present`, `content_hash`, `page_block_status`.

## Body

Per page, timestamped: H1, hero subhead/H2, value-prop (verbatim); copy skeleton (all H2/H3
headings in document order plus the lead sentence under each, mechanical extraction); proof
statements (verbatim); optional candidate compliance/banned-term strings flagged for the consumer
(flag only; the consumer applies the banned list).

See `skills/live-capture/phases/write.md` for the authoritative schema.
