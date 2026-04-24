"""
PostToolUse hook — Write tool
1. Appends an audit entry to decisions/log.md when a context file or CLAUDE.md is written.
2. Upserts a row in FILE_MAP.md for meaningful non-context file writes.
"""
import sys
import json
import os
import re
import datetime

data = json.load(sys.stdin)
path = data.get("tool_input", {}).get("file_path", "")

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # up from .claude/hooks/

# --- Part 1: decisions/log.md for context file writes ---
CONTEXT_TRIGGERS = ["context" + os.sep, "CLAUDE.md", "context/"]
if any(t in path for t in CONTEXT_TRIGGERS):
    log_path = os.path.join(project_root, "decisions", "log.md")
    filename = os.path.basename(path)
    today = datetime.date.today().isoformat()
    entry = f"[{today}] CONTEXT UPDATED: {filename} written.\n"
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        sys.stderr.write(f"post-write-log: failed to write audit entry: {e}\n")

# --- Part 2: FILE_MAP.md upsert for meaningful file writes ---
SKIP_PATTERNS = ["__pycache__", ".git", ".env", ".pyc", ".lock", "~", ".tmp"]
FILE_MAP_PATH = os.path.join(project_root, "FILE_MAP.md")

SECTION_MAP = {
    "projects/youtube-biz/pipelines": "Pipeline Entrypoints",
    "projects/youtube-biz/core": "Core Pipeline Modules",
    "projects/youtube-biz/config": "Config Files",
    ".claude/hooks": "Hooks",
    ".claude/agents": "Agent Definitions",
    "references/diagrams": "Reference Diagrams",
}

def should_skip(p):
    return any(pat in p for pat in SKIP_PATTERNS)

def get_section(p):
    rel = p.replace("\\", "/")
    for prefix, section in SECTION_MAP.items():
        if prefix in rel:
            return section
    return None

if not should_skip(path) and os.path.exists(FILE_MAP_PATH):
    section = get_section(path)
    if section:
        filename = os.path.basename(path)
        try:
            with open(FILE_MAP_PATH, encoding="utf-8") as f:
                content = f.read()

            # Skip if already tracked
            if f"| {filename} |" not in content:
                section_marker = f"## {section}"
                if section_marker in content:
                    rel = os.path.relpath(path, project_root).replace("\\", "/")
                    today = datetime.date.today().isoformat()
                    new_row = f"| {filename} | {rel} | Auto-added {today} |"

                    # Insert before next section or at end of file
                    section_start = content.index(section_marker)
                    next_sec = content.find("\n## ", section_start + 1)
                    block_end = next_sec if next_sec != -1 else len(content)
                    block = content[section_start:block_end]

                    # Find last table row in block
                    lines = block.split("\n")
                    last_row = None
                    for i, line in enumerate(lines):
                        if line.startswith("| ") and not line.startswith("| File") and not line.startswith("| ---") and not line.startswith("| Pattern"):
                            last_row = i
                    if last_row is not None:
                        lines.insert(last_row + 1, new_row)
                        new_block = "\n".join(lines)
                        content = content[:section_start] + new_block + content[block_end:]
                        with open(FILE_MAP_PATH, "w", encoding="utf-8") as f:
                            f.write(content)
        except Exception as e:
            sys.stderr.write(f"post-write-log: FILE_MAP upsert failed: {e}\n")
