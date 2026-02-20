# Slugify Module

Deterministic name-to-slug conversion for filenames. Referenced by render-default-deliverables (battle cards) and any skill that writes files keyed by entity name.

---

## Canonical Source Rule

Always derive slugs from a persisted field in a context file, never from conversation context. The LLM's in-session phrasing of a name will vary between runs. The context file field will not.

For battle cards, the canonical source is the `name` field in each competitor entry in `competitive-landscape.md`.

---

## Slugification Steps

Apply these steps in order:

1. **Lowercase** the entire string
2. **Strip leading articles:** remove leading "the ", "a ", "an " (with trailing space, case-insensitive after step 1)
3. **Strip trailing legal suffixes:** remove trailing "Inc", "Inc.", "LLC", "LLP", "Ltd", "Ltd.", "Corp", "Corp.", "Co.", "PLC" (case-insensitive after step 1). Do NOT strip brand-identity words like "Group", "Partners", "Consulting", "Advisory", "Solutions", "Digital", "Capital", "Global", "Associates", "International"
4. **Replace non-alphanumeric characters** (spaces, ampersands, dots, commas, apostrophes, parentheses, etc.) with hyphens
5. **Collapse consecutive hyphens** into one
6. **Strip leading and trailing hyphens**

---

## Python Fallback

If you are generating 3+ slugs in a single session, run this function rather than applying the rules manually. Determinism matters more than elegance.

```python
import re
def slugify(name):
    s = name.lower().strip()
    s = re.sub(r'^(the|a|an)\s+', '', s)
    s = re.sub(r'\s+(inc\.?|llc|llp|ltd\.?|corp\.?|co\.|plc)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')
```

---

## Test Table

Consuming agents should verify their output against this table.

| Input | Expected Slug |
|-------|---------------|
| The Acme Group | acme-group |
| Acme Group | acme-group |
| the acme group | acme-group |
| Globex Consulting | globex-consulting |
| Initech Solutions | initech-solutions |
| Hooli Labs, LLP | hooli-labs |
| Pied Piper | pied-piper |
| Stark Industries LLP | stark-industries |
| DUNDER | dunder |
| Vandelay Partners | vandelay-partners |
| Ernst & Young LLP | ernst-young |
| McKinsey & Company, Inc. | mckinsey-company |
| The Boston Consulting Group | boston-consulting-group |
