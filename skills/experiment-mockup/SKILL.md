---
name: experiment-mockup
version: 1.6.0
description: >-
  When the user wants to create a visual mockup of a proposed experiment change.
  Also use when the user mentions 'experiment mockup,' 'mockup hypothesis,'
  'inject change,' 'DOM injection,' 'visual mockup,' 'mock up experiment,'
  'show proposed change,' 'experiment preview,' or 'mockup for hypothesis N.'
  Takes a hypothesis from an experiment roadmap (KB-mode gold artifact or legacy
  deliverable), navigates to the target page, injects the proposed change styled
  to match the site, iterates with the user, and captures the approved state as a
  standalone HTML artifact with CRO placement rationale. Dual-mode I/O: KB mode
  reads the scope's gold roadmap and writes mockups under the bound knowledge
  base; legacy mode reads and writes under .claude/deliverables/. Three browser
  modes: live (Chrome DevTools MCP, interactive), playwright (Playwright MCP,
  screenshot-based iteration), and static (HTML extraction fallback,
  non-interactive).
updated: 2026-07-22
---

# Experiment Mockup

You are the orchestrator for the experiment-mockup skill. You parse arguments, detect execution mode, and route to the appropriate phase sequence.

**You do NOT execute phase logic directly.** You spawn agents that read phase files.

---

## Invocation

```
/experiment-mockup <hypothesis-number> [--url <override-url>] [--static] [--scope <slug>] [--no-kb]
```

