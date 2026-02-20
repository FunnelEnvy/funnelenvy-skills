# Reddit Research Module

Shared instructions for querying Reddit. Referenced by positioning-framework at all depth levels.

---

## How It Works

Uses Reddit's public JSON endpoints. No API key or OAuth token required. Append `.json` to any old.reddit.com URL to get structured JSON back.

Rate limit is roughly 10 requests/minute on the public endpoint. Skills stay well within this (2-8 calls per run).

---

## API Patterns

All queries use Bash with curl. Always include the User-Agent header.

### Search (cross-subreddit)

```bash
curl -s -H "User-Agent: funnelenvy-skills/1.0" \
  "https://old.reddit.com/search.json?q=QUERY&limit=10&sort=relevance&t=all"
```

URL-encode the query. Use `+` for spaces, `%22` for quotes. Examples:
- `q=%22typeform+alternative%22` searches for the exact phrase "typeform alternative"
- `q=reform+vs+typeform` searches for posts containing those words
- `q=%22reform%22+OR+%22reform.app%22` searches for either term

### Search within a specific subreddit

```bash
curl -s -H "User-Agent: funnelenvy-skills/1.0" \
  "https://old.reddit.com/r/SUBREDDIT/search.json?q=QUERY&restrict_sr=on&limit=10&sort=relevance&t=all"
```

Useful subreddits by category:
- SaaS/tools: r/SaaS, r/startups, r/indiehackers, r/SideProject, r/Entrepreneur
- Marketing: r/marketing, r/PPC, r/SEO, r/digital_marketing
- Dev tools: r/webdev, r/javascript, r/selfhosted
- Industry-specific: identify from the company's target market

### Read a thread with comments

```bash
curl -s -H "User-Agent: funnelenvy-skills/1.0" \
  "https://old.reddit.com/r/SUBREDDIT/comments/POST_ID.json?depth=2&limit=20"
```

The `POST_ID` is the 6-7 character alphanumeric ID from the thread URL. For example, from `/r/SaaS/comments/1pju3ty/...`, the POST_ID is `1pju3ty`.

`depth=2` gets top-level comments and one level of replies. `limit=20` caps comment count. Increase to `limit=50` for deep-depth reads.

### Response parsing

Use python3 to extract what you need from the JSON:

```bash
curl -s -H "User-Agent: funnelenvy-skills/1.0" \
  "https://old.reddit.com/search.json?q=QUERY&limit=10&sort=relevance" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for post in data['data']['children']:
    d = post['data']
    print(f\"Score: {d['score']} | Comments: {d['num_comments']} | r/{d['subreddit']}\")
    print(f\"  {d['title']}\")
    print(f\"  {d['selftext'][:200]}\")
    print()
"
```

For comments (thread reads), the response is an array of two listings:
- `[0]` is the post itself
- `[1]` is the comment tree

```bash
curl -s -H "User-Agent: funnelenvy-skills/1.0" \
  "https://old.reddit.com/r/SUBREDDIT/comments/POST_ID.json?depth=2&limit=20" | python3 -c "
import json, sys
data = json.load(sys.stdin)
post = data[0]['data']['children'][0]['data']
print(f\"POST: {post['title']}\")
print(f\"Body: {post['selftext'][:300]}\")
print('---')
for c in data[1]['data']['children']:
    if c['kind'] == 't1':
        d = c['data']
        print(f\"[{d['score']} pts] {d['body'][:200]}\")
        print()
"
```

Key fields:
- `data.children[].data.title` - post title
- `data.children[].data.selftext` - post body text
- `data.children[].data.score` - upvotes (quality signal)
- `data.children[].data.num_comments` - discussion depth
- `data.children[].data.permalink` - link to thread
- `data.children[].data.subreddit` - which subreddit

---

## Skill-Specific Query Templates

### positioning-framework at quick depth (1-2 searches, snippets only)

| Query | What it reveals |
|-------|----------------|
| `"[company]" OR "[product]"` | General sentiment, what users say unprompted |
| `"[company] vs" OR "[company] alternative"` | Buyer comparisons, competitive framing |

Read post titles and top-level comment snippets only. Do not read full threads. Budget: 2 API calls max.

### positioning-framework (3-5 searches, selective thread reads)

| Query | What it reveals |
|-------|----------------|
| `"[company]" OR "[product]"` | General sentiment |
| `"[company] vs" OR "[company] alternative"` | Buyer comparisons |
| `"switched from [company]" OR "switched to [company]"` | Switching stories (Four Forces) |
| `"[company] review" OR "[company] complaints"` | Objections, pain points |
| `"[category] recommendation" OR "best [category]"` | Category language, buyer framing |

Read 2-3 full threads that have the richest discussion (highest comment count + relevance). Budget: 5 API calls max.

### positioning-framework at deep depth (4-6 searches, deeper thread reads)

| Query | What it reveals |
|-------|----------------|
| `"[company] vs [competitor]"` per major competitor | Head-to-head buyer comparisons |
| `"best [category]" OR "[category] comparison"` | How buyers frame the competitive set |
| `"switched from [competitor]" OR "left [competitor]"` | Why buyers leave competitors (feeds "When We Win") |
| `"[competitor] problems" OR "[competitor] issues"` | Competitor weaknesses from real users |
| `"[category] recommendation"` in relevant subreddit | Targeted subreddit discussions |

Read 3-4 full threads. Prioritize threads with 10+ comments. Budget: 8 API calls max.

---

## Handling Low/No Results

If Reddit search returns no results for the company name:
- The company has low Reddit presence. This is itself a finding (note it in discoverability).
- Fall back to category-level searches: `"best [category]"`, `"[category] recommendation"`. These reveal what buyers care about even if the specific company isn't mentioned.
- Do NOT waste additional queries trying variations. Move on.

---

## Integration Points

Reddit data feeds into specific output sections per skill:

| Skill | Section | What Reddit adds |
|-------|---------|-----------------|
| positioning-framework (quick depth) | 1. What They Say | Real user language vs. marketing claims |
| positioning-framework (quick depth) | 3. Value Themes | Buyer-validated differentiators |
| positioning-framework | Switching Dynamics | Push/pull/habit/anxiety from real switchers |
| positioning-framework | Objection Handling | Objections from unmoderated sources |
| positioning-framework | Language Bank | Exact phrases buyers use |
| positioning-framework | Voice-of-Customer | Unfiltered sentiment |
| positioning-framework (deep) | Battle Cards ("When We Lose") | Honest competitive loss reasons |
| positioning-framework (deep) | Buyer Scenarios | Real purchase decision triggers |
| positioning-framework (deep) | Competitive White Space | Unmet needs from complaint threads |

---

## Source Attribution

When citing Reddit data in outputs, use this format:

```
[Reddit, r/subreddit, N upvotes]
```

Example: "Users describe Reform as 'what Typeform should have been' [Reddit, r/SaaS, 47 upvotes]"

Mark Reddit-sourced findings with the source tier label: `[Tier 2: Reddit]` in section confidence notes.
