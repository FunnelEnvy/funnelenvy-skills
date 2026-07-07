---
name: live-capture
version: 0.2.2
description: "When the user wants to capture a live site's page structure and copy as factual input for CRO analysis. Also use when the user mentions 'live capture,' 'capture pages,' 'page structure capture,' 'observation capture,' or 'structural capture.' Navigates selected pages, passively reads the rendered DOM across desktop and mobile, and writes two factual artifacts: live-observation.md (structure) and live-copy.md (copy). Legacy mode writes L0 to .claude/context/; KB mode writes bronze plus a silver structural artifact. Facts only, no analysis."
updated: 2026-07-07
---

# Live Capture

You capture the live, rendered state of a site's pages and record it as FACTS. You produce two artifacts: `live-observation.md` (page structure) and `live-copy.md` (verbatim copy). You do not analyze, score, or recommend. The skills that consume these artifacts (hypothesis-generator, experiment-mockup, positioning-framework) compute the judgments.

**This is a capture skill, not an analysis skill.** Read `agent-header.md` first. Its rules (factual-not-interpretive, tri-state existence, portable position encoding, two provenance axes, coverage-based confidence) govern every phase.

**Output (legacy mode):** `.claude/context/live-observation.md` + `.claude/context/live-copy.md`
**Output (KB mode):** bronze captures + a silver `reference/cro-{scope}/live-structure.md` (see `KB Mode`)
**Model:** Opus
**Browser:** Chrome DevTools MCP (preferred), Playwright MCP (secondary), static fallback (last resort)

---

## Operating Modes

Resolved once in Phase 0 and held in-session. The capture logic is identical in both; only the write targets and frontmatter differ.

- **Legacy mode** (default): writes the two artifacts to `.claude/context/` as L0 context files. No frontmatter beyond the artifact schema digest.
- **KB mode**: invoked when the working repo declares a knowledge base binding. Writes `live-observation.md` as a `bronze-note-capture` and `live-copy.md` as a `bronze-research-extraction` under `captures/`, then enriches the silver `silver-structural-observation` artifact at `reference/cro-{scope}/live-structure.md`. See `KB Mode (Dual-Mode Output)`.

---

## Invocation

```
/live-capture <url>
/live-capture <url> --scope b2c
/live-capture <url> --static
/live-capture <url> --urls /,/pricing,/contact
/live-capture <url> --viewports desktop,mobile
```

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `<url>` | required | Site root. Page selection discovers the rest unless `--urls` is given. |
| `--scope` | none | KB mode only. Selects the KB scope. Required in KB mode; warn-and-ignore in legacy. |
| `--no-kb` | off | Force legacy `.claude/context/` output even when a KB binding is detected. |
| `--static` | off | Force the static fallback (no browser MCP). Lower fidelity, no render/console data. |
| `--urls` | none | Explicit comma-separated page list. Bypasses Section 8 page selection and the no-profile nav-crawl. |
| `--viewports` | `desktop,mobile` | Comma-separated viewports to capture. |

---

## Preconditions

**Hard requirements (fail or stop if missing):**
- A target `<url>` argument.
- A working browser MCP (Chrome DevTools preferred, Playwright secondary), OR `--static`, OR the user's explicit "continue" at the no-browser gate. A configured-but-broken MCP is a STOP, never a silent fallback (see Browser-Mode Detection).
- KB mode only: a valid `--scope` (missing or invalid is a HARD STOP listing valid scopes).

**Soft requirements (degrade if missing):**
- Performance data for page selection: legacy `.claude/context/performance-profile.md`, or the scope's `silver-performance-analysis` in KB mode. Without it, Phase 1 falls back to the no-profile nav-crawl and overall confidence is capped at 3.

**Reads:** the performance data above (optional). Does NOT read other L0/L1 context files.
**Writes:** legacy mode `.claude/context/live-observation.md` + `live-copy.md`; KB mode bronze captures + the silver `live-structure.md` (see Operating Modes). Overwrites its own prior outputs (operational recapture model, not prior-work extension).

**Concurrency:** do not run while another producing skill is writing to the same context tree or KB scope (no locking).

