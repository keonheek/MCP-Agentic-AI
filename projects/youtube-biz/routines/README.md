# First Mover AI — Routines Setup Guide

This folder holds Claude Code Routine prompts that run on Anthropic's servers (PC can be off).

---

## What's here

| File | Purpose | Runs on |
|---|---|---|
| `daily_ai_digest.md` | Pulls viral AI news, writes Korean newsletter, commits to git branch | Anthropic server, daily 07:07 KST |

---

## Setup — Register the Routine (one-time, 5 minutes)

### Prerequisite
- Claude Code Pro or Max subscription
- GitHub repo for this project (pushed + accessible)

### Steps

1. **Open the Routines page**
   - Web: https://claude.ai/code/routines
   - Or inside Claude Code CLI: `/schedule`

2. **Click "New routine"**

3. **Fill the form:**

   | Field | Value |
   |---|---|
   | Name | `First Mover AI — Daily Digest` |
   | Repository | `keonhee3337/MCP_Agentic_AI` (or your repo path) |
   | Branch | `master` |
   | Schedule | `7 7 * * *` (daily 07:07, your local timezone = KST) |
   | Prompt | `Read projects/youtube-biz/routines/daily_ai_digest.md and execute every step in order.` |

4. **Allowed tools** (check these boxes):
   - `WebSearch`
   - `WebFetch`
   - `Read`
   - `Write`
   - `Bash` (for `git` commands)

5. **Save.**

6. **Test immediately** — click the "Run now" button. Wait 5-10 minutes.

---

## Verify the Routine Worked

After the test run completes:

```bash
cd c:/Users/keonh/Dev/MCP_Agentic_AI
git fetch origin
git branch -r | grep claude/newsletter
# Should list: origin/claude/newsletter-YYYY-MM-DD

git checkout claude/newsletter-$(date +%Y-%m-%d)
cat projects/youtube-biz/channels/first-mover-ai/newsletters/$(date +%Y-%m-%d).md
```

Expected: Korean newsletter file with 5 items, proper formatting, all URLs working.

---

## Daily Consumption

Each morning after 07:07 KST:

1. Pull the new branch (or use Obsidian Git plugin for auto-pull):
   ```bash
   git fetch origin
   git checkout claude/newsletter-$(date +%Y-%m-%d)
   ```

2. Read `newsletters/YYYY-MM-DD.md`

3. If good → merge to master or cherry-pick. If not → adjust `daily_ai_digest.md` prompt and re-run tomorrow.

---

## Quality Iteration

Review the newsletter weekly. If issues:

| Issue | Fix |
|---|---|
| Too generic, no Korean angle | Tighten "왜 중요한가" instruction in prompt Step 3/4 |
| Same sources every day | Add more search queries in Step 1 |
| Paywalled sources | Add more `site:` filters for free sources |
| Too long | Lower character cap in Hard Constraints |
| Missed a big story | Add the topic keyword to Category searches |

Commit prompt changes to `master`; next day's Routine pulls the updated version.

---

## Cost & Limits

- **Cost**: $0 extra (included in Claude Code Pro/Max subscription)
- **Daily run limit**: 5/day (Pro), 15/day (Max)
- **Session length**: ~5-10 minutes per run
- **Token usage**: ~15k input + ~3k output per run (well within plan limits)

---

## Troubleshooting

**"Routine failed: git push permission denied"**
→ Go to Routine settings, enable "Allow push to non-claude/ branches" OR leave default (pushes to `claude/*` which is already allowed).

**"WebSearch returned nothing"**
→ Check if it's a slow news day. Routine will still commit the file with fewer items (graceful degradation is built into the prompt).

**"Notion / ClickUp delivery needed"**
→ Phase 2. Current MVP is Git-only. See `cheeky-nibbling-valiant.md` Phase Routine-1.

**"I want to change the schedule"**
→ Edit the Routine in the web UI. No code changes needed.

**"I want a second Routine for YouTube longform"**
→ Copy `daily_ai_digest.md` to `daily_youtube_script.md`, adjust the prompt, register a second Routine. Budget: burns 2/5 daily runs on Pro.

---

## What This Routine Does NOT Do (yet)

- Post to Instagram / YouTube
- Email you the newsletter
- Update Notion pages
- Record video or generate images

These are Phase Routine-1+. Add only after daily Git-commit version is validated for 2 weeks.
