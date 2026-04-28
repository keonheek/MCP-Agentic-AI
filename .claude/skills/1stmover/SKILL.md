---
name: 1stmover
description: "@1stmover.ai daily Instagram content workflow. Discovers viral candidates via TWO paths: (1) top AI accounts on X, (2) trending SEO/GEO keywords via WebSearch + Naver. Reads dedup ledger to avoid repeats, downloads media, writes Korean magazine-style content.md, updates ledger, posts Discord notification. Trigger: /1stmover"
---

# Skill: 1stmover.ai Content Pipeline

Daily Instagram content workflow for @1stmover.ai.
Run `/1stmover` to start a full session.
Run `/1stmover scout` to only surface candidates without building content.
Run `/1stmover notify` to only send the Discord dedup notification.

Discovery uses TWO parallel paths — accounts AND keywords. Keywords often surface better content than following fixed accounts because viral moments spread across many creators simultaneously.

**Time window: 12-24 hours only.** All discovery is constrained to posts published within the last 12-24 hours. A viral post from 3 days ago already peaked and is no longer timely. Fresher = more relevant for same-day posting.

---

## Step 0 — Pre-flight checks (run before anything else)

```bash
# 1. Cookies file exists?
test -f /c/Users/keonh/Dev/clips/x_cookies.txt \
  && echo "PASS: cookies found" \
  || echo "FAIL: x_cookies.txt missing — run COOKIE_SETUP_KR.md first"

# 2. Cookies not too old? (>14 days = probably expired)
python -c "
import os
from pathlib import Path
from datetime import datetime, timezone
f = Path('/c/Users/keonh/Dev/clips/x_cookies.txt')
if f.exists():
    age_days = (datetime.now(timezone.utc).timestamp() - f.stat().st_mtime) / 86400
    if age_days > 14:
        print(f'WARN: cookies {age_days:.0f} days old — likely expired. Re-export recommended.')
    else:
        print(f'PASS: cookies {age_days:.0f} days old')
"

# 3. Clips folder exists?
mkdir -p /c/Users/keonh/Dev/clips
echo "PASS: clips/ ready"

# 4. Discord webhook set?
grep -q "DISCORD_WEBHOOK_AUTOMATION=" /c/Users/keonh/Dev/MCP_Agentic_AI/.env \
  && echo "PASS: Discord webhook found" \
  || echo "WARN: DISCORD_WEBHOOK_AUTOMATION missing from .env — notification will skip"

# 5. Quick cookie validity test
python -c "
import urllib.request, json
COOKIES_PATH = r'C:\Users\keonh\Dev\clips\x_cookies.txt'
cookies = {}
with open(COOKIES_PATH) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            parts = line.split('\t')
            if len(parts) >= 7: cookies[parts[5]] = parts[6]
ct0 = cookies.get('ct0','')
cookie_header = '; '.join(f'{k}={v}' for k,v in cookies.items())
BEARER = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
req = urllib.request.Request('https://x.com/i/api/graphql/32pL5BWe9WKeSK1MoPvFQQ/UserByScreenName?variables=%7B%22screen_name%22%3A%22OpenAI%22%7D&features=%7B%22hidden_profile_subscriptions_enabled%22%3Atrue%7D&fieldToggles=%7B%22withAuxiliaryUserLabels%22%3Afalse%7D',
  headers={'Authorization': f'Bearer {BEARER}', 'X-Csrf-Token': ct0, 'Cookie': cookie_header, 'User-Agent': 'Mozilla/5.0'})
try:
    urllib.request.urlopen(req, timeout=10)
    print('PASS: X API authenticated')
except Exception as e:
    print(f'FAIL: X API auth error ({e}) — re-export cookies')
" 2>&1
```

**If any FAIL:** stop and fix before continuing. WARN is OK to proceed.

