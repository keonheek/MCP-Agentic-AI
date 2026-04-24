# Playwright MCP — YouTube Visual Research Playbook

_For capturing visual context from YouTube (thumbnails, banners, page layouts) without burning anti-bot quota. Playwright MCP is already installed._

---

## Data split — what to use for what

| Data type | Tool | Why |
|---|---|---|
| Video metadata (title, views, duration, tags) | yt-dlp | Already wired, no anti-bot risk |
| Channel stats (subscribers, verified) | YouTube Data API | Official, rate-limited but free |
| Video transcripts | youtube-transcript MCP | Reliable, no browser needed |
| **Visual layout (thumbnails, banners, page structure)** | **Playwright MCP** | Only use for visuals |

Do NOT use Playwright for data you can get from yt-dlp or the API. Playwright is for what you can only get visually.

---

## Anti-bot guardrails

- **Treat Playwright as a spot-check tool, not a crawler.** Cap at ~30 page loads/day on YouTube.
- Insert 2–5 second delays between page loads if doing multiple in one session.
- Do NOT log in to any Google/YouTube account from Playwright. Use only logged-out public pages.
- If you see CAPTCHAs or throttling: stop, wait 24h, then resume.
- Do NOT pay for Browserbase or proxy services unless volume actually justifies it (you're not at that scale yet).

---

## Worked example 1 — Capture a channel banner

In a Claude Code session:

```
Use Playwright to:
1. Go to https://www.youtube.com/@nateherk
2. Wait for the page to load (wait for #channel-header)
3. Take a full-page screenshot
4. Save as projects/youtube-biz/visuals/nate-herk/2026-04-23-channel-banner.png
```

What you get: full channel page including the banner, avatar, and top video strip.

---

## Worked example 2 — Capture top-3 video thumbnails from a channel

```
Use Playwright to:
1. Go to https://www.youtube.com/@MrBeast/videos
2. Wait for the video grid to load
3. Screenshot the first 3 video thumbnails (element: ytd-grid-video-renderer:nth-child(-n+3))
4. Save each to projects/youtube-biz/visuals/mrbeast/2026-04-23-thumb-{1,2,3}.png
```

Note: If element selectors fail (YouTube changes their DOM frequently), use full-page screenshot and crop manually.

---

## Worked example 3 — Capture a video page layout

```
Use Playwright to:
1. Go to https://www.youtube.com/watch?v=<VIDEO_ID>
2. Wait for the player and sidebar to load
3. Take a full-page screenshot (above-the-fold only is fine for layout analysis)
4. Save as projects/youtube-biz/visuals/<channel>/<date>-video-page.png
```

Use this to analyze: title formatting, thumbnail choice, sidebar recommendations, like count display.

---

## Saving captured visuals

Standard save path: `projects/youtube-biz/visuals/<channel-slug>/<YYYY-MM-DD>-<description>.png`

Examples:
```
projects/youtube-biz/visuals/nate-herk/2026-04-23-channel-banner.png
projects/youtube-biz/visuals/chase-reiner/2026-04-23-thumb-1.png
projects/youtube-biz/visuals/mrbeast/2026-04-23-video-page.png
```

---

## Combining Playwright with youtube-transcript MCP

For a full competitor analysis of one video:

1. **Transcript:** `youtube-transcript MCP → get-transcript(<video_id>)` — who-said-what, timestamps
2. **Visual:** Playwright → capture intro frame + any flowchart/diagram moments
3. **Metadata:** yt-dlp → `yt-dlp --dump-json <URL>` for views, upload date, tags
4. Save everything to `research/YYYY-MM-DD-<creator>-analysis/`

This is the same pattern used in the YouTube Analyst Agent — Playwright adds the visual layer.

---

## When Playwright fails on YouTube

YouTube detects headless browsers via fingerprinting. Common failures:
- CAPTCHA on the first page load
- Redirect to consent/cookie page (just click through — Playwright can handle this)
- Video player not loading (doesn't matter — you only need the page layout, not the video)

Mitigation (in order of effort):
1. Add a `page.waitForTimeout(3000)` before screenshot to let JS render
2. Set a real user-agent: `--user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."`
3. If consistently blocked: switch to yt-dlp for metadata + direct thumbnail URL construction (YouTube thumbnail URLs follow a predictable pattern: `https://img.youtube.com/vi/<VIDEO_ID>/maxresdefault.jpg`)

Thumbnail URL pattern (no Playwright needed):
```
https://img.youtube.com/vi/<VIDEO_ID>/maxresdefault.jpg
https://img.youtube.com/vi/<VIDEO_ID>/hqdefault.jpg
```
This is the easiest visual capture path — just download the JPEG directly with a Python requests call.
