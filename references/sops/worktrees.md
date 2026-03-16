# SOP: Git Worktrees for Parallel Development

Use git worktrees when you want Claude to work on two different branches simultaneously without switching context — e.g., building the DART MCP server while keeping the main branch stable.

---

## What a worktree is

A worktree is a second (or third) checkout of the same repo, linked to a different branch. Each worktree has its own working directory and file state, but shares the same git history. Claude agents can work in separate worktrees in parallel.

---

## Setup (one-time per branch)

```bash
# From the project root
git worktree add ../MCP-Agentic-AI-langchain langchain
git worktree add ../MCP-Agentic-AI-dart-mcp dart-mcp
```

This creates:
- `../MCP-Agentic-AI-langchain/` — checked out to `langchain` branch
- `../MCP-Agentic-AI-dart-mcp/` — checked out to `dart-mcp` branch

If the branch doesn't exist yet:
```bash
git worktree add -b langchain ../MCP-Agentic-AI-langchain master
```

---

## Daily workflow with worktrees

```bash
# List active worktrees
git worktree list

# Work in main repo as normal
cd "c:/Users/keonh/OneDrive/바탕 화면/MCP_Agentic AI"

# Open a worktree in a separate VS Code window
code "../MCP-Agentic-AI-langchain"

# Remove a worktree when branch is merged
git worktree remove ../MCP-Agentic-AI-langchain
```

---

## Using worktrees with Claude agents

In Claude Code, you can tell an agent to work in a specific worktree:

> "Work in the langchain worktree at `../MCP-Agentic-AI-langchain` and build the LangChain demo. Don't touch the main repo."

The agent gets full isolation — its writes, reads, and Bash commands operate in that directory. The main session stays clean.

---

## Planned worktrees for this project

| Branch | Worktree path | Purpose |
|--------|--------------|---------|
| `langchain` | `../MCP-Agentic-AI-langchain` | LangChain learning project |
| `dart-mcp` | `../MCP-Agentic-AI-dart-mcp` | DART MCP server development |
| `finagent-v2` | `../MCP-Agentic-AI-finagent-v2` | FinAgent dynamic routing upgrade |

---

## Rules

- Never commit `.env` in any worktree — pre-commit hook applies to all worktrees
- Merge back to `master` via PR (GitHub Flow)
- Clean up worktrees after merging: `git worktree remove <path>`
- `.claude/` directory is shared across all worktrees — skills and agents work everywhere
