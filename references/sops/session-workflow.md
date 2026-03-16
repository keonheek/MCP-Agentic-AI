# SOP: Daily Claude Code Session Workflow

_How to use the second brain system effectively every session._

---

## Session start (30 seconds)

1. Open VS Code → this project
2. Check `context/current-priorities.md` — is anything stale?
3. Claude loads CLAUDE.md + all context files automatically. No re-explaining needed.

**If priorities have shifted:** Just say "update current priorities: [new focus]" — Claude updates the file.

---

## Using the right tool for the job

| Task type | Use |
|-----------|-----|
| Quick web lookup | `/web-search` or just ask |
| Deep research (quality matters) | `/research topic` |
| Cheap/fast research | Research sub-agent |
| Write code for AI projects | `coding-agent` or just ask |
| Draft cover letter / email | `writing-agent` |
| Financial analysis | `/financial-analyst:thesis` etc. |
| Data work | `/data-analyst:query` etc. |
| Add something to Notion | `notion-agent` or just say "add to Notion" |
| Interview prep | `/interview-prep` |
| Complex multi-step task | `director-agent` |

---

## Recurring automations (already running)

- **Monday 9am** — Weekly focus plan auto-generated to `templates/weekly-focus.md`
- **Pre-commit hook** — Blocks `.env` files from being committed
- **rm -rf warning** — Fires in stderr before any dangerous Bash command

**Re-register cron after restarting VS Code** — session-only, 3-day expiry. Just say "set up the weekly cron again."

---

## Logging decisions (important habit)

After any meaningful choice (tech stack, career, architecture), say:
> "Log this decision: [what you decided] because [why]"

Claude appends to `decisions/log.md` in the correct format. Over time this becomes a searchable record of why you built things the way you did — invaluable for interviews.

---

## When you want to remember something permanently

Say: **"Remember that I always want X"** or **"Remember: X"**

Claude saves it to persistent memory at `~/.claude/projects/.../memory/MEMORY.md`. This carries across all future sessions.

---

## Git workflow (GitHub Flow)

```
# Start a new feature/project
git checkout -b feature/your-feature-name

# Work, then commit
git add specific-files
git commit -m "feat: description"

# Push + PR when ready
git push origin feature/your-feature-name
# Then: gh pr create
```

Branches: `master` (stable), `dev` (integration), `skills` (new skills), `agents` (new agents), `projects` (project work).

---

## End of session

1. Say "session summary" → Claude fills `templates/session-summary.md`
2. If priorities shifted → update `context/current-priorities.md`
3. Any big decision made → confirm it's in `decisions/log.md`

---

## Skill quick reference

| Skill | Trigger |
|-------|---------|
| `web-search` | "search for X", "look up X" |
| `research` | "research X", "deep dive on X" |
| `financial-analyst` | "analyze this statement", `/financial-analyst:thesis` |
| `data-analyst` | "analyze this data", `/data-analyst:query` |
| `interview-prep` | "prep me for X interview" |
| `database-builder` | "set up a database for X" |
| `geo` | "optimize this for AI search", `/geo:github-readme` |
| `chat-log-summarizer` | "summarize our last conversation" |

---

## Loop / schedule reference

```
/loop 5m check build status
/loop 30m /research Korean AI hiring trends
/loop /financial-analyst:compare Samsung vs SK Hynix
```
Session-scoped, auto-expires in 3 days.