---

## Phase 0: Mode Resolution

Run before anything else. Two independent resolutions: I/O mode (legacy vs KB) and browser mode.

### I/O Mode Resolution

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy mode, and note in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy output."
3. Parse the KB root path (it may be `docs/` or the repo root) and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/`, then resolve the artifact types this skill writes using the two-level lookup (repo-local `{kb-type}/artifacts/{type}.md` first, then the `kb-start` base): `bronze-note-capture` (commonly inherited from kb-start, NOT repo-local), `bronze-research-extraction`, and `silver-structural-observation`. The KB-mode gate is `silver-structural-observation`: if it does not resolve, fall back to legacy (the skill has no silver target to enrich) and report it. A missing bronze type also falls back, reporting which. Do not require these to live in the repo-local `artifacts/` dir; inherited kb-start types are valid. Never write typed artifacts into a half-configured KB.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope.

There is deliberately no `--kb` force flag. A failed detection falls back to legacy loudly so a broken KB binding gets fixed instead of worked around.

When KB mode is confirmed, hold this in-session state for the capture and write phases:
`kb_root`, `kb_type`, `scope`, and the artifact-type-def paths (`.claude/skills/{kb-type}/artifacts/{bronze-note-capture,bronze-research-extraction,silver-structural-observation}.md`) -- read these at write time for the authoritative output paths and frontmatter contract. `governed_by` is composed at runtime as `{kb-type}/{artifact-type}`. This skill never hardcodes a KB type skill name or a client-specific path.

### Browser-Mode Detection

> Canonical contract: `modules/browser-mode.md`. When browser-mode detection semantics change, edit that module first, then re-sync every browser-driving skill it lists. The procedure below is this skill's runtime copy.

Do NOT ask the user whether a browser MCP is configured. Test it. But do NOT silently degrade to static: a rendered-DOM capture is dramatically higher fidelity, and the user deserves to know before falling back.

**Real (non-headless) Chrome is required for WAF-protected targets.** Enterprise bot management (Akamai, Cloudflare, DataDome, PerimeterX, Imperva) fingerprints and 403-blocks HEADLESS Chrome before any content loads (`HeadlessChrome` user-agent, `navigator.webdriver`, TLS/JA3 and missing-surface signals). A real Chrome (headful, or a normal Chrome instance attached over CDP) presents as a human browser and passes. The Chrome-DevTools-first ranking below is not only about fidelity: a real attached Chrome is also what gets past enterprise WAFs. Preferred configurations, in order:

- **Chrome DevTools MCP attached to a running real Chrome** (`--browserUrl http://127.0.0.1:9222` or `--wsEndpoint ws://...`), rather than letting it launch headless.
- **Playwright MCP run headful, or attached over CDP** (`connectOverCDP` to a real Chrome), rather than `--headless`.
- **Headless-only hosts** (servers, WSL, CI): run a real Chrome under a virtual display (WSLg / Xvfb) and attach to it, or attach over CDP to a real Chrome elsewhere. The failure mode is headless-LAUNCH, not the platform.

**Static fallback is NOT a WAF remedy.** A static HTTP fetch is blocked at least as hard as headless Chrome (usually harder). Never present `--static` as the answer to a WAF block.

1. **`--static` override.** If set, use STATIC MODE. Skip detection. Note: "Running in static mode as requested. No render, console, or computed-style data; confidence is capped at 2-3."
2. **Chrome DevTools test.** Call `mcp__chrome-devtools__list_pages` (exact tool name).
   - Success: CHROME DEVTOOLS MODE.
   - "No such tool" / "unknown tool": not configured. Go to step 3.
   - Connection error, timeout, or other failure: the MCP is configured but broken. **STOP.** Do not fall through. Surface the raw error and help the user fix it (Chrome not running, remote debugging not enabled, wrong port or host). Re-test with `mcp__chrome-devtools__list_pages` after each fix attempt. Only proceed to step 3 if the user explicitly says they want to skip Chrome DevTools.
