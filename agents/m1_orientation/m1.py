"""
M1 Orientation Agent -- Pure Data Collector
Runs daily at 6:30am KST. Reads working state, writes JSON brief to data/.
NO LLM calls. Synthesis happens via /m1-brief slash command in Claude Code session.
"""

import sys
import os
import json
import datetime
import subprocess
from pathlib import Path

from dotenv import load_dotenv

# Force UTF-8 output (Korean text on Windows)
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path("C:/Users/keonh/Dev/MCP_Agentic_AI")
OBSIDIAN_DAILY = Path("C:/Users/keonh/Claude_obs/Daily Notes")
DATA_DIR = Path(__file__).parent / "data"

load_dotenv(REPO_ROOT / ".env")

DISCORD_WEBHOOK = os.getenv("DISCORD_M1_WEBHOOK")
DRY_RUN = not DISCORD_WEBHOOK

# ---------------------------------------------------------------------------
# Data collectors
# ---------------------------------------------------------------------------

def read_file_safe(path: Path, max_chars: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]"
        return text
    except Exception:
        return f"[could not read {path}]"


def git_log(repo_path: Path, since: str = "7 days ago") -> str:
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = result.stdout.strip()
        return out if out else "[no commits in last 7 days]"
    except Exception as e:
        return f"[git error: {e}]"


def collect_subproject_logs() -> str:
    projects_root = REPO_ROOT / "projects"
    lines = []
    for proj in sorted(projects_root.iterdir()):
        if not proj.is_dir():
            continue
        git_dir = proj / ".git"
        if git_dir.exists():
            log = git_log(proj)
            lines.append(f"  [{proj.name}]: {log}")
    return "\n".join(lines) if lines else "[no subprojects with .git found]"


def read_obsidian_daily(days: int = 3) -> str:
    today = datetime.date.today()
    notes = []
    for i in range(days):
        d = today - datetime.timedelta(days=i)
        fname = OBSIDIAN_DAILY / f"{d.isoformat()}.md"
        if fname.exists():
            content = read_file_safe(fname, max_chars=1500)
            notes.append(f"--- {d.isoformat()} ---\n{content}")
    return "\n\n".join(notes) if notes else "[no Obsidian daily notes found for last 3 days]"


def collect_inputs() -> dict:
    return {
        "todo": read_file_safe(REPO_ROOT / "tasks" / "todo.md", max_chars=5000),
        "lessons": read_file_safe(REPO_ROOT / "tasks" / "lessons.md", max_chars=3000),
        "priorities": read_file_safe(
            REPO_ROOT / "context" / "current-priorities.md", max_chars=3000
        ),
        "decisions": read_file_safe(REPO_ROOT / "decisions" / "log.md", max_chars=2000),
        "git_main": git_log(REPO_ROOT),
        "git_subprojects": collect_subproject_logs(),
        "obsidian": read_obsidian_daily(days=3),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    today = datetime.date.today()
    today_str = today.isoformat()

    print(f"[M1] Collecting inputs for {today_str}...")
    data = collect_inputs()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DATA_DIR / f"brief_{today_str}.json"
    payload = {
        "date": today_str,
        "discord_webhook_set": bool(DISCORD_WEBHOOK),
        "inputs": data,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[M1] Data written to {out_path}")
    print("[M1] Next step: run /m1-brief in your Claude Code session to synthesize and post.")

    if DRY_RUN:
        print("[M1] DRY RUN: DISCORD_M1_WEBHOOK not set.")
        print("[SETUP NEEDED] Add DISCORD_M1_WEBHOOK=<your webhook url> to .env")


if __name__ == "__main__":
    main()
