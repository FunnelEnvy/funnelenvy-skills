---
fe-managed: true
name: bronze-company-facts
title: Bronze Company Facts
description: >
  Fixture artifact type for the verifiable facts about a scope's company: overview, services,
  stated differentiators, proof points and pricing. No analysis.
governed_by: kb-start/artifact-type
managed_by: change-management
version: "1.0.0"
created: 2026-11-23
updated: 2026-11-23
field_definitions:
  kb_layer:
    type: string
    required: true
    value: bronze
  scope:
    type: string
    required: true
  confidence:
    type: number
    required: true
---
# Bronze Company Facts

Raw facts about a scope's company. Holds what `company-identity.md` holds in legacy mode, minus the analysis.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope the facts cover. |
| `confidence` | number | Yes | 1 to 5. |

## Output Path

**Output path:** `captures/company-facts/{scope}-company-facts.md`
