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

VALID_AGENTS = ["GEO", "Lead Intel", "SME Diag", "Consulting", "Next Role", "Discord Bot"]
VALID_STATUSES = ["working", "idle", "done", "blocked"]


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
