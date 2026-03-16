# LinkedIn About Section

_Updated 2026-03-11: Consulting pivot applied._

---

## Headline (update in LinkedIn profile)

Agentic AI Developer | LangGraph · RAG · MCP | SKKU Business Administration

---

## Full About Section (~500 words, Korean + English bilingual)

### Korean (paste first)

성균관대학교 경영학부 재학 중인 김건희입니다.

저는 프로덕션 수준의 에이전트 AI 시스템을 직접 설계하고 배포합니다 — 튜토리얼이 아닌, 실제로 동작하는 소프트웨어입니다.

**FinAgent** (keonhee-finagent.streamlit.app)는 LangGraph 기반의 다중 에이전트 금융 분석 시스템입니다. 자연어 질문을 받아 Text2SQL로 SQLite 데이터베이스를 조회하고, RAG 파이프라인으로 재무 문서를 검색해 구조화된 분석 리포트를 생성합니다. ChromaDB가 Python 3.14와 호환되지 않을 때, 외부 의존성 없이 OpenAI 임베딩 + NumPy 코사인 유사도 기반의 커스텀 VectorDB를 직접 구현했습니다. FastAPI 백엔드, Streamlit 프론트엔드, 현재 배포 운영 중입니다.

**DART MCP Server**는 한국 금융감독원 DART 시스템의 기업 재무 데이터를 Claude Code에서 직접 조회할 수 있는 커스텀 MCP 서버입니다. KOSPI/KOSDAQ 상장 2,500개+ 기업의 재무제표, 공시, 기업 정보를 AI 도구로 노출합니다.

**SDC 컨설팅 동아리**에서는 Claude API를 활용한 자동화된 지원서 검토 시스템을 구축했습니다. Gmail → PDF 추출 → Claude Haiku 자동 평가 → Google Sheets 기록의 end-to-end 워크플로우입니다.

공통점: 기본 도구가 작동하지 않을 때, 한 단계 더 깊이 들어갑니다.

---

### English (paste second)

Business Administration student at Sungkyunkwan University (SKKU), South Korea.

I build and deploy production agentic AI systems — end-to-end, from architecture to live URL.

**Tech stack:** LangGraph · RAG · custom VectorDB · Text2SQL · MCP · FastAPI · Streamlit · OpenAI API · Python

**What's live:**
- **FinAgent** — Multi-agent financial analysis. LangGraph orchestration, dynamic routing (Router → SQL/RAG based on query type), custom VectorDB, GPT-4o. [keonhee-finagent.streamlit.app](https://keonhee-finagent.streamlit.app)
- **DART Financial App** — Korean public company data via DART API → SQLite → RAG → GPT-4o. [keonhee-strategy.streamlit.app](https://keonhee-strategy.streamlit.app)
- **DART MCP Server** — Custom MCP server: DART Korean financial data as AI-callable tools (2,500+ companies). [GitHub](https://github.com/keonhee3337-art/dart-mcp-server)

**Business + AI technical is rare at student level.** Business Administration gives me the ability to frame AI in terms of outcomes, not just tech. Combined with end-to-end AI engineering experience, I can work at the intersection of "what does the AI make possible" and "what does the business actually need."

Active in SDC Consulting Club (SKKU). Built AI-powered automated application review system for the club.

Currently targeting AI analyst / data science intern roles at consulting AI practices: McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI & Analytics, Accenture Song/AI.

If you're building or deploying AI systems and want someone who ships — let's connect.

---

## Short Headline Version (under 120 words)

SKKU Business Administration student building production agentic AI systems. Two live: FinAgent (multi-agent LangGraph + Text2SQL + RAG, deployed) and DART Financial App (Korean market data pipeline). Built a custom MCP server exposing Korean corporate financial data to AI agents.

Stack: LangGraph · RAG · custom VectorDB · FastAPI · Streamlit · OpenAI API · Python · MCP.

Business + AI technical depth at student level is rare. Targeting consulting AI practices: McKinsey QuantumBlack, BCG Gamma, Deloitte Korea AI, Accenture Song.

Live: keonhee-finagent.streamlit.app | keonhee-strategy.streamlit.app

---

## Instructions: How to paste this

1. Go to LinkedIn → Edit profile → About section
2. Paste the Korean section first
3. Add a blank line break
4. Paste the English section
5. Update your headline to: `Agentic AI Developer | LangGraph · RAG · MCP | SKKU Business Administration`
