# _fetch-registry.md Schema Reference

**Layer:** Operational metadata (not L0 or L1)
**Location:** `.claude/context/_fetch-registry.md`
**Schema version:** 1.0
**Produced by:** Agent 1 (`phases/research.md`)
**Consumed by:** Agent 2 (`phases/competitive.md`)
**Appended by:** Agent 2 (`phases/competitive.md`)

---

## Purpose

Coordination file that prevents duplicate fetches across agents. Agent 1 logs every URL it fetches. Agent 2 reads the registry before fetching and skips URLs where usable data already exists in L0. Agent 2 appends its own fetches after completing.

Not consumed by Agent 3 or Agent 4 (neither makes web requests).
Not consumed by render-deliverables (does not need fetch metadata).

---

## Frontmatter

```yaml
schema: fetch-registry
schema_version: "1.0"
generated_by: str           # skill + agent that created the file
last_updated: str           # ISO date
last_updated_by: str        # skill + agent that last appended
total_fetches: int          # total rows in the table
```

## Body

Markdown table with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| URL | string | Full URL fetched |
| Agent | string | Which agent fetched it (e.g., "Agent 1", "Agent 2") |
| Tag | string | Extraction quality tag: `[FULL]`, `[PARTIAL]`, `[PARTIAL:TOOL]`, `[PARTIAL:FALLBACK]`, `[EMPTY:SPA]`, `[EMPTY:BLOCKED]` |
| Words | int | Word count extracted |
| Key Content | string | Brief description of what was found |

## Rules

- Agents append rows. Never delete or overwrite existing rows.
- Agent 2 must read the registry before fetching. If a URL is already present with tag `[FULL]` or `[PARTIAL]` and the data it needs exists in L0, skip the fetch.
- The underscore prefix in the filename signals operational metadata. Downstream consumers that glob `.claude/context/*.md` for L0/L1 files should exclude files starting with `_`.
- No confidence score. This file tracks operational state, not analytical confidence.

## Classification

This file is NOT L0 (facts) or L1 (analysis). It is operational metadata used for cross-agent coordination. It has no downstream consumers beyond Agent 2. render-deliverables should ignore it. Future skills that glob context files should filter it out by the underscore prefix.
