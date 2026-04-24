# NotebookLM Skill

> **Single-video learning:** Prefer the `youtube-transcript` MCP tool — it's instant, no browser, no auth required. Just give Claude a YouTube URL and ask questions.
> **Use NotebookLM when:** combining 3+ videos/sources into one queryable notebook, or when you want to cross-reference across a corpus of sources over multiple sessions.


Automate Google NotebookLM via the `notebooklm-py` library. Uses Playwright to drive a real browser session. Feed YouTube URLs, articles, and docs into NotebookLM to build knowledge bases for learning.

Updated 2026-03-18: Fixed API patterns confirmed working on Python 3.14 + notebooklm-py.

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

## CRITICAL: Correct API Pattern (confirmed 2026-03-18)

`from_storage()` is an **async classmethod** — you must `await` it, then use the result as the context manager.
**WRONG** (crashes): `async with NotebookLMClient.from_storage() as client:`
**CORRECT**: `client = await NotebookLMClient.from_storage()` then `async with client:`

Response object uses `.answer`, not `.text`.
`wait_until_ready()` raises `SourceNotFoundError` intermittently — use `asyncio.sleep(15)` instead.
Always add `sys.stdout.reconfigure(encoding="utf-8")` on Windows (Korean paths + em-dashes crash cp949).

---

## Capabilities

### 1. Add YouTube link to existing notebook

```python
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

NOTEBOOK_ID = "your-notebook-id-here"
URL = "https://www.youtube.com/watch?v=XXXXXXX"

async def add_source(notebook_id: str, url: str):
    client = await NotebookLMClient.from_storage()
    async with client:
        source = await client.sources.add_url(notebook_id, url)
        print(f"Added: {source.id} — {getattr(source, 'title', 'processing...')}")
        await asyncio.sleep(15)  # wait for processing — wait_until_ready is unreliable
        return source.id

asyncio.run(add_source(NOTEBOOK_ID, URL))
```

`add_url` accepts any URL — YouTube, news articles, blog posts, documentation pages.

---

### 2. Create notebook from URL

```python
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

async def create_notebook_from_url(title: str, url: str):
    client = await NotebookLMClient.from_storage()
    async with client:
        notebook = await client.notebooks.create(title=title)
        source = await client.sources.add_url(notebook.id, url)
        print(f"Notebook ID: {notebook.id}")
        await asyncio.sleep(15)
        return notebook.id

asyncio.run(create_notebook_from_url(
    title="LangGraph Advanced Patterns 2026",
    url="https://www.youtube.com/watch?v=XXXXXXX"
))
```

---

### 3. Query a notebook

```python
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

async def ask_notebook(notebook_id: str, question: str):
    client = await NotebookLMClient.from_storage()
    async with client:
        response = await client.chat.ask(notebook_id, question)
        print(response.answer)  # .answer not .text

asyncio.run(ask_notebook(NOTEBOOK_ID, "What are the main findings?"))
```

---

### 4. List all notebooks

```python
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

async def list_notebooks():
    client = await NotebookLMClient.from_storage()
    async with client:
        notebooks = await client.notebooks.list()
        for nb in notebooks:
            print(f"{nb.title} -- ID: {nb.id}")

asyncio.run(list_notebooks())
```

---

### 5. List sources in a notebook

```python
import asyncio, sys
sys.stdout.reconfigure(encoding="utf-8")
from notebooklm import NotebookLMClient

async def list_sources(notebook_id: str):
    client = await NotebookLMClient.from_storage()
    async with client:
        sources = await client.sources.list(notebook_id)
        for s in sources:
            print(f"{getattr(s, 'title', s.id)}")

asyncio.run(list_sources(NOTEBOOK_ID))
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
