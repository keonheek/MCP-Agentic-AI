import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from notebooklm import NotebookLMClient, Source
from notebooklm.rpc import RPCMethod

# Full notebook UUIDs (short IDs fail for sources.list)
NOTEBOOK_CLAUDE_AI_TOOLS = "7c604276-c377-42fd-8b2b-640d0e1d8f10"
NOTEBOOK_AI_WORKFLOW = "a2e1b8e0-7238-4cac-a899-3000710d1748"

VIDEO1_URL = "https://www.youtube.com/watch?v=ZeJXI2MAhj0"
VIDEO2_URL = "https://www.youtube.com/watch?v=oHu_xWe0agI"
VIDEO3_URL = "https://www.youtube.com/watch?v=VzOYty0siaM"


async def add_youtube_patched(client, notebook_id, url):
    """
    Patched YouTube source add.
    Google's API changed: position 10 in source params must be 2 (not 1)
    for YouTube URLs. The library uses 1 which returns None.
    """
    core = client._core
    params = [
        [[None, None, None, None, None, None, None, [url], None, None, 2]],
        notebook_id,
        [2],
        [1, None, None, None, None, None, None, None, None, None, [1]],
    ]
    result = await core.rpc_call(
        RPCMethod.ADD_SOURCE,
        params,
        source_path=f"/notebook/{notebook_id}",
        allow_null=True,
    )
    if result is None:
        raise Exception(
            f"API returned no data for URL: {url} — source may already exist or API changed again"
        )
    return Source.from_api_response(result)


async def process_video1():
    print("=" * 60)
    print("VIDEO 1: Claude Cowork/Dispatch feature")
    print(f"URL: {VIDEO1_URL}")
    print(f"Notebook: Claude & AI Tools")
    print("=" * 60)

    client = await NotebookLMClient.from_storage()
    async with client:
        print("Adding source (patched YouTube RPC)...")
        try:
            source = await add_youtube_patched(client, NOTEBOOK_CLAUDE_AI_TOOLS, VIDEO1_URL)
            print(f"Added: {source.id} | title={getattr(source, 'title', 'processing...')}")
            print("Waiting 15s for processing...")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Add failed ({e}) — source may already exist, proceeding to query...")
            await asyncio.sleep(3)

        print("\nQ1: What is Claude Dispatch and how does it work? Is it available in VS Code?")
        r1 = await client.chat.ask(
            NOTEBOOK_CLAUDE_AI_TOOLS,
            "What is Claude Dispatch and how does it work? Is it available in VS Code?",
        )
        print(f"A1: {r1.answer}")

        print("\nQ2: What are the key features and limitations?")
        r2 = await client.chat.ask(
            NOTEBOOK_CLAUDE_AI_TOOLS,
            "What are the key features and limitations of Claude Dispatch?",
        )
        print(f"A2: {r2.answer}")

    return {"q1": r1.answer, "q2": r2.answer}


async def process_video2():
    print("\n" + "=" * 60)
    print("VIDEO 2: AI engineer guide")
    print(f"URL: {VIDEO2_URL}")
    print(f"Notebook: AI Workflow")
    print("=" * 60)

    client = await NotebookLMClient.from_storage()
    async with client:
        print("Adding source (patched YouTube RPC)...")
        try:
            source = await add_youtube_patched(client, NOTEBOOK_AI_WORKFLOW, VIDEO2_URL)
            print(f"Added: {source.id} | title={getattr(source, 'title', 'processing...')}")
            print("Waiting 15s for processing...")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Add failed ({e}) — source may already exist, proceeding to query...")
            await asyncio.sleep(3)

        print("\nQ1: What skills does the AI engineer guide say are most important for 2025-2026?")
        r1 = await client.chat.ask(
            NOTEBOOK_AI_WORKFLOW,
            "What skills does the AI engineer guide say are most important for 2025-2026?",
        )
        print(f"A1: {r1.answer}")

        print("\nQ2: What gaps does this reveal for someone who has LangGraph + RAG but not LLMOps or Docker?")
        r2 = await client.chat.ask(
            NOTEBOOK_AI_WORKFLOW,
            "What gaps does this reveal for someone who has LangGraph and RAG experience but not LLMOps or Docker?",
        )
        print(f"A2: {r2.answer}")

    return {"q1": r1.answer, "q2": r2.answer}


async def process_video3():
    print("\n" + "=" * 60)
    print("VIDEO 3: How I'd Become an AI Consultant If I Had To Start Over — Nate Herk")
    print(f"URL: {VIDEO3_URL}")
    print(f"Notebook: AI Workflow")
    print("=" * 60)

    client = await NotebookLMClient.from_storage()
    async with client:
        print("Adding source (patched YouTube RPC)...")
        try:
            source = await add_youtube_patched(client, NOTEBOOK_AI_WORKFLOW, VIDEO3_URL)
            print(f"Added: {source.id} | title={getattr(source, 'title', 'processing...')}")
            print("Waiting 15s for processing...")
            await asyncio.sleep(15)
        except Exception as e:
            print(f"Add failed ({e}) — source may already exist, proceeding to query...")
            await asyncio.sleep(3)

        print("\nQ1: What are the main actionable insights from this video?")
        r1 = await client.chat.ask(
            NOTEBOOK_AI_WORKFLOW,
            "What are the main actionable insights from this video about becoming an AI consultant?",
        )
        print(f"A1: {r1.answer}")

    return {"q1": r1.answer}


async def main():
    print("Starting NotebookLM batch operations (sequential — rate limit safe)...")
    print("Using patched YouTube RPC (position 10 = 2, not 1)\n")

    results = {}

    try:
        results["video1"] = await process_video1()
    except Exception as e:
        print(f"FATAL ERROR in Video 1: {e}")
        results["video1"] = {"error": str(e)}

    try:
        results["video2"] = await process_video2()
    except Exception as e:
        print(f"FATAL ERROR in Video 2: {e}")
        results["video2"] = {"error": str(e)}

    try:
        results["video3"] = await process_video3()
    except Exception as e:
        print(f"FATAL ERROR in Video 3: {e}")
        results["video3"] = {"error": str(e)}

    print("\n" + "=" * 60)
    print("STRUCTURED SUMMARY — ALL 3 VIDEOS")
    print("=" * 60)

    print("\n--- VIDEO 1: Claude Dispatch (Claude & AI Tools notebook) ---")
    if "error" in results.get("video1", {}):
        print(f"FAILED: {results['video1']['error']}")
    else:
        print(f"Q: What is Claude Dispatch and how does it work? Is it available in VS Code?")
        print(f"A: {results['video1']['q1']}")
        print(f"\nQ: What are the key features and limitations?")
        print(f"A: {results['video1']['q2']}")

    print("\n--- VIDEO 2: AI Engineer Guide (AI Workflow notebook) ---")
    if "error" in results.get("video2", {}):
        print(f"FAILED: {results['video2']['error']}")
    else:
        print(f"Q: Most important skills for 2025-2026?")
        print(f"A: {results['video2']['q1']}")
        print(f"\nQ: Gaps for someone with LangGraph + RAG but not LLMOps/Docker?")
        print(f"A: {results['video2']['q2']}")

    print("\n--- VIDEO 3: AI Consultant Path (AI Workflow notebook) ---")
    if "error" in results.get("video3", {}):
        print(f"FAILED: {results['video3']['error']}")
    else:
        print(f"Q: Main actionable insights?")
        print(f"A: {results['video3']['q1']}")

    return results


asyncio.run(main())
