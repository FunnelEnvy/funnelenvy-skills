**Target executor:** opus

# Execution Plan: experiment-mockup Browser MCP Strategy Update

Update experiment-mockup to support three browser tiers: Chrome DevTools MCP (primary) -> Playwright MCP (fallback) -> static (last resort). Repositions WSL troubleshooting from error-recovery to pre-flight. Bumps version to v1.2.0.

## Session Prompt

```
Read /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/EXECUTION-PLAN.md and execute all tasks in strict order.

Rules:
- One task at a time. Verify before moving to the next.
- If verification fails: STOP. Report. Do NOT proceed.
- ONLY modify files in each task's Modify/Create fields.
- Read every "Read first" file before changes. Actually read it, not from memory.
- Do not refactor, optimize, or "improve" anything not in the task.
- Do not add comments, docstrings, or formatting changes unless specified.
- If ambiguous, STOP and ask. Do not guess.
- This should complete with ZERO interaction prompts. If something asks a question, note it as unexpected.
```

## Execution Summary

| Task | Description | Files | Est. Context Load |
|------|-------------|-------|-------------------|
| 1 | SKILL.md Step 5: three-tier detection rewrite | SKILL.md | ~15K |
| 2 | SKILL.md Step 6: add Playwright routing block | SKILL.md | ~8K |
| 3 | SKILL.md Step 7 + Architecture Notes + frontmatter | SKILL.md | ~8K |
| 4 | inject.md: conditional iteration pattern | inject.md | ~10K |
| 5 | inspect.md: tool name abstraction | inspect.md | ~10K |
| 6 | capture.md: tool name abstraction | capture.md | ~8K |
| 7 | ARCHITECTURE.md: reference updates | ARCHITECTURE.md | ~20K |

**Total estimated context load:** ~79K tokens

---

## TASK 1: Rewrite SKILL.md Step 5 detection logic

**Depends on:** none
**Read first:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md`
**Modify:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md`
**Do NOT touch:** Steps 1-4 (argument parsing, hypothesis loading, URL resolution, slug generation). Step 6 (routing). Step 7 (completion summary). Architecture Notes section. Frontmatter.

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read SKILL.md in full. Locate Step 5 (starts at `### Step 5: Detect Execution Mode`, currently line ~105) through the end of the WSL troubleshooting sequence (ends just before `### Step 6`, currently line ~160).

2. Replace the entire Step 5 section (from `### Step 5: Detect Execution Mode` up to but NOT including `### Step 6`) with the following:

```markdown
### Step 5: Detect Execution Mode

**Do NOT ask the user** whether they have a browser MCP configured. Test it.

1. If `--static` flag is set: use STATIC MODE. Skip detection.

2. **Chrome DevTools pre-flight + connection:**

   a. **Detect environment.** Check for `/mnt/c/` to identify WSL2:
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

   **Verify the symlink target exists.** If the Windows-side file does not exist, Chrome is not running or remote debugging is not enabled. Tell the user to open Chrome and navigate to `chrome://inspect/#remote-debugging` to enable it.

   c. **Attempt a lightweight Chrome DevTools MCP tool call.** Try to list browser tabs or get browser version info.

   d. If the tool call succeeds: use **CHROME DEVTOOLS MODE**.

   e. If the tool call fails after pre-flight: retry once with a 3-second delay.

   f. If still failing: log the failure reason and continue to step 3.

3. **Playwright detection:**

   a. Attempt a lightweight Playwright MCP tool call (e.g., list browser contexts or get version).

   b. If the tool call succeeds: use **PLAYWRIGHT MODE**. Inform the user: "Chrome DevTools not available. Using Playwright for browser rendering. Iteration will use screenshots instead of your live browser."

   c. If the tool call fails: continue to step 4.

4. **STATIC MODE.**

   Inform the user: "No browser MCP available. Building static mockup from HTML extraction. For interactive mockups, configure Chrome DevTools MCP (recommended) or Playwright MCP."
```

3. Verify the new Step 5 ends immediately before the existing `### Step 6` header. No blank lines were added or removed between sections beyond what is shown above.

