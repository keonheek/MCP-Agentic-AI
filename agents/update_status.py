"""
Update agent status in agents/status.json.

Usage:
    python agents/update_status.py "GEO" "working" "Running audit on client website"
    python agents/update_status.py "Lead Intel" "done" "Exported 5 companies to Excel"
    python agents/update_status.py "Consulting" "idle" ""

Valid agent names: GEO, Lead Intel, SME Diag, Consulting, Next Role
Valid statuses:    working, idle, done
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# Resolve project root regardless of working directory or Korean path
_HERE = Path(__file__).resolve().parent          # agents/
PROJECT_ROOT = _HERE.parent                       # MCP_Agentic AI/
STATUS_FILE = PROJECT_ROOT / "agents" / "status.json"

# Load .env for STATUS_SERVER_URL
from dotenv import load_dotenv
for _p in [PROJECT_ROOT / ".env", _HERE / ".env"]:
    if _p.exists():
        load_dotenv(dotenv_path=_p)
        break

STATUS_SERVER_URL = os.environ.get("STATUS_SERVER_URL", "")

VALID_AGENTS = ["GEO", "Lead Intel", "SME Diag", "Consulting", "Next Role", "Discord Bot", "Claude Loop", "youtube-analyst"]
VALID_STATUSES = ["working", "idle", "done", "blocked"]


def _post_to_server(agent_name: str, status: str, task: str) -> None:
    """POST status update to Railway server. Silent on failure."""
    if not STATUS_SERVER_URL:
        return
    try:
        import urllib.request
        import json as _json
        data = _json.dumps({"agent": agent_name, "status": status, "task": task}).encode()
        req = urllib.request.Request(
            f"{STATUS_SERVER_URL.rstrip('/')}/status",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"[server] post failed (local write still succeeded): {e}")


def update(agent_name: str, status: str, task: str) -> None:
    if agent_name not in VALID_AGENTS:
        print(f"[warn] Unknown agent '{agent_name}'. Valid: {VALID_AGENTS}")

    if status not in VALID_STATUSES:
        print(f"[warn] Unknown status '{status}'. Valid: {VALID_STATUSES}")

    # Load existing state, start fresh if missing or malformed
    current = {}
    if STATUS_FILE.exists():
        try:
            current = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            current = {}

    current[agent_name] = {
        "task": task or "Idle",
        "status": status,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }

    # Atomic write: write to .tmp then replace to avoid corruption
    tmp = STATUS_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, STATUS_FILE)

    # Also POST to Railway server (cloud dashboard)
    _post_to_server(agent_name, status, task)

    print(f"[{agent_name}] {status} — {task or 'Idle'}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python agents/update_status.py <agent_name> <status> [task]")
        print(f"Agents:   {VALID_AGENTS}")
        print(f"Statuses: {VALID_STATUSES}")
        sys.exit(1)

    _agent = sys.argv[1]
    _status = sys.argv[2]
    _task = sys.argv[3] if len(sys.argv) > 3 else ""

    update(_agent, _status, _task)
