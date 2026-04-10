---
name: experiment-mockup
version: 1.2.0
description: >-
  When the user wants to create a visual mockup of a proposed experiment change.
  Also use when the user mentions 'experiment mockup,' 'mockup hypothesis,'
  'inject change,' 'DOM injection,' 'visual mockup,' 'mock up experiment,'
  'show proposed change,' 'experiment preview,' or 'mockup for hypothesis N.'
  Takes a hypothesis from experiment-roadmap.md, navigates to the target page,
  injects the proposed change styled to match the site, iterates with the user,
  and captures the approved state as a standalone HTML artifact with CRO
  placement rationale. Three modes: live (Chrome DevTools MCP, interactive),
  playwright (Playwright MCP, screenshot-based iteration), and static (HTML
  extraction fallback, non-interactive).
---

# Experiment Mockup

You are the orchestrator for the experiment-mockup skill. You parse arguments, detect execution mode, and route to the appropriate phase sequence.

**You do NOT execute phase logic directly.** You spawn agents that read phase files.

---

## Invocation

```
/experiment-mockup <hypothesis-number> [--url <override-url>] [--static]
```

**Arguments:**
- `<hypothesis-number>` (required): Which hypothesis from experiment-roadmap.md (e.g., "1" for hypothesis #1, matching the `### N. [Name]` heading pattern)
- `--url <override-url>` (optional): Override target URL when hypothesis references multiple pages or you want to mock up the change on a different page
- `--static` (optional): Force static fallback mode even if Chrome DevTools MCP is available

**Examples:**
```
/experiment-mockup 1
/experiment-mockup 3 --url https://example.com/contact
/experiment-mockup 2 --static
```

---

## Preconditions

| Condition | Type | What Happens If Missing |
|-----------|------|------------------------|
| `.claude/deliverables/experiment-roadmap.md` exists | Hard | STOP. Tell user: "No experiment roadmap found. Run /hypothesis-generator first." |
| Hypothesis number exists in roadmap | Hard | STOP. Tell user: "Hypothesis #N not found in experiment-roadmap.md. Available hypotheses: [list numbers and names]." |
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

Parse `<hypothesis-number>` from arguments. Parse optional `--url` and `--static` flags.

If no hypothesis number provided, STOP: "Usage: /experiment-mockup <hypothesis-number> [--url <url>] [--static]"

### Step 2: Load Hypothesis

Read `.claude/deliverables/experiment-roadmap.md`.

Find the hypothesis matching the provided number. Hypotheses are numbered sequentially with headings like `### 1. [Experiment Name]`. Extract:
- Hypothesis number
- Experiment name (the heading text after the number)
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

Derive the hypothesis slug from the experiment name using `modules/slugify.md` rules:
1. Take the experiment name (text after "### N. " in the heading)
2. Apply slugify rules: lowercase, strip articles, replace non-alphanumeric with hyphens, collapse consecutive hyphens, strip leading/trailing hyphens

Output directory: `.claude/deliverables/experiments/<hypothesis-slug>/`

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

Mode: [chrome-devtools|playwright|static]
Output: .claude/deliverables/experiments/<slug>/
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

- **Layer:** L2 deliverable skill. Writes to `.claude/deliverables/experiments/`. Does NOT write to `.claude/context/`.
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

If output files already exist for the same hypothesis slug:
- Ask user before overwriting: "Mockup files already exist for [hypothesis name]. Overwrite? (y/n)"
- If yes: overwrite all files
- If no: STOP
