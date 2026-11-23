---
fe-managed: true
name: gold-strategy-deliverable
title: Gold Strategy Deliverable
description: >
  Fixture artifact type for a scope's client-ready strategy deliverables: the executive
  summary, the messaging guide and the competitive matrix, told apart by deliverable_type.
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
  deliverable_type:
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
# Gold Strategy Deliverable

One client-ready strategy deliverable for a scope, composed from the scope's silver artifacts.

## Frontmatter

| Name | Type | Required | Description |
|---|---|---|---|
| `scope` | string | Yes | The scope the deliverable covers. |
| `deliverable_type` | string | Yes | One of the allowed values below. |
| `data_provenance` | string | Yes | `client` when any consumed silver is client-provenance, else `public`. |
| `review_approved` | boolean | Yes | Whether a reviewer approved this version for sharing. Default: `false`. Only a reviewer sets it to `true`. |
| `depends_on` | array | Yes | KB-root-relative paths of the silver artifacts composed. |

### Allowed `deliverable_type` Values

- `exec-summary`: the executive summary, a positioning assessment for leadership.
- `messaging-guide`: the messaging guide, persona-by-persona messaging for copywriters.
- `competitive-matrix`: the competitive comparison matrix, a grid of the company against its competitors.

No other value is allowed.

## Output Path

**Output path:** `deliverables/{scope}-{deliverable_type}.md`
