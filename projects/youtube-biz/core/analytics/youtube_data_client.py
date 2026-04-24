"""
YouTube Data API v3 client.
Handles channel info, video lists, search. No analytics/revenue data (see youtube_analytics_client).
Reuses OAuth pattern from core/layer4_publishing/youtube_api.py.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
# Token may live at youtube-biz root or one level up (projects/)
_token_candidates = [BASE_DIR / ".youtube_token.json", BASE_DIR.parent / ".youtube_token.json"]
TOKEN_PATH = next((p for p in _token_candidates if p.exists()), BASE_DIR / ".youtube_token.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
]


def _get_credentials():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
    except ImportError:
        raise RuntimeError(
            "Google API libraries not installed.\n"
            "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        )

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
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
            if not client_config["installed"]["client_id"]:
                raise RuntimeError(
                    "YOUTUBE_CLIENT_ID not set in .env.\n"
                    "Follow setup steps to create OAuth credentials in Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    return creds


class YouTubeDataClient:
    def __init__(self):
        from googleapiclient.discovery import build
        creds = _get_credentials()
        self.service = build("youtube", "v3", credentials=creds)

    def get_channel_info(self, channel_id: str) -> dict:
        resp = self.service.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id,
        ).execute()
        items = resp.get("items", [])
        if not items:
            return {}
        item = items[0]
        return {
            "id": channel_id,
            "title": item["snippet"]["title"],
            "description": item["snippet"].get("description", ""),
            "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
            "video_count": int(item["statistics"].get("videoCount", 0)),
            "view_count": int(item["statistics"].get("viewCount", 0)),
            "uploads_playlist_id": item["contentDetails"]["relatedPlaylists"]["uploads"],
        }

    def get_recent_videos(self, channel_id: str, max_results: int = 50) -> list[dict]:
        channel = self.get_channel_info(channel_id)
        playlist_id = channel.get("uploads_playlist_id")
        if not playlist_id:
            return []

        videos = []
        next_page = None
        while len(videos) < max_results:
            resp = self.service.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page,
            ).execute()
            for item in resp.get("items", []):
                videos.append({
                    "video_id": item["contentDetails"]["videoId"],
                    "title": item["snippet"]["title"],
                    "published_at": item["snippet"]["publishedAt"],
                })
            next_page = resp.get("nextPageToken")
            if not next_page:
                break

        if not videos:
            return []

        video_ids = [v["video_id"] for v in videos]
        stats_resp = self.service.videos().list(
            part="statistics,contentDetails,snippet",
            id=",".join(video_ids),
        ).execute()

        stats_map = {}
        for item in stats_resp.get("items", []):
            vid = item["id"]
            stats_map[vid] = {
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "like_count": int(item["statistics"].get("likeCount", 0)),
                "comment_count": int(item["statistics"].get("commentCount", 0)),
                "duration": item["contentDetails"].get("duration", ""),
                "tags": item["snippet"].get("tags", []),
                "thumbnail_url": item["snippet"].get("thumbnails", {}).get("high", {}).get("url", ""),
            }

        for v in videos:
            v.update(stats_map.get(v["video_id"], {}))

        return videos

    def search_channels(self, keyword: str, max_results: int = 50) -> list[dict]:
        resp = self.service.search().list(
            part="snippet",
            q=keyword,
            type="channel",
            maxResults=max_results,
            relevanceLanguage="ko",
        ).execute()
        results = []
        for item in resp.get("items", []):
            results.append({
                "channel_id": item["snippet"]["channelId"],
                "title": item["snippet"]["channelTitle"],
                "description": item["snippet"].get("description", ""),
            })
        return results
