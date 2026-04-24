# First Mover AI — Action Plan

**Status: Infrastructure built. Ready for real-world activation.**

---

## Build Status

| Component | Status |
|---|---|
| Directory structure | Done |
| Config files (channels/sources/hooks) | Done — First Mover AI only |
| Layer 1 ingestion (4 collectors) | Done |
| Layer 2 intelligence (ranker + dual script gen + QA loop) | Done |
| Layer 3 media (downloader + highlight + translator) | Done |
| Pipelines (YouTube + Instagram) | Done |
| `/first-mover-ai` slash command | Done |
| Remote cron (2 jobs, session-only) | Registered |
| Smoke test | 36/41 OK |

**Sing It files deleted.** Old First Signal branding cleared.

---

## What You Need to Do (In Order)

### Phase A — Unblock the Pipeline (this week)

#### 1. Install ffmpeg
The only remaining smoke test failure. Without ffmpeg, video editing is blocked.
- Download: https://www.gyan.dev/ffmpeg/builds/ (Windows)
- Extract to `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to Windows PATH (System Properties → Environment Variables)
- Verify: open new terminal → `ffmpeg -version`

#### 2. Fill in `.env` file
```bash
cd c:/Users/keonh/Dev/MCP_Agentic_AI/projects/youtube-biz
cp .env.example .env
```
Required now:
- `ANTHROPIC_API_KEY` — already in your main `.env` (copy over)

Required before Phase B:
- `YOUTUBE_CLIENT_ID` / `YOUTUBE_CLIENT_SECRET` — from Google Cloud Console (see step 3)
- `INSTAGRAM_ACCESS_TOKEN` / `INSTAGRAM_BUSINESS_ACCOUNT_ID` — Meta Business Manager (later)

#### 3. Google Cloud + YouTube API setup
For YouTube Data API v3 (needed when you automate uploads in Phase 2):
1. Go to https://console.cloud.google.com
2. Create new project: "First Mover AI"
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 Client ID (Desktop app)
5. Download JSON → copy `client_id` + `client_secret` to `.env`
6. First run opens browser for consent → token saved

**Phase 1 (manual upload) does NOT need this. Skip to step 4 if you're starting manual.**

#### 4. Create the actual channels
- YouTube: Brand Account on your Gmail → channel "First Mover AI" → handle @firstmoverai (verify availability on YouTube)
- Instagram: Business account (required for Graph API later) → @firstmoverai_kr
- Sign `config/partner-agreement.md` with Young Bum

#### 5. First manual test run
```bash
cd c:/Users/keonh/Dev/MCP_Agentic_AI/projects/youtube-biz

# Instagram pipeline (remote-safe, just needs API key)
python pipelines/first_mover_ai_instagram.py
# Output: channels/first-mover-ai/drafts/instagram/YYYY-MM-DD-carousels.json

# YouTube discover (no downloads, just scripts)
python pipelines/first_mover_ai_youtube.py --stage=discover
# Output: channels/first-mover-ai/drafts/youtube/YYYY-MM-DD-scripts.json

# If a script looks good, download one video (Local only)
python pipelines/first_mover_ai_youtube.py --stage=download --idx=0
# Output: channels/first-mover-ai/renders/originals/
```

---

### Phase B — First Week of Real Content

#### Day 1 (tomorrow)
- Review `drafts/instagram/*.json` (5 carousel texts)
- Canva or Figma: design 5 slides per carousel using the `slides` array
- Upload to @firstmoverai_kr
- Review `drafts/youtube/*.json` — pick 1
- Download source video, record Korean voiceover (or ElevenLabs), edit in CapCut/Premiere
- Upload to YouTube

#### Day 2-5
- Daily rhythm
- Remote cron auto-generates drafts at 07:07 (IG) and 22:03 (YT) KST
- If PC off: run manually via `/first-mover-ai instagram` or `/first-mover-ai youtube`

#### End of Week 1
- Count: posts, views, follower growth
- Check for takedowns
- Update `config/hook-templates.json` with what worked

---

### Phase C — Make It Durable (Week 2)

**Current limitation: Session-only crons die when this Claude session ends.**

#### Option 1 (recommended): `/schedule` skill → remote agents
```
/schedule
```
YouTube:
```
Cron: 3 22 * * *
Prompt: Run /first-mover-ai youtube. Report top candidate.
```
Instagram:
```
Cron: 7 7 * * 1-5
Prompt: Run /first-mover-ai instagram. Report 5 carousels generated.
```

#### Option 2: Windows Task Scheduler (for Layer 3 downloads)
```
schtasks /create /tn "FMA-YT" /tr "python C:\...\pipelines\first_mover_ai_youtube.py --stage=discover" /sc daily /st 22:03
schtasks /create /tn "FMA-IG" /tr "python C:\...\pipelines\first_mover_ai_instagram.py" /sc weekly /d MON,TUE,WED,THU,FRI /st 07:07
```

---

### Phase D — Upload Automation (Month 2)

**Only after 2-3 weeks of manual validation.**

1. **YouTube upload**: existing `core/layer4_publishing/youtube_api.py`. Add `--stage=upload` to pipeline.
2. **Instagram upload**: Meta Business Manager → App → Graph API permissions. Link Business account to Facebook Page. Use `instagram_graph.py`.
3. **Stories PNG rendering**: Add `core/layer3_media/first_mover_ai/carousel_renderer.py` (Puppeteer + HTML template). Auto-render 5 PNGs at 1080×1920.

---

## Weekly Rhythm (Target State, Month 2+)

| Day | Auto | Manual |
|---|---|---|
| Mon-Fri 07:07 | IG → drafts + PNGs + auto-upload | 0 min |
| Mon-Fri 22:03 | YT → top 3 scripts + video download | 0 min |
| Daily morning | — | Review YT draft → 30-60 min recording/editing → upload |
| Sunday evening | — | 15 min: weekly KPI review in Obsidian |

Total manual: ~5-7 hrs/week (mostly editing).

---

## Decision Triggers

- **Takedown 2+ times** → Switch YT to text-only (AI voice narration over slides)
- **IG engagement <1% after 4 weeks** → Kill 33/33/33, go 100% Claude news
- **YT subs <500 after 6 weeks** → Pivot to Shorts-first
- **YT subs >2000 before 6 weeks** → Accelerate Phase D upload automation

---

## What NOT to do

- Don't enable Instagrapi until Graph API bans you twice. It's the fallback.
- Don't automate thumbnails in Phase 1. Manual Canva wins for first 100 videos.
- Don't cross-post YouTube MP4 to Instagram. Algorithms deprioritize watermarked reuploads.
- Don't add Korean politics channel back until First Mover AI hits 5K subs.