**Done when:**
- [ ] Step 5 contains three-tier detection: Chrome DevTools -> Playwright -> static
- [ ] WSL pre-flight checks run BEFORE Chrome DevTools connection attempt (not after failure)
- [ ] DevToolsActivePort symlink fix is silent (no user prompt)
- [ ] The old `#### WSL Chrome troubleshooting sequence` subsection header is gone
- [ ] The URL `https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session` is gone
- [ ] Steps 1-4 and Step 6 onward are unchanged

**Verify:**
```bash
# New detection tiers present
grep -c "Chrome DevTools pre-flight" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1

grep -c "Playwright detection" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1

grep -c "PLAYWRIGHT MODE" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: at least 2 (Step 5 + Step 6 later, but Step 6 not yet modified -- expect 1 here)

# Old sections removed
grep -c "WSL Chrome troubleshooting sequence" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 0

grep -c "chrome-devtools-mcp-debug-your-browser-session" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 0

# Steps 1-4 untouched
grep -c "### Step 1: Parse Arguments" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## TASK 2: Add Playwright routing block to SKILL.md Step 6

**Depends on:** TASK 1
**Read first:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md`
**Modify:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md`
**Do NOT touch:** Steps 1-5. Step 7. Architecture Notes. Frontmatter. The LIVE MODE and STATIC MODE routing blocks (do not modify their content; only insert between them).

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read SKILL.md. Locate Step 6 (`### Step 6: Route to Phase Sequence`). Find the gap between the end of the LIVE MODE block and the start of `**STATIC MODE:**`.

2. Insert the following Playwright routing block between the LIVE MODE block and the STATIC MODE block:

```markdown

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

```

3. In the STATIC MODE block, find the line:
   ```
   - Note that this is static mode (no DevTools available)
   ```
   Replace with:
   ```
   - Note that this is static mode (no browser MCP available)
   ```

**Done when:**
- [ ] Step 6 has three routing blocks: LIVE MODE, PLAYWRIGHT MODE, STATIC MODE (in that order)
- [ ] Playwright routing block has identical file list to LIVE MODE
- [ ] Playwright routing block passes `Browser mode: "playwright"` to the agent
- [ ] LIVE MODE block is unchanged
- [ ] STATIC MODE block text updated from "no DevTools available" to "no browser MCP available"

**Verify:**
```bash
grep -c "PLAYWRIGHT MODE" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: at least 2 (Step 5 detection + Step 6 routing)

grep -c 'Browser mode: "playwright"' /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1

grep -c "no browser MCP available" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1

# LIVE MODE block preserved
grep -c "with user iteration" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## TASK 3: Update SKILL.md Step 7, Architecture Notes, and frontmatter

**Depends on:** TASK 2
**Read first:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md`
**Modify:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md`
**Do NOT touch:** Steps 1-6. Output Files table. Token Budget. Re-run Behavior.

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read SKILL.md.

2. **Frontmatter version bump.** Find `version: 1.1.0` and replace with `version: 1.2.0`.

3. **Frontmatter description.** Find the line:
   ```
   placement rationale. Two modes: live (Chrome DevTools MCP, interactive) and
   static (HTML extraction fallback, non-interactive).
   ```
   Replace with:
   ```
   placement rationale. Three modes: live (Chrome DevTools MCP, interactive),
   playwright (Playwright MCP, screenshot-based iteration), and static (HTML
   extraction fallback, non-interactive).
   ```

4. **Step 7 mode display.** In the completion summary code block, find:
   ```
   Mode: [live|static]
   ```
   Replace with:
   ```
   Mode: [chrome-devtools|playwright|static]
   ```

5. **Step 7 static mode note.** Find the line:
   ```
   [If static mode: "Note: Static mockup was built from HTML extraction. For interactive mockups with real computed styles, configure Chrome DevTools MCP."]
   ```
   Replace with:
   ```
   [If static mode: "Note: Static mockup was built from HTML extraction. For interactive mockups with real computed styles, configure Chrome DevTools MCP (recommended) or Playwright MCP."]

   [If playwright mode: "Note: Mockup built with Playwright (managed Chromium). For live browser iteration, configure Chrome DevTools MCP."]
   ```

6. **Architecture Notes graceful degradation.** Find the line:
   ```
   - **Graceful degradation:** Live mode -> static fallback. No hard dependency on Chrome DevTools MCP.
   ```
   Replace with:
   ```
   - **Graceful degradation:** Chrome DevTools (live browser) -> Playwright (screenshot iteration) -> static (curl fallback). Chrome DevTools is preferred for the live iteration UX. Playwright provides JS rendering and screenshot-based iteration when Chrome DevTools is unavailable.
   ```

**Done when:**
- [ ] Version is 1.2.0
- [ ] Frontmatter mentions three modes
- [ ] Step 7 mode display shows `chrome-devtools|playwright|static`
- [ ] Step 7 has both a static mode note and a playwright mode note
- [ ] Architecture Notes mentions three-tier degradation

**Verify:**
```bash
grep "version: 1.2.0" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1 match

