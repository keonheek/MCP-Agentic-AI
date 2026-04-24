import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

NOTEBOOK_ID = "5829dab3-ad55-4e94-a54b-66c98274a006"

NEW_URLS = [
    "https://www.youtube.com/watch?v=T2bd1kGEISo",
    "https://www.youtube.com/watch?v=cf6WEZUVbEI",
    "https://www.youtube.com/watch?v=mhIAd5lVMag",
    "https://www.youtube.com/watch?v=w-XPlC3a2oI",
]

QUESTIONS = [
    "Why does the speaker use Emergent (이머전트) specifically? What are its advantages over other AI coding tools like Replit, Lovable, or Manus?",
    "Can Claude Code replace Emergent for building the ERP/SaaS projects described? What are the differences in workflow?",
    "What is Antigravity? How does it work and how does it compare to Emergent or Claude Code for building web apps?",
    "What new customer acquisition channels, communities, or outreach methods are mentioned across all videos?",
    "What new product types, niches, or business models are described in the new videos? Any beyond ERP?",
    "What is the recommended workflow for going from a client brief to a delivered web app using AI coding tools?",
    "What are the biggest mistakes or failure modes when building this type of vibe coding business?",
    "What pricing strategies or packaging models are mentioned beyond the 5M KRW flat rate?",
    "Are there any Korea-specific tools, platforms, or cultural sales tactics mentioned in the new videos?",
    "What is the best entry point for a student with no portfolio who wants to start this type of business on Soomgo?",
]

async def main():
    client = await NotebookLMClient.from_storage()
    async with client:
        # Add new sources
        for url in NEW_URLS:
            print(f"Adding: {url}")
            s = await client.sources.add_url(NOTEBOOK_ID, url)
            print(f"  -> Source ID: {s.id}")
            await asyncio.sleep(2)

        print("\nWaiting 40s for all sources to process...")
        await asyncio.sleep(40)

        # Query
        print("\n=== QUERYING NOTEBOOK ===\n")
        for q in QUESTIONS:
            print(f"Q: {q[:90]}...")
            try:
                resp = await client.chat.ask(NOTEBOOK_ID, q)
                print(f"A: {resp.answer}\n{'-'*80}\n")
            except Exception as e:
                print(f"[ERROR: {e}]\n{'-'*80}\n")
            await asyncio.sleep(3)

asyncio.run(main())
