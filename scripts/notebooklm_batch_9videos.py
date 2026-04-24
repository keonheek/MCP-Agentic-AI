import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

NOTEBOOK_TITLE = "AI & Business Insights — Batch 2026-03-25"

URLS = [
    "https://www.youtube.com/watch?v=92ReEZwYBQQ",
    "https://www.youtube.com/watch?v=BlNJFa3Btm8",
    "https://www.youtube.com/watch?v=I9kO6-yPkfM",
    "https://www.youtube.com/watch?v=2aC2ly7vKtM",
    "https://www.youtube.com/watch?v=GZxjs8FD3Ck",
    "https://www.youtube.com/watch?v=L_FY6aW9cJ4",
    "https://www.youtube.com/watch?v=bGySYORLiG8",
    "https://www.youtube.com/watch?v=TX1Ij51esI0",
    "https://www.youtube.com/watch?v=KAX0cWk1fJE",
]

QUESTIONS = [
    # Categorization
    "For each video source, state its title and categorize it as either BUSINESS, AI, or BOTH. Give a one-sentence summary of what each video covers.",

    # AI-focused
    "What are the most important AI tools, frameworks, or workflows described across all videos? List them with what they do and who they are for.",
    "What new AI agent patterns, automation techniques, or multi-agent workflows are described? How do they work?",
    "What does each AI-focused video recommend as the most important skill or concept to learn right now?",

    # Business-focused
    "What business models, offer structures, or revenue strategies are described? Be specific about pricing, packaging, and target customers.",
    "What lead generation and customer acquisition strategies are mentioned? Which platforms, tactics, or communities are named?",
    "What are the key lessons about selling, positioning, or growing a service business in 2025-2026?",

    # Application to Keonhee
    "What actionable steps could a solo operator with technical AI skills (Python, LangGraph, Claude Code, FastAPI) take immediately based on these videos? Focus on things achievable within 1-2 weeks.",
    "Are there any product ideas, niches, or underserved markets identified that would suit someone building AI tools for Korean SMEs?",
    "What is the single most important insight from all these videos combined — the one that would most change how someone builds and sells an AI business?",
]

async def main():
    client = await NotebookLMClient.from_storage()
    async with client:
        print("Creating new notebook...")
        notebook = await client.notebooks.create(title=NOTEBOOK_TITLE)
        nb_id = notebook.id
        print(f"Notebook ID: {nb_id}")

        for url in URLS:
            print(f"Adding: {url}")
            s = await client.sources.add_url(nb_id, url)
            print(f"  -> {s.id}")
            await asyncio.sleep(2)

        print("\nWaiting 45s for all sources to process...")
        await asyncio.sleep(45)

        print("\n=== QUERYING ===\n")
        for q in QUESTIONS:
            print(f"Q: {q[:100]}...")
            try:
                resp = await client.chat.ask(nb_id, q)
                print(f"A: {resp.answer}\n{'-'*80}\n")
            except Exception as e:
                print(f"[ERROR: {e}]\n{'-'*80}\n")
            await asyncio.sleep(3)

        print(f"\nNotebook ID for future queries: {nb_id}")

asyncio.run(main())
