# Cover Letter — Kakao Brain

---

Dear Kakao Brain Hiring Team,

I am a Business Administration student at Sungkyunkwan University building AI systems grounded in Korean market data, and I want to contribute to Kakao Brain's work on Korean-language AI.

My most directly relevant project is a custom MCP server (Model Context Protocol — a standard for connecting AI agents to external tools) that exposes Korean financial data through structured tools: search_company, get_financials, and get_disclosures — pulling live data from the DART-FSS API (Korea's official corporate disclosure database). The live app is at keonhee-strategy.streamlit.app. Building this required understanding both the Korean regulatory data landscape and the technical layer needed to make that data usable by AI agents. That intersection — Korean business context plus AI systems engineering — is where I operate.

The second project is FinAgent (keonhee-finagent.streamlit.app) — a multi-agent financial analysis system built with LangGraph. The pipeline runs a StateGraph across three specialized agents: a RAG agent using custom vector embeddings (text-embedding-3-small, cosine similarity, no ChromaDB), a Text2SQL agent querying SQLite with GPT-4o, and an orchestration layer managing handoffs between them. I built the vector retrieval layer from scratch because Python 3.14 made ChromaDB unusable — understanding constraints well enough to engineer around them is the default mode.

Korean-language AI needs builders who understand Korean business context at the ground level. I have that, and I can build the systems to match. I would like to discuss how this maps to Kakao Brain's current priorities.

Keonhee Lee
github.com/keonhee3337-art
keonhee-strategy.streamlit.app
