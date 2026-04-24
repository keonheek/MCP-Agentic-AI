"""
Layer 4: 업로드 전략 디스패처
채널별 설정에 따라 YouTube API / Instagram Graph API / 수동 fallback 선택
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[3]
CHANNELS_CONFIG_PATH = BASE_DIR / "config" / "channels.yaml"


def load_channel_config(channel: str) -> dict:
    with open(CHANNELS_CONFIG_PATH) as f:
        return yaml.safe_load(f)["channels"][channel]


def schedule_time(hour: int, tz_offset: int = 9) -> datetime:
    """오늘 특정 시간 (KST → UTC 변환)"""
    now_kst = datetime.now()
    target_kst = now_kst.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target_kst <= now_kst:
        target_kst += timedelta(days=1)
    utc = target_kst - timedelta(hours=tz_offset)
    return utc.replace(tzinfo=timezone.utc)


def dispatch_youtube(channel: str, video_path: str, script: dict, video_id_hint: str = None) -> dict:
    from core.layer4_publishing.youtube_api import upload_short

    config = load_channel_config(channel)
    yt_config = config.get("platform", {}).get("youtube", {})

    if not yt_config.get("enabled", False):
        return {"status": "skipped", "reason": f"{channel} YouTube 비활성화 (config 확인)"}

    title = script.get("title_options", [""])[0] if script.get("title_options") else "제목 없음"
    description = script.get("youtube_description", "")
    hashtags = script.get("hashtags", [])
    tags = [t.lstrip("#") for t in hashtags]

    schedule_hour = yt_config.get("schedule_hour", 18)
    scheduled_at = schedule_time(schedule_hour)

    result = upload_short(
        video_path=video_path,
        title=title,
        description=description,
        tags=tags,
        scheduled_at=scheduled_at,
        privacy="private",  # 예약 → 자동 public
    )
    result["channel"] = channel
    result["scheduled_kst"] = scheduled_at.isoformat()
    return result


def dispatch_instagram_reel(channel: str, video_url: str, script: dict) -> dict:
    """공식 Graph API 우선, 실패 시 instagrapi 백업"""
    config = load_channel_config(channel)
    ig_config = config.get("platform", {}).get("instagram", {})

    if not ig_config.get("enabled", False):
        return {"status": "skipped", "reason": f"{channel} Instagram 비활성화"}

    caption = script.get("youtube_description", "")

    # 공식 API 시도
    from core.layer4_publishing.instagram_graph import upload_reel
    result = upload_reel(video_url=video_url, caption=caption)

    if result["status"] == "error":
        print(f"[Dispatcher] Graph API 실패 → instagrapi 백업 시도")
        from core.layer4_publishing.instagrapi_fallback import upload_reel_fallback
        result = upload_reel_fallback(video_url, caption)

    result["channel"] = channel
    return result


def manual_upload_prompt(channel: str, video_path: str, script: dict) -> dict:
    """수동 업로드 안내 (자동화 실패 시 fallback)"""
    title = script.get("title_options", [""])[0] if script.get("title_options") else "제목 없음"
    print("\n" + "=" * 50)
    print("[수동 업로드 필요]")
    print(f"채널: {channel}")
    print(f"파일: {video_path}")
    print(f"제목: {title}")
    print(f"설명:\n{script.get('youtube_description', '')}")
    print(f"해시태그: {' '.join(script.get('hashtags', []))}")
    print("=" * 50 + "\n")
    return {"status": "manual_required", "video_path": video_path, "channel": channel}


if __name__ == "__main__":
    print("[Dispatcher] 채널 설정 로드 확인:")
    for ch in ["singit", "ai", "politics"]:
        cfg = load_channel_config(ch)
        yt = cfg.get("platform", {}).get("youtube", {})
        print(f"  {ch}: enabled={yt.get('enabled')}, phase={cfg.get('phase')}")
