# Skills

Skills live in `.claude/skills/skill-name/SKILL.md`. Lazy-loaded — only the description is read until triggered.

## Tier 1 — Daily Drivers
Use weekly or more. These are the core tools.

| Skill | When to use |
|-------|------------|
| `research` | "research X", "deep dive on X" — Perplexity sonar, saves to `research/` |
| `geo` | "optimize this for AI search", `/geo:github-readme` — AI citability for any page |
| `autoresearch` | "score and improve", "iterate until good enough" — generate→score→improve loop |
| `obsidian` | Obsidian vault read/write — daily notes, tag search, knowledge base |
| `gsd` | "plan this project" — spec-driven dev with verification. For substantial features. |
| `life-review` | `/life-review` — holistic life+business scan: goals vs. reality, stale tasks, Obsidian patterns, auto-fix loop |

## Tier 2 — Situational
Use when a specific domain comes up.

| Skill | When to use |
|-------|------------|
| `financial-analyst` | "analyze this statement", `/financial-analyst:thesis` — financial modeling, DART data |
| `data-analyst` | "analyze this data", `/data-analyst:query` — pandas, SQL, visualizations |
| `interview-prep` | "prep me for X interview" — consulting + AI role preparation (Korean) |
| `mckinsey-consultant` | McKinsey-style problem framing — MECE, issue trees, recommendation structure |
| `ui-ux-designer` | UI/UX design guidance — layout, component decisions, visual hierarchy |
| `notebooklm` | Best for combining 3+ videos/sources into one queryable notebook |

## Tier 3 — Utility
Rarely invoked directly. Available when needed.

| Skill | When to use |
|-------|------------|
| `web-search` | "search for X", "look up X" — quick web lookup |
| `code-researcher` | "find how to implement X", "evaluate approach for X" |
| `database-builder` | "set up a database for X" |
| `chat-log-summarizer` | "summarize our last conversation" |
| `cli-anything` | "wrap this tool for Claude", "make X agent-native" |
| `github-skill-finder` | Find relevant GitHub skills/repos |
| `skill-creator` | Build a new skill from scratch |

## MCP Tools (not skills — no trigger needed)
| Tool | Trigger |
|------|---------|
| `youtube-transcript` | "watch this video", "learn from this YouTube", "get transcript of [URL]" — instant, no browser |

## Commands (slash shortcuts)
- `/life-review` — Holistic life+business scan with auto-fix loop
- `/today` — Daily briefing
- `/priorities` — Show current-priorities.md
- `/session-end` — Fill session summary template
- `/log-decision` — Append to decisions/log.md
- `/schedule` — Manage cron tasks
- `/apply` — Job application workflow
- `/code-review` — Review open PR
- `/daily-learn` — Daily learning lesson
- `/emerge` — Surface buried ideas
- `/execute-next` — Autonomous task executor
- `/ideate` — Process architect: generate automation loops from a project event, then wire live
