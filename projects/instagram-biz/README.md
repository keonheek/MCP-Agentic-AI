# Instagram Biz — Daily AI Feed

Automated daily Korean-language Instagram post drafts benchmarked against [@evolving.ai](https://instagram.com/evolving.ai/) (~4M followers, AI news curation).

## Purpose

Produce 3-5 ready-to-upload Korean IG drafts every morning from:
- Recent AI news + infrastructure updates (past 48h)
- Enterprise AI implementation case studies
- Viral AI posts from X.com (translated + adapted to IG format)

## Cadence

- Scheduled via `/schedule` → "Instagram Daily Feed" (9am daily, cron `0 9 * * *`)
- Runs after the 8am Daily AI Report so it can reuse filtered news

## Output

- `projects/instagram-biz/drafts/YYYY-MM-DD/post-NN.md` — one markdown file per post
- `projects/instagram-biz/drafts/YYYY-MM-DD/index.md` — list of that day's drafts + status
- `projects/instagram-biz/config/evolving-ai-style-live.md` — scraped style snapshot (overwritten daily)

## Run manually

```
Read .claude/commands/instagram-daily-feed.md and execute it.
```

## Upload flow

- **v1 (now):** manual copy-paste from the draft file into the Instagram app
- **v2 (future):** Meta Graph API wrapper once Instagram Business account is provisioned

## Image generation — PLACEHOLDER

Every draft includes a `## Image prompt — PLACEHOLDER` block with a ready-to-paste prompt for **Higgs Field** or **Nano Banana Pro**. The API wrapper lives in a future `scripts/generate_image.py` (not built yet). Until then, Keonhee pastes the prompt into the tool manually.

## Benchmark account

[@evolving.ai](https://instagram.com/evolving.ai/) — AI news curation, ~4M followers. The pipeline scrapes the last 20 posts each morning to capture the live caption style (hook pattern, beat count, hashtag mix, length) and feeds that into the draft generator.

## Playwright MCP — REQUIRED

Both source types need a headless browser because WebFetch hits 403 on X.com and Instagram.

**Setup checklist:**
1. Playwright MCP must be connected (run `/mcp` to verify)
2. Must be able to load `https://x.com/karpathy` and return visible tweet text (logged-out is fine for X)
3. Must be able to load `https://instagram.com/evolving.ai/` without hitting a login wall
   - If it hits the wall: log in once inside the Playwright browser profile so cookies persist across runs
   - If login persistence is unreliable, the pipeline falls back to the static `config/evolving-ai-style.md` baseline and logs the skip in `index.md`

## Config files

- `config/sources.md` — WebSearch query strings + curated X.com handles to track
- `config/evolving-ai-style.md` — static baseline style guide (fallback when live scrape fails)
- `config/evolving-ai-style-live.md` — live style snapshot, regenerated each run
