# M1 Orientation Agent

Nightly morning brief. Reads todo.md, lessons.md, current-priorities.md, decisions/log.md,
git history (main repo + subprojects), and Obsidian daily notes. Synthesizes into 5 blunt
bullets via Claude Sonnet. Posts to Discord. Runs at 6:30am KST daily.

## What the 5 bullets cover

1. Ship today: 1-2 specific actions from todo.md mapped to priority blockers
2. Slipping: stalled decisions, stale todos, dead git projects
3. Pattern check: lessons.md match against today's planned work (quotes the lesson if it fires)
4. Drift signal: git commits vs current-priorities mismatch
5. One blunt question: what is being avoided

## Setup

### 1. Install dependencies

```
pip install -r agents/m1_orientation/requirements.txt
```

### 2. Add Discord webhook to root .env

Create a webhook: Discord server -> Edit Channel -> Integrations -> Webhooks -> New Webhook -> Copy URL

Add to `C:\Users\keonh\Dev\MCP_Agentic_AI\.env`:
```
DISCORD_M1_WEBHOOK=https://discord.com/api/webhooks/...
```

Without this, m1.py runs in dry-run mode (prints brief to stdout only).

### 3. Test manually

```
python agents/m1_orientation/m1.py
```

### 4. Schedule via Windows Task Scheduler

```powershell
schtasks /Create /XML "C:\Users\keonh\Dev\MCP_Agentic_AI\agents\m1_orientation\m1_schedule.xml" /TN "M1OrientationAgent" /F
```

To verify it registered:
```powershell
schtasks /Query /TN "M1OrientationAgent"
```

To run it immediately for testing:
```powershell
schtasks /Run /TN "M1OrientationAgent"
```

To remove it:
```powershell
schtasks /Delete /TN "M1OrientationAgent" /F
```

## Notes

- Idempotent: running twice on the same day just overwrites the previous Discord message embed
- Dry-run if DISCORD_M1_WEBHOOK is missing (safe to run without setup)
- Obsidian daily notes path: `C:\Users\keonh\Claude_obs\Daily Notes\YYYY-MM-DD.md`
- Git subprojects scanned: any folder under `projects/` that contains a `.git` directory