**Arguments:**
- `<hypothesis-number>` (required): Which hypothesis from the experiment roadmap (e.g., "1" for hypothesis #1, matching the `### N. [Name]` heading pattern)
- `--url <override-url>` (optional): Override target URL when hypothesis references multiple pages or you want to mock up the change on a different page
- `--static` (optional): Force static fallback mode even if Chrome DevTools MCP is available

**I/O mode flags** (independent of the browser-mode detection above):

| Flag | Default | Description |
|------|---------|-------------|
| `--scope` | none | KB mode only. Selects which KB scope the run targets (the type skill defines valid scopes). Required in KB mode; warn-and-ignore in legacy mode. See `KB Mode (Dual-Mode Output)`. |
| `--no-kb` | off | Force legacy `.claude/deliverables/` I/O even when a KB binding is detected. See `KB Mode (Dual-Mode Output)`. |

**Examples:**
```
/experiment-mockup 1
/experiment-mockup 3 --url https://example.com/contact
/experiment-mockup 2 --static
/experiment-mockup 1 --scope b2c
/experiment-mockup 2 --no-kb
```

---

## KB Mode (Dual-Mode Output)

The skill runs in one of two I/O modes, resolved once in the orchestrator (Step 1b) and held in-session. The browser-mode detection (live / playwright / static) and all phase logic are identical in both I/O modes; only the roadmap-read path and the mockup-write base differ.

- **Legacy mode** (default): reads the roadmap from `.claude/deliverables/experiment-roadmap.md` and writes mockups to `.claude/deliverables/experiments/<slug>/`.
- **KB mode**: the run resolved a `{scope}`; reads the gold roadmap at `{kb_root}/deliverables/{scope}-experiment-roadmap.md` and writes mockups to `{kb_root}/deliverables/experiments/<slug>/`.

Mode resolution mirrors hypothesis-generator's and render-program-site's `KB Mode (Dual-Mode Output)` exactly, so all three skills behave identically about KB binding and `--scope` semantics. The mockups experiment-mockup writes in KB mode are the artifacts a render-program-site tactical spoke references through its test's `mockup` block at `{kb_root}/deliverables/experiments/<slug>/`.

### Mode Resolution Procedure (orchestrator, Step 1b)

> Canonical contract: `modules/kb-mode.md`. When KB-mode semantics change, edit that module first, then re-sync every dual-mode skill it lists. The procedure below is this skill's runtime copy.

1. If `--no-kb` is set: legacy mode. Done.
2. Read the working repo's `CLAUDE.md`. Find a `Knowledge Bases` section. If absent: legacy mode, and note in the run output: "No `Knowledge Bases` section in CLAUDE.md; using legacy I/O."
3. Parse the KB root path and KB type skill name from that section. Verify the type skill exists at `.claude/skills/{kb-type}/` and its `artifacts/` directory defines `gold-experiment-roadmap` (the roadmap source artifact type). If the check fails: legacy mode, and report which check failed.
4. KB mode confirmed. Resolve scope: `--scope <slug>` must match a valid scope defined by the type skill. If `--scope` is missing or invalid: HARD STOP. Display the valid scope list and ask the user to re-run with `--scope`. Do not guess a scope.

There is deliberately no `--kb` force flag. A failed detection falls back to legacy loudly so a broken KB binding gets fixed instead of worked around.

When KB mode is confirmed, hold this in-session state for the load and write steps: `kb_root`, `kb_type`, `scope`. The roadmap-read path and the mockup output base derive from these per `Operating mode targets` below. This skill never hardcodes a KB type skill name or a client-specific path.

### Operating mode targets

| Target | Legacy mode | KB mode |
|--------|-------------|---------|
| Roadmap source (read, hard precondition) | `.claude/deliverables/experiment-roadmap.md` | `{kb_root}/deliverables/{scope}-experiment-roadmap.md` |
| Mockup output base (write) | `.claude/deliverables/experiments/<slug>/` | `{kb_root}/deliverables/experiments/<slug>/` |

The mockup output is NOT a KB artifact: it carries no `kb_layer` frontmatter. The KB-mode path only co-locates the mockups under the KB deliverables tree so render-program-site can resolve them via the tactical `mockup` block. The existing `placement.md` / `mockup.html` frontmatter rules are unchanged in both modes.

---

## Preconditions

| Condition | Type | What Happens If Missing |
|-----------|------|------------------------|
| The roadmap source for the resolved mode exists (legacy: `.claude/deliverables/experiment-roadmap.md`; KB: `{kb_root}/deliverables/{scope}-experiment-roadmap.md`) | Hard | STOP. Tell user: "No experiment roadmap found at [resolved path]. Run /hypothesis-generator first (with --scope <slug> in KB mode)." |
| Hypothesis number exists in roadmap | Hard | STOP. Tell user: "Hypothesis #N not found in the roadmap. Available hypotheses: [list numbers and names]." |
| Target URL is reachable | Hard | Validated in Phase 1 (live) or static-build (static). If unreachable, STOP with error. |
| Chrome DevTools MCP connected | Recommended | Auto-detected. If unavailable, STOP and recommend setup. Static fallback only with explicit user consent (see Step 5.5). |

**No dependency on L0/L1 context files.** The hypothesis already contains synthesized context. Re-reading L0/L1 would risk the mockup contradicting the hypothesis. **Exception:** brand design files (`brand-design-system.md`, `brand-components.html`) in `.claude/context/` are read if they exist. These are visual references, not positioning context.

---

## Agent Model Selection

| Agent Role | Model |
|-----------|-------|
| All phase agents | opus |

---

## Orchestrator Steps

### Step 1: Parse Arguments

Parse `<hypothesis-number>` from arguments. Parse optional `--url`, `--static`, `--scope`, and `--no-kb` flags.

If no hypothesis number provided, STOP: "Usage: /experiment-mockup <hypothesis-number> [--url <url>] [--static] [--scope <slug>] [--no-kb]"

### Step 1b: Resolve I/O Mode

Run the `Mode Resolution Procedure` from `KB Mode (Dual-Mode Output)`. This sets the mode (legacy or KB) and, in KB mode, the in-session `kb_root` / `kb_type` / `scope`. The resolved mode determines the roadmap-read path (Step 2) and the mockup output base (Step 4). It does NOT affect browser-mode detection (Step 5).

### Step 2: Load Hypothesis

Read the roadmap source for the resolved mode:
- **Legacy mode:** `.claude/deliverables/experiment-roadmap.md`
- **KB mode:** `{kb_root}/deliverables/{scope}-experiment-roadmap.md`

If the file does not exist, STOP per the Preconditions table (roadmap-exists gate).

Find the hypothesis matching the provided number. Hypotheses are numbered sequentially with headings like `### 1. [Experiment Name]`. Extract:
- Hypothesis number
- Experiment name (the heading text after the number)
- **Key:** field (the stable resolution key; absent on legacy / un-backfilled roadmaps)
- **Page:** field (target URL or path)
- **What to test:** field (the proposed change description)
- **Change type:** field (one or more of `insert | replace-copy | modify | remove | reorder`, primary first). **Fallback when absent** (a legacy / un-backfilled roadmap that predates the field): do NOT fail. Set the change type to "classify locally" and pass that to the phase agent, which classifies from What-to-test + Proposed-change using the same enum (duplicated into inject.md so the agent is self-contained). This mirrors the `**Key:**` fallback contract: no hard failure. The resolved source (`roadmap` or `local`) is recorded in placement.md frontmatter (`change_type_source`).
- **Current state:** field
- **Proposed change:** field
- **Before:** / **After:** quoted copy (if present)
- **Variation block** (if present, from hypothesis-generator construct.md Step 3b): the variations (A/B/C with anchors and copy) and the `**Recommended:**` line. When present, the default behavior is to mock the Recommended variation; the phase agent names which variation was used at first presentation and lists the others (the user can switch variations during live/playwright iteration, a copy revision). Never build all variations in one invocation (the single-hypothesis-per-invocation rule is unchanged). If no Variation block is present, there is a single proposed change; proceed normally.

If the hypothesis number does not exist, STOP with the error from the Preconditions table.

### Step 3: Resolve Target URL

Extract the URL or path from the hypothesis **Page:** field.

- If it's a full URL (starts with http/https): use it directly
- If it's a path (starts with /): resolve against the company domain from the hypothesis context or ask the user
- If it references multiple pages: check for `--url` flag. If no `--url` flag, ask the user which page to mock up (list the URLs found)
- If `--url` flag is set: use the override URL regardless of what the hypothesis says

### Step 4: Generate Output Directory Slug

Resolve the output directory name from the matched hypothesis's persisted `**Key:**` field (the stable mockup-resolution key minted by hypothesis-generator). The shared fallback contract: **prefer the `**Key:**` field; when it is absent (a legacy / un-backfilled roadmap), fall back to `slugify(experiment name)` and print a one-line warning** naming the experiment and the missing `**Key:**` field, then proceed. No hard failure on keyless roadmaps.

1. If the matched hypothesis carries a `**Key:**` field, use its value verbatim as the directory name.
2. Otherwise, fall back to `slugify(experiment name)` per `modules/slugify.md` (lowercase, strip articles, replace non-alphanumeric with hyphens, collapse consecutive hyphens, strip leading/trailing hyphens) and print the one-line warning.

Output directory (resolved against the mockup output base for the mode from Step 1b):
- **Legacy mode:** `.claude/deliverables/experiments/<key>/`
- **KB mode:** `{kb_root}/deliverables/experiments/<key>/`

The full resolved output directory path is passed to the phase agent; the phases write to the path the orchestrator computes here (the phase files show the legacy path as the canonical example).

### Step 5: Detect Execution Mode

> Canonical contract: `modules/browser-mode.md`. When browser-mode detection semantics change, edit that module first, then re-sync every browser-driving skill it lists. The steps below are this skill's runtime copy.

**Do NOT ask the user** whether they have a browser MCP configured. Test it. But do NOT silently degrade to static mode -- browser-based mockups are dramatically better, and the user deserves to know that before proceeding with a lower-fidelity fallback.

**Real (non-headless) Chrome is required for WAF-protected targets.** Enterprise bot management (Akamai, Cloudflare, DataDome, PerimeterX, Imperva) fingerprints and 403-blocks HEADLESS Chrome before any content loads (`HeadlessChrome` user-agent, `navigator.webdriver`, TLS/JA3 and missing-surface signals). A real Chrome (headful, or a normal Chrome instance attached over CDP) presents as a human browser and passes. The Chrome-DevTools-first ranking below is not only about fidelity: a real attached Chrome is also what gets past enterprise WAFs. Preferred configurations, in order:

- **Chrome DevTools MCP attached to a running real Chrome** (`--browserUrl http://127.0.0.1:9222` or `--wsEndpoint ws://...`), rather than letting it launch headless.
- **Playwright MCP run headful, or attached over CDP** (`connectOverCDP` to a real Chrome), rather than `--headless`.
- **Headless-only hosts** (servers, WSL, CI): run a real Chrome under a virtual display (WSLg / Xvfb) and attach to it, or attach over CDP to a real Chrome elsewhere. The failure mode is headless-LAUNCH, not the platform.

**Static fallback is NOT a WAF remedy.** A static HTTP fetch is blocked at least as hard as headless Chrome (usually harder). Never present `--static` as the answer to a WAF block.

#### 5.1: Static flag override

If `--static` flag is set: use STATIC MODE. Skip detection. Briefly note: "Running in static mode as requested. Output will be lower fidelity (~60-80% CSS accuracy, no screenshots, no iteration). Remove `--static` to use Chrome DevTools MCP instead."

#### 5.2: Chrome DevTools pre-flight (WSL2 only)

a. **Detect environment:**
```bash
test -d /mnt/c/ && echo "WSL2" || echo "NATIVE"
```

b. **If WSL2, run pre-flight checks** (silently fix what can be fixed, stop only when user action is required):

**Check .wslconfig for mirrored networking:**
```bash
cat /mnt/c/Users/$USER/.wslconfig 2>/dev/null
```
If `networkingMode=mirrored` is NOT present, tell the user:

> WSL2 mirrored networking is required for Chrome DevTools to work across the WSL/Windows boundary. Run this in PowerShell, then restart WSL:
>
> ```powershell
> "[wsl2]`nnetworkingMode=mirrored" | Set-Content "$env:USERPROFILE\.wslconfig"
> wsl --shutdown
> ```
>
> Restart the session after WSL comes back up.

STOP here. Do not fall back to Playwright or static. The user needs to restart WSL.

**Check DevToolsActivePort symlink:**
```bash
ls -la /home/$USER/.config/google-chrome/DevToolsActivePort 2>/dev/null
```
If missing or stale (not a symlink to the Windows Chrome profile), create it silently:
```bash
mkdir -p /home/$USER/.config/google-chrome
ln -sf "/mnt/c/Users/$USER/AppData/Local/Google/Chrome/User Data/DevToolsActivePort" \
  /home/$USER/.config/google-chrome/DevToolsActivePort
```
Do not inform the user. This is a silent fix.

**Verify the symlink target exists.** If the Windows-side file does not exist, Chrome is not running or remote debugging is not enabled. Tell the user to open Chrome and navigate to `chrome://inspect/#remote-debugging` to enable it. STOP and wait for confirmation.

#### 5.3: Chrome DevTools connection test

Call `mcp__chrome-devtools__list_pages` (the exact tool name -- do not guess alternatives).

- **Success:** use **CHROME DEVTOOLS MODE**. Proceed to Step 6.
- **"No such tool" or "unknown tool" error:** The Chrome DevTools MCP server is not configured. Proceed to 5.4.
- **Connection error, timeout, or other failure:** The MCP is configured but broken. **STOP.** Do not fall through. Show the user the specific error and help them fix it:
  - "Connection refused" -> Chrome likely not running or remote debugging not enabled. Ask user to launch Chrome with `--remote-debugging-port=9222` or check that Chrome is open.
  - Timeout -> Retry once after 5 seconds. If still failing, suggest the MCP server config may have a wrong port or host.
  - Other errors -> Surface the raw error message so the user can diagnose.
  - After each fix attempt, re-test with `mcp__chrome-devtools__list_pages` before moving on.
  - Only proceed to 5.4 if the user explicitly says they want to skip Chrome DevTools.

#### 5.4: Playwright detection (secondary)

Call the Playwright MCP's page listing or version tool (the specific tool depends on which Playwright MCP is installed -- try `browser_list_contexts` or `playwright_list_pages`).

- **Success:** use **PLAYWRIGHT MODE**. Inform the user: "Using Playwright for browser rendering. You'll get real browser screenshots but iteration uses screenshot-based feedback instead of your live browser window."
- **"No such tool" error:** No Playwright MCP configured. Proceed to 5.5.
- **Connection error:** Same as Chrome -- STOP and help debug before falling through.

#### 5.5: No browser MCP available -- STOP and recommend

**This is a blocking gate, not a silent fallback.**

Tell the user:

> **No browser MCP is available.** Mockups built without a browser use static HTML extraction and produce significantly lower fidelity output (~60-80% CSS accuracy, no screenshots, no interactive iteration).
>
> **Recommended: Set up Chrome DevTools MCP** for the best experience (live browser injection, real computed styles, interactive iteration with screenshots).
>
> To set it up:
> 1. Install the Chrome DevTools MCP server in your Claude Code settings (`~/.claude/settings.json` or project `.mcp.json`)
> 2. Launch Chrome with remote debugging: `google-chrome --remote-debugging-port=9222` (or on Mac: `open -a "Google Chrome" --args --remote-debugging-port=9222`)
> 3. Re-run `/experiment-mockup` after setup
>
> **Alternative:** Playwright MCP also works (screenshot-based iteration, no live browser window needed).
>
> **Or proceed anyway** with static mode by replying "continue" -- but the output will be a basic HTML mockup without real browser rendering, screenshots, or iteration.

STOP and wait for the user's response:
- If they want to set up Chrome DevTools MCP: help them configure it, then re-run detection from 5.3.
- If they say "continue" or equivalent: proceed to STATIC MODE with the degradation context carried forward.
- If they want to set up Playwright: help them configure it, then re-run detection from 5.4.

#### 5.6: Headless pre-flight probe (after a browser mode is selected, before Step 6)

A connected browser is not necessarily a usable one for WAF-protected targets. Once Chrome DevTools or Playwright mode is selected, run one in-page check (script evaluation in the connected browser) and record `browser_headless`:

```
isHeadless = (navigator.webdriver === true) || /HeadlessChrome/.test(navigator.userAgent)
```

If `isHeadless` is true, surface this BEFORE launching the phase agent: "Connected browser is headless. WAF-protected targets (Akamai/Cloudflare/etc.) will likely return 403. If the target is enterprise-protected, attach to a real Chrome (see the preferred configurations above) and re-run." This is cheap and catches the block before Phase 1 (Inspect) grinds against a 403. Pass `browser_headless` to the phase agent so a 403 during inspect is diagnosed as a WAF block, not a broken selector.

### Step 6: Route to Phase Sequence

**Dimension loading (all three modes).** The lp-audit-taxonomy dimensions loaded are conditional on the change type extracted in Step 2. Use this mapping to decide which dimensions to load, then list them in the mode's load list below:

| Condition | Dimensions to load |
|-----------|--------------------|
| Base (always) | D1, D3, D5, D8 |
| Target element is a CTA or a form | add D6 (CTA Strategy and Form Design) |
| Hypothesis mechanism references social proof, urgency, scarcity, authority, or loss framing | add D7 (Persuasion Psychology) |
| Change type is `reorder` or `remove` | add D4 (Page Structure and Content Hierarchy) |
| Change type absent (legacy roadmap, classify-locally) | load base D1/D3/D5/D8 plus D6 (cheap; covers the most common ambiguity) |

Load `modules/copy-craft.md` in every mode (it governs the Distillation Contract for any copy rewrite).

**LIVE MODE:**
Launch a single agent with the following files loaded (in this order):
1. `skills/experiment-mockup/agent-header.md`
2. `skills/experiment-mockup/phases/inspect.md`
3. `skills/experiment-mockup/phases/inject.md`
4. `skills/experiment-mockup/phases/capture.md`
5. `skills/experiment-mockup/phases/annotate.md`
6. `modules/conversion-playbook.md` (sections 1-6)
7. `modules/lp-audit-taxonomy.md` (dimensions per the Dimension loading table above)
8. `modules/copy-craft.md` (Distillation Contract)
9. `modules/slugify.md`

Pass to the agent:
- Hypothesis number, name, and full hypothesis text
- Change type (the roadmap value, or "classify locally" when the field is absent)
- Variation set and recommended variation (when the hypothesis carries a Variation block)
- Target URL
- Output directory path

The agent executes phases sequentially: inspect -> inject (with user iteration) -> capture -> annotate.

**PLAYWRIGHT MODE:**
Launch a single agent with the following files loaded (in this order):
1. `skills/experiment-mockup/agent-header.md`
2. `skills/experiment-mockup/phases/inspect.md`
3. `skills/experiment-mockup/phases/inject.md`
4. `skills/experiment-mockup/phases/capture.md`
5. `skills/experiment-mockup/phases/annotate.md`
6. `modules/conversion-playbook.md` (sections 1-6)
7. `modules/lp-audit-taxonomy.md` (dimensions per the Dimension loading table above)
8. `modules/copy-craft.md` (Distillation Contract)
9. `modules/slugify.md`

Pass to the agent:
- Hypothesis number, name, and full hypothesis text
- Change type (the roadmap value, or "classify locally" when the field is absent)
- Variation set and recommended variation (when the hypothesis carries a Variation block)
- Target URL
- Output directory path
- Browser mode: "playwright" (agent uses this to select tool names and iteration pattern)

The agent executes phases sequentially: inspect -> inject (with screenshot-based iteration) -> capture -> annotate.

**STATIC MODE:**
Launch a single agent with the following files loaded (in this order):
1. `skills/experiment-mockup/agent-header.md`
2. `skills/experiment-mockup/phases/static-build.md`
3. `skills/experiment-mockup/phases/annotate.md`
4. `modules/web-extract.md`
5. `modules/conversion-playbook.md` (sections 1-6)
6. `modules/lp-audit-taxonomy.md` (dimensions per the Dimension loading table above)
7. `modules/copy-craft.md` (Distillation Contract)
8. `modules/slugify.md`

Pass to the agent:
- Hypothesis number, name, and full hypothesis text
- Change type (the roadmap value, or "classify locally" when the field is absent)
- Variation set and recommended variation (when the hypothesis carries a Variation block)
- Target URL
- Output directory path
- Note that this is static mode (no browser MCP available). The agent should flag any CSS values it could not extract with `/* DEFAULT - could not extract */` comments.

The agent executes: static-build -> annotate.

**After the static agent completes**, append a notice to the bottom of `placement.md`:

```
---

> **Note:** This mockup was built in static mode (no browser MCP). CSS values marked with `/* DEFAULT */` are estimates. For higher fidelity, re-run with Chrome DevTools MCP configured.
```

### Step 7: Completion Summary

After the agent completes, display:

```
Experiment mockup complete for hypothesis #[N]: [name]

I/O mode: [KB (scope: <slug>) | legacy]
Browser mode: [chrome-devtools|playwright|static]
Change type: [resolved change type] (source: [roadmap | classified locally])
Variation mocked: [variation id, or "n/a (single proposed change)"]
Self-review: [performed at desktop + 390px mobile; N self-fix cycles | not applicable (static reasoning pass)]
Output: [resolved output directory: .claude/deliverables/experiments/<slug>/ or {kb_root}/deliverables/experiments/<slug>/]
  - mockup.html (standalone, open in any browser)
  - placement.md (CRO rationale + implementation notes)
  - control-screenshot.png / mockup-screenshot.png (desktop before/after; live & playwright modes only)
  - control-screenshot-mobile.png / mockup-screenshot-mobile.png (390px before/after; live & playwright modes only)

[If static mode: "Note: Static mockup was built from HTML extraction (no screenshots, desktop or mobile; responsive behavior is a recommendation, not observed). For interactive mockups with real computed styles, configure Chrome DevTools MCP (recommended) or Playwright MCP."]

[If playwright mode: "Note: Mockup built with Playwright (managed Chromium). For live browser iteration, configure Chrome DevTools MCP."]
```

---

## Output Files

| File | Format | Contents |
|------|--------|----------|
| `mockup.html` | HTML (self-contained, inline CSS) | Approved mockup state with surrounding page context, styled to match the target site |
| `placement.md` | Markdown (YAML frontmatter) | CRO placement rationale, attention strategy, content distillation, alternatives, implementation notes, risk flags |
| `control-screenshot.png` | PNG (live & playwright modes only) | Desktop viewport screenshot of the unmodified "before" state, framed identically to the after shot. Consumed by render-program-site to render a Before/After pair. |
| `mockup-screenshot.png` | PNG (live & playwright modes only) | Desktop viewport screenshot of the injected "after" state |
| `control-screenshot-mobile.png` | PNG (live & playwright modes only) | 390px viewport screenshot of the unmodified "before" state, framed identically to the mobile after shot |
| `mockup-screenshot-mobile.png` | PNG (live & playwright modes only) | 390px viewport screenshot of the injected "after" state |

---

## Architecture Notes

- **Layer:** L2 deliverable skill. Writes to the mockup output base for the resolved I/O mode (legacy `.claude/deliverables/experiments/`; KB `{kb_root}/deliverables/experiments/`). Does NOT write to `.claude/context/`. The KB-mode output is not a KB artifact (no `kb_layer` frontmatter); see `KB Mode (Dual-Mode Output)`.
- **Layer violation (documented):** This skill makes web requests (DevTools navigation or curl extraction), which violates the "L2 skill NEVER makes web requests" invariant. This is the same category of contained violation as hypothesis-generator's L1/L2 hybrid position. The alternative (an L1 skill that extracts page structure into a context file, then a separate L2 skill that builds the mockup) adds a file, a schema, and a skill boundary for zero user benefit.
- **Does NOT re-read L0/L1 context files.** The hypothesis is the single source of truth.
- **Single hypothesis per invocation.** No batching.
- **Graceful degradation:** Chrome DevTools (live browser) -> Playwright (screenshot iteration) -> static (curl fallback). Chrome DevTools is preferred for the live iteration UX. Playwright provides JS rendering and screenshot-based iteration when Chrome DevTools is unavailable.

---

## Token Budget

| Mode | Estimated Tokens | Notes |
|------|-----------------|-------|
| Live mode | ~40-80K | Variable due to user iteration cycles. More iterations = more tokens. |
| Static mode | ~30-50K | Single pass, no iteration. |

---

## Re-run Behavior

If output files already exist for the same hypothesis slug (within the resolved mode's output base):
- Ask user before overwriting: "Mockup files already exist for [hypothesis name]. Overwrite? (y/n)"
- If yes: overwrite all files
- If no: STOP

---

## Quality Checks

Before reporting a mockup complete, verify:

- [ ] The mockup matches the hypothesis exactly: the injected change is the roadmap's proposed change for hypothesis #[N], not an interpretation of it
- [ ] The treatment respects the change type: the type-appropriate branch was applied (a `replace-copy` edited text in place at the original tag/styles; a `modify` changed only named properties; a `remove` verified reflow; a `reorder` checked seams; an `insert` followed the subordination rules), and the treatment changed only what the hypothesis specifies
- [ ] The Distillation Contract was honored: quantified claims from the hypothesis copy are unchanged, no new claim/number/outcome was introduced, and any copy rewrite followed copy-craft
- [ ] `mockup.html` is standalone (inline CSS, no external requests) and opens correctly in a browser
- [ ] The mockup shows a clean treatment: no "PROPOSED" labels, fidelity banners, or annotation overlays baked into the artifact
- [ ] Styling matches the target site (extracted values, not defaults); static mode flags every unextracted value with `/* DEFAULT */`
- [ ] `placement.md` has valid frontmatter (including `change_type` / `change_type_source`, schema_version 1.2) and covers placement rationale, attention strategy, content distillation, alternatives (from the candidate pass), implementation notes, risk flags, and Capture Fidelity Notes (Section 7)
- [ ] Live/playwright modes: the self-review gate ran at desktop and 390px mobile; desktop and mobile control/mockup screenshot pairs exist and each pair is framed identically (same scroll position and viewport)
- [ ] Overlay hygiene: consent banners, chat widgets, and sticky overlays were dismissed/hidden in every screenshot, identically across the pair, with no in-flow content removed (live/playwright only; static takes no screenshots)
- [ ] Salience framing: element/copy-scale treatments captured as a tight crop, section-scale at viewport; the primary type governs a bundled type; the size backstop applied one-directionally (tightens only, never loosens a tight crop)
- [ ] Spot-the-diff: the Before/After change is identifiable at a glance, or the self-review log records the re-frame it forced (within the 2-cycle budget)
- [ ] Target-fidelity: the hypothesis's named region was resolved to the page's visual reality, and a named-region-vs-visual-structure disagreement was surfaced to the user (live/playwright) or flagged as a Risk (static) rather than silently resolved to the copy-match
- [ ] Output landed in the resolved mode's output base (legacy `.claude/deliverables/experiments/<slug>/` or `{kb_root}/deliverables/experiments/<slug>/`); no writes to `.claude/context/`
- [ ] No existing mockup files were overwritten without the user confirming
- [ ] The completion summary states I/O mode, browser mode, and the resolved output directory

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.6.0 | Capture-fidelity bundle (P1-P4). **P1 overlay hygiene:** a new `capture.md` Step 0 precondition (and a cross-reference in inject.md Step 2b) dismisses/hides floating overlays (consent banners, chat widgets, sticky promos) before every screenshot, identically across the pair, hiding only floating overlays and never in-flow content or the treatment's layout context; capture-time only, recorded in placement metadata, not shared into live-capture. **P2 salience-scaled framing:** `capture.md` Step 1 now scales the frame to the treatment keyed on the resolved `change_type` (element/copy-scale = tight crop; section-scale = viewport framing; primary type governs a bundled type) plus a one-directional size backstop that only tightens (never loosens a tight crop); the 390px mobile pair follows the same rule; output filenames unchanged (the tight crop replaces the full-viewport primary pair, no context pair). **P3 spot-the-diff:** inject.md Step 2b adds a side-by-side check that the change is identifiable at a glance by someone who has not read the hypothesis, forcing a tighter-crop re-frame within the existing 2-cycle self-fix budget; annotation overlays remain forbidden (fix framing, not labeling). **P4 target-fidelity gate:** a new inject.md pre-build gate resolves the hypothesis's named region to the page's visual reality and stops-and-asks on a named-region-vs-visual-structure disagreement (naming both candidates) instead of silently picking the copy-match; static-build.md folds the same check into its existing Step 2 clarification ask (DOM-structure reasoning) with a Risk Flag when running non-interactively. placement.md `schema_version` 1.1 -> 1.2 with a new `Section 7: Capture Fidelity Notes`; four new Quality Checks; `generated_by` literal swept to v1.6.0 across the phase templates. [experiment-mockup-capture-communicates-change] |
| 1.5.0 | Treatment-quality bundle (P1-P5). **P1 treatment-type taxonomy:** consumes hypothesis-generator's new `**Change type:**` field (extracted in Step 2; classified locally on legacy roadmaps that predate it, no hard failure, mirroring the `**Key:**` fallback). `inject.md`'s single insert-only "CRO Placement Principles" doctrine is restructured into "Treatment Principles by Change Type": cross-type invariants plus five per-type branches (insert = the prior rules verbatim; replace-copy edits text in place at original tag/styles; modify changes only named properties with an explicit primary-CTA-prominence exception; remove verifies reflow; reorder checks seams). Step 1 generalized to "Build the Treatment" and branches on type; `static-build.md` Step 5 gets the same branch logic. `annotate.md` becomes type-aware (Section 1/2 framing) and its frontmatter gains `change_type` / `change_type_source` with schema_version -> "1.1". Fixes the previously-broken archetypes (a headline or CTA-label test was forbidden by the old "never h1/h2" / "never the primary CTA color" rules). **P2 copy-craft + distillation contract:** `modules/copy-craft.md` loaded in all three modes; a Distillation Contract in inject.md/static-build.md makes quantified claims from the hypothesis copy immutable (they passed proof-integrity upstream and this skill has no registry access) and forbids introducing new claims. **P3 candidate pass + self-review:** inject Step 1a sketches/scores 2-3 candidates internally and builds only the winner (Section 4 now documents a real comparison), with a skip rule when the treatment is fully pinned; inject Step 2b screenshots the injected state and self-reviews before first presentation (2-cycle fix budget); static mode runs the checklist as a reasoning pass. **P4 mobile:** the self-review and `capture.md` add a 390px pair (`control-screenshot-mobile.png` / `mockup-screenshot-mobile.png`); annotate Section 5 responsive note becomes observed (live/playwright) vs speculative (static). **P5 type-conditional dimensions + variation awareness:** Step 6 loads lp-audit-taxonomy conditionally (base D1/D3/D5/D8; +D6 for CTA/form; +D7 for persuasion mechanisms; +D4 for reorder/remove; base+D6 when the type is absent); when the hypothesis carries a Variation block, the Recommended variation is mocked and named, others listed. Also fixed the pre-existing `generated_by: experiment-mockup v1.0.0` literal (now v1.5.0) in the capture/static-build/annotate templates. [experiment-mockup-treatment-quality] |
| 1.4.2 | Browser-mode contract parity back-port: Step 5 gains the WAF/enterprise-bot-management guidance (fingerprinting signals, preferred real-Chrome configurations, "static fallback is NOT a WAF remedy") and a new Step 5.6 headless pre-flight probe (`navigator.webdriver` / `HeadlessChrome` check, surfaced before launching the phase agent) that live-capture already carried; the two skills' duplicated detection contract had drifted. The contract now has a canonical editing source at `modules/browser-mode.md` (drift canary enforced by `scripts/registry_check.py`); the inline copy stays runtime-self-contained. |
| 1.4.1 | Repo-audit contract completion, no behavior change: added the Quality Checks section (the dev rules require one; the file previously had none). Also gains the `modules/kb-mode.md` canonical-contract pointer in its KB-mode section (drift canary enforced by `scripts/registry_check.py`). |
| 1.4.0 | Control ("before") screenshot capture. `capture.md` Step 1 now captures a Before/After pair from the same scroll position and viewport: it restores the original state (removes the injected element, restores any modified originals), screenshots the unmodified viewport as `control-screenshot.png`, then re-injects and screenshots the after as `mockup-screenshot.png`. `inject.md` Step 5 now hands off the injected element's class/id and any modified-original markup so capture can restore the control. New live/playwright-only output `control-screenshot.png` added to agent-header Section 2, SKILL.md Output Files, and the Step 7 completion summary. Static mode writes no control (documented in `static-build.md`). Pairs with render-program-site's optional `control_screenshot` to render a Before/After comparison; absence is backward compatible (after-only). |
| 1.3.2 | Reference rename: roadmap-presentation -> render-program-site across the KB-mode and mockup-output prose (the consumer skill was replaced). No behavioral change. |
| 1.3.0 | Key-based output-directory resolution: `Step 4` now resolves the output directory from the matched hypothesis's persisted `**Key:**` field instead of `slugify(experiment name)`, with a shared fallback contract (prefer `**Key:**`; when absent, fall back to `slugify(title)` and print a one-line warning, no hard failure on keyless roadmaps). `Step 2` now also extracts the `**Key:**` field. Decouples mockup resolution from mutable roadmap heading titles (chg_2026-06-18_stable-mockup-resolution-key). |
| 1.3.0 | Dual-mode I/O retrofit (KB / legacy). New `KB Mode (Dual-Mode Output)` section: mode resolution mirrors hypothesis-generator and roadmap-presentation exactly (`--no-kb` forces legacy; a detected `Knowledge Bases` binding plus a valid `--scope` selects KB mode; missing/invalid `--scope` in KB mode is a HARD STOP listing valid scopes; failed detection falls back to legacy loudly). Read side: KB mode reads the gold roadmap at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`; legacy unchanged. Write side: KB mode writes mockups to `{kb_root}/deliverables/experiments/<slug>/` (co-located so roadmap-presentation resolves them; not a KB artifact, no `kb_layer`); legacy unchanged. New `--scope` and `--no-kb` flags; mode-aware roadmap-exists precondition, output-directory resolution (Step 1b, Step 2, Step 4), completion message, and Architecture Notes layer line. Phase path references generalized to the orchestrator-provided output directory (legacy path shown as the canonical example). |
| 1.2.0 | Playwright browser mode added (screenshot-based iteration) as the secondary detection tier between Chrome DevTools and static. |
