# System Architecture

## Overview

```mermaid
graph TD
    subgraph Session["Claude Code Session"]
        CC[Claude Code<br/>Opus / Sonnet]
        CM[CLAUDE.md<br/>~40 lines]
        CTX[context/]
        DOCS[docs/]
        CM -->|@ref| DOCS
        CM -->|@ref| CTX
    end

    subgraph MCP["MCP Servers (active)"]
        OBS[obsidian<br/>Claude_obs vault]
        CTXOPT[context-mode<br/>SQLite session sandbox + BM25]
    end

    subgraph MCPOff["MCP Servers (disabled)"]
        NOTION[notion]
        GITHUB[github]
        DART_MCP[dart]
        SDC[notion-sdc]
    end

    subgraph Skills[".claude/skills/ (lazy-loaded)"]
        S1[research<br/>Perplexity sonar]
        S2[geo<br/>GEO optimization]
        S3[financial-analyst]
        S4[data-analyst]
        S5[interview-prep]
        S6[14 more...]
    end

    subgraph Agents[".claude/agents/"]
        A1[director-agent<br/>Opus — orchestrator]
        A2[coding-agent<br/>Sonnet — Python/AI]
        A3[writing-agent<br/>Sonnet — docs]
        A4[notion-agent<br/>Haiku — Notion CRUD]
        A5[research-agent<br/>Haiku — cheap research]
        A6[sdc-agent<br/>Haiku — SDC ops KR]
        A7[hormozi-agent<br/>Opus — biz strategy]
    end

    subgraph Projects["projects/ (folder CLAUDE.md per project)"]
        P1[geo-agency<br/>GEO audit service]
        P2[sme-diagnostic-ai<br/>LangGraph 4-node]
        P3[lead-intelligence<br/>DART screener]
        P4[consulting-emulation<br/>M&A suite — deployed]
    end

    subgraph External["External Projects"]
        E1[FinAgent<br/>keonhee-finagent.streamlit.app]
        E2[Samsung Forecast<br/>keonhee-strategy.streamlit.app]
        E3[RAG Demo<br/>FastAPI + Pinecone + ngrok]
    end

    CC --> MCP
    CC --> Skills
    CC --> Agents
    CC --> Projects
    Agents --> Projects
    Agents --> External
```

## Context Loading Strategy

| Layer | Always loaded | Loaded on demand |
|-------|--------------|------------------|
| CLAUDE.md | Yes (~40 lines) | — |
| context/ | Yes (5 files) | — |
| docs/ | Only when @referenced | When working on tools/skills/agents |
| projects/X/CLAUDE.md | Only when in that folder | When switching to project X |
| Skills | Description only | Full SKILL.md on trigger |
| Agents | On invocation | Fresh context per run |

## Worktree Strategy

Use `git worktree` to work on multiple projects in parallel without context collision:

```
main repo:   MCP_Agentic AI/          ← master branch, SDC + admin work
worktree 1:  MCP_Agentic_AI_geo-agency/  ← worktree/geo-agency branch
worktree 2:  MCP_Agentic_AI_sme/         ← worktree/sme-diagnostic branch
```

Each worktree = separate VS Code window = separate Claude session = no cross-contamination.
