# Phase 3: Capture -- Live Mode Only

**Purpose:** Persist the approved mockup as a standalone HTML artifact and browser screenshot for async sharing.

**Applies to:** Live mode only. Static mode builds mockup.html directly in `static-build.md`.

---

## Required Inputs

- Final injection HTML and CSS (from Phase 2)
- Final insertion point / DOM path (from Phase 2)
- Hypothesis number, name, target URL (from orchestrator)
- Output directory path (from orchestrator)

## Outputs

- `.claude/deliverables/experiments/<slug>/mockup.html` (standalone self-contained HTML)
- `.claude/deliverables/experiments/<slug>/mockup-screenshot.png` (browser viewport screenshot)

---

## Steps

### Step 1: Capture Screenshot

Use Chrome DevTools MCP to capture a screenshot of the current viewport showing the injected change.

Requirements:
- The injected element must be visible in the viewport. If needed, scroll to center it.
- Capture the full viewport width (desktop resolution)
- Save as PNG

Write the screenshot to the output directory as `mockup-screenshot.png`.

### Step 2: Extract Modified Section HTML

Use Chrome DevTools MCP to read the `outerHTML` of the section containing the injection. This should be the parent section identified in Phase 1, not the entire page.

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
  generated_by: experiment-mockup v1.0.0
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

1. Create the output directory if it doesn't exist: `.claude/deliverables/experiments/<slug>/`
2. Write `mockup.html` to the output directory
3. Write `mockup-screenshot.png` to the output directory (already saved in Step 1)
4. Confirm both files are written: "Mockup captured. Files written to [output directory]."
