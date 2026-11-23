# Acme CRO Repo Fixture

A small fictional working repo with a bound CRO knowledge base, for running a skill's KB mode end to end. The company is Acme. Its competitors are Northwind and Globex. All three are fictional.

## Not Live Configuration

This directory holds a `CLAUDE.md` with a `Knowledge Bases` section, a KB root `kb/CLAUDE.md` and a type skill under `.claude/skills/`. They describe the fixture, not the funnelenvy-skills repo.

- **Instructions:** Both `CLAUDE.md` files open with a fixture notice. A session working on the funnelenvy-skills repo ignores them.
- **Type skill:** `kb-type-acme-cro` sets `disable-model-invocation: true` and says it is a fixture. A run reads it as a file.
- **Resources:** Rule 10 makes no directory under `_tests/fixtures/` a managed resource.

## Run Setup

Never run a skill against this directory in place. Every run uses a copy.

1. Copy the fixture to a dated directory under the repo's `tmp/`, such as `tmp/<date>_rdd-kb-run/`.
2. Run `git init -q` in the copy. The copy is then its own repo root, so the KB validator finds the repo-local type skill there.
3. Record `find kb -type f -exec sha256sum {} +` in the copy, to tell later what a run wrote.
4. Run the skill with the copy as the working repo and `--scope acme`.

## Layout

- **Root `CLAUDE.md`:** `Knowledge Bases` section naming KB root `kb/` and type skill `kb-type-acme-cro`.
- **`.claude/skills/kb-type-acme-cro/`:** The type skill, with valid scope `acme`, and one type definition per artifact type in `artifacts/`.
- **`kb/captures/company-facts/`:** The bronze company facts.
- **`kb/reference/cro-acme/`:** The four silver inputs: strategy context, positioning scorecard, audience analysis and competitive analysis. Each is at confidence 4 with `data_provenance: public`.
- **`kb/deliverables/`:** Two prior gold renders, described under `Planted Conditions`.

## Planted Conditions

Each condition exercises one arm of the render-default-deliverables 1.2.0 KB mode.

1. **Values:** `gold-strategy-deliverable` allows `exec-summary`, `messaging-guide` and `competitive-matrix`, with output path `deliverables/{scope}-{deliverable_type}.md`. None of them is the old default `executive-summary` or `competitive-comparison-matrix`.
2. **Card path:** `gold-battle-card` sets `deliverables/battle-cards/{scope}-{competitor-slug}.md` and requires `competitor`. The old default was `battle-cards/` at the KB root.
3. **Prose default:** Both gold types require a boolean `review_approved`. Only their prose states its default, `false`.
4. **Prior at the resolved path:** `kb/deliverables/acme-messaging-guide.md` carries `review_approved: true`, `source_name`, `source_ref`, `created: 2026-10-01` and `version: "1.0.0"`. An overwrite must keep the first four and raise the version.
5. **Prior at another path:** `kb/deliverables/acme-competitive-comparison-matrix.md` is set to `deliverable_type: competitive-matrix` and carries no `generated_by`. Nothing exists at `kb/deliverables/acme-competitive-matrix.md`, the path that value resolves to.

## Left Out

The fixture holds only what a full three-tier render needs. It has no `bronze-research-extraction` or `bronze-fetch-registry` type, so positioning-framework's KB-mode gate does not pass here. It also has no roadmap types, no second scope, no `.claude/context/` legacy files, no client-provenance input, no orphaned battle cards and no Python. A later change adds what its own run needs.
