"""
Nightly Autonomous Evolution Loop
Runs at 2:00am KST via cron. Pure data collector + applier.

Zero API cost. No LLM calls. Each strand picks 1 improvement,
writes data/evolution_YYYY-MM-DD.json.
Git commits only when tests pass.
"""

import sys
import os
import json
import datetime
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_HERE = Path(__file__).resolve().parent
REPO_ROOT = Path("C:/Users/keonh/Dev/MCP_Agentic_AI")
DATA_DIR = _HERE / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(_HERE))
from strands import speed_to_lead, automation_workflows, saas_integrations, pipa_tier_p, geo_seo_blog, service_v

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_result(result: dict) -> bool:
    """
    Write files specified in result dict. Returns True if applied.
    Supports single file_path+write_content, append_content, and multi_write.
    """
    if result.get("skipped"):
        print(f"  [SKIP] {result.get('reason', 'already ran today')}")
        return False

    writes = []

    if "multi_write" in result:
        writes = result["multi_write"]
    elif "file_path" in result:
        if "write_content" in result:
            writes = [{"file_path": result["file_path"], "write_content": result["write_content"]}]
        elif "append_content" in result:
            writes = [{"file_path": result["file_path"], "append_content": result["append_content"]}]

    for w in writes:
        target = REPO_ROOT / w["file_path"]
        target.parent.mkdir(parents=True, exist_ok=True)

        if "write_content" in w:
            target.write_text(w["write_content"], encoding="utf-8")
        elif "append_content" in w:
            existing = target.read_text(encoding="utf-8") if target.exists() else ""
            # Idempotency: check if content already appended
            idempotent_key = result.get("idempotent_key", "")
            if idempotent_key and idempotent_key in existing:
                print(f"  [SKIP] idempotent_key already in file: {idempotent_key}")
                return False
            target.write_text(existing + w["append_content"] + "\n", encoding="utf-8")

    return bool(writes)


def _run_tests(strand_name: str) -> tuple[bool, str]:
    """
    Run pytest for the relevant product. Returns (passed, output_snippet).
    Budget: max 30s per test run.
    """
    test_map = {
        "speed_to_lead": "projects/ai-agency/products/speed-to-lead/tests/",
        "automation_workflows": "projects/ai-agency/products/automation-workflows/tests/",
        "saas_integrations": "projects/ai-agency/products/saas-integrations/tests/",
        "pipa_tier_p": "projects/ai-agency/products/pipa-tier-p/tests/",
        "geo_seo_blog": "projects/ai-agency/products/geo-seo-blog/tests/",
        "service_v": None,  # no tests for pre-launch service
    }
    test_path = test_map.get(strand_name)
    if not test_path:
        return True, "no tests (pre-launch)"

    full_path = REPO_ROOT / test_path
    if not full_path.exists():
        return True, "test directory not found, skipping"

    try:
        proc = subprocess.run(
            ["python", "-m", "pytest", str(full_path), "-q", "--tb=short", "--timeout=30"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO_ROOT),
        )
        passed = proc.returncode == 0
        output = (proc.stdout + proc.stderr)[-500:]  # last 500 chars
        return passed, output
    except subprocess.TimeoutExpired:
        return False, "test timeout after 60s"
    except Exception as e:
        return False, f"test runner error: {e}"


def _git_commit(commit_message: str) -> bool:
    """Stage all changes and commit. Returns True on success."""
    try:
        # Stage all tracked and new files in data dir and relevant product paths
        subprocess.run(
            ["git", "add",
             "agents/evolution_loop/data/",
             "agents/evolution_loop/strands/",
             "projects/ai-agency/services/video/"],
            cwd=str(REPO_ROOT),
            check=True,
            capture_output=True,
        )
        proc = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return True
        if "nothing to commit" in proc.stdout + proc.stderr:
            return True  # idempotent
        print(f"  [GIT ERROR] {proc.stderr[:200]}")
        return False
    except Exception as e:
        print(f"  [GIT EXCEPTION] {e}")
        return False


