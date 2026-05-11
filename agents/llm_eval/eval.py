"""
Korean LLM Eval Harness - Skincare D2C Customer Service
Tests: Solar Pro 3, Gemini 2.5 Flash, GPT-4o-mini, Claude Haiku 4.5
Judge: runs via /llm-eval-judge slash command in Claude Code session (zero API cost)

Usage:
    python eval.py                  # auto-detect dry/live
    python eval.py --dry            # force dry mode
    python eval.py --no-sheet       # skip Google Sheet output (judge handles sheet writes)
"""
import os
import sys
import json
import time
import argparse
import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

from models import MODEL_REGISTRY

DATA_DIR = Path(__file__).parent / "data" / "eval_runs"

REQUIRED_KEYS = {
    "UPSTAGE_API_KEY":    "solar-pro-3",
    "GEMINI_API_KEY":     "gemini-2.5-flash",
    "OPENAI_API_KEY":     "gpt-4o-mini",
    "ANTHROPIC_API_KEY":  "claude-haiku-4-5",
}


def check_keys() -> tuple[list[str], list[str]]:
    present = [k for k in REQUIRED_KEYS if os.getenv(k)]
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    return present, missing


def load_prompts() -> dict:
    p = Path(__file__).parent / "prompts.json"
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(brand_context: str, base_system: str) -> str:
    return f"{base_system}\n\n브랜드 정보:\n{brand_context}"


def run_eval(force_dry: bool = False) -> list[dict]:
    data = load_prompts()
    brand_context = data["brand_context"]
    base_system = data["system_prompt"]
    prompts = data["prompts"]
    system_prompt = build_system_prompt(brand_context, base_system)

    present, missing = check_keys()
    is_dry = force_dry or len(missing) > 0

    if missing:
        print("\n[MISSING KEYS - DRY MODE for affected models]")
        for k in missing:
            print(f"  {k} -> {REQUIRED_KEYS[k]}")
    else:
        print("\n[ALL KEYS PRESENT - LIVE MODE]")

    results = []
    total_calls = len(MODEL_REGISTRY) * len(prompts)
    call_n = 0

    for model_key, model_fn in MODEL_REGISTRY.items():
        for prompt in prompts:
            call_n += 1
            print(f"  [{call_n}/{total_calls}] {model_key} | P{prompt['id']}: {prompt['category']}", end=" ... ", flush=True)

            if force_dry:
                resp = {
                    "text": "[DRY MODE: --dry flag set]",
                    "latency_ms": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                    "dry": True,
                }
            else:
                try:
                    resp = model_fn(system_prompt, prompt["inquiry"])
                except Exception as e:
                    resp = {
                        "text": f"[ERROR: {e}]",
                        "latency_ms": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "cost_usd": 0.0,
                        "dry": True,
                    }

            result = {
                "model": model_key,
                "prompt_id": prompt["id"],
                "category": prompt["category"],
                "inquiry": prompt["inquiry"],
                "brand_context": brand_context,
                "response": resp["text"],
                "latency_ms": resp["latency_ms"],
                "input_tokens": resp["input_tokens"],
                "output_tokens": resp["output_tokens"],
                "cost_usd": resp["cost_usd"],
                "dry": resp.get("dry", False),
            }
            results.append(result)
            print(f"{'DRY' if resp.get('dry') else 'OK'} | {resp['latency_ms']:.0f}ms")

    return results


def main():
    parser = argparse.ArgumentParser(description="Korean LLM Eval Harness")
    parser.add_argument("--dry", action="store_true", help="Force dry mode")
    args = parser.parse_args()

    print("Korean LLM Eval: Skincare D2C Customer Service")
    print("Models: Solar Pro 3 | Gemini 2.5 Flash | GPT-4o-mini | Claude Haiku 4.5")
    print("Judge: /llm-eval-judge slash command (Claude Code session, zero API cost)")
    print("Prompts: 10 Korean skincare D2C inquiries")
    print()

    present, missing = check_keys()
    print(f"Keys present: {', '.join(present) if present else 'none'}")
    if missing:
        print(f"Keys missing: {', '.join(missing)}")

    t_start = time.perf_counter()
    results = run_eval(force_dry=args.dry)
    elapsed = time.perf_counter() - t_start

    print(f"\nTotal runtime: {elapsed:.1f}s")
    print(f"Total model calls: {len(results)}")
    live = len([r for r in results if not r.get("dry")])
    print(f"Live responses: {live} | Dry: {len(results) - live}")

    # Write raw results to data/eval_runs/
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_path = DATA_DIR / f"run_{timestamp}.json"
    run_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nRaw responses saved: {run_path}")
    print("Next step: run /llm-eval-judge in your Claude Code session to score all responses and write to Google Sheet.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
