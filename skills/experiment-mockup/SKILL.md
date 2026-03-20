---
name: experiment-mockup
version: 1.0.0
description: >-
  When the user wants to create a visual mockup of a proposed experiment change.
  Also use when the user mentions 'experiment mockup,' 'mockup hypothesis,'
  'inject change,' 'DOM injection,' 'visual mockup,' 'mock up experiment,'
  'show proposed change,' 'experiment preview,' or 'mockup for hypothesis N.'
  Takes a hypothesis from experiment-roadmap.md, navigates to the target page,
  injects the proposed change styled to match the site, iterates with the user,
  and captures the approved state as a standalone HTML artifact with CRO
  placement rationale. Two modes: live (Chrome DevTools MCP, interactive) and
  static (HTML extraction fallback, non-interactive).
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
| Chrome DevTools MCP connected | Soft | Auto-detected. Falls back to static mode. |

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

**Do NOT ask the user** whether they have DevTools MCP configured. Test it.

1. If `--static` flag is set: use STATIC MODE. Skip detection.
2. Otherwise, attempt a lightweight Chrome DevTools MCP tool call. Try to list browser tabs or get browser version info.
   - If the tool call succeeds: use LIVE MODE
   - If the tool call fails, errors, or the tool is not available: use STATIC MODE. Inform the user: "DevTools MCP not detected. Building static mockup. For live interactive mockups, configure Chrome DevTools MCP: https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session"

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
- Note that this is static mode (no DevTools available)

The agent executes: static-build -> annotate.

### Step 7: Completion Summary

After the agent completes, display:

```
Experiment mockup complete for hypothesis #[N]: [name]

Mode: [live|static]
Output: .claude/deliverables/experiments/<slug>/
  - mockup.html (standalone, open in any browser)
  - placement.md (CRO rationale + implementation notes)
  - mockup-screenshot.png (live mode only)

[If static mode: "Note: Static mockup was built from HTML extraction. For interactive mockups with real computed styles, configure Chrome DevTools MCP."]
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
- **Graceful degradation:** Live mode -> static fallback. No hard dependency on Chrome DevTools MCP.

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