grep -c "Three modes" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1

grep "chrome-devtools|playwright|static" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1 match

grep -c "If playwright mode" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1

grep -c "Playwright (screenshot iteration)" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## TASK 4: Update inject.md with conditional iteration pattern

**Depends on:** none
**Read first:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md`
**Modify:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md`
**Do NOT touch:** The entire CRO Placement Principles section (Section headers: Visual Hierarchy, Proximity to Intent Signal, Attention Without Disruption, Contrast Calibration, Using Existing Patterns -- lines ~26-82). Step 1 (Build HTML/CSS). Step 5 (Lock Final State). Required Inputs. Outputs.

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read inject.md in full.

2. **Step 2 tool name.** Find:
   ```
   Use Chrome DevTools MCP to insert the element:
   ```
   Replace with:
   ```
   Use the browser MCP to insert the element:

   - Chrome DevTools mode: use Puppeteer DOM manipulation tools
   - Playwright mode: use browser_evaluate() with insertAdjacentHTML:

     ```javascript
     browser_evaluate(`
       document.querySelector('[target-selector]')
         .insertAdjacentHTML('beforebegin', \`[injection HTML]\`)
     `)
     ```
   ```

   The rest of Step 2 (insertion positions list, verification, scrolling) remains unchanged.

3. **Step 3 presentation.** Replace the entire Step 3 content (from `### Step 3: Present to User` up to but NOT including `### Step 4: Iterate`) with:

   ```markdown
   ### Step 3: Present to User

   Present the change to the user.

   **Chrome DevTools mode:**
   Tell the user to look at their browser. Be specific about what was added and where:

   "I've injected a [description of content block] [position relative to landmark element] on [page path]. Check your browser."

   **Playwright mode:**
   Take a screenshot of the current viewport (scroll to center the injected element if needed). Present the screenshot to the user:

   "I've injected a [description of content block] [position relative to landmark element] on [page path]. Here's how it looks:"

   [present screenshot]

   Then ask for feedback (same in both modes):
   "Does this placement work? I can:"
   "- Move it (above/below/beside different elements)"
   "- Restyle it (different size, color, spacing, pattern)"
   "- Revise the copy (shorter, different headline, reframe)"
   "- Try a completely different content block style"
   ```

4. **Step 4 iteration.** Find:
   ```
   1. **Remove the previous injection.** Use DevTools to find and remove the `proposed-change-block` element (or whatever class name was used).
   ```
   Replace with:
   ```
   1. **Remove the previous injection.** Use the browser MCP to find and remove the `proposed-change-block` element (or whatever class name was used).
      - Chrome DevTools: use Puppeteer DOM removal
      - Playwright: `browser_evaluate('document.querySelector(".proposed-change-block").remove()')`
   ```

5. **Step 4 presentation sub-step.** Find the existing step 3 within the iteration cycle:
   ```
   3. **Present again.** Describe what changed and ask for feedback.
   ```
   Replace with:
   ```
   3. **Present again.**
      - Chrome DevTools: describe what changed and ask for feedback.
      - Playwright: take a new screenshot, present it, describe what changed, ask for feedback.
   ```

