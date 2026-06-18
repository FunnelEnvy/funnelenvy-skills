---
name: experiment-mockup
version: 1.3.0
description: >-
modes: live (Chrome DevTools MCP, interactive), playwright (Playwright MCP,
updated: 2026-06-18
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

Mode resolution mirrors hypothesis-generator's and roadmap-presentation's `KB Mode (Dual-Mode Output)` exactly, so all three skills behave identically about KB binding and `--scope` semantics. The mockups experiment-mockup writes in KB mode are exactly the source artifacts roadmap-presentation resolves at `{kb_root}/deliverables/experiments/<slug>/`.

### Mode Resolution Procedure (orchestrator, Step 1b)

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

The mockup output is NOT a KB artifact: it carries no `kb_layer` frontmatter. The KB-mode path only co-locates the mockups under the KB deliverables tree so roadmap-presentation can resolve them. The existing `placement.md` / `mockup.html` frontmatter rules are unchanged in both modes.

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
- **Current state:** field
- **Proposed change:** field
- **Before:** / **After:** quoted copy (if present)

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

**Do NOT ask the user** whether they have a browser MCP configured. Test it. But do NOT silently degrade to static mode -- browser-based mockups are dramatically better, and the user deserves to know that before proceeding with a lower-fidelity fallback.

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

### Step 6: Route to Phase Sequence

**LIVE MODE:**
Launch a single agent with the following files loaded (in this order):
1. `skills/experiment-mockup/agent-header.md`
2. `skills/experiment-mockup/phases/inspect.md`
3. `skills/experiment-mockup/phases/inject.md`
4. `skills/experiment-mockup/phases/capture.md`
5. `skills/experiment-mockup/phases/annotate.md`
6. `modules/conversion-playbook.md` (sections 1-6)
7. `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)
8. `modules/slugify.md`

Pass to the agent:
- Hypothesis number, name, and full hypothesis text
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
7. `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)
8. `modules/slugify.md`

Pass to the agent:
- Hypothesis number, name, and full hypothesis text
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
6. `modules/lp-audit-taxonomy.md` (dimensions D1, D3, D5, D8)
7. `modules/slugify.md`

Pass to the agent:
- Hypothesis number, name, and full hypothesis text
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
Output: [resolved output directory: .claude/deliverables/experiments/<slug>/ or {kb_root}/deliverables/experiments/<slug>/]
  - mockup.html (standalone, open in any browser)
  - placement.md (CRO rationale + implementation notes)
  - mockup-screenshot.png (live mode only)

[If static mode: "Note: Static mockup was built from HTML extraction. For interactive mockups with real computed styles, configure Chrome DevTools MCP (recommended) or Playwright MCP."]

[If playwright mode: "Note: Mockup built with Playwright (managed Chromium). For live browser iteration, configure Chrome DevTools MCP."]
```

---

## Output Files

| File | Format | Contents |
|------|--------|----------|
| `mockup.html` | HTML (self-contained, inline CSS) | Approved mockup state with surrounding page context, styled to match the target site |
| `placement.md` | Markdown (YAML frontmatter) | CRO placement rationale, attention strategy, content distillation, alternatives, implementation notes, risk flags |
| `mockup-screenshot.png` | PNG (live mode only) | Browser viewport screenshot of injected state |

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

## Changelog

| Version | Changes |
|---------|---------|
| 1.3.0 | Key-based output-directory resolution: `Step 4` now resolves the output directory from the matched hypothesis's persisted `**Key:**` field instead of `slugify(experiment name)`, with a shared fallback contract (prefer `**Key:**`; when absent, fall back to `slugify(title)` and print a one-line warning, no hard failure on keyless roadmaps). `Step 2` now also extracts the `**Key:**` field. Decouples mockup resolution from mutable roadmap heading titles (chg_2026-06-18_stable-mockup-resolution-key). |
| 1.3.0 | Dual-mode I/O retrofit (KB / legacy). New `KB Mode (Dual-Mode Output)` section: mode resolution mirrors hypothesis-generator and roadmap-presentation exactly (`--no-kb` forces legacy; a detected `Knowledge Bases` binding plus a valid `--scope` selects KB mode; missing/invalid `--scope` in KB mode is a HARD STOP listing valid scopes; failed detection falls back to legacy loudly). Read side: KB mode reads the gold roadmap at `{kb_root}/deliverables/{scope}-experiment-roadmap.md`; legacy unchanged. Write side: KB mode writes mockups to `{kb_root}/deliverables/experiments/<slug>/` (co-located so roadmap-presentation resolves them; not a KB artifact, no `kb_layer`); legacy unchanged. New `--scope` and `--no-kb` flags; mode-aware roadmap-exists precondition, output-directory resolution (Step 1b, Step 2, Step 4), completion message, and Architecture Notes layer line. Phase path references generalized to the orchestrator-provided output directory (legacy path shown as the canonical example). |
| 1.2.0 | Playwright browser mode added (screenshot-based iteration) as the secondary detection tier between Chrome DevTools and static. |
