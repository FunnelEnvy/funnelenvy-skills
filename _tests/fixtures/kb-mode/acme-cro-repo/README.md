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
3. Delete `README.md` from the copy. It names the planted conditions and the behavior each one expects, so a runner must not read it.
4. Record `find kb -type f -exec sha256sum {} +` in the copy, to tell later what a run wrote.
5. Run the skill with the copy as the working repo and `--scope acme`.

## Layout

- **Root `CLAUDE.md`:** `Knowledge Bases` section naming KB root `kb/` and type skill `kb-type-acme-cro`.
- **`.claude/skills/kb-type-acme-cro/`:** The type skill, with valid scope `acme`, and one type definition per artifact type in `artifacts/`.
- **`kb/captures/company-facts/`:** The bronze company facts.
- **`kb/captures/notes/`:** One bronze note capture, the input for positioning-update runs. It uses kb-start's shared `bronze-note-capture` type, so the fixture type skill defines no type for it.
- **`kb/reference/cro-acme/`:** The four silver inputs: strategy context, positioning scorecard, audience analysis and competitive analysis. Each is at confidence 4 with `data_provenance: public`.
- **`kb/deliverables/`:** Two prior gold renders, described under `Planted Conditions`.

## Planted Conditions

Each condition exercises one arm of the render-default-deliverables 1.2.0 KB mode.

1. **Values:** `gold-strategy-deliverable` allows `exec-summary`, `messaging-guide` and `competitive-matrix`, with output path `deliverables/{scope}-{deliverable_type}.md`. None of them is the old default `executive-summary` or `competitive-comparison-matrix`.
2. **Card path:** `gold-battle-card` sets `deliverables/battle-cards/{scope}-{competitor-slug}.md` and requires `competitor`. The old default was `battle-cards/` at the KB root.
3. **Prose defaults and field classes:** Both gold types require a boolean `review_approved`, described as recording a reviewer's approval of one version, so it is tied. `gold-strategy-deliverable` adds two optional booleans. `confidential` holds across versions, so it is standing. `sales_ready` says neither, so it is unclear. Only the prose states each default, `false`.
4. **Prior at the resolved path:** `kb/deliverables/acme-messaging-guide.md` carries `review_approved: true`, `confidential: true`, `sales_ready: true`, `source_name`, `source_ref`, `created: 2026-10-01` and `version: "1.0.0"`. The plan must list `review_approved` as reset to `false` and `confidential: true` as kept at a non-default value, and must ask Reset or Keep for `sales_ready`. An overwrite must reset `review_approved`, keep `confidential`, `source_name`, `source_ref` and `created`, apply the operator's answer to `sales_ready`, and raise the version.
5. **Prior at another path:** `kb/deliverables/acme-competitive-comparison-matrix.md` is set to `deliverable_type: competitive-matrix` and carries no `generated_by`. Nothing exists at `kb/deliverables/acme-competitive-matrix.md`, the path that value resolves to.

## Positioning Update Input

`kb/captures/notes/2026-11-20_acme-positioning-update.md` is the input for positioning-update 1.1.0 KB-mode runs. It carries no `scope`, since a capture can span scopes. Its `## Note` holds two items:

1. **Correction:** Acme has about 140 employees, not 120. The fact lives only in the company facts' `Company Overview`, so it targets `bronze-company-facts`.
2. **Addition:** Buying cooperatives of independent distributors are a new target segment. Neither L0 artifact names them. By positioning-framework's L0 section table, target segments belong to `silver-strategy-context`.

The strategy context's type declares `depends_on` and `data_provenance`, and the company facts' type declares neither. The audience analysis depends on the strategy context, and the competitive analysis on the company facts, so both are stale after a run that amends the two L0 artifacts.

The company facts departs from positioning-framework's bronze contract in two places. Its `Target Segments` section belongs in the strategy context by the L0 section table, and its `data_provenance: public` is a field positioning-framework writes on silver only. So a run leaves the bronze `Target Segments` unamended, and a client run leaves `data_provenance: public` beside `has_client_input: true`. A kb-start review flags both. Neither is a skill defect.

Run commands, each on a fresh copy made per `Run Setup`:

- **Run 1, input outside the KB:** `/positioning-update --scope acme --file CLAUDE.md --context-dir foo`. The copy's root `CLAUDE.md` sits outside `kb/` and has no `kb_layer`, so the path names no bronze artifact inside the KB.
- **Run 2, research input:** `/positioning-update --scope acme --file kb/captures/notes/2026-11-20_acme-positioning-update.md --provenance research`
- **Run 3, client input:** `/positioning-update --scope acme --file kb/captures/notes/2026-11-20_acme-positioning-update.md --provenance client --skip-render`

## Left Out

The fixture holds only what a full three-tier render needs. It has no `bronze-research-extraction` or `bronze-fetch-registry` type, so positioning-framework's KB-mode gate does not pass here. It also has no roadmap types, no second scope, no `.claude/context/` legacy files, no client-provenance input, no orphaned battle cards and no Python. A later change adds what its own run needs.
