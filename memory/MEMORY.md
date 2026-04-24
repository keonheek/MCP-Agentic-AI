# Memory — Keonhee Kim's Second Brain

## Writing Quality
- [feedback_ai_slop_writing.md](feedback_ai_slop_writing.md) — Never use forced negation or staccato repetition — Hormozi's two AI slop tells; compress to one clear sentence instead
- [feedback_proofread_before_delivery.md](feedback_proofread_before_delivery.md) — Always proofread edited/revised written output before returning it; never deliver mechanically-patched text with duplication or broken flow

## Critical Safety Rules
- [feedback_notion_destructive_actions.md](feedback_notion_destructive_actions.md) — NEVER delete Notion pages/databases autonomously — always confirm per-item before any destructive action

## Context Management
- [feedback_context_mode_notion.md](feedback_context_mode_notion.md) — Notion sessions: ctx_index large fetches, no re-fetch to verify, batch ops, summarize and drop, targeted IDs only

## Workflow Preferences
- [feedback_use_websearch_for_unknowns.md](feedback_use_websearch_for_unknowns.md) — Always WebSearch/WebFetch when lacking info on anything — never guess. Applies broadly, not just .exe files
- [feedback_research_method.md](feedback_research_method.md) — Research via WebSearch+WebFetch only — no Perplexity API, no research-agent
- [feedback_aicpa_dropped.md](feedback_aicpa_dropped.md) — AI CPA exam dropped — never mention as priority, non-negotiable, or task
- [feedback_jeja_notion_only.md](feedback_jeja_notion_only.md) — 제자훈련 content goes to Notion 트래커 only, never local files
- [feedback_jeja_visual_format.md](feedback_jeja_visual_format.md) — /jeja Notion pages: toggle headings with color-coded bg; 교재 과제 always full analysis; verses before 육하원칙
- [feedback_jeja_new_week_format.md](feedback_jeja_new_week_format.md) — new-week: full 3주차-style format — toggles, verse text before analysis, full 교재 과제, pre-fill 설교 from Notion source
- [feedback_jeja_qt_format.md](feedback_jeja_qt_format.md) — QT format: 관찰 3-4줄, 해석 2-3절 묶음, 느낀점 personal story prompts, 적용 short+flexible
- [feedback_jeja_writing_format.md](feedback_jeja_writing_format.md) — Full /jeja format spec: toggle colors, 관찰/해석/느낀점/적용 structure, Assignment plain text rules, 결단 always left blank
- [feedback_bypass_permissions.md](feedback_bypass_permissions.md) — Bypass permissions mode: execute directly, no confirmation
- [feedback_no_streamlit_reboots.md](feedback_no_streamlit_reboots.md) — Never remind about Streamlit app reboots
- [feedback_obsidian_primary.md](feedback_obsidian_primary.md) — Obsidian is primary reading surface; sync goals/priorities/todo/decisions to vault
- [feedback_autoresearch_native.md](feedback_autoresearch_native.md) — Use native in-conversation autoresearch loop (not Python scripts)
- [feedback_notion_projects.md](feedback_notion_projects.md) — Notion primary: Projects database. Update todo.md AND Notion Projects on task updates
- [feedback_session_end_context.md](feedback_session_end_context.md) — Run /session-end before context auto-compacts
- [feedback_warm_leads.md](feedback_warm_leads.md) — No warm network. Cold outreach only (KakaoTalk open chats). Don't suggest SDC member connections
- [feedback_terminal.md](feedback_terminal.md) — Run ALL terminal commands autonomously. Pause only if action costs $3+
- [feedback_model_switching.md](feedback_model_switching.md) — Remind to switch to Sonnet before executing any plan

## Identity
- **Full name:** Keonhee Kim (last name: Kim, not Lee)
- SKKU Business Administration student, South Korea (UTC+9)
- [user_faith_discipleship.md](user_faith_discipleship.md) — Christian; 제자훈련 church course (Sat 12-4, jwj.kr, /jeja command)
- **과외:** Teaches English speaking to a student — active commitment

