---
fe-managed: true
name: gold-battle-card
title: Gold Battle Card
description: >
  Fixture artifact type for a one-page battle card on one competitor of a scope's company,
  composed from the scope's competitive analysis.
governed_by: kb-start/artifact-type
managed_by: change-management
version: "1.0.0"
created: 2026-11-23
updated: 2026-11-23
field_definitions:
  kb_layer:
    type: string
    required: true
    value: gold
  scope:
    type: string
    required: true
  competitor:
    type: string
    required: true
  data_provenance:
    type: string
    required: true
  review_approved:
    type: boolean
    required: true
  depends_on:
    type: array
    required: true
---
# Gold Battle Card

A one-page competitor reference for sales and marketing, one per major competitor.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope whose company the card serves. |
| `competitor` | string | Yes | The competitor's name, as the competitive analysis gives it. |
| `data_provenance` | string | Yes | `client` when the consumed silver is client-provenance, else `public`. |
| `review_approved` | boolean | Yes | Whether a reviewer approved this version for sharing. Default: `false`. Only a reviewer sets it to `true`. |
| `depends_on` | array | Yes | KB-root-relative paths of the silver artifacts composed. |

## Output Path

**Output path:** `deliverables/battle-cards/{scope}-{competitor-slug}.md`

`{competitor-slug}` is the competitor's name as a lowercase hyphenated slug.
