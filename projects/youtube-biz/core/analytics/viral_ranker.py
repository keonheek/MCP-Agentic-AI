"""
Viral video ranker.
For each competitor channel, fetches recent videos and ranks by composite score:
  velocity (views/hour) + engagement (likes + 3*comments / views)
Also extracts hook patterns from titles.
"""
import re
from datetime import datetime, timedelta, timezone


class ViralRanker:
    def __init__(self, data_client, thresholds: dict):
        self.yt = data_client
        self.thresholds = thresholds

    def rank_competitor_videos(self, competitor: dict) -> list[dict]:
        viral_window = self.thresholds.get("competitors", {}).get("viral_window_days", 30)
        top_n = self.thresholds.get("competitors", {}).get("top_n_viral", 10)
        channel_id = competitor["id"]

        cutoff = datetime.now(timezone.utc) - timedelta(days=viral_window)
        videos = self.yt.get_recent_videos(channel_id, max_results=50)

        scored = []
        for v in videos:
            pub = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
            if pub < cutoff:
                continue
            hours = max(1, (datetime.now(timezone.utc) - pub).total_seconds() / 3600)
            views = v.get("view_count", 0)
            likes = v.get("like_count", 0)
            comments = v.get("comment_count", 0)

            velocity = views / hours
            engagement = (likes + 3 * comments) / max(views, 1)
            scored.append({
                **v,
                "view_velocity_per_hour": round(velocity, 2),
                "engagement_score": round(engagement, 4),
                "hook_pattern": self._classify_hook(v.get("title", "")),
            })

        if not scored:
            return []

        # z-score normalization
        def z_scores(vals):
            if not vals:
                return vals
            mean = sum(vals) / len(vals)
            std = (sum((x - mean) ** 2 for x in vals) / len(vals)) ** 0.5
            return [(v - mean) / std if std > 0 else 0 for v in vals]

        velocities = [v["view_velocity_per_hour"] for v in scored]
        engagements = [v["engagement_score"] for v in scored]
        zv = z_scores(velocities)
        ze = z_scores(engagements)

        for i, v in enumerate(scored):
            v["composite_rank_score"] = round(zv[i] + ze[i], 3)

        scored.sort(key=lambda x: x["composite_rank_score"], reverse=True)
        return scored[:top_n]

    def _classify_hook(self, title: str) -> str:
        title_lower = title.lower()
        if re.search(r"\?|무엇|왜|어떻게|how|why|what|when|who", title_lower):
            return "question"
        if re.search(r"\d+", title):
            return "number"
        if re.search(r"충격|실화|미침|OMG|insane|shocking|crazy|wtf|대박|헐", title_lower):
            return "shock_emotion"
        if re.search(r"드디어|마침내|결국|finally|revealed|exposed", title_lower):
            return "reveal"
        return "statement"

    def extract_patterns(self, ranked_videos: list[dict]) -> dict:
        if not ranked_videos:
            return {}
        hooks = [v["hook_pattern"] for v in ranked_videos]
        hook_counts = {}
        for h in hooks:
            hook_counts[h] = hook_counts.get(h, 0) + 1
        dominant_hook = max(hook_counts, key=hook_counts.get)

        durations = []
        for v in ranked_videos:
            dur = v.get("duration", "")
            if dur:
                # ISO 8601 duration PT1M30S -> seconds
                match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur)
                if match:
                    h, m, s = match.groups(default="0")
                    durations.append(int(h) * 3600 + int(m) * 60 + int(s))

        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "dominant_hook_pattern": dominant_hook,
            "hook_distribution": hook_counts,
            "avg_video_duration_seconds": round(avg_duration),
            "top_titles": [v["title"] for v in ranked_videos[:5]],
        }
