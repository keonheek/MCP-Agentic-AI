"""
Claude subprocess orchestrator.
Spawns 'claude --print <command>' on a loop. Reads loop_control.json for pause/stop.
Writes to agents/status.json and orchestrator_registry.json.

Usage:
    python tools/orchestrator.py --name "GEO" --command "/execute-next" --interval 300
    python tools/orchestrator.py --name "SME Diag" --command "/loop" --interval 180 --max-runs 10
    python tools/orchestrator.py --name "GEO" --command "/execute-next" --dry-run
"""

import sys
import os
import json
import time
import signal
import atexit
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent          # tools/
PROJECT_ROOT = _HERE.parent                       # MCP_Agentic AI/

CONTROL_FILE  = PROJECT_ROOT / "tasks" / "loop_control.json"
REGISTRY_FILE = PROJECT_ROOT / "tasks" / "orchestrator_registry.json"
STATUS_SCRIPT = PROJECT_ROOT / "agents" / "update_status.py"
LOG_FILE      = PROJECT_ROOT / "tools" / "orchestrator_log.md"

# ---------------------------------------------------------------------------
# Registry helpers (atomic writes)
# ---------------------------------------------------------------------------

def _load_registry() -> dict:
    if not REGISTRY_FILE.exists():
        return {}
    try:
        return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_registry(data: dict) -> None:
    tmp = REGISTRY_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, REGISTRY_FILE)


def register(name: str, command: str) -> None:
    registry = _load_registry()
    registry[name] = {
        "pid": os.getpid(),
        "command": command,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "runs": 0,
    }
    _save_registry(registry)


def deregister(name: str) -> None:
    registry = _load_registry()
    registry.pop(name, None)
    _save_registry(registry)


def increment_runs(name: str) -> int:
    registry = _load_registry()
    entry = registry.get(name, {})
    entry["runs"] = entry.get("runs", 0) + 1
    registry[name] = entry
    _save_registry(registry)
    return entry["runs"]


# ---------------------------------------------------------------------------
# Control + status helpers
# ---------------------------------------------------------------------------

def check_control() -> str:
    """Return loop mode: 'running', 'paused', or 'stopped'."""
    if not CONTROL_FILE.exists():
        return "running"
    try:
        data = json.loads(CONTROL_FILE.read_text(encoding="utf-8"))
        return data.get("mode", "running")
    except (json.JSONDecodeError, OSError):
        return "running"


def update_status(name: str, status: str, task: str) -> None:
    try:
        subprocess.run(
            [sys.executable, str(STATUS_SCRIPT), name, status, task],
            timeout=10,
            capture_output=True,
        )
    except Exception as e:
        print(f"[warn] status update failed: {e}")


# ---------------------------------------------------------------------------
# Claude binary resolution
# ---------------------------------------------------------------------------

def find_claude_binary() -> str:
    """
    Find the claude CLI binary. Checks PATH first, then known Windows locations.
    Returns the command string to invoke claude.
    """
    import shutil

    # 1. Check PATH (works if user has claude in PATH or on non-Windows)
    if shutil.which("claude"):
        return "claude"

    # 2. Known Windows locations (VS Code extension, installed app)
    candidates = [
        Path.home() / ".vscode" / "extensions",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Packages",
    ]
    for base in candidates:
        if base.exists():
            for match in base.rglob("claude.exe"):
                return str(match)

    # 3. Fallback — will fail at runtime with a clear error
    return "claude"


_CLAUDE_BIN = find_claude_binary()


# ---------------------------------------------------------------------------
# Claude invocation
# ---------------------------------------------------------------------------

