"""
Layer 1: 채널별 ingestion 배치 실행기
크론에서 호출: python run_ingestion.py [channel]
channel: singit | ai | politics | all
"""
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE_DIR.parent.parent))  # MCP_Agentic_AI root


def run_singit(date_str: str):
    from core.layer1_ingestion.vocal_trending import run
    return run(date_str)


def run_ai(date_str: str):
    from core.layer1_ingestion.ai_news import run
    return run(date_str)


def run_politics(date_str: str):
    from core.layer1_ingestion.naver_news import run
    return run(date_str)


def main():
    channel = sys.argv[1] if len(sys.argv) > 1 else "all"
    date_str = datetime.now().strftime("%Y-%m-%d")

    results = {}

    if channel in ("singit", "all"):
        try:
            path = run_singit(date_str)
            results["singit"] = {"status": "ok", "path": path}
        except Exception as e:
            results["singit"] = {"status": "error", "error": str(e)}

    if channel in ("ai", "all"):
        try:
            path = run_ai(date_str)
            results["ai"] = {"status": "ok", "path": path}
        except Exception as e:
            results["ai"] = {"status": "error", "error": str(e)}

    if channel in ("politics", "all"):
        try:
            path = run_politics(date_str)
            results["politics"] = {"status": "ok", "path": path}
        except Exception as e:
            results["politics"] = {"status": "error", "error": str(e)}

    for ch, result in results.items():
        status = result["status"]
        detail = result.get("path") or result.get("error")
        print(f"[{status.upper()}] {ch}: {detail}")

    errors = [k for k, v in results.items() if v["status"] == "error"]
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
