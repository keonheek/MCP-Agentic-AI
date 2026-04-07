"""
benchmark.py — IMMUTABLE. Do not modify this file.

Measures ERP app module import time as a proxy for cold-start latency.
Lower = better. Returns a single float: median import time in seconds.

Usage:
    python benchmark.py          # prints METRIC: X.XXXs
    python benchmark.py --runs 5 # override run count
"""
import subprocess, sys, statistics, time, argparse

RUNS = 3
TARGET = "app_optimized"  # the file the agent edits (without .py)


def measure(runs: int = RUNS) -> float:
    times = []
    for _ in range(runs):
        result = subprocess.run(
            [sys.executable, "-c", f"import time; t=time.perf_counter(); import importlib; importlib.import_module('{TARGET}'); print(time.perf_counter()-t)"],
            capture_output=True, text=True,
            cwd=str(__import__("pathlib").Path(__file__).parent)
        )
        if result.returncode != 0:
            print(f"ERROR: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        times.append(float(result.stdout.strip()))
    median = statistics.median(times)
    return median


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=RUNS)
    args = parser.parse_args()

    m = measure(args.runs)
    print(f"METRIC: {m:.3f}s")
    sys.exit(0)
