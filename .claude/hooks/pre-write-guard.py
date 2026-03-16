"""
PreToolUse hook — Write tool guard.
Blocks writes to .env files (secrets protection).
Warns on writes to CLAUDE.md or context/ (high-impact files).
"""
import sys
import json
import os

data = json.load(sys.stdin)
file_path = data.get("tool_input", {}).get("file_path", "")
basename = os.path.basename(file_path)

# Block .env writes entirely
if basename == ".env" or basename.endswith(".env"):
    sys.stderr.write("BLOCKED: Writing to .env file is not allowed. Edit .env manually to protect secrets.\n")
    sys.exit(2)

# Warn on high-impact files (but allow)
if "context/" in file_path or basename == "CLAUDE.md":
    sys.stderr.write(f"NOTE: Writing to high-impact file: {file_path}\n")
