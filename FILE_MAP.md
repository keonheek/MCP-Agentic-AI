# FILE_MAP — MCP_Agentic_AI

_Auto-updated by Claude Code PostToolUse hook. Last updated: 2026-04-22_

Use this file to find anything. Ask Claude: "where is X?" and it reads here first.

---

## Pipeline Entrypoints

| File | Path | Purpose |
|------|------|---------|
| first_mover_ai_youtube.py | projects/youtube-biz/pipelines/first_mover_ai_youtube.py | YouTube discover+download pipeline (`--stage=discover` remote-safe) |
| first_mover_ai_instagram.py | projects/youtube-biz/pipelines/first_mover_ai_instagram.py | Instagram carousel pipeline (5 carousels/day) |

## Core Pipeline Modules

| File | Path | Purpose |
|------|------|---------|
| viral_ai_videos.py | projects/youtube-biz/core/layer1_ingestion/viral_ai_videos.py | Layer 1: viral AI video ingestion |
| claude_news.py | projects/youtube-biz/core/layer1_ingestion/claude_news.py | Layer 1: Claude-related news ingestion |
| ai_business_news.py | projects/youtube-biz/core/layer1_ingestion/ai_business_news.py | Layer 1: AI business news ingestion |
| ai_news.py | projects/youtube-biz/core/layer1_ingestion/ai_news.py | Layer 1: AI trends ingestion |
| ranker.py | projects/youtube-biz/core/layer2_intelligence/ranker.py | Layer 2: candidate scoring + selection |
| script_generator.py | projects/youtube-biz/core/layer2_intelligence/script_generator.py | Layer 2: Claude script + carousel generation |
| channel_crawler.py | projects/youtube-biz/core/layer1_ingestion/channel_crawler.py | Auto-added 2026-04-22 |
| instagram_competitor_scraper.py | projects/youtube-biz/core/analytics/instagram_competitor_scraper.py | Auto-added 2026-04-22 |

## Daily Output Files (auto-generated, date-stamped)

| Pattern | Location | Created by |
|---------|----------|-----------|
| YYYY-MM-DD-scripts.json | projects/youtube-biz/channels/first-mover-ai/drafts/youtube/ | YouTube pipeline discover stage |
| YYYY-MM-DD-carousels.json | projects/youtube-biz/channels/first-mover-ai/drafts/instagram/ | Instagram pipeline |
| YYYY-MM-DD-youtube-*.md | research/ | youtube-analyst agent reports |

## Config Files

| File | Path | Purpose |
|------|------|---------|
| channels.yaml | projects/youtube-biz/config/channels.yaml | Channel config (keys, targets) |
| sources.yaml | projects/youtube-biz/config/sources.yaml | Ingestion source URLs |
| thresholds.yaml | projects/youtube-biz/config/thresholds.yaml | Scoring + retention thresholds (edit to tune algorithm) |
| hook-templates.json | projects/youtube-biz/config/hook-templates.json | Script hook library |
| partner-agreement.md | projects/youtube-biz/config/partner-agreement.md | 영범 partnership terms |
| competitors.yaml | projects/youtube-biz/config/competitors.yaml | Competitor channel list |

## Claude Code System Files

| File | Path | Purpose |
|------|------|---------|
| CLAUDE.md | CLAUDE.md | Session prompt + project rules |
| current-priorities.md | context/current-priorities.md | Active focus areas (update when focus shifts) |
| todo.md | tasks/todo.md | Working task list |
| log.md | decisions/log.md | Decision log (append-only) |
| FILE_MAP.md | FILE_MAP.md | This file — central file registry |

## Hooks

| File | Path | Trigger |
|------|------|---------|
| post-write-log.py | .claude/hooks/post-write-log.py | PostToolUse(Write) — logs context file changes to decisions/log.md + upserts FILE_MAP |
| update-file-map.py | .claude/hooks/update-file-map.py | Stop — scans session writes, upserts FILE_MAP rows |
| pre-write-guard.py | .claude/hooks/pre-write-guard.py | PreToolUse(Write) — safety guard |

## Agent Definitions

| File | Path | Trigger phrases |
|------|------|----------------|
| youtube-analyst.md | .claude/agents/youtube-analyst.md | "analyze youtube", "channel report", "competitor scout" |

## Plans

| File | Path | Status |
|------|------|--------|
| ok-i-want-to-vectorized-teapot.md | C:\Users\keonh\.claude\plans\ok-i-want-to-vectorized-teapot.md | n8n setup — Phase 1 done, Phases 2-7 pending Docker |
| keen-drifting-toucan.md | C:\Users\keonh\.claude\plans\keen-drifting-toucan.md | Automation stack + ClickUp + file tracking — current |

## Reference Diagrams

| File | Path | Content |
|------|------|---------|
| _HOW_TO_CRAFT.md | references/diagrams/_HOW_TO_CRAFT.md | Mermaid diagram guide + Claude handoff protocol |
| sdic-curriculum.md | references/diagrams/sdic-curriculum.md | SDIC AI curriculum diagrams (3 diagrams) |
| content-business-pipelines.md | references/diagrams/content-business-pipelines.md | YouTube biz pipeline diagrams (4 diagrams) |
| finagent-architecture.md | references/diagrams/finagent-architecture.md | FinAgent architecture diagrams (3 diagrams) |
| _WHERE_TO_RENDER.md | references/diagrams/_WHERE_TO_RENDER.md | Auto-added 2026-04-24 |
| youtube-channel-intro-template.md | references/diagrams/youtube-channel-intro-template.md | Auto-added 2026-04-24 |
