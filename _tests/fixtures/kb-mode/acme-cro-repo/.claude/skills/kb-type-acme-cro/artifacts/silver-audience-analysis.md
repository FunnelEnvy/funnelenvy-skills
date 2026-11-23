---
fe-managed: true
name: silver-audience-analysis
title: Silver Audience Analysis
description: >
  Fixture artifact type for a scope's audience and messaging analysis: positioning statement,
  personas, message hierarchy and voice rules.
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
# Silver Audience Analysis

A scope's personas, messaging and voice. Holds what `audience-messaging.md` holds in legacy mode.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope covered. |
| `data_provenance` | string | Yes | `public` or `client`. |
| `confidence` | number | Yes | 1 to 5. |
| `depends_on` | array | Yes | The scope's `silver-strategy-context` path. |

## Output Path

**Output path:** `reference/cro-{scope}/audience-analysis.md`
