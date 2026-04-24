"""
Layer 1: 해외 AI YouTube 바이럴 영상 탐색 (First Mover AI 번역 소스)
yt-dlp로 채널 최신 업로드 + 검색 결과 수집
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = BASE_DIR / "config" / "sources.yaml"
INBOX_DIR = BASE_DIR / "data" / "inbox"


def load_sources() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)["sources"]["first_mover_ai_youtube"]


def fetch_channel_latest(channels: list[str], max_per_channel: int = 3) -> list[dict]:
    try:
        import yt_dlp
    except ImportError:
        print("[WARN] yt-dlp 미설치")
        return []

    candidates = []
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "playlistend": max_per_channel,
    }

    for ch in channels:
        url = f"https://www.youtube.com/{ch}/videos"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info or "entries" not in info:
                    continue
                for entry in info["entries"][:max_per_channel]:
                    if not entry:
                        continue
                    duration = entry.get("duration") or 0
                    candidates.append({
                        "id": entry.get("id"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "title": entry.get("title", ""),
                        "channel": ch,
                        "duration": duration,
                        "view_count": entry.get("view_count") or 0,
                        "source_platform": "youtube",
                        "content_type": "ai_viral_video",
                        "category": "youtube_longform_source",
                        "language": "en",
                        "thumbnail": entry.get("thumbnail", ""),
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"[WARN] {ch} 수집 실패: {e}")
    return candidates


def fetch_search_queries(queries: list[str], per_query: int = 5) -> list[dict]:
    try:
        import yt_dlp
    except ImportError:
        return []

    ydl_opts = {"quiet": True, "no_warnings": True, "extract_flat": True}
    candidates = []

    for q in queries:
        search = f"ytsearch{per_query}:{q}"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search, download=False)
                if not info or "entries" not in info:
                    continue
                for entry in info["entries"]:
                    if not entry:
                        continue
                    candidates.append({
                        "id": entry.get("id"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "title": entry.get("title", ""),
                        "channel": entry.get("uploader", ""),
                        "duration": entry.get("duration") or 0,
                        "view_count": entry.get("view_count") or 0,
                        "source_platform": "youtube",
                        "content_type": "ai_viral_video",
                        "category": "youtube_longform_source",
                        "language": "en",
                        "search_query": q,
                        "collected_at": datetime.now(timezone.utc).isoformat(),
                    })
        except Exception as e:
            print(f"[WARN] 검색 '{q}' 실패: {e}")
    return candidates


def run(date_str: str = None) -> str:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    sources = load_sources()
    max_dur = sources.get("max_duration_seconds", 1800)
    min_views = sources.get("min_views_last_7d", 100000)

    channel_videos = fetch_channel_latest(sources.get("viral_channels", []))
    search_videos = fetch_search_queries(sources.get("search_queries", []))

    all_videos = channel_videos + search_videos

    # 필터: 길이 제한 + 최소 조회수
    filtered = []
    seen = set()
    for v in all_videos:
        vid = v.get("id")
        if vid in seen:
            continue
        if v.get("duration", 0) > max_dur:
            continue
        if v.get("view_count", 0) < min_views:
            continue
        seen.add(vid)
        filtered.append(v)

    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    output_path = INBOX_DIR / f"{date_str}-viral-ai-videos.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(filtered[:30], f, ensure_ascii=False, indent=2)

    print(f"[Layer1/Viral] 후보 {len(filtered[:30])}개 수집 → {output_path}")
    return str(output_path)


if __name__ == "__main__":
    run()
