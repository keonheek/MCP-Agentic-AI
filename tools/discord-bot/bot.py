"""
Discord bot — Keonhee's mobile Claude interface.

Listens in a specific channel, calls Claude Haiku (cheap), replies in Discord.
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
import time
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


_LOG_FILE = _PROJECT_ROOT / "tools" / "discord-bot" / "discord_log.md"
_INBOX_FILE = _PROJECT_ROOT / "tasks" / "discord_inbox.json"
_OUTBOX_FILE = _PROJECT_ROOT / "tasks" / "discord_outbox.json"
_LOOP_CONTROL_FILE = _PROJECT_ROOT / "tasks" / "loop_control.json"


def _write_to_log(author: str, content: str) -> None:
    """Append message to discord_log.md — VS Code auto-refreshes the open file."""
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n**[{timestamp}] {author}:**\n{content}\n\n---\n"
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"[log] write failed: {e}")


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
# Task queue helpers (inbox / outbox / loop control)
# ---------------------------------------------------------------------------

def _atomic_write(path: Path, data: dict) -> None:
    """Atomic JSON write via .tmp -> os.replace to prevent corruption."""
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path, default) -> dict:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _queue_task(channel_id: int, author: str, content: str) -> None:
    """Append a new task to discord_inbox.json."""
    data = _read_json(_INBOX_FILE, {"tasks": []})
    task = {
        "id": f"disc-{int(time.time())}",
        "created_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "channel_id": channel_id,
        "author": author,
        "content": content,
        "status": "pending",
    }
    data["tasks"].append(task)
    _atomic_write(_INBOX_FILE, data)
    print(f"[inbox] Queued task from {author}: {content[:60]}")


def _write_loop_control(mode: str) -> None:
    _atomic_write(_LOOP_CONTROL_FILE, {
        "mode": mode,
        "updated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "updated_by": "discord",
    })


def _format_status() -> str:
    """Build mobile-friendly status block from status.json + loop_control.json."""
    agents = _read_json(_STATUS_FILE, {})
    control = _read_json(_LOOP_CONTROL_FILE, {"mode": "unknown"})
    lines = [f"LOOP: {control.get('mode', 'unknown')}", "---"]
    order = ["GEO", "Lead Intel", "SME Diag", "Consulting", "Discord Bot", "Claude Loop"]
    for name in order:
        info = agents.get(name)
        if info:
            lines.append(f"{name}: {info.get('status','?')} — {info.get('task','')}")
    return "\n".join(lines)


async def _handle_command(content: str, channel_id: int, author: str, channel) -> None:
    """Handle ! commands without going through Claude."""
    parts = content.strip().split(None, 1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "!task":
        if not arg:
            await channel.send("Usage: `!task <description of what to do>`")
            return
        _queue_task(channel_id, author, arg)
        await channel.send(f"Queued. Claude will pick it up on the next loop tick (every 3 min while VS Code is open).")

    elif cmd == "!pause":
        _write_loop_control("paused")
        await channel.send("Loop paused. Send `!resume` to continue.")

    elif cmd == "!resume":
        _write_loop_control("running")
        await channel.send("Loop resumed.")

    elif cmd == "!stop":
        _write_loop_control("stopped")
        await channel.send("Loop stopped. Run `/schedule` in Claude Code to restart.")

    elif cmd == "!status":
        await channel.send(_format_status())

    elif cmd == "!help":
        await channel.send(
            "**Commands:**\n"
            "`!task <text>` — queue a task for Claude to execute\n"
            "`!pause` — pause the autonomous loop\n"
            "`!resume` — resume the loop\n"
            "`!stop` — stop the loop (requires /schedule to restart)\n"
            "`!status` — show agent status\n"
            "`!help` — this message\n\n"
            "Regular messages (no `!`) go directly to Claude for conversation."
        )
    else:
        await channel.send(f"Unknown command `{cmd}`. Send `!help` for the list.")


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
            model="claude-haiku-4-5-20251001",
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

# Python 3.14 removed default event loop — must create explicitly before discord.Client
_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

intents = discord.Intents.all()
client = discord.Client(intents=intents)


async def _poll_outbox():
    """Background task: check discord_outbox.json every 10s and deliver undelivered results."""
    while True:
        await asyncio.sleep(10)
        try:
            data = _read_json(_OUTBOX_FILE, {"results": []})
            changed = False
            for result in data.get("results", []):
                if result.get("delivered"):
                    continue
                channel = client.get_channel(result["channel_id"])
                if channel:
                    reply = result.get("reply", "(no reply)")
                    if len(reply) <= 2000:
                        await channel.send(reply)
                    else:
                        for i in range(0, len(reply), 1900):
                            await channel.send(reply[i:i+1900])
                    result["delivered"] = True
                    changed = True
                    print(f"[outbox] Delivered result {result.get('id')} to channel {result['channel_id']}")
            if changed:
                _atomic_write(_OUTBOX_FILE, data)
        except Exception as e:
            print(f"[outbox] poll error: {e}")


@client.event
async def on_ready():
    print(f"[bot] Logged in as {client.user} (ID: {client.user.id})")
    print(f"[bot] Listening on channel ID: {DISCORD_CHANNEL_ID}")
    _write_status("idle", "Waiting for messages")
    asyncio.create_task(_poll_outbox())
    print("[bot] Outbox poller started (10s interval)")


@client.event
async def on_message(message: discord.Message):
    # Ignore own messages
    if message.author == client.user:
        return

    # Debug: log all incoming messages with channel ID
    print(f"[debug] channel={message.channel.id} author={message.author} content={message.content[:40]!r}")

    # Only respond in the configured channel
    if message.channel.id != DISCORD_CHANNEL_ID:
        print(f"[debug] ignoring — expected {DISCORD_CHANNEL_ID}, got {message.channel.id}")
        return

    user_input = message.content.strip()
    if not user_input:
        return

    print(f"[msg] {message.author}: {user_input[:80]}")

    # Handle ! commands without going through Claude
    if user_input.startswith("!"):
        _write_to_log(str(message.author), user_input)
        await _handle_command(user_input, message.channel.id, str(message.author), message.channel)
        return

    _write_status("working", f"Replying to: {user_input[:60]}")

    # Option 1: also write message to file in VS Code workspace (auto-refreshes in editor)
    _write_to_log(str(message.author), user_input)

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
    _write_to_log("Claude_Agent", reply)
    _write_status("idle", "Waiting for messages")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("[bot] Starting Discord bot...")
    client.run(DISCORD_BOT_TOKEN)
