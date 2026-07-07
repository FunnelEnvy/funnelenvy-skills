# Browser Mode: Canonical Detection Contract

**This module is the canonical editing source for browser-mode detection semantics.** Two
skills carry an inline copy of the detection procedure so their runtime read is self-contained
(the same inline-authority pattern the schemas and `modules/kb-mode.md` use). When browser-mode
semantics change, edit THIS file first, then re-sync every skill listed below in the same
change. A drift canary in `scripts/registry_check.py` verifies the invariant markers below
exist in every browser-driving SKILL.md.

## Browser-driving skills

| Skill | Inline copy location | Interaction model |
|---|---|---|
| experiment-mockup | SKILL.md Step 5 (Detect Execution Mode) | ACTIVE: injects proposed content into the live DOM and iterates with the user |
| live-capture | SKILL.md Phase 0 (Browser-Mode Detection) | PASSIVE: reads the rendered DOM only, no injection, no mutation |

Both skills navigate the same client pages, so the WAF guidance and the headless pre-flight
probe apply equally to both, regardless of interaction model.

## Canonical Detection Procedure

Do NOT ask the user whether a browser MCP is configured. Test it. But do NOT silently degrade
to static: browser-rendered output is dramatically higher fidelity, and the user deserves to
know before falling back.

1. **`--static` override.** If set, use STATIC MODE. Skip detection. Note briefly that static
   mode is lower fidelity (no render, console, or computed-style data) and how to get the
   browser path back.
2. **Chrome DevTools test (primary).** Call `mcp__chrome-devtools__list_pages` (the exact tool
   name -- do not guess alternatives).
   - Success: CHROME DEVTOOLS MODE.
   - "No such tool" / "unknown tool" error: the Chrome DevTools MCP server is not configured.
     Go to step 3.
   - Connection error, timeout, or other failure: the MCP is configured but broken. **STOP.**
     Do not fall through. Surface the raw error and help the user fix it (Chrome not running,
     remote debugging not enabled, wrong port or host). Re-test with
     `mcp__chrome-devtools__list_pages` after each fix attempt. Only proceed to step 3 if the
     user explicitly says they want to skip Chrome DevTools.
3. **Playwright test (secondary).** Call the Playwright MCP's page/context listing tool (the
   specific tool depends on which Playwright MCP is installed).
   - Success: PLAYWRIGHT MODE. Inform the user that iteration uses managed-browser
     screenshots rather than their live browser window.
   - "No such tool" error: not configured. Go to step 4.
   - Connection error: same as Chrome -- STOP and help debug before falling through.
4. **No browser MCP -- STOP and recommend.** This is a blocking gate, not a silent fallback.
   Tell the user a browser MCP (Chrome DevTools preferred, Playwright alternative) gives far
   higher fidelity, give brief setup steps, and offer: reply "continue" to proceed in static
   mode (lower fidelity), or set up a browser MCP and re-run. Proceed to STATIC MODE only on
   an explicit "continue".
5. **Headless pre-flight probe (after a browser mode is selected, before the first page
   phase).** A connected browser is not necessarily a usable one for WAF-protected targets.
   Once Chrome DevTools or Playwright mode is selected, run one in-page check and record
   `browser_headless`:

   ```
   isHeadless = (navigator.webdriver === true) || /HeadlessChrome/.test(navigator.userAgent)
   ```

   If `isHeadless` is true, surface it BEFORE any page work: "Connected browser is headless.
   WAF-protected targets (Akamai/Cloudflare/etc.) will likely return 403. If the target is
   enterprise-protected, attach to a real Chrome (see the preferred configurations below) and
   re-run." This is cheap and catches the systemic-block situation before grinding through
   the page work.

## WAF / Enterprise Bot Management Guidance

**Real (non-headless) Chrome is required for WAF-protected targets.** Enterprise bot management
(Akamai, Cloudflare, DataDome, PerimeterX, Imperva) fingerprints and 403-blocks HEADLESS Chrome
before any content loads (`HeadlessChrome` user-agent, `navigator.webdriver`, TLS/JA3 and
missing-surface signals). A real Chrome (headful, or a normal Chrome instance attached over
CDP) presents as a human browser and passes. The Chrome-DevTools-first ranking above is not
only about fidelity: a real attached Chrome is also what gets past enterprise WAFs. Preferred
configurations, in order:

- **Chrome DevTools MCP attached to a running real Chrome** (`--browserUrl
  http://127.0.0.1:9222` or `--wsEndpoint ws://...`), rather than letting it launch headless.
- **Playwright MCP run headful, or attached over CDP** (`connectOverCDP` to a real Chrome),
  rather than `--headless`.
- **Headless-only hosts** (servers, WSL, CI): run a real Chrome under a virtual display
  (WSLg / Xvfb) and attach to it, or attach over CDP to a real Chrome elsewhere. The failure
  mode is headless-LAUNCH, not the platform.

**Static fallback is NOT a WAF remedy.** A static HTTP fetch is blocked at least as hard as
headless Chrome (usually harder). Never present `--static` as the answer to a WAF block.

## Invariants (must hold verbatim in spirit in every browser-driving skill)

- **Test, don't ask.** Availability is established by calling the exact tool name, never by
  asking the user or guessing alternative tool names.
- **Configured-but-broken = STOP.** A connection error, timeout, or other failure on a
  configured MCP never falls through to the next mode. Stop, surface the error, help the user
  fix it, re-test. Falling through only on an explicit user skip.
- **No-MCP is a blocking gate, not a silent fallback.** Static mode is entered only on an
  explicit user "continue" (or the `--static` flag), never by default.
- **WAF guidance travels with the contract.** Both skills navigate client pages; both carry
  the headless-403 guidance and the "static is not a WAF remedy" warning.
- **Headless pre-flight probe runs in every browser mode** before the first page phase, and
  its result is surfaced before any capture or injection work.

## Per-skill variations

These are legitimate differences, not drift:

- **experiment-mockup** additionally runs a WSL2-specific Chrome DevTools pre-flight (Step 5.2:
  `.wslconfig` mirrored-networking check, `DevToolsActivePort` symlink repair) before the
  connection test. live-capture reuses experiment-mockup's browser stack and inherits that
  environment work implicitly.
- **live-capture** feeds the probe's `browser_headless` result into the systemic-block rule in
  its `phases/capture.md` Step 1. experiment-mockup surfaces the probe result as a pre-flight
  warning before Phase 1 (Inspect); it has no systemic-block rule because it works one page at
  a time.
- **Static-mode confidence:** live-capture caps artifact confidence at 2-3 in static mode;
  experiment-mockup states a fidelity range (~60-80% CSS accuracy, no screenshots, no
  iteration) instead, because its output is a visual artifact, not a scored context file.
