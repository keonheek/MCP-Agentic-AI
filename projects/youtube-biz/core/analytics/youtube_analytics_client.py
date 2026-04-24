"""
YouTube Analytics API v2 client.
Accesses owner-only metrics: retention curve, RPM, CPM, watch time, revenue.
Requires yt-analytics.readonly + yt-analytics-monetary.readonly scopes.
"""
from datetime import date, timedelta
from .youtube_data_client import _get_credentials


class YouTubeAnalyticsClient:
    def __init__(self):
        from googleapiclient.discovery import build
        creds = _get_credentials()
        self.service = build("youtubeAnalytics", "v2", credentials=creds)

    def _query(self, channel_id: str, metrics: str, dimensions: str = "",
               start_days_ago: int = 30, filters: str = "") -> dict:
        end = date.today()
        start = end - timedelta(days=start_days_ago)
        params = {
            "ids": f"channel=={channel_id}",
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "metrics": metrics,
        }
        if dimensions:
            params["dimensions"] = dimensions
        if filters:
            params["filters"] = filters
        return self.service.reports().query(**params).execute()

    def get_channel_kpis(self, channel_id: str, days: int = 30) -> dict:
        resp = self._query(
            channel_id=channel_id,
            metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,"
                    "subscribersGained,subscribersLost,estimatedRevenue,cpm,playbackBasedCpm",
            start_days_ago=days,
        )
        rows = resp.get("rows", [])
        if not rows:
            return {}
        row = rows[0]
        headers = [h["name"] for h in resp.get("columnHeaders", [])]
        data = dict(zip(headers, row))
        return {
            "views": int(data.get("views", 0)),
            "watch_time_minutes": float(data.get("estimatedMinutesWatched", 0)),
            "avg_view_duration_seconds": float(data.get("averageViewDuration", 0)),
            "avg_view_percentage": float(data.get("averageViewPercentage", 0)),
            "subscribers_gained": int(data.get("subscribersGained", 0)),
            "subscribers_lost": int(data.get("subscribersLost", 0)),
            "estimated_revenue_usd": float(data.get("estimatedRevenue", 0)),
            "cpm": float(data.get("cpm", 0)),
            "playback_based_cpm": float(data.get("playbackBasedCpm", 0)),
            "period_days": days,
        }

    def get_video_retention(self, channel_id: str, video_id: str) -> list[dict]:
        """Returns retention curve as list of {elapsed_ratio, retained_pct} per video."""
        resp = self._query(
            channel_id=channel_id,
            metrics="audienceWatchRatio,relativeRetentionPerformance",
            dimensions="elapsedVideoTimeRatio",
            filters=f"video=={video_id}",
            start_days_ago=90,
        )
        rows = resp.get("rows", [])
        curve = []
        for row in rows:
            curve.append({
                "elapsed_ratio": float(row[0]),
                "retained_pct": float(row[1]) * 100,
                "relative_retention": float(row[2]) if len(row) > 2 else None,
            })
        return sorted(curve, key=lambda x: x["elapsed_ratio"])

    def get_traffic_sources(self, channel_id: str, days: int = 30) -> list[dict]:
        resp = self._query(
            channel_id=channel_id,
            metrics="views,estimatedMinutesWatched",
            dimensions="insightTrafficSourceType",
            start_days_ago=days,
        )
        rows = resp.get("rows", [])
        return [{"source": r[0], "views": int(r[1]), "watch_minutes": float(r[2])} for r in rows]
