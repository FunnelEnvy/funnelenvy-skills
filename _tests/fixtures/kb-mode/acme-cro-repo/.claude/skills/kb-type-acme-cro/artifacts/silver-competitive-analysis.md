---
fe-managed: true
name: silver-competitive-analysis
title: Silver Competitive Analysis
description: >
  Fixture artifact type for a scope's competitive landscape: market overview, competitor
  profiles with battle card data, claim overlap and white space.
governed_by: kb-start/artifact-type
managed_by: change-management
version: "1.0.0"
created: 2026-11-23
updated: 2026-11-23
field_definitions:
  kb_layer:
    type: string
    required: true
    value: silver
  scope:
    type: string
    required: true
  data_provenance:
    type: string
    required: true
  confidence:
    type: number
    required: true
  depends_on:
    type: array
    required: true
---
# Silver Competitive Analysis

A scope's competitive landscape. Holds what `competitive-landscape.md` holds in legacy mode.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope covered. |
| `data_provenance` | string | Yes | `public` or `client`. |
| `confidence` | number | Yes | 1 to 5. |
| `depends_on` | array | Yes | The bronze and silver artifacts analyzed. |

## Output Path

**Output path:** `reference/cro-{scope}/competitive-analysis.md`
