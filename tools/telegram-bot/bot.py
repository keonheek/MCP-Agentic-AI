"""
Telegram bot — mobile Claude interface via Claude CLI.

Receives messages in Telegram, passes to `claude --print`, returns response.
~50 lines. Zero extra API cost beyond Claude subscription.

Run:
    pip install python-telegram-bot python-dotenv
    python tools/telegram-bot/bot.py

Requires in .env:
    TELEGRAM_BOT_TOKEN   — from @BotFather on Telegram

Setup (one-time):
    1. Message @BotFather on Telegram → /newbot → copy token
    2. Add TELEGRAM_BOT_TOKEN=<token> to root .env
    3. Run the bot, message it from your Telegram account
"""

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

sys.stdout.reconfigure(encoding="utf-8")

# Load .env from this file's dir or up to 2 parents
for _p in [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]:
    if _p.exists():
        load_dotenv(dotenv_path=_p)
        break

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN not set in .env")

_LOG = Path(__file__).parent / "telegram_log.md"


async def handle(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    user = update.effective_user.username or update.effective_user.first_name
    print(f"[{user}] {text}")

    await update.message.reply_text("Thinking...")

    try:
        result = subprocess.run(
            ["claude", "--print", text],
            capture_output=True, text=True, timeout=120, encoding="utf-8",
        )
        reply = result.stdout.strip() or result.stderr.strip() or "(no response)"
    except subprocess.TimeoutExpired:
        reply = "Timeout — try a shorter prompt."
    except FileNotFoundError:
        reply = "Claude CLI not found. Install: npm install -g @anthropic-ai/claude-code"

    # Telegram hard limit: 4096 chars per message
    for chunk in [reply[i : i + 4096] for i in range(0, len(reply), 4096)]:
        await update.message.reply_text(chunk)

    # Append to log
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n**[{user}]** {text}\n\n{reply[:500]}{'...' if len(reply) > 500 else ''}\n")


if __name__ == "__main__":
    print("Telegram bot running. Ctrl+C to stop.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
