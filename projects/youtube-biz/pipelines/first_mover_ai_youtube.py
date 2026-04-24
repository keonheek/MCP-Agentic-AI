"""
First Mover AI — YouTube 롱폼 파이프라인
Remote cron (22:00 KST 매일): Layer 1+2 (텍스트만, 후보 + 스크립트 초안)
Local /loop 후속 실행: Layer 3 (영상 다운로드 + 자막 + 하이라이트 + 번역)

사용:
  python pipelines/first_mover_ai_youtube.py --stage=discover   # Remote-safe (Layer 1+2)
  python pipelines/first_mover_ai_youtube.py --stage=download   # Local (Layer 3)
  python pipelines/first_mover_ai_youtube.py --stage=all        # 전체
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


def _notify_activepieces(event: str, payload: dict):
    """POST to Activepieces webhook if ACTIVEPIECES_WEBHOOK_YOUTUBE is set in .env."""
    url = os.environ.get("ACTIVEPIECES_WEBHOOK_YOUTUBE", "")
    if not url:
        return
    try:
        import urllib.request
        body = json.dumps({"event": event, **payload}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass  # Non-blocking — pipeline runs regardless

from core.layer1_ingestion.viral_ai_videos import run as ingest_viral
from core.layer2_intelligence.ranker import run as rank_candidates
from core.layer2_intelligence.script_generator import run_youtube as generate_scripts

CHANNEL_KEY = "first_mover_ai_youtube"


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def stage_discover() -> dict:
    """Remote-safe: 텍스트 수집 + 스크립트 초안만 (영상 다운로드 X)"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    log("Stage 1: Discover (Remote-safe)")

    # Layer 1
    inbox_path = ingest_viral(date_str)
    log(f"  Ingestion: {inbox_path}")

    # Layer 2: 채점 → top 3 → 스크립트 초안
    top = rank_candidates(inbox_path, CHANNEL_KEY, top_n=3)
    scripts_path = generate_scripts(top, date_str)
    log(f"  Scripts: {scripts_path}")

    return {
        "stage": "discover",
        "inbox_path": inbox_path,
        "scripts_path": scripts_path,
        "top_candidates": len(top),
        "date": date_str,
    }


def stage_download(chosen_script_idx: int = 0) -> dict:
    """Local 전용: 선택한 영상 다운로드 + 자막 + 번역 + 하이라이트"""
    from core.layer3_media.first_mover_ai.downloader import download_video
    from core.layer3_media.first_mover_ai.highlight_extractor import process as extract_highlights
    from core.layer3_media.first_mover_ai.translator import process as translate_highlights

    date_str = datetime.now().strftime("%Y-%m-%d")
    scripts_path = BASE_DIR / "channels" / "first-mover-ai" / "drafts" / "youtube" / f"{date_str}-scripts.json"

    if not scripts_path.exists():
        return {"status": "error", "error": f"스크립트 파일 없음: {scripts_path}. --stage=discover 먼저 실행"}

    with open(scripts_path, encoding="utf-8") as f:
        scripts = json.load(f)

    if chosen_script_idx >= len(scripts):
        return {"status": "error", "error": f"인덱스 범위 초과 (총 {len(scripts)}개)"}

    chosen = scripts[chosen_script_idx]
    url = chosen.get("source_candidate", {}).get("url", "")
    if not url:
        return {"status": "error", "error": "URL 없음"}

    log(f"Stage 2: Download + Transcript + Translate: {url}")

    # Layer 3: 다운로드
    dl = download_video(url)
    if dl["status"] != "ok":
        return {"status": "error", "stage": "download", "error": dl.get("error")}
    log(f"  다운로드 완료: {dl['video_path']}")

    # Layer 3: 자막 + 하이라이트
    highlights = extract_highlights(dl["video_path"])
    log(f"  하이라이트 {len(highlights.get('highlights', []))}개")

    # Layer 3: 번역
    highlights_path = Path(dl["video_path"]).with_suffix(".highlights.json")
    translate_highlights(str(highlights_path))
    log(f"  번역 완료")

    return {
        "status": "ok",
        "stage": "download",
        "video_path": dl["video_path"],
        "highlights_path": str(highlights_path),
        "chosen_script_idx": chosen_script_idx,
    }


def main():
    stage = "all"
    chosen_idx = 0
    for arg in sys.argv[1:]:
        if arg.startswith("--stage="):
            stage = arg.split("=")[1]
        elif arg.startswith("--idx="):
            chosen_idx = int(arg.split("=")[1])

    if stage in ("discover", "all"):
        result = stage_discover()
        log(f"Discover 완료: {result}")
        _notify_activepieces("youtube_discover", result)

    if stage in ("download", "all"):
        result = stage_download(chosen_idx)
        log(f"Download 완료: {result}")


if __name__ == "__main__":
    main()
