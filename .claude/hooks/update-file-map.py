"""
Stop hook — upserts FILE_MAP.md rows for meaningful files written this session.

Called by: ~/.claude/settings.json Stop hook
Input: JSON on stdin from Claude Code Stop event (contains session tool calls)

Only updates FILE_MAP for files that are:
- Not in __pycache__, .git, node_modules
- Not .env, *.pyc, *.lock temporary files
- In a known "interesting" path prefix
"""
import sys
import json
import os
import datetime
import re

PROJECT_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
)
FILE_MAP_PATH = os.path.join(PROJECT_ROOT, "FILE_MAP.md")

SKIP_PATTERNS = [
    "__pycache__", ".git", "node_modules", ".env",
    ".pyc", ".lock", "~", ".tmp", ".log",
]

SECTION_MAP = {
    "projects/youtube-biz/pipelines": "Pipeline Entrypoints",
    "projects/youtube-biz/core": "Core Pipeline Modules",
    "projects/youtube-biz/config": "Config Files",
    ".claude/hooks": "Hooks",
    ".claude/agents": "Agent Definitions",
    "references/diagrams": "Reference Diagrams",
    "context/": "Claude Code System Files",
    "tasks/": "Claude Code System Files",
    "decisions/": "Claude Code System Files",
}


def should_skip(path: str) -> bool:
    for pat in SKIP_PATTERNS:
        if pat in path:
            return True
    return False


def get_section(path: str) -> str:
    rel = path.replace("\\", "/")
    for prefix, section in SECTION_MAP.items():
        if prefix in rel:
            return section
    return None


def upsert_row(file_map_content: str, filename: str, rel_path: str, section: str) -> str:
    """Add or update a row in the given section table of FILE_MAP.md."""
    today = datetime.date.today().isoformat()

    # Check if row already exists (by filename)
    if f"| {filename} |" in file_map_content:
        return file_map_content  # Already tracked, skip

    # Find the section header
    section_marker = f"## {section}"
    if section_marker not in file_map_content:
        return file_map_content  # Section not found, skip gracefully

    # Find the end of that section's table (next ## or end of file)
    section_start = file_map_content.index(section_marker)
    next_section = file_map_content.find("\n## ", section_start + 1)
    section_block = file_map_content[section_start:next_section] if next_section != -1 else file_map_content[section_start:]

    # Find the last table row in the section
    lines = section_block.split("\n")
    last_row_idx = None
    for i, line in enumerate(lines):
        if line.startswith("| ") and not line.startswith("| File") and not line.startswith("| ---"):
            last_row_idx = i

    if last_row_idx is None:
        return file_map_content  # No table found

    # Build new row (3-col or 4-col based on section)
    if "Daily Output" in section:
        return file_map_content  # Skip auto-generated output files
    new_row = f"| {filename} | {rel_path} | Auto-added {today} |"

    # Insert after last row
    lines.insert(last_row_idx + 1, new_row)
    new_section = "\n".join(lines)

    if next_section != -1:
        return file_map_content[:section_start] + new_section + file_map_content[next_section:]
    else:
        return file_map_content[:section_start] + new_section


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # Stop hook event contains tool_calls or similar; extract written file paths
    # The Stop hook receives the stop_hook_active event — we look for any file paths in the payload
    written_paths = []

    # Claude Code Stop hook passes the full event as JSON
    # Look for file_path keys anywhere in the structure
    raw = json.dumps(data)
    matches = re.findall(r'"file_path"\s*:\s*"([^"]+)"', raw)
    written_paths.extend(matches)

    if not written_paths:
        sys.exit(0)

    if not os.path.exists(FILE_MAP_PATH):
        sys.exit(0)

    with open(FILE_MAP_PATH, encoding="utf-8") as f:
        content = f.read()

    # Update timestamp header
    today = datetime.date.today().isoformat()
    content = re.sub(
        r"_Auto-updated by Claude Code PostToolUse hook\. Last updated: [\d-]+_",
        f"_Auto-updated by Claude Code PostToolUse hook. Last updated: {today}_",
        content,
    )

    changed = False
    for path in written_paths:
        if should_skip(path):
            continue
        section = get_section(path)
        if not section:
            continue
        filename = os.path.basename(path)
        # Make path relative to project root
        rel = os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")
        new_content = upsert_row(content, filename, rel, section)
        if new_content != content:
            content = new_content
            changed = True

    if changed:
        with open(FILE_MAP_PATH, "w", encoding="utf-8") as f:
            f.write(content)


if __name__ == "__main__":
    main()
