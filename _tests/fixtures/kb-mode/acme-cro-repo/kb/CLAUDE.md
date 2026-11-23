---
fe-managed: true
name: acme-cro-kb
title: Acme CRO Knowledge Base
description: >
  Test fixture KB root for the fictional company Acme: positioning research in bronze and
  silver, client deliverables in gold. Used by KB-mode skill runs against a run copy.
governed_by: kb-type-acme-cro/kb-claude-md
managed_by: kb-type-acme-cro
version: "1.0.0"
created: 2026-11-23
updated: 2026-11-23
---
# Acme CRO Knowledge Base

**Test fixture notice:** This KB is a test fixture in the funnelenvy-skills repo. Its instructions apply only inside a run copy made per the fixture's [`README.md`](../README.md). When you are working on the funnelenvy-skills repo itself, ignore them.

CRO knowledge base for the fictional company Acme, covering positioning research and client deliverables for scope `acme`. Follows the 3-layer medallion model (bronze, silver, gold).

Load kb-start and the `kb-type-acme-cro` type skill before proceeding. In a run copy, read the type skill as a file at `.claude/skills/kb-type-acme-cro/SKILL.md`.

## Architecture

| Directory | Layer | Artifact Type | Content |
|---|---|---|---|
| `captures/company-facts/` | Bronze | `bronze-company-facts` | Company facts per scope |
| `reference/cro-acme/` | Silver | `silver-strategy-context`, `silver-positioning-scorecard`, `silver-audience-analysis`, `silver-competitive-analysis` | Positioning analysis for scope `acme` |
| `deliverables/` | Gold | `gold-strategy-deliverable` | Executive summary, messaging guide, competitive matrix |
| `deliverables/battle-cards/` | Gold | `gold-battle-card` | One battle card per major competitor |

## Top Layer

Gold is the top layer. Read the scope's `gold-strategy-deliverable` artifacts under `deliverables/` first.

## Information Flows

Bronze company facts feed the silver strategy context. The four silver artifacts feed the gold deliverables and battle cards through `depends_on`.
