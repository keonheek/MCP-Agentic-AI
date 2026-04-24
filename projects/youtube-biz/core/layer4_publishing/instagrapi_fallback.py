"""
Layer 4: Instagrapi 비공식 백업
공식 Graph API 실패 시에만 사용. 계정 ban 리스크 있음.
별도 서브 계정으로 먼저 테스트 권장.
"""
import json
import os
from pathlib import Path


def get_client():
    """Instagrapi 클라이언트 초기화"""
    try:
        from instagrapi import Client
    except ImportError:
        raise RuntimeError(
            "instagrapi 미설치.\n"
            "pip install instagrapi\n"
            "주의: 비공식 API — 계정 ban 리스크 있음."
        )

    client = Client()
    username = os.getenv("INSTAGRAM_USERNAME", "")
    password = os.getenv("INSTAGRAM_PASSWORD", "")

    if not username or not password:
        raise ValueError("INSTAGRAM_USERNAME / INSTAGRAM_PASSWORD 환경변수 미설정")

    session_path = Path(f".ig_session_{username}.json")
    if session_path.exists():
        client.load_settings(str(session_path))
        client.login(username, password)
    else:
        client.login(username, password)
        client.dump_settings(str(session_path))

    return client


def upload_reel_fallback(video_path: str, caption: str) -> dict:
    """Instagrapi로 Reels 업로드 (로컬 파일 직접 업로드)"""
    try:
        client = get_client()
        media = client.clip_upload(video_path, caption=caption[:2200])
        return {
            "status": "ok",
            "media_id": str(media.pk),
            "url": f"https://www.instagram.com/reel/{media.code}/",
            "method": "instagrapi",
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "method": "instagrapi"}


def upload_story_fallback(video_path: str) -> dict:
    """Instagrapi로 Story 영상 업로드"""
    try:
        client = get_client()
        media = client.video_upload_to_story(video_path)
        return {"status": "ok", "media_id": str(media.pk), "method": "instagrapi"}
    except Exception as e:
        return {"status": "error", "error": str(e), "method": "instagrapi"}


if __name__ == "__main__":
    print("[Instagrapi] 백업 경로. 공식 API 먼저 시도 권장.")