## SDIC 학회 (renamed from SDC, 2026-04)
- **SDIC** = SKKU Digital IT Consulting (legal rename from SDC/SKKU-Deloitte Consulting)
- Always 학회, never 클럽. 회장: 김건희, 부회장: 김태훈
- 12명: IM 3, PR 4, EDU 3 (팀장 포함) + 임원 2. 모집 완료 2026-03. 1차 OT held.
- Notion workspace: https://www.notion.so/SDC-SKKU-Deloitte-Consulting-3254a5d3118a806994d7cf06afd971e3
- sdc-agent handles all club ops in Korean. External messages: no emojis, professional Korean.

## Business State (as of 2026-04-18 — PIVOTED)
- [project_pivot_youtube_ai.md](project_pivot_youtube_ai.md) — GEO/SME/ERP set aside. New plan: partner + 4 YouTube channels (politics, table tennis, AI, TBD) → revenue → AI business. AI study 6hr/day Mon-Fri.
- **Previous stack (paused, not dead):** GEO Agency, SME Diagnostic, ERP Demo — do not surface as priorities until Keonhee revives them.

## Job Search — PAUSED
- BCGX: "Best CV I've read. Come back at graduation ('27)." Gap = work experience.
- Strategy: build GEO client work now → case study → re-engage BCGX at graduation.
- Unique angle: Business Admin + agentic AI technical skills = consulting AI practices (not ML labs)

## Critical Paths
- DART MCP server: `c:/Users/keonh/OneDrive/바탕 화면/dart-mcp-server/server.py`
- FinAgent: `c:/Users/keonh/OneDrive/바탕 화면/FinAgent/`
- MCP config: `.mcp.json` (gitignored — contains PAT)
- GitHub PAT: token 'superagent' — **EXPIRED Apr 8 2026. Renew immediately.**

## System State (as of 2026-04-12)
- **Skills:** 18 active (life-review added 2026-04-12). Tiered in docs/skills.md.
- **Agents:** 7 active (director, coding, writing, notion, research, sdc-agent, hormozi-agent). DO NOT reference improvement-scout — deleted, never suggest reviving it or cite it as a pattern.
- **MCP servers active:** obsidian, context-optimizer, youtube-transcript, Notion, notion-sdc, github, Gmail, Google Calendar
- **Subagents cannot access notion-sdc tools** — main session only
- **Hooks:** pre-write-guard (blocks .env), rm-rf warn, post-write-log
- **NotebookLM:** Hormozi, AI Workflow (a2e1b8e0), Claude & AI Tools (7c604276), Consulting Interview (e05089cd)

## PDF Reading (Windows)
- [feedback_pdf_reading_windows.md](feedback_pdf_reading_windows.md) — pdftoppm missing; use pymupdf→UTF-8 file→Read tool. Never print Korean directly to terminal (cp949 error)

## Windows / Node.js Patterns
- npx in `.mcp.json` requires full path: `C:/Program Files/nodejs/npx.cmd`
- GitHub MCP: use `node.exe` + absolute path to package, not npx
- DART search: Korean names only (`삼성전자` not `Samsung Electronics`)

## RAGAS Cost Policy
- Do NOT run RAGAS benchmark without explicit permission — 15 OpenAI calls per run

## Claude Partner Network
- [project_claude_partner.md](project_claude_partner.md) — Cleared initial review. Solo operator issue. Wait for next email.

## Pending (human action needed)
- **Renew GitHub PAT** — expired Apr 8 2026. Go to github.com/settings/tokens
- FinAgent reboot: keonhee-finagent.streamlit.app (chromadb fix pushed 2026-03-17)
- keonhee-strategy.streamlit.app reboot (beautifulsoup4 fix pushed 2026-03-17)
- NotebookLM auth: `python -m notebooklm auth login` once
- Neo4j install: neo4j.com/download (consulting emulation Phase 1.3 — deferred)
- List GEO agency on Soomgo + Kmong (500K KRW tier)

## Website & Design
- [feedback_website_3d_hero.md](feedback_website_3d_hero.md) — 3D hero: circular particle texture mandatory, fog for depth, no Vanta, no white bg, GSAP line reveals
- [feedback_website_dark_landing.md](feedback_website_dark_landing.md) — Dark landing page CSS patterns that hit 8.76/10 vision score: split hero, star field, stat callout, per-team colors, ghost nums in green

## Archive
Stale entries moved to `memory/archive/`: dart_fss_quirks, aws_cli_patterns, sdc_grader, consulting_emulation_state