3. **Playwright test.** Try the Playwright MCP page/context listing tool.
   - Success: PLAYWRIGHT MODE. Inform the user that iteration uses managed Chromium.
   - "No such tool": not configured. Go to step 4.
   - Connection error: same as Chrome, STOP and help debug before falling through.
4. **No browser MCP -- STOP and recommend (blocking gate, not a silent fallback).** Tell the user a browser MCP (Chrome DevTools preferred, Playwright alternative) gives far higher fidelity, give brief setup steps, and offer: reply "continue" to proceed in static mode (lower fidelity, no render/console data), or set up a browser MCP and re-run. Proceed to STATIC MODE only on explicit "continue".

5. **Headless pre-flight probe (after a browser mode is selected, before Phase 1).** A connected browser is not necessarily a usable one for WAF-protected targets. Once Chrome DevTools or Playwright mode is selected, run one in-page check and record `browser_headless`:

   ```
   isHeadless = (navigator.webdriver === true) || /HeadlessChrome/.test(navigator.userAgent)
   ```

   If `isHeadless` is true, surface this in the pre-flight summary BEFORE any capture: "Connected browser is headless. WAF-protected targets (Akamai/Cloudflare/etc.) will likely return 403. If the target is enterprise-protected, attach to a real Chrome (see the preferred configurations above) and re-run." This is cheap and catches the systemic-block situation before grinding through the page set. The probe result also feeds the systemic-block rule in `phases/capture.md` Step 1.

---

## Phase 1: Page Selection

Read and follow `phases/select.md`.

Determine which pages to capture. If `--urls` was provided, use exactly that list (skip selection). Otherwise apply the Section 8 leverage algorithm against available performance data, with the homepage and a positive-control page always included, and a no-profile nav-crawl fallback.

Output: the ordered page list to capture, plus a coverage note (and a confidence cap if the no-profile fallback was used).

---

## Phase 2: Capture

Read and follow `phases/capture.md` (browser modes) or `phases/static-capture.md` (static mode).

For each selected page, for each viewport, passively read the rendered DOM and record the structural facts (blocks A-I + K) and verbatim copy. No DOM injection, no mutation. Compute `content_hash` per page via `scripts/content_hash.py`.

Output: per-page captured facts + copy, carried in-session to Phase 3.

---

## Phase 3: Write

Read and follow `phases/write.md`.

Assemble `live-observation.md` and `live-copy.md` per the authoritative inline schema. Apply the coverage-weighted confidence model. In legacy mode, write both to `.claude/context/`. In KB mode, write the two bronze artifacts and enrich the silver structural artifact, apply the KB frontmatter contract and prior-work supersede, then run the post-write validation gate.

---

## KB Mode (Dual-Mode Output)

### Write-side mapping

| Artifact | KB artifact type | Path under KB root | depends_on |
|---|---|---|---|
| `live-copy.md` | `bronze-research-extraction` | `captures/research-extractions/{scope}-live-copy.md` | -- |
| `live-observation.md` | `bronze-note-capture` | `captures/notes/{capture_date}_{scope}-live-observation.md` | `captures/research-extractions/{scope}-live-copy.md` (optional) |
| `live-structure.md` (silver enrichment) | `silver-structural-observation` | `reference/cro-{scope}/live-structure.md` | the two bronze artifacts above |

Read each artifact-type def (resolved in Phase 0) at write time for the authoritative output path and frontmatter contract; the paths above are the convention, the type def wins on divergence.

### Frontmatter contract

- **Bronze** (`live-copy.md`, `live-observation.md`): `fe-managed: true`, `name`, `description`, `kb_layer: bronze`, `governed_by: {kb-type}/{bronze-type}`, `scope`, `generated_by: live-capture`, `tags` (3-7), `version`, `created`, `updated`. No `depends_on` is required on bronze, but `live-observation.md` MAY carry a `depends_on` to the `live-copy.md` bronze when both were captured in the same run. No `data_provenance` on bronze.
- **Silver** (`live-structure.md`): all of the above with `kb_layer: silver`, `governed_by: {kb-type}/silver-structural-observation`, plus `data_provenance: public`, `depends_on` (the two bronze paths, KB-root-relative), and the coverage-weighted `confidence`.

