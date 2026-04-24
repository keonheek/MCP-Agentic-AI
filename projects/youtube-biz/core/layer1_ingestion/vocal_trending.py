"""
Layer 1: Sing It 채널 소스 수집
YouTube 보컬/음악 영상 + Instagram Reels 트렌딩 후보 수집
TikTok 의존도 30% 이하 유지
"""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = BASE_DIR / "config" / "sources.yaml"
INBOX_DIR = BASE_DIR / "data" / "inbox"


def load_sources() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)["sources"]["singit"]


def fetch_youtube_candidates(sources: dict) -> list[dict]:
    """yt-dlp으로 YouTube 후보 영상 수집"""
    try:
        import yt_dlp
    except ImportError:
        print("[WARN] yt-dlp 미설치. pip install yt-dlp 실행 필요.")
        return []

    candidates = []
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": 10,
    }

    # 채널 최신 업로드 수집
    for channel in sources.get("channels", []):
        url = f"https://www.youtube.com/{channel}/shorts"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info or "entries" not in info:
                    continue
                for entry in info["entries"][:5]:
                    if not entry:
                        continue
                    duration = entry.get("duration", 0) or 0
                    if duration > sources.get("max_duration_seconds", 180):
                        continue
                    candidates.append({
                        "id": entry.get("id"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "title": entry.get("title", ""),
                        "channel": channel,
                        "duration": duration,
                        "view_count": entry.get("view_count", 0),
                        "source_platform": "youtube",
                        "language": "en",
                        "thumbnail": entry.get("thumbnail", ""),
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"[WARN] {channel} 수집 실패: {e}")

    # 검색 쿼리로 추가 수집
    for query in sources.get("search_queries", []):
        search_url = f"ytsearch10:{query} shorts"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_url, download=False)
                if not info or "entries" not in info:
                    continue
                for entry in info["entries"][:3]:
                    if not entry:
                        continue
                    view_count = entry.get("view_count", 0) or 0
                    if view_count < sources.get("min_views", 50000):
                        continue
                    candidates.append({
                        "id": entry.get("id"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "title": entry.get("title", ""),
                        "channel": entry.get("uploader", ""),
                        "duration": entry.get("duration", 0) or 0,
                        "view_count": view_count,
                        "source_platform": "youtube",
                        "language": "en",
                        "thumbnail": entry.get("thumbnail", ""),
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"[WARN] 검색 '{query}' 실패: {e}")

    return candidates


def fetch_tiktok_candidates(sources: dict, max_count: int) -> list[dict]:
    """TikTok 해시태그 트렌딩 수집 (의존도 30% 이하)"""
    try:
        from TikTokApi import TikTokApi
    except ImportError:
        print("[WARN] TikTokApi 미설치. TikTok 수집 건너뜀.")
        return []

    candidates = []
    hashtags = sources.get("hashtags", [])

    for tag in hashtags[:2]:  # 상위 2개 해시태그만
        try:
            with TikTokApi() as api:
                for video in api.hashtag(name=tag).videos(count=5):
                    data = video.as_dict
                    candidates.append({
                        "id": data.get("id"),
                        "url": f"https://www.tiktok.com/@{data.get('author', {}).get('uniqueId')}/video/{data.get('id')}",
                        "title": data.get("desc", ""),
                        "channel": data.get("author", {}).get("uniqueId", ""),
                        "duration": data.get("video", {}).get("duration", 0),
                        "view_count": data.get("stats", {}).get("playCount", 0),
                        "source_platform": "tiktok",
                        "language": "en",
                        "thumbnail": "",
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
                    if len(candidates) >= max_count:
                        break
        except Exception as e:
            print(f"[WARN] TikTok #{tag} 수집 실패: {e}")

    return candidates


def deduplicate(candidates: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for item in candidates:
        key = item.get("id") or item.get("url")
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    sources = load_sources()
    max_candidates = 30

    # YouTube 우선 (70% 이상)
    youtube_candidates = fetch_youtube_candidates(sources["youtube"])

    # TikTok 보조 (30% 이하)
    tiktok_max = max(0, max_candidates - len(youtube_candidates))
    tiktok_candidates = fetch_tiktok_candidates(
        sources.get("tiktok", {}),
        max_count=min(tiktok_max, int(max_candidates * 0.30)),
    )

    all_candidates = deduplicate(youtube_candidates + tiktok_candidates)[:max_candidates]

    output_path = INBOX_DIR / f"{date_str}-singit-candidates.json"
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_candidates, f, ensure_ascii=False, indent=2)

    print(f"[Layer1] Sing It 후보 {len(all_candidates)}개 저장: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    run()
