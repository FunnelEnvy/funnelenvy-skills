# Web Extract Module

Three-tier content extractor for positioning research. Primary: markdown.new (Cloudflare service, handles SPAs natively). Fallback Tier 1: curl + python3 HTMLParser. Fallback Tier 2: WebFetch tool. Referenced by positioning-framework research and competitive phases.

---

## Pipeline Overview

Three-tier fallback chain for extracting web content from any URL:

1. **markdown.new (primary).** Cloudflare Workers service that converts any URL to clean markdown. Internally uses content negotiation, Workers AI, and headless browser rendering. Returns `text/markdown; charset=utf-8`. Handles SPAs natively (headless browser tier renders JS). Rate limit: 500 requests/day/IP. HTTP 429 triggers immediate fallback to Tier 1 (no retry).
2. **curl + HTMLParser (Fallback Tier 1).** Local Python extractor. Strips scripts/styles/SVG and preserves heading hierarchy as markdown. Used when markdown.new fails or returns insufficient content (<100 words).
3. **WebFetch (Fallback Tier 2, last resort).** Claude Code built-in tool. Used when both markdown.new and curl+HTMLParser fail to extract sufficient content. Filter CSS noise from output before assessing word count.

If markdown.new returns <100 words or the request fails (timeout, HTTP error, empty response), fall through to Tier 1. If Tier 1 returns <100 words, fall through to Tier 2.

---

## Tier 0 -- markdown.new (Primary)

Command template:

```bash
curl -s --max-time 10 "https://markdown.new/$URL"
```

Replace `$URL` with the full target URL including protocol (e.g., `https://markdown.new/https://example.com/pricing`).

Output is raw markdown. No HTML parsing needed. No CSS noise. No artifact stripping needed (markdown.new strips it server-side).

Word count check: count words in the returned content. Apply thresholds from the Quality Assessment Thresholds section below.

If the curl command fails (non-zero exit, empty stdout, or HTTP 429 status), fall through to Tier 1 immediately. Do NOT retry markdown.new.

To detect 429: use `curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://markdown.new/$URL"` first if rate limiting is suspected after multiple requests. Otherwise, check if content is empty or contains an error message.

---

## Tier 1 -- curl + HTMLParser (Fallback)

Fallback when markdown.new fails or returns insufficient content (<100 words).

```bash
curl -sL -H "User-Agent: funnelenvy-skills/1.0" "URL" | python3 -c "
import sys
from html.parser import HTMLParser

class Extractor(HTMLParser):
    STRIP_TAGS = {'style', 'script', 'svg', 'noscript', 'head'}

    def __init__(self):
        super().__init__()
        self.skip_depth = 0
        self.lines = []
        self.current_line = ''
        self.in_heading = None

    def handle_starttag(self, tag, attrs):
        if tag in self.STRIP_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in ('h1','h2','h3','h4','h5','h6'):
            self.in_heading = tag
            level = int(tag[1])
            self.flush()
            self.current_line = '#' * level + ' '
        elif tag in ('p','div','li','tr','br','hr'):
            self.flush()

    def handle_endtag(self, tag):
        if tag in self.STRIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == self.in_heading:
            self.in_heading = None
            self.flush()
        elif tag in ('p','div','li','tr'):
            self.flush()

    def handle_data(self, data):
        if self.skip_depth:
            return
        text = data.strip()
        if text:
            if self.current_line and not self.current_line.endswith(' '):
                self.current_line += ' '
            self.current_line += text

    def flush(self):
        line = self.current_line.strip()
        if line:
            self.lines.append(line)
        self.current_line = ''

    def result(self):
        self.flush()
        deduped = []
        for line in self.lines:
            if not deduped or line != deduped[-1]:
                deduped.append(line)
        out = []
        blank_run = 0
        for line in deduped:
            if line == '':
                blank_run += 1
                if blank_run < 3:
                    out.append(line)
            else:
                blank_run = 0
                out.append(line)
        return '\n'.join(out)

e = Extractor()
e.feed(sys.stdin.read())
print(e.result())
"
```

Replace `URL` with the target page URL.

---

## Tier 2 -- WebFetch (Last Resort)

Last resort when both markdown.new and curl+HTMLParser fail to extract sufficient content (<100 words from both).

Use the WebFetch tool on the same URL.

Filter CSS noise from WebFetch output before assessing word count: discard `<style>` blocks, CSS class definitions, and inline styling rules. Focus on HTML semantic elements: headings, paragraphs, lists, links with visible text, and image alt text.

Assess by word count after filtering.

---

## Tier 3 -- Screenshot / Manual Content (Human Fallback)

When all three automated tiers fail and the page is tagged `[EMPTY:BLOCKED]` or `[EMPTY:SPA]`, request human-provided content before giving up:

```
The page at [URL] is blocking automated extraction (Akamai CDN / bot protection). To continue with page-specific analysis, please share one of:
- A full-page screenshot (share it in this conversation and I will read it directly)
- A browser PDF export (File > Print > Save as PDF)
- Paste the page copy directly into the chat

Without this, section-level content analysis cannot proceed.
```

When content is provided, extract it as follows:

