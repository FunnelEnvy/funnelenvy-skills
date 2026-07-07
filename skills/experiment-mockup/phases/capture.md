# Phase 3: Capture -- Live Mode Only

**Purpose:** Persist the approved mockup as a standalone HTML artifact and browser screenshot for async sharing.

**Applies to:** Live mode only. Static mode builds mockup.html directly in `static-build.md`.

---

## Required Inputs

- Final injection HTML and CSS (from Phase 2)
- Final insertion point / DOM path (from Phase 2)
- The injected element's class/id (from Phase 2, e.g. `proposed-change-block`)
- Hypothesis number, name, target URL (from orchestrator)
- Output directory path (from orchestrator)

## Outputs

Written to the output directory the orchestrator passes (legacy `.claude/deliverables/experiments/<slug>/`; KB mode `{kb_root}/deliverables/experiments/<slug>/`):

- `<output-dir>/control-screenshot.png` (desktop viewport screenshot of the unmodified "before" state)
- `<output-dir>/mockup-screenshot.png` (desktop viewport screenshot of the injected "after" state)
- `<output-dir>/control-screenshot-mobile.png` (390px viewport screenshot of the unmodified "before" state)
- `<output-dir>/mockup-screenshot-mobile.png` (390px viewport screenshot of the injected "after" state)
- `<output-dir>/mockup.html` (standalone self-contained HTML)

---

## Steps

### Step 1: Capture the Before/After Screenshot Pair

Capture two screenshots from the same scroll position and viewport width so they are directly comparable: the unmodified control ("before") and the injected state ("after"). The injected element is currently present in the DOM (Phase 2 left it injected). Capture in this order so the control is the genuine pre-change state:

1. **Frame the region.** Scroll so the injected element is centered (or fully visible) in the viewport. Do NOT change the scroll position or viewport width again until both screenshots are taken. Both shots must frame the same region.
2. **Restore the original state.** Remove the injected element using the class/id from Phase 2.
   - Chrome DevTools mode: remove the element via DevTools DOM manipulation.
   - Playwright mode: `browser_evaluate('document.querySelector(".proposed-change-block").remove()')` (use the actual class/id Phase 2 used).
   If Phase 2 also modified or replaced existing elements (not just inserted one), restore those originals too, so the control shows the true unmodified page.
3. **Capture the control.** Screenshot the current viewport (now unmodified) and write it to the output directory as `control-screenshot.png`. Full viewport width, PNG.
4. **Re-apply the change.** Re-inject the final injection HTML at the same insertion point, exactly as Phase 2 left it. Verify it rendered.
5. **Capture the after.** Screenshot the current viewport (now showing the injected change) and write it to the output directory as `mockup-screenshot.png`. Full viewport width, PNG.

- Chrome DevTools mode: use the DevTools screenshot tool.
- Playwright mode: use browser_take_screenshot.

Requirements:
- The injected element must be visible in the "after" shot, and its (now empty) location visible in the "before" shot, at the same scroll position.
- Both screenshots frame the same region at the same viewport width so the pair is comparable.
- Save both as PNG.

**Mobile pair (390px).** After the desktop pair, capture the same Before/After pair at a 390px viewport width, using the same restore/re-inject choreography so the mobile control is the genuine pre-change state:

6. **Resize to 390px** width. Scroll so the injected element (still present from step 5) is centered or fully visible. Do NOT change scroll or width again until both mobile shots are taken.
7. **Restore the original state** (remove the injected element, and restore any modified/replaced originals) exactly as in step 2.
8. **Capture the mobile control.** Screenshot the current 390px viewport and write it as `control-screenshot-mobile.png`.
9. **Re-apply the change** at the same insertion point, exactly as Phase 2 left it. Verify it rendered.
10. **Capture the mobile after.** Screenshot the current 390px viewport and write it as `mockup-screenshot-mobile.png`.
11. **Restore the desktop viewport** so any downstream step runs at the original width.

Mobile-pair requirements: both mobile shots frame the same region at 390px; leave the element injected at the end (Phase 3 Step 2 reads the DOM from the injected state).

### Step 2: Extract Modified Section HTML

Use the browser MCP to read the outerHTML of the section containing the injection. This should be the parent section identified in Phase 1, not the entire page.

- Chrome DevTools mode: use DevTools DOM inspection tools
- Playwright mode: `browser_evaluate('document.querySelector("[section-selector]").outerHTML')`

Also extract:
- The section immediately ABOVE the target section (for surrounding context)
- The section immediately BELOW the target section (for surrounding context)

This gives us three sections: context-above, target-with-injection, context-below.

### Step 3: Build Standalone mockup.html

Create a self-contained HTML file from the extracted sections.

Structure:
```html
<!--
  schema: experiment-mockup
  schema_version: "1.0"
  hypothesis: [number]
  hypothesis_title: "[name]"
  target_url: "[url]"
  insertion_point: "[DOM path]"
  mode: live
  generated_by: experiment-mockup v1.5.0
  last_updated: [YYYY-MM-DD]
-->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mockup: [hypothesis name]</title>
  <style>
    /* Reset */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    /* Base styles extracted from computed styles */
    body {
      font-family: [extracted body font-family];
      font-size: [extracted body font-size];
      line-height: [extracted body line-height];
      color: [extracted body color];
      background-color: [page background color];
    }

    /* Container to match site content width */
    .mockup-container {
      max-width: [extracted content max-width];
      margin: 0 auto;
      padding: [extracted content padding];
    }

    /* Section styles - inlined from computed styles of each section */
    [section-specific CSS here, extracted from the three captured sections]

  </style>
</head>
<body>
  <div class="mockup-container">
    <!-- Section above (surrounding context) -->
    [extracted HTML of section above, with inline styles]

    <!-- Target section with injection (the mockup) -->
    [extracted HTML of target section including the injected element]

    <!-- Section below (surrounding context) -->
    [extracted HTML of section below, with inline styles]
  </div>
</body>
</html>
```

Requirements:
- ALL CSS must be inline (in `<style>` tag or inline `style` attributes). Zero external stylesheet references.
- ALL images should use their original absolute URLs (https://...). Do not download or embed images.
- Remove any `<script>` tags from extracted HTML (the mockup is static, no JS needed unless the hypothesis requires interactive behavior)
- The file must render correctly when opened standalone in a browser
- Target file size: under 50KB of HTML (excluding image URLs)

### Step 4: Write Files

1. Create the orchestrator-provided output directory if it doesn't exist (legacy `.claude/deliverables/experiments/<slug>/`; KB mode `{kb_root}/deliverables/experiments/<slug>/`)
2. Write `mockup.html` to the output directory
3. Write `control-screenshot.png`, `mockup-screenshot.png`, `control-screenshot-mobile.png`, and `mockup-screenshot-mobile.png` to the output directory (already saved in Step 1)
4. Confirm the files are written: "Mockup captured (before + after, desktop + mobile). Files written to [output directory]."
