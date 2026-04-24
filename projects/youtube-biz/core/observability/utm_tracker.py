"""
Observability: Sing It UTM 리퍼럴 추적
YouTube Analytics API로 설명란 링크 클릭 수 수집
"""
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
LOGS_DIR = BASE_DIR / "logs"


def get_video_analytics(video_id: str, start_date: str = None, end_date: str = None) -> dict:
    """
    YouTube Analytics API로 영상별 카드/링크 클릭 수 수집
    """
    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
    except ImportError:
        return {"error": "google-api-python-client 미설치"}

    token_path = BASE_DIR / ".youtube_token.json"
    if not token_path.exists():
        return {"error": "YouTube 인증 토큰 없음. youtube_api.py 먼저 실행 필요."}

    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-01")
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    try:
        creds = Credentials.from_authorized_user_file(str(token_path))
        analytics = build("youtubeAnalytics", "v2", credentials=creds)

        response = analytics.reports().query(
            ids="channel==MINE",
            startDate=start_date,
            endDate=end_date,
            metrics="views,likes,comments,shares",
            dimensions="video",
            filters=f"video=={video_id}",
        ).execute()

        rows = response.get("rows", [])
        if not rows:
            return {"video_id": video_id, "views": 0, "likes": 0}

        row = rows[0]
        return {
            "video_id": video_id,
            "views": row[1] if len(row) > 1 else 0,
            "likes": row[2] if len(row) > 2 else 0,
            "comments": row[3] if len(row) > 3 else 0,
            "shares": row[4] if len(row) > 4 else 0,
        }
    except Exception as e:
        return {"error": str(e), "video_id": video_id}


def collect_utm_summary(video_ids: list[str], date_str: str = None) -> dict:
    """
    여러 영상의 분석 데이터 수집 + 집계
    실제 Sing It 앱 전환 데이터는 Sing It 측 대시보드에서 별도 확인 필요
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    results = []
    for vid in video_ids:
        data = get_video_analytics(vid)
        results.append(data)

    summary = {
        "date": date_str,
        "videos": results,
        "totals": {
            "views": sum(r.get("views", 0) for r in results),
            "likes": sum(r.get("likes", 0) for r in results),
            "shares": sum(r.get("shares", 0) for r in results),
        },
        "collected_at": datetime.now().isoformat(),
    }

    output_path = LOGS_DIR / f"{date_str}-utm-summary.json"
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[UTM] 집계 완료: 총 {summary['totals']['views']:,}뷰 | 저장: {output_path}")
    return summary


if __name__ == "__main__":
    print("[UTM Tracker] 테스트: video_id 없이 실행하면 빈 결과")
    print(collect_utm_summary([]))