# ---------------------------------------------------------------------------
# Strand runners
# ---------------------------------------------------------------------------

STRANDS = [
    ("speed_to_lead", speed_to_lead.run),
    ("automation_workflows", automation_workflows.run),
    ("saas_integrations", saas_integrations.run),
    ("pipa_tier_p", pipa_tier_p.run),
    ("geo_seo_blog", geo_seo_blog.run),
    ("service_v", service_v.run),
]

# Budget: max 6 file changes per strand per night
MAX_FILE_CHANGES_PER_STRAND = 6


def main():
    today_str = datetime.date.today().isoformat()
    print(f"[EVOLVE] Starting evolution loop for {today_str}")
    print()

    # Idempotency at top level: check if evolution already ran today
    out_path = DATA_DIR / f"evolution_{today_str}.json"
    if out_path.exists():
        print(f"[EVOLVE] Already ran today ({out_path}). Exiting.")
        sys.exit(0)

    results = {}
    summary_lines = []

    for strand_name, strand_fn in STRANDS:
        print(f"[EVOLVE] Running strand: {strand_name}...")
        try:
            result = strand_fn(DATA_DIR)
            results[strand_name] = result

            if result.get("skipped"):
                print(f"  [SKIP] {result.get('reason')}")
                summary_lines.append(f"[{strand_name}] SKIPPED: {result.get('reason')}")
                continue

            applied = _apply_result(result)
            result["applied"] = applied

            if applied:
                # Count file changes (budget check)
                file_count = len(result.get("multi_write", [])) or (1 if "file_path" in result else 0)
                if file_count > MAX_FILE_CHANGES_PER_STRAND:
                    print(f"  [BUDGET] {file_count} changes exceeds max {MAX_FILE_CHANGES_PER_STRAND}. Skipping commit.")
                    result["commit_skipped"] = True
                    result["commit_skip_reason"] = "budget exceeded"
                else:
                    tests_passed, test_output = _run_tests(strand_name)
                    result["tests_passed"] = tests_passed
                    result["test_output_snippet"] = test_output

                    if tests_passed:
                        committed = _git_commit(result.get("commit_message", f"chore(evolution): {strand_name}"))
                        result["committed"] = committed
                        status = "OK" if committed else "COMMIT_FAILED"
                    else:
                        result["committed"] = False
                        status = "TEST_FAIL"
                        print(f"  [FAIL] Tests failed: {test_output[-200:]}")

                    flag = " [FLAG]" if result.get("flag_for_report") else ""
                    summary_lines.append(f"[{strand_name}] {result.get('summary', 'applied')}{flag} ({status})")
                    print(f"  -> {status}: {result.get('summary', '')}")
            else:
                result["applied"] = False
                summary_lines.append(f"[{strand_name}] no-op (already applied)")
                print(f"  -> no-op")

        except Exception as e:
            import traceback
            err = traceback.format_exc()
            results[strand_name] = {"error": str(e), "traceback": err}
            summary_lines.append(f"[{strand_name}] ERROR: {str(e)[:80]}")
            print(f"  [ERROR] {e}")

        print()

    # Write evolution JSON
    payload = {
        "date": today_str,
        "strands": results,
        "summary_lines": summary_lines,
        "strand_count": len(STRANDS),
        "applied_count": sum(1 for r in results.values() if r.get("applied")),
        "committed_count": sum(1 for r in results.values() if r.get("committed")),
        "flagged_count": sum(1 for r in results.values() if r.get("flag_for_report")),
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[EVOLVE] Done. Data written to {out_path}")
    print(f"[EVOLVE] Applied: {payload['applied_count']}/{payload['strand_count']}")
    print(f"[EVOLVE] Committed: {payload['committed_count']}")
    print()
    print("Summary:")
    for line in summary_lines:
        print(f"  {line}")
    print()
    print("[EVOLVE] Next step: run /evolve-report in Claude Code session at 7am.")


if __name__ == "__main__":
    main()
