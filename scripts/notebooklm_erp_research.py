import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

URL1 = "https://www.youtube.com/watch?v=zMhuUyDo_1E"
URL2 = "https://www.youtube.com/watch?v=WW4DDHB4y34"
NOTEBOOK_TITLE = "ERP / SME Software Business Korea 2026"

QUESTIONS = [
    "What type of business is this person building? Describe the product, target market, and revenue model in detail.",
    "Which communities and channels does he use to find customers in Korea? Specific platforms, open chats, methods.",
    "What is his pricing model and how does he position his product vs competitors?",
    "What does ERP mean in this context and what are the core features of the product he is building?",
    "What are the best practices he recommends for building and selling this type of software business to Korean SMEs?",
    "How could a GEO (Generative Engine Optimization) audit service expand into or integrate with this type of ERP/SaaS business model? What are the synergies?",
    "What are the key pain points of Korean SMEs that this business model addresses?",
    "What tools, tech stack, or no-code platforms does he use or recommend?",
]

async def main():
    client = await NotebookLMClient.from_storage()
    async with client:
        print("Creating notebook...")
        notebook = await client.notebooks.create(title=NOTEBOOK_TITLE)
        nb_id = notebook.id
        print(f"Notebook ID: {nb_id}")

        print(f"Adding URL 1: {URL1}")
        s1 = await client.sources.add_url(nb_id, URL1)
        print(f"Source 1 added: {s1.id}")

        print(f"Adding URL 2: {URL2}")
        s2 = await client.sources.add_url(nb_id, URL2)
        print(f"Source 2 added: {s2.id}")

        print("Waiting 30s for sources to process...")
        await asyncio.sleep(30)

        results = {}
        for q in QUESTIONS:
            print(f"\nAsking: {q[:80]}...")
            try:
                resp = await client.chat.ask(nb_id, q)
                answer = resp.answer
            except Exception as e:
                answer = f"[ERROR: {e}]"
            results[q] = answer
            print(f"Answer: {answer[:300]}...")
            await asyncio.sleep(2)

        print("\n\n=== FULL RESULTS ===\n")
        for q, a in results.items():
            print(f"Q: {q}\nA: {a}\n{'-'*80}\n")

        return nb_id, results

asyncio.run(main())
