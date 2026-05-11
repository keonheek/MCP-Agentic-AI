"""
Strand 5: Internal Drift -- Pure Data Gatherer
Reads decisions log, lessons.md, todo.md, priorities, Obsidian daily notes.
Returns raw text for the slash command to synthesize.
NO LLM calls.
"""

import datetime
from pathlib import Path


OBSIDIAN_DAILY = Path("C:/Users/keonh/Claude_obs/Daily Notes")


def read_file_safe(path: Path, max_chars: int = 4000) -> str:
    try:
        text = path.read_text(encoding="utf-8")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n...[truncated]"
        return text
    except Exception:
        return f"[could not read {path}]"


def read_obsidian_daily(days: int = 7) -> str:
    today = datetime.date.today()
    notes = []
    for i in range(days):
        d = today - datetime.timedelta(days=i)
        for fmt in [f"{d.isoformat()}.md", f"{d.strftime('%Y-%m-%d')}.md"]:
            fname = OBSIDIAN_DAILY / fmt
            if fname.exists():
                content = read_file_safe(fname, max_chars=800)
                notes.append(f"--- {d.isoformat()} ---\n{content}")
                break
    return "\n\n".join(notes) if notes else "[No Obsidian daily notes found for last 7 days]"


def run(repo_root: Path, today_str: str) -> dict:
    """
    Returns all raw file contents for the slash command to analyze.
    """
    return {
        "decisions": read_file_safe(repo_root / "decisions" / "log.md", max_chars=6000),
        "lessons": read_file_safe(repo_root / "tasks" / "lessons.md", max_chars=4000),
        "todo": read_file_safe(repo_root / "tasks" / "todo.md", max_chars=3000),
        "priorities": read_file_safe(repo_root / "context" / "current-priorities.md", max_chars=2000),
        "obsidian": read_obsidian_daily(days=7),
    }
