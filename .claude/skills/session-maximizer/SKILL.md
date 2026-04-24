---
name: session-maximizer
description: At session start, reads the user's first message and surfaces the most relevant tools, skills, agents, and MCP tools for the task. Combats dormant capabilities by actively recommending the right tool for the job.
---

# Skill: Session Maximizer

Surfaces the right tools for each session based on what Keonhee is about to do. Prevents capable tools from sitting dormant.

## Trigger phrases
- "what tools should I use for this"
- "maximize this session"
- "what's available for X"
- Automatically runs at the start of any session if the first message describes a task (not a question)

---

## Tool Inventory to Cross-Reference

### Skills (lazy-loaded)
- research — WebSearch+WebFetch synthesis, deep research loop (routes: WebSearch → Gemini grounding → Naver by query type)
- notion — Notion workspace conventions + MCP patterns (no agent spawn needed)
- proofread — formal/academic text QA loop, auto-triggered, loops to 10/10
- research-pipeline — post-research Obsidian ingest + YouTube transcript extraction
- geo — GEO optimization for public-facing content
- autoresearch — generate→score→improve loop (Mode 1) or Karpathy loop (Mode 2)
- obsidian — read/write/search Obsidian vault, wiki ingest/query/lint
- gsd — spec-driven development for substantial features
- financial-analyst — financial statements, DART data, Korean market analysis
- data-analyst — pandas, SQL, visualizations, data pipelines
- interview-prep — consulting + AI role prep (Korean)
- mckinsey-consultant — MECE framing, issue trees, recommendation structure
- ui-ux-designer — layout, component decisions, visual hierarchy
- daily-content-machine — generate one piece of public content, scored to 8.0+
- project-health-scanner — scan for stale projects, generate revival tasks
- framework-check — fetch library docs via context7, check code for breaking changes

### Agents
- coding-agent — Python code, LangGraph, RAG, FastAPI, Streamlit (spawn for new modules; in-session for small edits)
- writing-agent — cover letters, business plans, emails, professional docs
- hormozi-agent — offer design, pricing, lead gen strategy
- devils-advocate — challenge directional decisions before committing
- director-agent — orchestrate multi-step tasks across multiple agents
- qa-agent — auto-triggered after business output generation

### MCP Tools (always available)
- Gmail — search threads, create drafts, label messages
- Google Calendar — list events, create events, suggest times
- Notion — create/update/search pages and databases
- youtube-transcript — extract transcript from any YouTube URL instantly

### Commands
- /today — daily briefing with Calendar + Gmail + priorities
- /framework-check — library breaking change check
- /generate-tasks — populate todo.md with automatable tasks
- /wiki-lint — clean Obsidian wiki
- /life-review — holistic life + business scan
- /session-end — fill session summary

---

## Steps

### Step 1 — Read the task
Understand what Keonhee is trying to accomplish from his first message.

### Step 2 — Match tools
Cross-reference the task against the full tool inventory above.
Pick the 2-4 most relevant tools. Be specific about WHY each tool fits.

### Step 3 — Output recommendation
Format:
```
## Session Setup — [task summary in 5 words]

**Best tools for this:**
- [Tool name] — [why it fits this specific task]
- [Tool name] — [why it fits this specific task]
- [Tool name] — [why it fits this specific task]

**Suggested workflow:**
[1-3 steps describing how to chain the tools]

**Skip:** [tools that might seem relevant but aren't needed here]
```

Keep it under 10 lines. Do not list every tool — only what's genuinely useful.

### Step 4 — Proceed
After outputting the recommendation, immediately start executing the task. Do not wait for confirmation unless the task is ambiguous.

---

## Rules
- Never list more than 4 tools — more is noise
- Always include a "Skip" line to prevent over-tooling
- If the task is a simple question or conversation, skip this skill entirely
- The recommendation should take 3 seconds to read, not 30