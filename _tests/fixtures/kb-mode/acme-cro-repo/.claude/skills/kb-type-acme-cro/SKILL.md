---
name: kb-type-acme-cro
description: "Test fixture only. Fictional CRO knowledge base type for the KB-mode fixture under _tests/fixtures/kb-mode/acme-cro-repo/ in the funnelenvy-skills repo. Not a live skill. Never invoke it; a KB-mode run reads it as a file inside a run copy of the fixture."
disable-model-invocation: true
---

# Acme CRO KB Type (Test Fixture)

Fixture KB type skill for the fictional company Acme. It gives a KB-mode skill run a bound type to read. A run reads this file and its `artifacts/` directory as files. Nothing invokes it as a skill.

## Valid Scopes

| Scope | Company |
|---|---|
| `acme` | Acme (fictional) |

`acme` is the only valid scope.

## Directory Layout

Paths are relative to the KB root, `kb/`.

| Directory | Layer | Artifact types |
|---|---|---|
| `captures/company-facts/` | Bronze | `bronze-company-facts` |
| `reference/cro-{scope}/` | Silver | `silver-strategy-context`, `silver-positioning-scorecard`, `silver-audience-analysis`, `silver-competitive-analysis` |
| `deliverables/` | Gold | `gold-strategy-deliverable` |
| `deliverables/battle-cards/` | Gold | `gold-battle-card` |

## Artifact Types

| Artifact type | Layer | Output path |
|---|---|---|
| [bronze-company-facts](artifacts/bronze-company-facts.md) | Bronze | `captures/company-facts/{scope}-company-facts.md` |
| [silver-strategy-context](artifacts/silver-strategy-context.md) | Silver | `reference/cro-{scope}/strategy-context.md` |
| [silver-positioning-scorecard](artifacts/silver-positioning-scorecard.md) | Silver | `reference/cro-{scope}/positioning-scorecard.md` |
| [silver-audience-analysis](artifacts/silver-audience-analysis.md) | Silver | `reference/cro-{scope}/audience-analysis.md` |
| [silver-competitive-analysis](artifacts/silver-competitive-analysis.md) | Silver | `reference/cro-{scope}/competitive-analysis.md` |
| [gold-strategy-deliverable](artifacts/gold-strategy-deliverable.md) | Gold | `deliverables/{scope}-{deliverable_type}.md` |
| [gold-battle-card](artifacts/gold-battle-card.md) | Gold | `deliverables/battle-cards/{scope}-{competitor-slug}.md` |

Each artifact type's own file is the authority for its fields, allowed values and output path. The table above is a map.

The fixture defines no `bronze-research-extraction` or `bronze-fetch-registry` type, so a skill whose KB-mode gate needs all seven CRO types falls back to legacy mode here.