def run_claude(command: str, timeout: int, dry_run: bool) -> tuple[bool, str]:
    """
    Invoke `claude --print <command>`. Returns (success, output_text).
    """
    if dry_run:
        print(f"  [dry-run] would run: {_CLAUDE_BIN} --print \"{command}\"")
        return True, "[dry-run] no output"

    try:
        result = subprocess.run(
            [_CLAUDE_BIN, "--print", "--dangerously-skip-permissions", command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "NO_BEEP": "1"},
        )
        output = result.stdout.strip() if result.stdout else ""
        if result.returncode != 0:
            err = result.stderr.strip() if result.stderr else "unknown error"
            return False, f"exit {result.returncode}: {err}"
        return True, output
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout}s"
    except FileNotFoundError:
        return False, f"claude CLI not found at: {_CLAUDE_BIN}"
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log_run(name: str, run_num: int, command: str, success: bool, output: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_icon = "✓" if success else "✗"
    # Truncate long output for log readability
    preview = output[:300] + "..." if len(output) > 300 else output
    entry = (
        f"\n---\n"
        f"**[{timestamp}] {status_icon} {name} — run #{run_num}**  \n"
        f"Command: `{command}`  \n"
        f"```\n{preview}\n```\n"
    )
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(entry)
    except OSError as e:
        print(f"[warn] log write failed: {e}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Claude subprocess orchestrator")
    parser.add_argument("--name",     required=True,  help="Agent name (e.g. 'GEO', 'SME Diag')")
    parser.add_argument("--command",  required=True,  help="Claude command (e.g. '/execute-next', '/loop')")
    parser.add_argument("--interval", type=int, default=300, help="Seconds between runs (default: 300)")
    parser.add_argument("--max-runs", type=int, default=20,  help="Max iterations before stopping (default: 20)")
    parser.add_argument("--timeout",  type=int, default=300, help="Claude subprocess timeout in seconds (default: 300)")
    parser.add_argument("--dry-run",  action="store_true",   help="Print what would happen without calling Claude")
    args = parser.parse_args()

    name     = args.name
    # Fix Git Bash path mangling: /execute-next → C:/Program Files/Git/execute-next
    # Strip any Windows path prefix that Git Bash injects and restore the slash command
    import re
    command = args.command
    git_bash_mangle = re.match(r"^[A-Za-z]:[/\\].*?[/\\]([\w-]+)$", command)
    if git_bash_mangle:
        command = "/" + git_bash_mangle.group(1)
    interval = args.interval
    max_runs = args.max_runs
    timeout  = args.timeout
    dry_run  = args.dry_run

    print(f"[orchestrator] starting: name={name!r} command={command!r} interval={interval}s max_runs={max_runs}")
    if dry_run:
        print("[orchestrator] DRY RUN — no Claude calls will be made")

    # Register PID + cleanup on exit
    register(name, command)
    atexit.register(deregister, name)

    # Handle Ctrl+C gracefully
    def _handle_signal(sig, frame):
        print(f"\n[orchestrator] caught signal {sig} — shutting down {name!r}")
        deregister(name)
        update_status(name, "idle", "Orchestrator stopped")
        sys.exit(0)

    signal.signal(signal.SIGINT, _handle_signal)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_signal)

    run_count = 0

    while run_count < max_runs:
        # --- Check control file ---
        mode = check_control()

        if mode == "stopped":
            print(f"[{name}] loop_control.json mode=stopped — exiting")
            break

        if mode == "paused":
            print(f"[{name}] paused — waiting 30s...")
            update_status(name, "idle", "Paused")
            time.sleep(30)
            continue

        # --- Execute ---
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{name}] [{timestamp}] run #{run_count + 1}/{max_runs} — invoking {command!r}")
        update_status(name, "working", f"Run #{run_count + 1} — {command}")

        success, output = run_claude(command, timeout, dry_run)
        run_count += 1
        total_runs = increment_runs(name)

        if success:
            # Extract first line of output as task summary (max 60 chars)
            first_line = output.split("\n")[0][:60] if output else "Done"
            update_status(name, "done", first_line)
            print(f"[{name}] run #{run_count} OK — {first_line}")
        else:
            update_status(name, "blocked", f"Error: {output[:50]}")
            print(f"[{name}] run #{run_count} FAILED — {output[:100]}")
            print(f"[{name}] waiting 60s before retry...")
            log_run(name, total_runs, command, success, output)
            time.sleep(60)
            continue

        log_run(name, total_runs, command, success, output)

        if run_count >= max_runs:
            print(f"[{name}] reached max_runs={max_runs} — stopping")
            break

        print(f"[{name}] sleeping {interval}s until next run...")
        time.sleep(interval)

    update_status(name, "idle", f"Orchestrator finished ({run_count} runs)")
    print(f"[{name}] orchestrator done. Total runs: {run_count}")


if __name__ == "__main__":
    main()
