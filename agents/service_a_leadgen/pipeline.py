"""
Service A Lead-Gen Fleet: Orchestrator
Runs A1 -> A2 -> A3 -> A4 -> A5 -> A6 in sequence.

Usage:
  python pipeline.py              # full run
  python pipeline.py --dry-run    # prints what each agent would do, no LLM calls, no real scraping
  python pipeline.py --skip A1    # skip specific agent(s), e.g. A1 (useful when sheet already seeded)
"""

import argparse
import sys
import os
import time
import traceback

# Ensure this directory is on the path so imports work when run from anywhere
sys.path.insert(0, os.path.dirname(__file__))

import a1_meta_ad_scanner as a1
import a2_response_time_tester as a2
import a3_platform_detector as a3
import a4_decision_maker_finder as a4
import a5_dm_draft_writer as a5
import a6_discord_digest as a6


def run(dry_run: bool = False, skip: set[str] = None) -> None:
    skip = skip or set()
    start = time.time()

    steps = [
        ("A1", a1.scan),
        ("A2", a2.test),
        ("A3", a3.detect),
        ("A4", a4.find),
        ("A5", a5.draft),
        ("A6", a6.digest),
    ]

    print("=" * 60)
    print(f"Service A Lead-Gen Fleet starting{' (DRY RUN)' if dry_run else ''}...")
    print("=" * 60)

    for label, fn in steps:
        if label in skip:
            print(f"\n[Pipeline] Skipping {label} (explicitly skipped)")
            continue

        print(f"\n[Pipeline] Running {label}...")
        try:
            fn(dry_run=dry_run)
        except Exception as e:
            print(f"\n[Pipeline] ERROR in {label}: {e}")
            traceback.print_exc()
            print(f"[Pipeline] Continuing to next agent...")

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"Pipeline complete in {elapsed:.1f}s")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Service A Lead-Gen Fleet")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what each agent would do without making real requests or LLM calls",
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="Agent labels to skip, e.g. --skip A1 A2",
    )
    args = parser.parse_args()

    run(dry_run=args.dry_run, skip=set(args.skip))
