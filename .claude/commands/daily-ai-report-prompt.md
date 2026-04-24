# Daily AI Intelligence Report — Automated Prompt

_This file is read by the `/schedule` cron job. Do not run manually — use `/schedule` or `/loop`._

## Instructions

You are running an automated daily AI intelligence sweep for Keonhee Kim. Execute the following steps autonomously:

### Step 1 — Research (WebSearch + WebFetch)

Use WebSearch and WebFetch to query the following topics:
- "Latest agentic AI developments in the past 24 hours"
- "New MCP servers or Model Context Protocol tools released this week"
- "Claude API or Anthropic updates in the past week"
- "LangGraph, LangChain, CrewAI updates or new patterns"
- "New AI developer tools or frameworks worth implementing"

### Step 2 — Filter for Keonhee's Stack

Keonhee's stack: Python, FastAPI, Streamlit, LangGraph, RAG pipelines, VectorDB (custom cosine), OpenAI API, Claude API, Pinecone, SQLite, MCP, Supabase.

Filter findings to only include:
- Tools/frameworks he can integrate within 1-3 days
- Patterns that improve his existing projects (FinAgent, RAG Demo, DART MCP)
- Things that would strengthen his portfolio or consulting narrative

### Step 3 — Write Report

Save to `research/YYYY-MM-DD-daily-ai-report.md` with this structure:

```
# Daily AI Report — [DATE]

## Top Developments (past 24-48h)
[3-5 bullet points, source + 1-line summary]

## Implementable This Week
[For each item: what it is, why it matters to Keonhee, estimated effort, which project it improves]

## Portfolio / Narrative Angles
[How today's news could strengthen Keonhee's consulting pitch or GEO presence]

## Action Queue
[ ] Item 1
[ ] Item 2
...
```

### Step 4 — Append to Action Queue

If there are high-priority action items, append them to `tasks/todo.md`.

### Step 5 — Autoresearch quality loop

Run autoresearch Mode 1 on the report content:
- Score dimensions: relevance to Keonhee's stack, actionability, specificity (are sources cited?), no generic filler
- Threshold: 8.0
- Max iterations: 5
- Scoring model: Claude Haiku (cheap)
- If score < 8.0: rewrite the weakest sections and re-score. Repeat until 8.0+ or 5 iterations reached.
- Once threshold met, overwrite the saved report file with the improved version.

### Step 6 — Done

Confirm: "Daily AI report saved to research/[DATE]-daily-ai-report.md — [N] implementable items found. Quality score: [X]/10."
