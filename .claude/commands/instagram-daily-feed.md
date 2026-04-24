# Instagram Daily Feed — Automated Prompt

_This file is read by the `/schedule` cron job. Do not run manually in most cases — prefer `/schedule` or "Read this file and execute it"._

## Instructions

You are running the daily Korean-language Instagram feed pipeline for Keonhee, benchmarked against @evolving.ai. Execute all 7 steps autonomously. Requires **Playwright MCP** — if not connected, abort at Step 0 with a clear error.

Read `projects/instagram-biz/README.md` once at the start for context. Read `projects/instagram-biz/config/sources.md` for the query list and handle list.

---

### Step 0 — Preflight

- Confirm Playwright MCP is connected. If not, abort: `Instagram feed pipeline aborted — Playwright MCP not connected. See projects/instagram-biz/README.md setup checklist.`
- Compute `TODAY=YYYY-MM-DD` (Asia/Seoul). Create `projects/instagram-biz/drafts/$TODAY/` if it doesn't exist.

---

### Step 1 — Research AI news

First, check if `research/$TODAY-daily-ai-report.md` exists (the 8am Daily AI Report). If yes, read it and extract the concrete news items listed there — these already went through a relevance filter.

Then run **WebSearch** for each query in `projects/instagram-biz/config/sources.md` under "News queries" to fill gaps. Keep only items with a concrete event (release, launch, adoption, benchmark, company AI deployment). Drop opinion and speculation.

Target: 10-15 candidate news items going into Step 4.

---

### Step 2 — Discover + scrape viral X.com posts

**Substep 2a (Discovery — WebSearch):**
- For each handle in `sources.md` → `site:x.com/<handle>` query, past 48h
- Also run broader queries: `site:x.com AI agents viral`, `site:x.com "just shipped" AI`
- Collect 10-20 candidate tweet URLs

**Substep 2b (Scrape — Playwright MCP):**
For each candidate URL:
- Open with Playwright MCP, wait for `article[role="article"]` to render
- Extract: tweet text, author handle, timestamp, like count, repost count (pull numbers from aria-labels on engagement buttons)
- Timeout: 15s per URL. Skip on failure, do not retry hard.
- Drop tweets under 5k likes unless the author is in the curated handle list

Emit a structured list of `{url, author, text, likes, reposts, captured_at}` into your working context for Step 4.

---

### Step 3 — Refresh @evolving.ai live style reference

Use Playwright MCP to open `https://instagram.com/evolving.ai/`.

**If login wall is hit:** skip this step, note `evolving-ai live scrape SKIPPED — login wall` in Step 7's index.md, and Step 5 falls back to the static `projects/instagram-biz/config/evolving-ai-style.md`.

**If feed loads:** scroll to render ~20 posts, click into each (or parse caption from feed if visible), extract caption text only (ignore media). For each: hook line (first line), body length, hashtag count, approximate format (reel/carousel/static based on icon).

Write to `projects/instagram-biz/config/evolving-ai-style-live.md` (overwrite):

```
# @evolving.ai — Last-20-post snapshot
Captured: <ISO timestamp>

## Observed hook patterns
- <pattern 1 with example>
- <pattern 2 with example>
- ...

## Structure
- Average body length: <N> characters
- Average hashtag count: <N>
- Dominant format: <reel | carousel | static> (<%>)

## Sample hooks (verbatim, first 5)
1. <hook 1>
2. <hook 2>
...
```

---

### Step 4 — Rank + select top 3-5

Score each news item and each scraped tweet by:
- **Concreteness** — concrete event > speculation
- **SDIC teachability** — would Keonhee's SDIC audience find it useful?
- **Visual hook potential** — does it have an obvious image/video angle for future Higgs Field / Nano Banana Pro generation?
- **Novelty** — dedupe near-identical stories across news + X (one story, pick the better source)

Pick top **3-5 items**. Mix at least 1 news + 1 X post if both source types yielded candidates.

---

### Step 5 — Draft each post

For each selected item, write to `projects/instagram-biz/drafts/$TODAY/post-NN.md` (NN = 01, 02, ...).

Reference **`projects/instagram-biz/config/evolving-ai-style-live.md`** if it exists and is from today. Otherwise fall back to `projects/instagram-biz/config/evolving-ai-style.md`.

Template:

```
# <English working title>

**Source:** <URL>
**Source type:** news | x.com | company-announcement
**Original language:** en | ko | other
**Captured:** <ISO timestamp>
**Engagement (if X):** <likes> likes, <reposts> reposts

## English summary (for reference)
<3-4 sentences, the core news>

## Korean caption (for upload)
<Hook — 1 line, question or bold claim>

<Beat 1 — what happened, 1-2 sentences>

<Beat 2 — why it matters, 1-2 sentences>

<Beat 3 — takeaway or action, 1 sentence>

<CTA — 1 line>

#AI #인공지능 #<5-8 total tags, mix KR+EN>

## Image prompt — PLACEHOLDER (Higgs Field / Nano Banana Pro)
<Ready-to-paste prompt: visual concept, style reference, aspect ratio 4:5 or 1:1 or 9:16, mood, text-overlay hint>
<!-- TODO: wire to Higgs Field / Nano Banana Pro API when accounts are provisioned -->

## Alt-format notes
- Carousel breakdown: <slide 1 / slide 2 / slide 3 if this works as carousel>
- Reel angle: <if this works better as 15-30s reel, note the beat structure>
```

Korean fluency rules:
- No em dashes in captions (reserved for internal docs)
- No emoji spam (0-2 max, only if they add meaning)
- Hook + body total 80-150 Korean characters (excluding hashtags)
- Hashtags: 5-8, mix Korean + English

---

### Step 6 — Self-review pass

Re-read each draft once. Rewrite any of:
- Weak Korean (awkward phrasing, English calques, machine-translation feel)
- Flat hooks (no bite, generic "AI 뉴스")
- Generic hashtags (just `#AI` with no specificity)
- Missing beats or over-length captions

One pass only. No scoring loop. Save back to the same file.

---

### Step 7 — Wrap up

Write `projects/instagram-biz/drafts/$TODAY/index.md`:

```
# Instagram Feed Drafts — $TODAY

Playwright status: <connected | evolving-ai scrape skipped: login wall | X scrape partial: N/M posts>
Style reference used: <live | static-fallback>

## Posts

| # | Title | Source type | Status |
|---|-------|-------------|--------|
| 01 | <title> | news | draft |
| 02 | <title> | x.com | draft |
| ... | ... | ... | ... |

## Notes
- <any skips, rate limits, anomalies worth flagging>
```

Append one line to `tasks/todo.md`:
```
- [ ] Review IG drafts — projects/instagram-biz/drafts/$TODAY/
```

Print final confirmation:
```
IG feed drafts saved — <N> posts at projects/instagram-biz/drafts/$TODAY/. Style reference: <live|static>. Playwright: <OK|partial|skipped>.
```
