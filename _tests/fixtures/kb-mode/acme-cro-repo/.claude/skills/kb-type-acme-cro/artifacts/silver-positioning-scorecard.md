---
fe-managed: true
name: silver-positioning-scorecard
title: Silver Positioning Scorecard
description: >
  Fixture artifact type for a scope's positioning health check: categorical ratings per
  dimension, gap analysis and priority recommendations.
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
# Silver Positioning Scorecard

A scope's positioning health check. Holds what `positioning-scorecard.md` holds in legacy mode.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope covered. |
| `data_provenance` | string | Yes | `public` or `client`. |
| `confidence` | number | Yes | 1 to 5. |
| `depends_on` | array | Yes | The silver and bronze artifacts scored. |

## Output Path

**Output path:** `reference/cro-{scope}/positioning-scorecard.md`
