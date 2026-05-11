# M2 Blindspot Scanner

Weekly adversarial scan. Runs every Sunday at 10pm KST.
Attacks Keonhee's current frame rather than reinforcing it.

## What it does

5 strands, each designed to find things he doesn't know he doesn't know:

| Strand | Focus |
|---|---|
| 1. Competitive Moves | New Korean AI agency entrants, pricing undercuts, competitor ICP grabs |
| 2. Stack Obsolescence | Model/tool releases in the past 7 days that would change his architecture |
| 3. Regulation Drift | PIPA amendments, 식약처 cosmetics ad rule changes, AI Basic Act updates |
| 4. Positioning Gaps | Queries he should rank for but doesn't, unclaimed open territory |
| 5. Internal Drift | Reversed decisions, violated lessons, build-vs-ship pattern recurring |

Output: Google Doc in Drive folder + Discord summary to DISCORD_M2_WEBHOOK.

## Setup

1. Add to root `.env`:
   ```
   DISCORD_M2_WEBHOOK=https://discord.com/api/webhooks/...
   ```
2. ANTHROPIC_API_KEY must already be set (shared with M1).
3. gws CLI must be installed and authenticated for Google Doc creation.

## Run manually

```powershell
python C:\Users\keonh\Dev\MCP_Agentic_AI\agents\m2_blindspot\m2.py
```

Missing DISCORD_M2_WEBHOOK triggers dry-run mode (prints to console, no Discord post).
Missing gws CLI skips Doc creation (report printed to console).

## Register schedule (Windows Task Scheduler)

```powershell
schtasks /create /xml "C:\Users\keonh\Dev\MCP_Agentic_AI\agents\m2_blindspot\m2_schedule.xml" /tn "M2 Blindspot Scanner"
```

To verify it is registered:
```powershell
schtasks /query /tn "M2 Blindspot Scanner"
```

## Architecture

- Web search: Anthropic `web_search_20250305` tool (free, no external API key)
- Synthesis: Claude Sonnet 4.6 (one call per strand after search pass)
- Doc creation: gws CLI (Google Workspace CLI)
- Discord: requests POST to webhook

## Difference from M1

M1 (orientation, daily) keeps him oriented within his current frame.
M2 (blindspot, weekly) attacks the frame itself.
M1 is a mirror. M2 is a critic.
