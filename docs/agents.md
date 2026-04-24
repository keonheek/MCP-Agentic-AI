# Sub-Agents

Sub-agents live in `.claude/agents/`. Each runs with a fresh context window and its own model + tools.

| Agent | Model | Use when |
|-------|-------|----------|
| `director-agent` | Opus | Complex multi-step tasks: "run the full pipeline", "coordinate this" |
| `coding-agent` | Sonnet | Writing/debugging Python — LangGraph, RAG, FastAPI, Streamlit |
| `writing-agent` | Sonnet | Cover letters, applications, business plans, emails |
| `notion-agent` | Haiku | Notion CRUD: create pages, search, update databases |
| `research-agent` | Haiku | Cheap/fast research via Perplexity sonar |
| `sdc-agent` | Haiku | SDIC club ops in Korean — 공지, 회의록, 멤버 관리, Notion |
| `hormozi-agent` | Opus | Business strategy — offers, pricing, lead gen |
| `devils-advocate` | Opus | **Devil's advocate** for directional decisions (ICP, offer, pivot, "should I target X"). Attacks premises, not execution. Invoke BEFORE committing to strategic choices to prevent sunk-cost bias from the context files. |
| `qa-agent` | Sonnet | **Auto-triggered** after any business output is generated (PDF, PPTX, XLSX, HTML, kit). MECE 4-dimension audit (structure, data quality, completeness, polish), traces problems to source lines, fixes code, regenerates, loops until all scores >= 9.0 or 5 iterations. No manual trigger needed — fires automatically. |

## Notes
- Sub-agents cannot access `mcp__notion-sdc__*` tools — those are main-session only.
- Sub-agents cannot spawn other sub-agents. Chain from main session.
- Use agents to protect main context from large outputs (logs, test results, research dumps).
