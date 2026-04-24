"""Add a YouTube video to NotebookLM AI Workflow notebook and query for insights."""

import sys
import asyncio

sys.stdout.reconfigure(encoding="utf-8")

from notebooklm import NotebookLMClient

NOTEBOOK_ID = "a2e1b8e0-7238-4cac-a899-3000710d1748"
VIDEO_URL = "https://www.youtube.com/watch?v=oHu_xWe0agI"

QUESTIONS = [
    "What are the most in-demand AI engineering skills for 2026 and what percentage of job postings require them?",
    "What evaluation frameworks and quality metrics are mentioned for RAG pipelines?",
    "What production and deployment skills are most valued? Docker, cloud platforms, CI/CD?",
    "What advice is given for someone with LangGraph, RAG, and FastAPI experience but lacking Docker and evaluation framework experience?",
    "What are the recommended next steps for an AI engineer who has built financial analysis tools and MCP servers?",
]


async def main():
    print("=" * 70)
    print("NotebookLM: Add YouTube Video + Query")
    print("=" * 70)

    # Step 1: Connect
    print("\n[1/3] Connecting to NotebookLM...")
    try:
        client = await NotebookLMClient.from_storage()
    except Exception as e:
        print(f"AUTH FAILED: {e}")
        print("Storage state may be expired. Run: python -m notebooklm auth login")
        return

    async with client:
        print("Connected.")

        # Step 2: Add the YouTube video
        print(f"\n[2/3] Adding YouTube video to notebook {NOTEBOOK_ID}...")
        print(f"  URL: {VIDEO_URL}")
        try:
            source = await client.sources.add_url(NOTEBOOK_ID, VIDEO_URL)
            print(f"  Source added: id={source.id}, title={source.title}")
        except Exception as e:
            print(f"  WARNING: Could not add source (may already exist): {e}")

        # Wait for processing
        print("  Waiting 20 seconds for source processing...")
        await asyncio.sleep(20)

        # Step 3: Query the notebook
        print(f"\n[3/3] Querying notebook with {len(QUESTIONS)} questions...")
        print("=" * 70)

        conversation_id = None
        for i, question in enumerate(QUESTIONS, 1):
            print(f"\n--- Question {i}/{len(QUESTIONS)} ---")
            print(f"Q: {question}")
            print()

            try:
                result = await client.chat.ask(
                    NOTEBOOK_ID,
                    question,
                    conversation_id=conversation_id,
                )
                conversation_id = result.conversation_id
                print(f"A: {result.answer}")
            except Exception as e:
                print(f"ERROR: {e}")

            # Small delay between questions to avoid rate limiting
            if i < len(QUESTIONS):
                await asyncio.sleep(5)

        print("\n" + "=" * 70)
        print("DONE. All queries complete.")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