### IG cool-down check (date-aware)
```python
from datetime import date
cooldown_end = date(2026, 5, 10)
today = date.today()
if today < cooldown_end:
    days_left = (cooldown_end - today).days
    print(f"WARN: IG cool-down active. {days_left} days until 2026-05-10. Manual phone posting ONLY.")
else:
    print("OK: IG cool-down ended. Graph API automation permitted.")
```

---

## Paths (always use these)

```
Clips root:     c:/Users/keonh/Dev/clips/
Scrapers:       c:/Users/keonh/Dev/kh-yb-shared/scripts/
Cookies:        c:/Users/keonh/Dev/clips/x_cookies.txt
Ledger:         c:/Users/keonh/Dev/kh-yb-shared/used_topics/YYYY-MM-DD.md
Template:       c:/Users/keonh/Dev/kh-yb-shared/templates/content_template.md
Thumb prompts:  c:/Users/keonh/Dev/kh-yb-shared/templates/thumbnail_prompts.md
```

---

## Step 1 — Read the dedup ledger (ALWAYS FIRST)

```python
# Read used_topics/ for the last 7 days
import os
from pathlib import Path
ledger_dir = Path("c:/Users/keonh/Dev/kh-yb-shared/used_topics")
used = set()
for f in sorted(ledger_dir.glob("*.md"))[-7:]:
    for line in f.read_text(encoding="utf-8").splitlines():
        if line and line[0].isdigit() and ". " in line[:4]:
            used.add(line.split(". ", 1)[1].strip().lower())
```

Print the list of used topics so user can see what's already covered.

---

## Step 2A — Keyword-based discovery (do this FIRST — broader reach)

### Time constraint
All discovery must respect the **12-24 hour window in KST (Korean Standard Time, UTC+9).**

```python
from datetime import datetime, timezone, timedelta
# Use KST for the cutoff — Korean audience = Korean morning is the signal
KST = timezone(timedelta(hours=9))
now_kst = datetime.now(KST)
cutoff_utc = (now_kst - timedelta(hours=24)).astimezone(timezone.utc)
print(f"Discovery window: {cutoff_utc.strftime('%Y-%m-%d %H:%M UTC')} → now")
```

- Posts trending during Korean morning (06:00-12:00 KST) are the most relevant for that day's posts
- A post from 9pm UTC the previous night = 6am KST = valid (within 24h KST)
- Discard anything older than 24h KST even if it has high engagement

### 2A-1: Find trending AI keywords right now

Use WebSearch + Naver MCP in parallel to identify what's being searched/talked about.

**If Naver MCP is disconnected** (check system-reminder for "mcp__naver-search disconnected"): skip Naver and use WebSearch + Reddit sweep only. Do not block on Naver.

```
# Global signals
WebSearch: "most viral AI news today [TODAY]"
WebSearch: "trending AI topics X Twitter last 24 hours"
WebSearch: "site:x.com AI viral since:[TODAY-1d]"

# Korean signals (Naver MCP — skip if disconnected)
mcp__naver-search__search_news: query="AI 오늘 최신" display=10 sort=date
mcp__naver-search__search_news: query="인공지능 오늘" display=10 sort=date
mcp__naver-search__search_news: query="챗GPT 딥시크 최신" display=10 sort=date
mcp__naver-search__datalab_search: keywords=["ChatGPT","Claude","딥시크","생성형AI","네이버AI","카카오AI"] period="1days"

# Korean AI company angles (add these manually to keyword list)
# 네이버 AI, 카카오 AI, 삼성 AI, LG AI, SK텔레콤 AI
```