**Done when:**
- [ ] Step 2 mentions both Chrome DevTools and Playwright tool patterns
- [ ] Step 3 has separate presentation paths for Chrome DevTools and Playwright
- [ ] Step 4 has browser-mode-specific removal and presentation instructions
- [ ] CRO Placement Principles section is completely unchanged
- [ ] No references to "Chrome DevTools MCP" remain (only "Chrome DevTools mode" and "browser MCP")

**Verify:**
```bash
# Old reference gone
grep -c "Chrome DevTools MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md
# Expected: 0

# New references present
grep -c "browser MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md
# Expected: 2 (Step 2 and Step 4)

grep -c "Playwright mode" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md
# Expected: at least 2

# CRO section intact
grep -c "Visual Hierarchy" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md
# Expected: 1

grep -c "Proximity to Intent Signal" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md
# Expected: 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## TASK 5: Update inspect.md with tool name abstraction

**Depends on:** none
**Read first:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md`
**Modify:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md`
**Do NOT touch:** Step 3 (Load Brand Design System). Step 5 (Identify Existing Content Block Patterns). Step 6 (Compile Working State). Required Inputs. Outputs.

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read inspect.md in full.

2. **Step 1 navigation.** Find:
   ```
   Use Chrome DevTools MCP to open the target URL in the connected Chrome instance.

   Wait for full page load:
   - Document ready state
   - Network idle (no pending requests for 500ms+)
   ```
   Replace with:
   ```
   Use the browser MCP to open the target URL.

   - Chrome DevTools mode: navigate using DevTools MCP tools (the page opens in the user's Chrome)
   - Playwright mode: navigate using Playwright MCP tools (browser_navigate; the page opens in managed Chromium)

   Wait for full page load:
   - Document ready state
   - Network idle (no pending requests for 500ms+)
   ```

3. **Step 2 tool reference.** Find:
   ```
   Use DevTools MCP to locate the target area:
   ```
   Replace with:
   ```
   Use the browser MCP to locate the target area:
   ```

4. **Step 4 tool reference.** Find:
   ```
   For the elements surrounding the insertion point, read computed styles via DevTools MCP. Extract:
   ```
   Replace with:
   ```
   For the elements surrounding the insertion point, read computed styles via the browser MCP. Extract:
   ```

5. **Step 4 Playwright batching note.** After the last design token category in Step 4 (the "CTA styling" paragraph ending with "uses LOWER visual weight"), add the following:

   ```markdown

   **Playwright mode note:** Computed styles are extracted via browser_evaluate() executing window.getComputedStyle() in the page context. The output is functionally identical to Chrome DevTools' direct CDP access. Extract all tokens in a single evaluate() call to minimize tool call overhead:

   ```javascript
   browser_evaluate(`
     JSON.stringify({
       body: window.getComputedStyle(document.body),
       heading: window.getComputedStyle(document.querySelector('h2')),
       // ... additional elements per the token categories above
     })
   `)
   ```
   ```

**Done when:**
- [ ] Step 1 mentions both Chrome DevTools and Playwright navigation
- [ ] Step 2 says "browser MCP" not "DevTools MCP"
- [ ] Step 4 says "browser MCP" not "DevTools MCP"
- [ ] Playwright batching note added after the CTA styling paragraph
- [ ] No references to "Chrome DevTools MCP" or "DevTools MCP" remain (only "Chrome DevTools mode" and "browser MCP")

**Verify:**
```bash
# Old references gone
grep -c "Chrome DevTools MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md
# Expected: 0

grep "DevTools MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md | grep -v "Chrome DevTools'" | grep -vc "DevTools mode"
# Expected: 0

# New references present
grep -c "browser MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md
# Expected: 3 (Steps 1, 2, 4)

grep -c "Playwright mode" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md
# Expected: at least 2 (Step 1 navigation + Step 4 batching note)

grep -c "browser_evaluate" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inspect.md
# Expected: at least 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## TASK 6: Update capture.md with tool name abstraction

**Depends on:** none
**Read first:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/capture.md`
**Modify:** `/home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/capture.md`
**Do NOT touch:** Step 3 (Build Standalone mockup.html). Step 4 (Write Files). Required Inputs. Outputs.

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read capture.md in full.

2. **Step 1 screenshot.** Find:
   ```
   Use Chrome DevTools MCP to capture a screenshot of the current viewport showing the injected change.
   ```
   Replace with:
   ```
   Use the browser MCP to capture a screenshot of the current viewport showing the injected change.

   - Chrome DevTools mode: use DevTools screenshot tool
   - Playwright mode: use browser_take_screenshot (scroll to center the injected element if needed)
   ```

3. **Step 2 HTML extraction.** Find:
   ```
   Use Chrome DevTools MCP to read the `outerHTML` of the section containing the injection. This should be the parent section identified in Phase 1, not the entire page.
   ```
   Replace with:
   ```
   Use the browser MCP to read the outerHTML of the section containing the injection. This should be the parent section identified in Phase 1, not the entire page.

   - Chrome DevTools mode: use DevTools DOM inspection tools
   - Playwright mode: `browser_evaluate('document.querySelector("[section-selector]").outerHTML')`
   ```

**Done when:**
- [ ] Step 1 mentions both Chrome DevTools and Playwright screenshot tools
- [ ] Step 2 mentions both Chrome DevTools and Playwright HTML extraction
- [ ] No references to "Chrome DevTools MCP" remain
- [ ] Steps 3 and 4 are unchanged

**Verify:**
```bash
# Old references gone
grep -c "Chrome DevTools MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/capture.md
# Expected: 0

# New references present
grep -c "browser MCP" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/capture.md
# Expected: 2 (Steps 1 and 2)

grep -c "Playwright mode" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/capture.md
# Expected: 2

# mockup.html build step untouched
grep -c "Build Standalone mockup.html" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/capture.md
# Expected: 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## TASK 7: Update ARCHITECTURE.md references

**Depends on:** none
**Read first:** `/home/david/funnelenvy-skills/docs/ARCHITECTURE.md`
**Modify:** `/home/david/funnelenvy-skills/docs/ARCHITECTURE.md`
**Do NOT touch:** All sections not listed below. All non-experiment-mockup content. All other skill entries, dependency maps, data flows, and gotchas.

**SCOPE LOCK:** Only files listed in Modify/Create may be changed. Editing any other file is a bug.

**Steps:**

1. Read ARCHITECTURE.md in full (it is large; read in batches if needed).

2. **Component map version.** Find line ~66:
   ```
     SKILL.md                  Orchestrator (v1.0.0) -- parses flags, detects mode, routes phases
   ```
   Replace with:
   ```
     SKILL.md                  Orchestrator (v1.2.0) -- parses flags, detects mode, routes phases
   ```

3. **Module dependency map -- LIVE MODE phase annotations.** Find lines ~170-174:
   ```
     |-- LIVE MODE:
     |     |-- phases/inspect.md (Chrome DevTools MCP: navigate, inspect, extract computed styles)
     |     |-- phases/inject.md (Chrome DevTools MCP: DOM injection, user iteration loop)
     |     |     +-- reads modules/conversion-playbook.md (sections 1-6: placement principles)
     |     |     +-- reads modules/lp-audit-taxonomy.md (D1, D3, D5, D8: rationale dimensions)
     |     |-- phases/capture.md (Chrome DevTools MCP: screenshot, extract HTML, write mockup.html)
   ```
   Replace each `(Chrome DevTools MCP:` with `(browser MCP:`:
   ```
     |-- LIVE MODE:
     |     |-- phases/inspect.md (browser MCP: navigate, inspect, extract computed styles)
     |     |-- phases/inject.md (browser MCP: DOM injection, user iteration loop)
     |     |     +-- reads modules/conversion-playbook.md (sections 1-6: placement principles)
     |     |     +-- reads modules/lp-audit-taxonomy.md (D1, D3, D5, D8: rationale dimensions)
     |     |-- phases/capture.md (browser MCP: screenshot, extract HTML, write mockup.html)
   ```

4. **Data flow diagram.** Find lines ~361-366:
   ```
     +-- 4. Detect execution mode (test DevTools MCP availability)
     |
     +-- LIVE MODE (single agent: agent-header.md + inspect + inject + capture + annotate):
     |     +-- Phase 1: Navigate to page, locate target section, extract computed styles (DevTools MCP)
     |     +-- Phase 2: Build + inject content block, iterate with user (DevTools MCP)
     |     +-- Phase 3: Screenshot, extract HTML, write mockup.html (DevTools MCP)
   ```
   Replace with:
   ```
     +-- 4. Detect execution mode (test browser MCP availability)
     |
     +-- CHROME DEVTOOLS MODE (single agent: agent-header.md + inspect + inject + capture + annotate):
     |     +-- Phase 1: Navigate to page, locate target section, extract computed styles (browser MCP)
     |     +-- Phase 2: Build + inject content block, iterate with user (browser MCP)
     |     +-- Phase 3: Screenshot, extract HTML, write mockup.html (browser MCP)
     |     +-- Phase 4: Write placement.md (CRO rationale + implementation notes)
     |
     +-- PLAYWRIGHT MODE (single agent: same file list as Chrome DevTools mode):
     |     +-- Phases 1-4 same as Chrome DevTools, with screenshot-based iteration instead of live browser
   ```

5. **Data flow -- STATIC MODE.** Find lines ~369-371:
   ```
     +-- STATIC MODE (single agent: agent-header.md + static-build + annotate):
           +-- Fallback: Fetch page HTML (modules/web-extract.md), parse CSS, build mockup.html
           +-- Phase 4: Write placement.md (CRO rationale + implementation notes)
   ```
   Replace with:
   ```
     +-- STATIC MODE (single agent: agent-header.md + static-build + annotate):
           +-- Fallback: Fetch page HTML (modules/web-extract.md), parse CSS, build mockup.html
           +-- Phase 4: Write placement.md (CRO rationale + implementation notes)
   ```
   (Content is the same, but verify the indentation is consistent with the new blocks above.)

6. **Non-Obvious Decisions -- single agent rationale.** Find the section starting with:
   ```
   **Why a single agent for all live-mode phases instead of one agent per phase?**
   ```
   At the end of that paragraph (after "well within Opus's capacity."), append:
   ```
    The same rationale applies in Playwright mode: shared working state (computed styles, DOM paths, injection HTML) stays in context across phases.
   ```

7. **Known Gotchas -- add entry 13.** After the last gotcha entry (entry 12, ending with "rules from visual specs."), add:

   ```markdown

   **13. Playwright mode iteration is screenshot-based.** In Playwright mode, the user does not see changes in their browser window. The agent takes a screenshot after each injection and presents it. This is a UX downgrade from Chrome DevTools mode but produces the same output quality. If a user reports "I can't see the changes," check which browser mode is active.
   ```

8. **Entry points -- invocation example.** Find line ~743:
   ```
   /experiment-mockup 2 --static                              # force static mode (no DevTools MCP)
   ```
   Replace with:
   ```
   /experiment-mockup 2 --static                              # force static mode (no browser MCP)
   ```

9. **Prerequisites -- experiment-mockup dependency note.** Find line ~769:
   ```
   - experiment-mockup needs `experiment-roadmap.md` in `.claude/deliverables/` (hard req). No L0/L1 context file dependencies. Chrome DevTools MCP is a soft dependency: without it, degrades to static mode with ~70% visual fidelity.
   ```
   Replace with:
   ```
   - experiment-mockup needs `experiment-roadmap.md` in `.claude/deliverables/` (hard req). No L0/L1 context file dependencies. Browser MCP is a soft dependency. Chrome DevTools provides live iteration in the user's browser. Playwright provides screenshot-based iteration with full JS rendering. Without either, degrades to static mode with ~70% visual fidelity.
   ```

**Done when:**
- [ ] Component map shows v1.2.0
- [ ] Module dependency map uses "browser MCP" instead of "Chrome DevTools MCP"
- [ ] Data flow diagram includes Playwright mode between Chrome DevTools and Static
- [ ] Non-Obvious Decisions section mentions Playwright mode rationale
- [ ] Known Gotchas has entry 13 about Playwright screenshot-based iteration
- [ ] Entry points example says "no browser MCP" not "no DevTools MCP"
- [ ] Prerequisites note mentions three-tier degradation

**Verify:**
```bash
# Old references in experiment-mockup sections
grep "Chrome DevTools MCP" /home/david/funnelenvy-skills/docs/ARCHITECTURE.md | grep -ic "experiment-mockup\|DevTools MCP:\|soft dependency"
# Expected: 0

# New references
grep -c "browser MCP" /home/david/funnelenvy-skills/docs/ARCHITECTURE.md
# Expected: at least 6

grep -c "PLAYWRIGHT MODE" /home/david/funnelenvy-skills/docs/ARCHITECTURE.md
# Expected: at least 1

grep -c "v1.2.0" /home/david/funnelenvy-skills/docs/ARCHITECTURE.md
# Expected: 1

grep -c "Playwright mode iteration is screenshot-based" /home/david/funnelenvy-skills/docs/ARCHITECTURE.md
# Expected: 1
```

**STOP IF:** Verification fails or output doesn't match expected. Report failure and actual output. Do not proceed.

---

## Final Verification

Run after all tasks complete:

```bash
echo "=== Residual Chrome DevTools MCP references (should be 0 in skill files) ==="
grep -rn "Chrome DevTools MCP" \
  /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/ \
  --include="*.md"
# Expected: 0 matches

echo "=== Residual bare 'DevTools MCP' references (should be 0 in skill files) ==="
grep -rn "DevTools MCP" \
  /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/ \
  --include="*.md" | grep -v "Chrome DevTools'" | grep -v "DevTools mode"
# Expected: 0 matches

echo "=== Em dash check ==="
grep -rn "\u2014" \
  /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/ \
  /home/david/funnelenvy-skills/docs/ARCHITECTURE.md \
  --include="*.md"
# Expected: only pre-existing em dashes (the phase file headers use " -- " with spaces, not em dashes)

echo "=== Version check ==="
grep "version:" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: version: 1.2.0

echo "=== Three modes in frontmatter ==="
grep "Three modes" /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/SKILL.md
# Expected: 1 match

echo "=== CRO Placement Principles intact ==="
grep -c "Visual Hierarchy\|Proximity to Intent Signal\|Attention Without Disruption\|Contrast Calibration\|Using Existing Patterns" \
  /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/inject.md
# Expected: 5

echo "=== static-build.md unchanged ==="
git diff --stat /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/static-build.md
# Expected: no output (file unchanged)

echo "=== agent-header.md unchanged ==="
git diff --stat /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/agent-header.md
# Expected: no output (file unchanged)

echo "=== annotate.md unchanged ==="
git diff --stat /home/david/funnelenvy-skills/funnelenvy-skills/skills/experiment-mockup/phases/annotate.md
# Expected: no output (file unchanged)
```

---

## If Something Goes Wrong

**Verification fails:** STOP. Report which task, which command, expected vs. actual. Do NOT fix or proceed. Wait for user.
**Need to edit an unlisted file:** STOP. Report which file and why. Do NOT edit. Wait for user.
**File doesn't match plan description:** STOP. Report discrepancy. Do NOT improvise. Wait for user.
**Unsure about a step's intent:** STOP. Quote it, explain ambiguity. Do NOT guess. Wait for user.
**Human interaction point reached:** STOP. Display prompt. Do NOT auto-answer or skip. Wait for human.

---

## Feedback Log

| Phase | Task | Issue | Root Cause | Resolution | Optimizer Gap? |
|-------|------|-------|------------|------------|----------------|
| - | - | - | - | - | - |
