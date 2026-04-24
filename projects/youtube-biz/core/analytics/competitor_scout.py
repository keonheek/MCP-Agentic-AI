"""
Competitor auto-discovery.
Reads seed keywords from competitors.yaml, queries YouTube Data API,
filters by subscriber range + upload cadence, ranks by view velocity.
Results cached weekly to conserve API quota.
"""
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
CACHE_DIR = BASE_DIR / "data"
CACHE_DIR.mkdir(exist_ok=True)


class CompetitorScout:
    def __init__(self, data_client, config: dict, thresholds: dict):
        self.yt = data_client
        self.cfg = config  # competitors.yaml my_channel + competitor_filters
        self.thresholds = thresholds

    def _cache_path(self) -> Path:
        week = date.today().isocalendar()
        return CACHE_DIR / f"competitors_{week.year}_w{week.week:02d}.json"

    def _is_cache_valid(self) -> bool:
        path = self._cache_path()
        if not path.exists():
            return False
        ttl_days = self.cfg.get("competitor_filters", {}).get("cache_ttl_days", 7)
        age = datetime.now(timezone.utc) - datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        return age < timedelta(days=ttl_days)

    def _load_cache(self) -> list[dict]:
        text = self._cache_path().read_text(encoding="utf-8").strip()
        if not text:
            return []
        return json.loads(text)

    def _save_cache(self, data: list[dict]):
        self._cache_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def discover(self, force_refresh: bool = False) -> list[dict]:
        if not force_refresh and self._is_cache_valid():
            print("[CompetitorScout] Using cached competitor list.")
            return self._load_cache()

        filters = self.cfg.get("competitor_filters", {})
        min_subs = filters.get("min_subscribers", 10000)
        max_subs = filters.get("max_subscribers", 1000000)
        min_uploads = filters.get("min_uploads_last_90_days", 3)
        top_n = self.thresholds.get("competitors", {}).get("top_n_competitors", 5)
        my_channel_id = self.cfg["my_channel"]["id"]

        candidates: dict[str, dict] = {}
        for keyword in self.cfg.get("seed_keywords", []):
            print(f"[CompetitorScout] Searching: {keyword}")
            channels = self.yt.search_channels(keyword, max_results=10)
            for ch in channels:
                cid = ch["channel_id"]
                if cid == my_channel_id or cid in candidates:
                    continue
                candidates[cid] = ch

        scored = []
        for cid, ch in candidates.items():
            info = self.yt.get_channel_info(cid)
            if not info:
                continue
            subs = info.get("subscriber_count", 0)
            if not (min_subs <= subs <= max_subs):
                continue

            # check upload cadence via recent videos
            recent = self.yt.get_recent_videos(cid, max_results=10)
            cutoff = datetime.now(timezone.utc) - timedelta(days=90)
            recent_count = sum(
                1 for v in recent
                if datetime.fromisoformat(v["published_at"].replace("Z", "+00:00")) > cutoff
            )
            if recent_count < min_uploads:
                continue

            # view velocity = avg views / avg hours since upload for recent videos
            velocities = []
            for v in recent[:5]:
                pub = datetime.fromisoformat(v["published_at"].replace("Z", "+00:00"))
                hours = max(1, (datetime.now(timezone.utc) - pub).total_seconds() / 3600)
                velocities.append(v.get("view_count", 0) / hours)

            scored.append({
                **info,
                "recent_uploads_90d": recent_count,
                "avg_view_velocity": sum(velocities) / len(velocities) if velocities else 0,
                "recent_videos": recent[:5],
            })

        scored.sort(key=lambda x: x["avg_view_velocity"], reverse=True)
        result = scored[:top_n]
        self._save_cache(result)
        print(f"[CompetitorScout] Found {len(result)} competitors.")
        return result
