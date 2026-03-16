"""
PostToolUse hook — Write tool
Appends an audit entry to decisions/log.md when a context file or CLAUDE.md is written.
"""
import sys
import json
import os
import datetime

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

TRIGGERS = ["context" + os.sep, "CLAUDE.md", "context/"]
matched = any(t in path for t in TRIGGERS)

if matched:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))  # up from .claude/hooks/
    log_path = os.path.join(project_root, "decisions", "log.md")

    filename = os.path.basename(path)
    today = datetime.date.today().isoformat()
    entry = f"[{today}] CONTEXT UPDATED: {filename} written.\n"

    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        sys.stderr.write(f"post-write-log: failed to write audit entry: {e}\n")
