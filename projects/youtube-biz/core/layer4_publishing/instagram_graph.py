"""
Layer 4: Instagram Graph API (공식)
Stories + Reels 업로드 (Phase 2에서 활성화)
Meta Business Account 필요
"""
import json
import os
import time
from pathlib import Path


IG_BASE = "https://graph.facebook.com/v21.0"


def _get(endpoint: str, params: dict) -> dict:
    try:
        import httpx
    except ImportError:
        raise RuntimeError("pip install httpx 필요")
    params["access_token"] = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    resp = httpx.get(f"{IG_BASE}/{endpoint}", params=params, timeout=30)
    return resp.json()


def _post(endpoint: str, data: dict) -> dict:
    try:
        import httpx
    except ImportError:
        raise RuntimeError("pip install httpx 필요")
    data["access_token"] = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    resp = httpx.post(f"{IG_BASE}/{endpoint}", data=data, timeout=60)
    return resp.json()


def upload_reel(
    video_url: str,
    caption: str,
    account_id: str = None,
    cover_url: str = None,
) -> dict:
    """
    Instagram Reels 업로드 (2단계: container 생성 → publish)
    video_url: 공개 접근 가능한 MP4 URL (S3, CDN 등)
    """
    if account_id is None:
        account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    # Step 1: container 생성
    container_data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption[:2200],
    }
    if cover_url:
        container_data["thumb_offset"] = "0"

    container_resp = _post(f"{account_id}/media", container_data)
    container_id = container_resp.get("id")

    if not container_id:
        return {"status": "error", "error": f"Container 생성 실패: {container_resp}"}

    # Step 2: 처리 완료 대기 (최대 3분)
    for _ in range(18):
        status_resp = _get(f"{container_id}", {"fields": "status_code,status"})
        status_code = status_resp.get("status_code")
        if status_code == "FINISHED":
            break
        if status_code in ("ERROR", "EXPIRED"):
            return {"status": "error", "error": f"Container 처리 실패: {status_resp}"}
        time.sleep(10)

    # Step 3: publish
    publish_resp = _post(f"{account_id}/media_publish", {"creation_id": container_id})
    media_id = publish_resp.get("id")

    if not media_id:
        return {"status": "error", "error": f"Publish 실패: {publish_resp}"}

    return {
        "status": "ok",
        "media_id": media_id,
        "url": f"https://www.instagram.com/p/{media_id}/",
    }


def upload_story_image(image_url: str, account_id: str = None) -> dict:
    """Instagram Stories 이미지 업로드"""
    if account_id is None:
        account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    container_resp = _post(f"{account_id}/media", {
        "media_type": "STORIES",
        "image_url": image_url,
    })
    container_id = container_resp.get("id")
    if not container_id:
        return {"status": "error", "error": str(container_resp)}

    publish_resp = _post(f"{account_id}/media_publish", {"creation_id": container_id})
    media_id = publish_resp.get("id")
    if not media_id:
        return {"status": "error", "error": str(publish_resp)}

    return {"status": "ok", "media_id": media_id}


if __name__ == "__main__":
    print("[IG Graph API] Phase 2에서 활성화됩니다.")
    print(f"Account ID: {os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '(미설정)')}")
