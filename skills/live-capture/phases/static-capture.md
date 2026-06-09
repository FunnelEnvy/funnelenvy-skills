# Phase 2 (fallback): Static Capture

Used only when no browser MCP is available and the user chose to continue (Phase 0 browser-mode detection). Lower fidelity (~70%): no computed styles, no console, no network, no render data.

Read `agent-header.md` first.

## Procedure

### Step 1: Fetch page HTML + CSS

Use `modules/web-extract.md`, prioritizing raw HTML over markdown:

1. `curl -sL --max-time 15 <url>` for raw HTML.
2. If curl fails or returns empty: fall through to `web-extract.md` Tier 0 (markdown.new) for at least structural understanding.
3. If all tiers fail: record `page_block_status` (`akamai-403` / `challenge` / `partial`) for that page and continue. Do not abort the run.

Also fetch linked stylesheets (`<link rel="stylesheet">`, resolve relative URLs) for any structural class hints.

### Step 2: Parse structure

From the raw HTML, extract the same blocks as `capture.md` Steps 2-4 to the extent they are observable in static HTML:

- **A-G, I:** Parse from the DOM string. H1, headings, CTAs (anchors/buttons with their text + href), forms (field `<input>`/`<select>` counts, required attributes, labels), login links, nav labels, proof/logo/team sections, chatbot script tags. Position encoding (fold/ordinal/region) is approximate in static mode: use document order for ordinal and region (header/main/footer landmarks); fold is `not_checked` unless inferable.
- **E (sequential UI):** count accordion/tab/carousel markup; nested content is `in_dom` if present in the HTML, else `not_checked` (cannot detect lazy-load without a browser).
- **H. Render / technical:** write `[NOT AVAILABLE: static mode]` for `console_error_count`, `page_error_count`, `failed_request_count`, `render_correctness`. `rendered_page_height` is `not_checked` (no layout). NEVER write a false `clean`.
- **Copy (live-copy.md):** H1, subhead, value-prop, copy skeleton, proof statements verbatim from the HTML.

### Step 3: content_hash + confidence

- Compute `content_hash` via `scripts/content_hash.py` exactly as in `capture.md` Step 5.
- Per-page confidence in static mode is 2 (static dominant) or 3 (clean static with good extraction). Never higher.

## Output

Per-page captured facts and copy with static-mode caveats, carried to Phase 3 (`write.md`). Block H carries the `[NOT AVAILABLE: static mode]` marker so downstream consumers do not mistake missing render data for a clean render.
