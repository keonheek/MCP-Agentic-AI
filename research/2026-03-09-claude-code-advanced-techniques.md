# Claude Code — Advanced Techniques (2026)
_Research date: 2026-03-09_

## Sources
- Nate Herk | AI Automation (YouTube @nateherk, 563K subscribers)
- General practitioner community (dev.to, hackceleration, claude-world, towardsai)
- Perplexity sonar live search

---

## Nate Herk — Key Techniques

### What he focuses on
- Building full agentic workflows from scratch fast (zero-to-agent in under 30 mins)
- Claude Code Skills as the core primitive — everything is a skill
- n8n + Claude Code integration via MCP — Claude auto-generates and fixes n8n workflows
- "Vanilla builds" — no heavy frameworks needed with Opus 4 models
- AI Agent Teams using skills to spawn and coordinate multiple agents

### Specific techniques
- **Skills with annotations** — feeds Claude examples (e.g. Twitter post style) so it replicates them in future outputs
- **CLAUDE.md as project root** — always creates CLAUDE.md alongside skills for scoped context
- **@ feature + AskUserQuestion tool** — Claude clarifies scope before building (target audience, pricing, features in/out)
- **Incremental scaffolding** — Claude generates to-do lists, file structures, exact commands, live preview
- **Deploy via Netlify drag-and-drop** — fast deployment for Streamlit/HTML apps
- **n8n MCP integration** — grants Claude access to n8n MCP, Claude auto-builds and auto-fixes workflows

### Notable videos
- "From Zero to Your First Agentic AI Workflow in 26 Minutes" (Feb 2026)
- "21 Essential Tips for Claude Code in 2026" (Mar 2026)
- "Claude Code Skills Just Built Me an AI Agent Team" (Dec 2025)
- "The ONLY Claude Code Tutorial You'll Ever Need in 2026" (Mar 2026)
- "I Will Never Fix Another n8n Workflow" (Claude Code + n8n MCP)

---

## Chase AI & Ritesh Verma
Perplexity could not find specific content from these channels — likely newer/smaller channels or content not indexed. Recommend checking their YouTube directly for their latest uploads.

---

## Advanced Claude Code Features (2026 — Community Best Practices)

### 1. Hooks (Pre/Post Tool Hooks)
Intercept and modify tool calls before/after execution.
- **Pre-commit hook example:** Detects `.env` in staged files, removes it automatically before commit
- **Input modification hook:** Alter what gets passed to a tool transparently
- Defined in skill frontmatter or `.claude/settings.json`

### 2. Subagents with Custom Models
- Skill Context Forking creates isolated sub-agent contexts
- Each subagent can run a different model (Haiku for cheap tasks, Opus for complex)
- Example: One subagent writes tests (TDD), another implements code — parallel, isolated
- Your existing `research-agent` uses this pattern with Haiku

### 3. MCP Server Creation
- **Context7 MCP** — pulls real-time, version-specific library docs (no token limits)
- Example: `/vercel/next.js/v15.1.0` pulls current Next.js docs mid-session
- You can build custom MCP servers in Python or Node that expose any data source

### 4. CLAUDE.md Best Practices
- **Nest CLAUDE.md files** — root for global rules, subfolder versions for project-specific rules
- Claude reads all of them automatically (hierarchical context)
- Keep under 150 lines — imports via @ for everything else
- Brand/style rules go here so Claude applies them without repeating yourself

### 5. Skills System — Hot Reload (v2.1.0+)
- Edit a skill file → switch tabs → changes take effect in under 30 seconds, no restart
- Skills support input modification and Bash wildcards
- Wrapper pattern: simple trigger → progressive disclosure of complex logic

### 6. Plan Mode
- Trigger: type `/plan` or shift+tab (depending on setup)
- Claude asks clarifying questions before executing anything
- Use for complex builds — prevents wasted tokens on wrong direction
- You have this available right now in VS Code extension

### 7. Worktrees
- Git worktrees = parallel branches, each in its own working directory
- Claude can work on `feature/login` and `feature/search` simultaneously without conflicts
- Command: `git worktree add ../branch-name branch-name`
- Claude Code has native worktree support — can spawn agents per worktree

### 8. Headless / CI Mode
- Run Claude Code non-interactively in CI pipelines
- Example: Paste GitHub issue → Claude auto-generates PR with tests (4-5 min for complex features)
- Integrates with GitHub Actions

### 9. Cron / Scheduling (available in your environment)
- `CronCreate` tool available in this VS Code extension right now
- Schedule recurring Claude tasks — daily summaries, weekly priority reviews, auto-commits
- Example: every Monday 9am → Claude reads priorities, drafts a weekly focus plan

### 10. Director Mode (Agent Teams)
- One "director" agent coordinates multiple specialist agents
- Director reads output from each, decides next steps, reassigns tasks
- Skills define what each specialist can do
- This is what Nate Herk calls "AI Agent Teams"

---

## What You Should Implement Next (Prioritized)

| # | Feature | Value | Effort |
|---|---------|-------|--------|
| 1 | Hooks — auto-protect .env on commit | High | Low |
| 2 | Cron — weekly priority review | High | Low |
| 3 | Worktrees — parallel project branches | High | Medium |
| 4 | Director agent + specialist subagents | High | Medium |
| 5 | n8n MCP integration | High | Medium (needs n8n install) |
| 6 | Custom MCP server (Notion deeper) | Medium | Medium |
| 7 | Headless/CI mode for GitHub | Medium | Medium |

---

## Key Insight from Research

> "The bottleneck in 2026 is no longer writing code — it's knowing *what* to build." — Nate Herk

Your skills, CLAUDE.md, and context files are already solving this. The next layer is automation (hooks, cron) and parallelism (worktrees, agent teams).
