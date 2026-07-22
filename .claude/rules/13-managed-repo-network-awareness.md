---
version: "0.1.0"
updated: 2026-07-20
---
# Managed Repo Network Awareness

This repo belongs to the fe-sys-hq managed-repo network, and the network's registry is discoverable from within this environment.

## Managed Repo Network — MANDATORY

Skipping this gate means an agent treats the repo as standalone and cannot discover the registry or resolve cross-repo references, silently breaking any cross-repo operation.

- This repo is governed by fe-sys-hq — its rules and enabled plugins are distributed from the fe-sys-hq marketplace. You MUST treat fe-sys-hq as the origin of this repo's governance.
- The fe-sys-hq source present in this environment carries `repo-registry.yaml`, the single source of truth for the managed-repo network (repo names, tiers, local paths, knowledge bases, `enabledPlugins`).
- To discover fe-sys-hq, read the registry, or resolve a registry entry or a cross-repo `{repo-name}:path` link, you MUST use the `registry_resolve.py` resolver rather than assuming a path — the registry's location varies by environment, so this rule hardcodes none.
- The authority for the discovery model and resolution rules is fe-repo-management's `Managed Repo Resolution` convention (the `fe-sys-hq Presence & Discovery` subsection); the resolver is its operative implementation. Consult it for how resolution works.
