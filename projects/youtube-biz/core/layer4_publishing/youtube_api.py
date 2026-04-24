"""
Layer 4: YouTube Data API v3 업로드
OAuth2 인증 + Shorts 업로드 + 스케줄 예약
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
TOKEN_PATH = BASE_DIR / ".youtube_token.json"


def get_youtube_service():
    """YouTube API 서비스 객체 반환 (OAuth2)"""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "Google API 라이브러리 미설치.\n"
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), scopes)

    if not creds or not creds.valid:
        from google.auth.transport.requests import Request
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
                    "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
                    "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://accounts.google.com/o/oauth2/token",
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, scopes)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_short(
    video_path: str,
    title: str,
    description: str,
    tags: list[str] = None,
    scheduled_at: datetime = None,
    privacy: str = "public",
) -> dict:
    """
    YouTube Shorts 업로드
    Returns: {"status": "ok", "video_id": str, "url": str} or {"status": "error", "error": str}
    """
    try:
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        return {"status": "error", "error": "google-api-python-client 미설치"}

    try:
        youtube = get_youtube_service()
    except Exception as e:
        return {"status": "error", "error": f"YouTube 인증 실패: {e}"}

    # 스케줄 예약
    publish_at = None
    actual_privacy = privacy
    if scheduled_at:
        actual_privacy = "private"
        publish_at = scheduled_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": (tags or [])[:500],
            "categoryId": "10",  # Music
        },
        "status": {
            "privacyStatus": actual_privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    if publish_at:
        body["status"]["publishAt"] = publish_at

    try:
        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"  업로드 진행: {pct}%")

        video_id = response.get("id")
        print(f"[Layer4] 업로드 완료: https://youtu.be/{video_id}")
        return {
            "status": "ok",
            "video_id": video_id,
            "url": f"https://youtu.be/{video_id}",
            "scheduled_at": publish_at,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python youtube_api.py <video_path> <title>")
        sys.exit(1)
    result = upload_short(sys.argv[1], sys.argv[2], "테스트 업로드")
    print(json.dumps(result, ensure_ascii=False))
