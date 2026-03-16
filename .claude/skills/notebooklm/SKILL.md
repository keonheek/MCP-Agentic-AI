# NotebookLM Skill

Automate Google NotebookLM via the `notebooklm-py` library. Uses Playwright to drive a real browser session. Feed YouTube URLs, articles, and docs into NotebookLM to build knowledge bases for learning.

Updated 2026-03-11: Added workflow integration with research skill and learning path suggestions.

## Installation (already done)

```bash
pip install notebooklm-py
pip install "notebooklm-py[browser]"
playwright install chromium
```

## First-Time Auth (required once — user action)

Run this in a terminal. A Chromium browser will open — log in to your Google account. The session is saved and reused automatically after that.

```bash
python -m notebooklm auth login
```

Auth storage: `C:\Users\keonh\.notebooklm\storage_state.json`

---

## When to use this skill

| Use case | Action |
|----------|--------|
| YouTube tutorial to learn from | Add URL to NotebookLM, then ask questions |
| Research paper or article | Add URL, summarize + Q&A |
| Technical docs for a framework | Add docs URL, ask specific implementation questions |
| Multiple sources on one topic | Create a notebook, add all sources, query across them |

**Integration with research skill:** When research returns YouTube links or articles, escalate to NotebookLM for deep learning. Research = find it. NotebookLM = understand it.

---

## Capabilities

### 1. Add YouTube link to NotebookLM

```python
import asyncio
from notebooklm import NotebookLMClient

NOTEBOOK_ID = "your-notebook-id-here"
YOUTUBE_URL = "https://www.youtube.com/watch?v=XXXXXXX"

async def add_youtube(notebook_id: str, url: str):
    async with NotebookLMClient.from_storage() as client:
        source = await client.sources.add_url(notebook_id, url)
        await client.sources.wait_until_ready(notebook_id, [source.id])
        print(f"Added source: {source.id}")

asyncio.run(add_youtube(NOTEBOOK_ID, YOUTUBE_URL))
```

`add_url` accepts any URL — YouTube, news articles, blog posts, documentation pages.

---

### 2. Create notebook from URL

```python
import asyncio
from notebooklm import NotebookLMClient

async def create_notebook_from_url(title: str, url: str):
    async with NotebookLMClient.from_storage() as client:
        notebook = await client.notebooks.create(title=title)
        source = await client.sources.add_url(notebook.id, url)
        await client.sources.wait_until_ready(notebook.id, [source.id])
        print(f"Notebook created: {notebook.id}")
        return notebook.id

asyncio.run(create_notebook_from_url(
    title="LangGraph Streaming — 2026",
    url="https://www.youtube.com/watch?v=XXXXXXX"
))
```

---

### 3. Query a notebook

```python
import asyncio
from notebooklm import NotebookLMClient

async def ask_notebook(notebook_id: str, question: str):
    async with NotebookLMClient.from_storage() as client:
        response = await client.chat.ask(notebook_id, question)
        print(response.text)

asyncio.run(ask_notebook(NOTEBOOK_ID, "What are the main findings?"))
```

---

### 4. List all notebooks

```python
import asyncio
from notebooklm import NotebookLMClient

async def list_notebooks():
    async with NotebookLMClient.from_storage() as client:
        notebooks = await client.notebooks.list()
        for nb in notebooks:
            print(f"{nb.title} — ID: {nb.id}")

asyncio.run(list_notebooks())
```

---

## Suggested learning notebooks to create

| Topic | Why |
|-------|-----|
| LangGraph advanced patterns | Needed for McKinsey QuantumBlack technical assessment |
| BCG Gamma / McKinsey consulting cases | Interview prep |
| Korean AI Framework Act | Context for consulting AI pitches |
| Consulting case methodology | BCG / McKinsey interview prep |

---

## Key Notes

- **Auth storage:** `C:\Users\keonh\.notebooklm\storage_state.json` — delete to force re-login
- **`wait_until_ready`:** always call after `add_url` before querying — sources take time to process
- **Undocumented API:** notebooklm-py reverse-engineers Google's internal RPC. May break on NotebookLM updates. Check the [repo](https://github.com/cbroms/notebooklm-py) for fixes.
- **Rate limits:** Add `asyncio.sleep(1)` between bulk operations

## Common Trigger Phrases

- "add [YouTube URL] to NotebookLM"
- "create a notebook from [URL]"
- "ask my notebook about X"
- "summarize my notebook"
- "list my NotebookLM notebooks"
- "I want to learn from this video: [URL]"
