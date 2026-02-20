# Web Extract Module

Primary content extractor for positioning research. Uses curl + lightweight HTML parser to extract text content from any URL. Referenced by positioning-framework research phase.

---

## When to Use

Run this extractor as the first-pass extraction method for every URL. It runs before WebFetch and handles the majority of pages cleanly without CSS noise or markdown conversion artifacts.

If the extractor returns <100 words, fall through to WebFetch as described in the Website Content Extraction Flow (see `phases/research.md`).

---

## Command Template

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

## Quality Assessment Thresholds

After running the extractor, count the words in the extracted output and tag accordingly:

| Words | Tag | Meaning |
|-------|-----|---------|
| 500+ | `[FULL]` | Successful extraction. Usable content recovered. |
| 100-499 | `[PARTIAL]` | Partial extraction. Some content recovered but likely incomplete. |
| <100 | Fall through to WebFetch | Curl extraction failed. Try WebFetch per the extraction flow. |

Tag the page fetch in research notes using these tags. These tags are internal to research and do not appear in context files or deliverables.

---

## Limitations

- No link URLs preserved. Anchor text is extracted but `href` targets are discarded.
- No image alt text extracted.
- No fine-grained markdown structure beyond headings (no bold, italic, lists, or tables).
- Heading hierarchy (`#` through `######`) is preserved. All other structure is flattened to plain text lines.

This is sufficient for positioning research where the agent needs headlines, copy, CTAs, and service descriptions. It is NOT sufficient for tasks requiring link mapping, image analysis, or structured content audits.

---

## Source Attribution

Content extracted via curl uses the same source attribution as WebFetch-extracted content. The extraction method is noted in the Copy Verification checkpoint (see SKILL.md) but does not change how content is cited in context files or deliverables.
