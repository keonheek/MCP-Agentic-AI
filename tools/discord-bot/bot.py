"""
Discord bot — Keonhee's mobile Claude interface.

Listens in a specific channel, calls Claude claude-sonnet-4-6, replies in Discord.
Also auto-updates agent status in agents/status.json.

Run:
    python tools/discord-bot/bot.py          (foreground, shows logs)
    pythonw tools/discord-bot/bot.py         (Windows background, no console window)

Requires in .env:
    DISCORD_BOT_TOKEN
    DISCORD_CHANNEL_ID
    ANTHROPIC_API_KEY
"""

import sys
import os
import asyncio
from pathlib import Path
from collections import deque

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Load .env — walk up from this file's location
# ---------------------------------------------------------------------------
from dotenv import load_dotenv

for _p in [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]:
    if _p.exists():
        load_dotenv(dotenv_path=_p)
        break

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not DISCORD_BOT_TOKEN:
    raise EnvironmentError("DISCORD_BOT_TOKEN not set in .env")
if not DISCORD_CHANNEL_ID:
    raise EnvironmentError("DISCORD_CHANNEL_ID not set in .env")
if not ANTHROPIC_API_KEY:
    raise EnvironmentError("ANTHROPIC_API_KEY not set in .env")

# ---------------------------------------------------------------------------
# Status writer (inline — no subprocess needed)
# ---------------------------------------------------------------------------
import json

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_STATUS_FILE = _PROJECT_ROOT / "agents" / "status.json"


def _write_status(status: str, task: str) -> None:
    """Write Discord bot status to the shared status.json."""
    try:
        current = {}
        if _STATUS_FILE.exists():
            try:
                current = json.loads(_STATUS_FILE.read_text(encoding="utf-8"))
            except Exception:
                current = {}
        current["Discord Bot"] = {
            "task": task,
            "status": status,
            "updated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        }
        tmp = _STATUS_FILE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, _STATUS_FILE)
    except Exception as e:
        print(f"[status] write failed: {e}")


# ---------------------------------------------------------------------------
# Anthropic client
# ---------------------------------------------------------------------------
import anthropic

_anthropic = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are Keonhee's AI assistant, available via Discord.
Keonhee is a SKKU Business Administration student building agentic AI systems.
His active projects: GEO Agency (AI search optimization), Lead Intelligence (DART screener),
SME Diagnostic AI (LangGraph pipeline), Consulting Emulation (M&A due diligence), Next AI Role (job prep).
Be direct, concise, no emojis unless asked. Respond in the same language as the message (Korean or English)."""

# Per-channel conversation history (last 10 turns)
_history: dict[int, deque] = {}


def _call_claude(channel_id: int, user_message: str) -> str:
    """Call Claude with conversation history and return response text."""
    if channel_id not in _history:
        _history[channel_id] = deque(maxlen=20)  # 10 turns = 20 messages

    _history[channel_id].append({"role": "user", "content": user_message})

    try:
        response = _anthropic.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=list(_history[channel_id]),
        )
        reply = response.content[0].text
        _history[channel_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"[error] Claude API call failed: {e}"


# ---------------------------------------------------------------------------
# Discord client
# ---------------------------------------------------------------------------
import discord

# Fix asyncio event loop issue on Windows Python 3.10+
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"[bot] Logged in as {client.user} (ID: {client.user.id})")
    print(f"[bot] Listening on channel ID: {DISCORD_CHANNEL_ID}")
    _write_status("idle", "Waiting for messages")


@client.event
async def on_message(message: discord.Message):
    # Ignore own messages
    if message.author == client.user:
        return

    # Only respond in the configured channel
    if message.channel.id != DISCORD_CHANNEL_ID:
        return

    user_input = message.content.strip()
    if not user_input:
        return

    print(f"[msg] {message.author}: {user_input[:80]}")
    _write_status("working", f"Replying to: {user_input[:60]}")

    # Show typing indicator while calling Claude
    async with message.channel.typing():
        reply = await asyncio.get_event_loop().run_in_executor(
            None, _call_claude, message.channel.id, user_input
        )

    # Discord has a 2000 char limit — chunk if needed
    if len(reply) <= 2000:
        await message.channel.send(reply)
    else:
        for i in range(0, len(reply), 1900):
            await message.channel.send(reply[i:i+1900])

    print(f"[reply] {reply[:80]}...")
    _write_status("idle", "Waiting for messages")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("[bot] Starting Discord bot...")
    client.run(DISCORD_BOT_TOKEN)