Extract the top 5-10 keywords/topics that are currently peaking (not just big accounts — what's being searched).

Examples of strong keyword signals:
- A specific model name spiking (e.g., "GPT-Image-3", "Claude 5")
- A viral moment people are searching (e.g., "AI Minecraft", "AI replaces designer")
- A Korean-specific angle blowing up (e.g., "딥시크 한국", "카카오 AI", "삼성 AI")
- A concept trending globally (e.g., "agentic AI", "AI memory", "AI glasses")

### 2A-2: Search X by those keywords (12-24h window)

For each keyword with strong signal, search X **with time filter**:

```bash
# X search URL with since: filter (past 24 hours)
# Format: https://x.com/search?q=<keyword>+min_faves:1000+since:YYYY-MM-DD&f=top
WebSearch: "site:x.com <keyword> since:[TODAY-1d] min_faves:1000"
```

Then scrape the top post URL directly:
```bash
python scripts/scrape_x_post.py "<specific_post_url>" \
  --download-media c:/Users/keonh/Dev/clips/<topic>/
```

**Time-filter rule when checking post timestamps:**
```python
from datetime import datetime, timezone, timedelta
cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
# If post['created_at'] < cutoff → skip, already stale
```

### 2A-3: Reddit keyword sweep — today only (use `t=day`)

Reddit's `t=day` parameter limits to the last 24 hours. Always use it.

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
for sub in ChatGPT aiArt singularity OpenAI; do
  curl -sL -H "User-Agent: $UA" \
    "https://old.reddit.com/r/$sub/top/.json?t=day&limit=10" \
    | python -c "
import json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
data=json.load(sys.stdin)
for p in data.get('data',{}).get('children',[]):
    d=p['data']
    url=d.get('url_overridden_by_dest','')
    if any(x in url for x in ['.jpg','.jpeg','.png','i.redd.it','gallery']):
        print(f\"{d['score']}pts | {d['title'][:70]}\")
        print(f\"  {url}\")
"
done 2>&1
```

---

## Step 2B — Account-based discovery (secondary, fills gaps)

Run only when keyword discovery didn't surface enough strong candidates.
Use `--media-only` to surface only visually-strong posts.

```bash
cd c:/Users/keonh/Dev/kh-yb-shared

# Run with 2-second gaps between calls to avoid X rate-limiting
python scripts/scrape_x_user.py @sama --top 5 --media-only; sleep 2
python scripts/scrape_x_user.py @OpenAI --top 5 --media-only; sleep 2
python scripts/scrape_x_user.py @AnthropicAI --top 3 --media-only; sleep 2
python scripts/scrape_x_user.py @minchoi --top 5 --media-only; sleep 2
python scripts/scrape_x_user.py @rowancheung --top 3 --media-only; sleep 2
python scripts/scrape_x_user.py @deepseek_ai --top 3; sleep 2
python scripts/scrape_x_user.py @demishassabis --top 3
```

**After scraping accounts, apply the 24-hour filter:**
The scraper returns last 40 tweets sorted by engagement. Before presenting to user, filter by `created_at`:
```python
from datetime import datetime, timezone, timedelta
cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
recent = [t for t in tweets if datetime.fromisoformat(t['created_at'].replace('Z','+00:00')) > cutoff]
```
If a post is older than 24 hours, skip it even if it has high likes. Engagement from old posts is residual, not active virality.

**Note:** Keywords > accounts. A viral moment surfaced by keyword search often has more posts to choose from and is more in-the-moment than a single creator's feed.

---

## Step 2C — Score and merge candidates

Combine results from 2A + 2B. **First discard anything older than 24 hours.** Then score what remains:

| Signal | Score |
|---|---|
| Posted within last 12 hours | +2 (extra freshness bonus) |
| Posted 12-24 hours ago | +0 (acceptable) |
| Posted >24 hours ago | **Discard** |
| Trending keyword AND account-confirmed | +3 |
| Trending keyword only | +2 |
| Account-based, >10k likes | +2 |
| Account-based, 1k-10k likes | +1 |
| Has video/image media | +1 |
| Strong Korean angle | +1 |
| Similar to used topic (last 7 days) | -5 (exclude) |

Show top 7-10 scored candidates to user in this format:
```
[4h ago] 📹 VIDEO | @OpenAI (51,703 ❤️) — "Introducing GPT-5.5: a new class of..."
[7h ago] 🖼️ IMAGE | @minchoi (872 ❤️) — "Nothing is real anymore. These are not..."
[2h ago] 📝 TEXT  | @sama (8,231 ❤️) — "We tried a new thing with NVIDIA to roll..."
```

Tags: 📹 = has video, 🖼️ = image only, 📝 = text only (can still be strong — see karpathy example)

### Category diversity check
Before asking user to pick, check if top candidates are all the same type. Ideally today's posts mix:
- 1 AI News (company launch / announcement)
- 1 AI Trend (viral demo / tool reaction)
- 1 AI Education / Tutorial

If all top candidates are "model launches", note this to user: "All candidates are model launches today — consider also checking @minchoi or Reddit aiArt for visual variety."

---

## Step 3 — Present candidates (exclude already-used)

For each candidate:
- Show URL, likes count, text snippet, has video/image
- Flag if topic feels similar to a used topic (fuzzy match)
- Exclude if clearly duplicate (same company + same launch event)

Ask user: "Which of these do you want to develop? Pick 1-7."

---

## Step 4 — For each confirmed topic

### 4a. Create topic folder
```bash
mkdir -p "c:/Users/keonh/Dev/clips/<topic-name>"
```

Naming: lowercase hyphens matching the topic (e.g., `deepseek-v4`, `evenrealities`).

### 4b. Download media + validate
```bash
cd c:/Users/keonh/Dev/kh-yb-shared
python scripts/scrape_x_post.py "<url>" \
  --download-media "c:/Users/keonh/Dev/clips/<topic>/" \
  --json "c:/Users/keonh/Dev/clips/<topic>/source.json"
```

After download, validate each media file:

```bash
# Check resolution (minimum 1080×720; prefer 1080×1080 or 1080×1920)
for f in /c/Users/keonh/Dev/clips/<topic>/*.{jpg,jpeg,png,mp4}; do
  [ -f "$f" ] && ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height -of csv=p=0 "$f" 2>/dev/null \
    | awk -F, '{
      w=$1; h=$2
      if (w<720 || h<720) print "WARN: "$0" is low-res ("w"x"h") — may look blurry on IG"
      else if (w==h) print "OK: square ("w"x"h")"
      else if (h>w) print "OK: vertical ("w"x"h")"
      else print "NOTE: landscape ("w"x"h") — IG may crop to square"
    }'
done
```

**Aspect ratio guide for IG:**
- 1:1 (1080×1080) — carousel cards ✅
- 4:5 (1080×1350) — portrait, most reach ✅
- 9:16 (1080×1920) — Reels ✅ (highest reach)
- 16:9 (1920×1080) — landscape, gets cropped to 1:1 ⚠️

**Video preference:** When a topic has both video and images, **use video as Card 1 / cover** — Reels get 2-3x more reach than static carousels on IG.

**Text-only topic path (no media):**
Some strong topics (e.g., Karpathy-style thread, 10-prompt lists) have no good visual from X.
In that case: note `[NO MEDIA — text card]` in the checklist and write a GPT-Image-2 prompt
from `templates/thumbnail_prompts.md` Category A (text-heavy), and proceed with text cards.

### 4c. Write content.md + verify completeness
Follow the template at `templates/content_template.md`.
- Korean magazine declarative tone
- 5 cards (or 3 for short topics / single demos)
- ─ dividers in caption
- 30 hashtags (#1stmoverai #퍼스트무버 always)

**After writing, verify these sections exist (completeness check):**
```
[ ] frontmatter (날짜, 카테고리, 점수, 권장 게시 시간)
[ ] 핵심 훅
[ ] 미디어 체크리스트
[ ] 표지 (헤드 + 서브 + 미디어 + 알트)
[ ] Card 1 (minimum)
[ ] 마감 카드
[ ] 캡션 (has ─ dividers + Source/Editor sig)
[ ] 첫 댓글
[ ] 해시태그 (count ~30, includes #1stmoverai #퍼스트무버)
```
If any section missing → fill it before marking done.

---

## Step 5 — Update ledger + Discord notification (ALWAYS AFTER CREATING TOPICS)

### What "update ledger" means
The ledger is a plain text file in `kh-yb-shared/used_topics/`. Each day has one file listing which topics were covered. Before each session, the skill reads these files to know what NOT to suggest again. After building topics, we write the new ones into today's file. Then we send a Discord message to 영범 so he can see the same list. That's it — no database, no complex system. Just a text file + Discord message.

### Update ledger
Add today's new topics to `kh-yb-shared/used_topics/YYYY-MM-DD.md`:

```markdown
# YYYY-MM-DD 사용 토픽 (건희)

1. <topic-name>
2. <topic-name>
...

총 N개. 영범은 위 토픽 외 다른 주제로 진행 요망.
```

Commit + push to GitHub:
```bash
cd c:/Users/keonh/Dev/kh-yb-shared
git add used_topics/
git commit -m "chore: update used_topics YYYY-MM-DD"
git push 2>&1 | grep -E "(Error|error|pushed|Everything)" | head -3
# If push fails (auth error): ledger is saved locally, but 영범 won't sync until next push.
# Tell user: "Ledger saved locally. Push manually when network/auth is available."
```

### Discord notification (use curl — NOT Python)
Python urllib gets Cloudflare-blocked from Claude's IP. Always use Bash curl:

```bash
WEBHOOK=$(grep DISCORD_WEBHOOK_AUTOMATION /c/Users/keonh/Dev/MCP_Agentic_AI/.env | cut -d= -f2-)
curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H "Content-Type: application/json" \
  -d "{\"content\":\"<message>\"}" \
  "$WEBHOOK"
# 204 = success
```

---

## Step 6 — Summary to user

Show:
- Which folders were created with media
- Which content.md files are done
- Which topics need GPT-Image-2 thumbnail (list the prompts inline if needed)
- Reminder: post manually via Instagram phone app (no automation — IG 14-day cool-down active until 2026-05-10)

---

## Dedup rules

1. NEVER create a topic that was in `used_topics/` in the last 7 days
2. **Fuzzy-match criteria — what counts as "same topic":**
   - Same company + same product/event in the same week (e.g., `deepseek-v4` and `deepseek-v4-pro` = same)
   - Same model launch even if framed differently (e.g., `gpt-image-2-launch` and `gpt-image-2-demos` = same week)
   - Different company or clearly different event = OK (e.g., `deepseek-v4` and `deepseek-v3` = different)
   - Korean angle of same story = OK only if it adds genuinely new information (e.g., `google-ai-campus-seoul` and `hassabis-korea-visit` = too similar within same week)
3. After creating topics, ALWAYS update ledger AND send Discord notification
4. If user says "skip notification", skip the Discord post but still update the ledger
5. **Daily volume limit:** 1-3 posts per day is sustainable. More than 5 in one day usually means lower quality on each. Ask user to confirm if selecting >5 candidates.

---

## Korean content quick-reference

**Tone**: 매거진 선언형 (not 해요/예요 in card bodies, only in caption)
**Card body**: 3 sentences max, specific numbers/names/dates
**Caption structure**: Hook line → ─ → Detail → ─ → Korean angle → ─ → Question + 💬
**Hashtag count**: exactly 30 (not 28, not 32)
**Cover image**: 1080×1080 preferred; 1280×720 minimum; video frame OK if strong

---

## When NOT to run

- If `x_cookies.txt` is missing or expired → remind user to re-export first
- If it's before 2026-05-10 → do NOT automate Instagram posting. Manual phone app only.
- If 7+ topics already exist for today → ask user if they want to continue or wrap up

---

## Future: Claude Routines

When user is ready to automate, register at claude.ai/code/routines:
```
Cron: 7 7 * * 1-5
Prompt: Run /1stmover scout. Report top 5 candidates.
```

For now: manual /1stmover invocation only.
