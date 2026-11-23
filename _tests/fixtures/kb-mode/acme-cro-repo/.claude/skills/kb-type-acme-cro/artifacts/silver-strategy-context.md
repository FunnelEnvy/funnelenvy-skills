---
fe-managed: true
name: silver-strategy-context
title: Silver Strategy Context
description: >
  Fixture artifact type for the analysis portion of a scope's company identity: category,
  target segments, category gap and business constraints.
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
# Silver Strategy Context

The strategic reading of a scope's company facts. Together with `bronze-company-facts`, it carries what `company-identity.md` carries in legacy mode.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope covered. |
| `data_provenance` | string | Yes | `public` or `client`. |
| `confidence` | number | Yes | 1 to 5. |
| `depends_on` | array | Yes | The scope's `bronze-company-facts` path. |

## Output Path

**Output path:** `reference/cro-{scope}/strategy-context.md`