### Prior work detection (KB mode)

Glob the three target paths for the scope. If present, supersede in place: preserve `created`, bump `version` (minor when the captured pages changed since the prior run, detected via `content_hash`; patch for a re-capture of unchanged pages), set `updated` to the capture date, overwrite the body. Artifacts from another scope are never read or written. Scope isolation is absolute.

### Post-write validation gate

After writing each KB artifact:

```
PY=$(python3 --version >/dev/null 2>&1 && echo python3 || echo python)
$PY <kb-start-scripts>/kb_type_validate.py validate <artifact-path>
```

Resolve `<kb-start-scripts>` from the fe-knowledge-base plugin's kb-start skill `scripts/` directory (marketplace plugin cache or source repo). If validation reports errors, fix the artifact frontmatter/sections and re-validate. If the script cannot be resolved, log a warning, continue, and flag manual validation in the completion message.

### Boundary

KB enrichment is additive only. The structural artifact enriches `silver-structural-observation`; it NEVER writes to `silver-performance-analysis` / `performance-profile.md`. Behavior data and structure data stay in separate files (hard boundary). Structure never records a count of behavior; the performance profile never records DOM layout.

---

## Completion Summary

Legacy mode:

```
Live capture written to .claude/context/
  live-observation.md  (N pages, M viewports, method: [chrome-devtools|playwright|static])
  live-copy.md         (N pages)
  Confidence: [coverage-weighted score] | Page selection: [profile-driven | no-profile nav-crawl (capped at 3)]
  Pages: [list]
```

KB mode: replace the file lines with the bronze + silver artifact paths, types, and confidence, and append:

```
  Validation: kb_type_validate.py passed | failed (fixed and re-validated) | unresolved (manual validation needed)
```

---

## Scripts

| Script | Description | Use when |
|---|---|---|
| [scripts/page_select.py](scripts/page_select.py) | Deterministic page-selection ranking. Reads a per-page-metrics JSON (sessions, cvr, bounce, mobile/desktop bounce) plus a benchmark CVR; computes normalized leverage and returns the two-lane ranked selection with the always-capture pages injected. CLI + JSON output. | Phase 1 page selection when a performance profile is available |
| [scripts/content_hash.py](scripts/content_hash.py) | Deterministic hash of a page's H1 + structural skeleton, for cheap recapture-diff. CLI reads the skeleton on stdin or as an arg, emits the hash. | Phase 2, computing per-page `content_hash` |

## Module Dependencies

Modules resolve from the repository-root `modules/` directory (a sibling of `skills/`), not from this skill's folder.

```
SKILL.md (this file)
  ├── agent-header.md            Shared agent rules (read first)
  ├── phases/select.md           Phase 1: page selection (Section 8 leverage)
  ├── phases/capture.md          Phase 2: passive rendered-DOM capture (browser modes)
  ├── phases/static-capture.md   Phase 2: static fallback capture
  ├── phases/write.md            Phase 3: assembly + dual-mode output + authoritative schema
  ├── scripts/page_select.py     Deterministic leverage ranking
  ├── scripts/content_hash.py    Deterministic recapture-diff hash
  └── modules/web-extract.md     Static-mode page fetch (three-tier extractor)
```

## Quality Rules

1. **Facts only.** No judgments, scores, or recommendations in either artifact. The two permitted mechanical derivations (`mobile_render_clean`, `nav_persona_segmented`) each follow their stated rule.
2. **Tri-state for pass-dependent existence.** Never a bare `false` from a pass that did not run.
3. **Portable position encoding.** fold + ordinal + region. No absolute pixels.
4. **Static mode is honest.** Block H writes `[NOT AVAILABLE: static mode]`, never a false `clean`. Confidence capped at 2-3.
5. **Broken browser MCP stops.** Configured-but-broken never silently degrades to static.
6. **Coverage-weighted confidence.** File-level confidence aggregates per-page confidence by weight, never a `min()`.
7. **No third writer to performance data.** Structure enriches the silver structural artifact only.
8. **Scope isolation is absolute** in KB mode.
9. **No em dashes.**