- **Screenshot:** Use the Read tool on the image file. Extract all visible headings, body copy, CTAs, navigation tabs, accordion labels, form fields, and any stats or proof points. Structured sections (e.g., "Key Features", "Services and Software", "Valuation Inputs") should be recorded as named sections in research notes.
- **PDF:** Read with the Read tool (PDF mode). Extract the same elements.
- **Pasted text:** Accept as-is and parse into named sections where possible.

**Quality tags for human-provided content:**

| Tag | Meaning |
|-----|---------|
| `[PARTIAL:SCREENSHOT]` | Content extracted from a user-provided screenshot |
| `[PARTIAL:PDF]` | Content extracted from a browser PDF export |
| `[PARTIAL:MANUAL]` | Content pasted directly by the user |

Apply the same word-count thresholds as other tiers when determining completeness. Log the human-provided source in the fetch registry with the appropriate tag.

**Important:** If a spec or brief lists named page sections (e.g., "key features", "services & software", "valuation inputs"), verify that each named section was captured in the extracted content. If a section is missing from the screenshot (cut off, collapsed accordion, or not visible), note it explicitly in research notes and flag it in the fetch registry entry.

---

## Quality Assessment Thresholds

After running extraction, count the words in the output and tag accordingly:

| Words | Source | Tag | Meaning |
|-------|--------|-----|---------|
| 500+ | markdown.new | `[FULL]` | Successful extraction from primary extractor |
| 100-499 | markdown.new | `[PARTIAL]` | Partial extraction from primary extractor |
| 500+ | curl + HTMLParser | `[FULL:CURL]` | Successful extraction from Fallback Tier 1 |
| 100-499 | curl + HTMLParser | `[PARTIAL:CURL]` | Partial extraction from Fallback Tier 1 |
| 100+ | WebFetch | `[PARTIAL:TOOL]` | Extraction from Fallback Tier 2 (last resort) |
| 100+ | Screenshot | `[PARTIAL:SCREENSHOT]` | Content extracted from user-provided screenshot |
| 100+ | PDF export | `[PARTIAL:PDF]` | Content extracted from browser PDF export |
| 100+ | Pasted manually | `[PARTIAL:MANUAL]` | Content pasted directly by the user |
| <100 | All three failed, SPA indicators | `[EMPTY:SPA]` | JS-heavy site, no content extracted by any method |
| <100 | All three failed, access blocked | `[EMPTY:BLOCKED]` | Bot protection blocked all automated extraction -- request Tier 3 |
| <100 | All three failed, other | `[EMPTY]` | Content genuinely absent or all tools failed |

Tag the page fetch in research notes using these tags. Tags are internal to research and do not appear in context files or deliverables.

The source suffix (`:CURL`, `:TOOL`) tells downstream consumers which extractor succeeded. Unqualified `[FULL]` and `[PARTIAL]` mean markdown.new (primary) was sufficient.

---

## Extraction Flow (Step-by-Step)

Follow this procedure for each URL:

1. Run markdown.new: `curl -s --max-time 10 "https://markdown.new/$URL"`
2. Count words in output.
3. If 500+ words: tag `[FULL]`, use content. Done.
4. If 100-499 words: tag `[PARTIAL]`, use content. Done.
5. If <100 words, empty, or request failed: proceed to step 6.
6. Run curl + HTMLParser using the Tier 1 command template.
7. Count words in output.
8. If 500+ words: tag `[FULL:CURL]`, use content. Done.
9. If 100-499 words: tag `[PARTIAL:CURL]`, use content. Done.
10. If <100 words: proceed to step 11.
11. Run WebFetch on the same URL.
12. Filter CSS noise from WebFetch output.
13. If 100+ words after filtering: tag `[PARTIAL:TOOL]`, use content. Done.
14. If <100 words after filtering: triage failure:
    - SPA indicators present? Tag `[EMPTY:SPA]`. Proceed to step 15 (Tier 3 request).
    - Access blocked? Tag `[EMPTY:BLOCKED]`. Proceed to step 15 (Tier 3 request).
    - Neither? Tag `[EMPTY]`. Write `[NOT EXTRACTED - tool parse failure]`. Stop.
15. **Tier 3 -- Human fallback.** Output the Tier 3 prompt from the Tier 3 section above and wait for the user to provide a screenshot, PDF, or pasted content. When received, extract content using the Read tool or accept pasted text directly. Tag with `[PARTIAL:SCREENSHOT]`, `[PARTIAL:PDF]`, or `[PARTIAL:MANUAL]` as appropriate. If no content is provided, write `[NOT EXTRACTED - access blocked, no human fallback provided]` and continue with remaining URLs.

---

## Limitations

- markdown.new output is clean markdown with headings, bold, italic, lists, links, and tables preserved. This is richer than the curl+HTMLParser output.
- curl+HTMLParser limitations: no link URLs preserved (anchor text extracted but `href` targets discarded), no image alt text extracted, no fine-grained markdown structure beyond headings (no bold, italic, lists, or tables), heading hierarchy (`#` through `######`) preserved but all other structure flattened to plain text lines.
- WebFetch may include CSS noise that requires filtering.
- Rate limit: 500 requests/day/IP for markdown.new. A standard-depth run fetches 15-20 pages (well within budget). Deep-depth with competitor research may approach 35+ total fetches across agents. If rate-limited, the fallback chain handles it transparently.

---

## Source Attribution

Content extracted via any tier uses the same source attribution rules. The extraction method is noted in research notes (via quality tags) but does not change how content is cited in context files or deliverables.
