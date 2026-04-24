"""
CLI entry point for youtube-analyst agent.

Usage:
  python scripts/run_youtube_analysis.py --channel=UCalLyZ2lZVPlnfoTxYzpl8w --competitors=auto
  python scripts/run_youtube_analysis.py --channel=UCalLyZ2lZVPlnfoTxYzpl8w --competitors=auto --dry-run
  python scripts/run_youtube_analysis.py --competitors-only   # skip own channel analytics
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))  # youtube-biz root so `core` is importable

import yaml


def load_config():
    competitors_path = BASE_DIR / "config" / "competitors.yaml"
    thresholds_path = BASE_DIR / "config" / "thresholds.yaml"
    with open(competitors_path, encoding="utf-8") as f:
        competitors_cfg = yaml.safe_load(f)
    with open(thresholds_path, encoding="utf-8") as f:
        thresholds_cfg = yaml.safe_load(f)
    return competitors_cfg, thresholds_cfg


def config_staleness_days(path: Path) -> int:
    mtime = path.stat().st_mtime
    age = (datetime.now(timezone.utc).timestamp() - mtime) / 86400
    return int(age)


def main():
    parser = argparse.ArgumentParser(description="YouTube Channel Analyst")
    parser.add_argument("--channel", default=None, help="Channel ID to analyze (overrides competitors.yaml)")
    parser.add_argument("--competitors", default="auto", choices=["auto", "skip"], help="Competitor discovery mode")
    parser.add_argument("--competitors-only", action="store_true", help="Skip own channel analytics")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen without calling APIs")
    parser.add_argument("--force-refresh", action="store_true", help="Bypass competitor cache")
    parser.add_argument("--days", type=int, default=30, help="Analytics lookback period in days")
    args = parser.parse_args()

    from dotenv import load_dotenv
    # load project-level .env first, then repo root as fallback
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(BASE_DIR.parent.parent / ".env")

    competitors_cfg, thresholds_cfg = load_config()
    channel_id = args.channel or competitors_cfg["my_channel"]["id"]
    channel_name = competitors_cfg["my_channel"]["name"]

    if args.dry_run:
        print(f"[DRY RUN] Would analyze channel: {channel_id} ({channel_name})")
        print(f"[DRY RUN] Competitor mode: {args.competitors}")
        print(f"[DRY RUN] Lookback: {args.days} days")
        print(f"[DRY RUN] Thresholds: cliff={thresholds_cfg['retention']['cliff_drop_pct']}%, "
              f"hook_window={thresholds_cfg['retention']['hook_window_seconds']}s")
        print("[DRY RUN] Config files: OK")
        return

    # lazy imports after dry-run check
    from core.analytics import (
        YouTubeDataClient, YouTubeAnalyticsClient,
        CompetitorScout, ViralRanker, RetentionCliffDetector,
        build_report, SelfCritique,
    )

    print(f"[youtube-analyst] Initializing API clients...")
    data_client = YouTubeDataClient()
    analytics_client = YouTubeAnalyticsClient()
    scout = CompetitorScout(data_client, competitors_cfg, thresholds_cfg)
    ranker = ViralRanker(data_client, thresholds_cfg)
    cliff_detector = RetentionCliffDetector(thresholds_cfg)
    critique = SelfCritique(thresholds_cfg)

    report_data = {
        "channel_niche": competitors_cfg["my_channel"].get("niche", ""),
        "config_modified_days_ago": config_staleness_days(BASE_DIR / "config" / "thresholds.yaml"),
        "competitor_cache_age_days": 0,
    }

    # own channel analytics
    if not args.competitors_only:
        print(f"[youtube-analyst] Fetching channel KPIs for {channel_id}...")
        kpis = analytics_client.get_channel_kpis(channel_id, days=args.days)
        if not kpis:
            print("[youtube-analyst] WARNING: No analytics data returned. Channel may have insufficient data.")
        report_data["channel_kpis"] = kpis

        # retention for most recent video
        print("[youtube-analyst] Fetching recent videos for retention analysis...")
        recent_videos = data_client.get_recent_videos(channel_id, max_results=5)
        retention_result = {}
        edit_suggestions = []
        if recent_videos:
            latest = recent_videos[0]
            print(f"[youtube-analyst] Analyzing retention for: {latest['title']}")
            curve = analytics_client.get_video_retention(channel_id, latest["video_id"])
            import re
            dur_str = latest.get("duration", "PT60S")
            match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur_str)
            if match:
                h, m, s = match.groups(default="0")
                duration_sec = int(h) * 3600 + int(m) * 60 + int(s)
            else:
                duration_sec = 60
            retention_result = cliff_detector.detect(curve, duration_sec)
            edit_suggestions = cliff_detector.generate_edit_suggestions(retention_result, duration_sec)
        else:
            print("[youtube-analyst] No videos found. Competitor-only mode.")
        report_data["retention_analysis"] = retention_result
        report_data["edit_suggestions"] = edit_suggestions

    # competitor discovery
    all_competitor_patterns = {}
    enriched_competitors = []
    if args.competitors == "auto":
        print("[youtube-analyst] Discovering competitors...")
        competitors = scout.discover(force_refresh=args.force_refresh)

        cache_path = BASE_DIR / "data"
        cache_files = sorted(cache_path.glob("competitors_*.json"), reverse=True)
        if cache_files:
            cache_age = config_staleness_days(cache_files[0])
            report_data["competitor_cache_age_days"] = cache_age

        print(f"[youtube-analyst] Ranking viral videos for {len(competitors)} competitors...")
        all_patterns = []
        for comp in competitors:
            viral = ranker.rank_competitor_videos(comp)
            patterns = ranker.extract_patterns(viral)
            all_patterns.append(patterns)
            enriched_competitors.append({**comp, "viral_videos": viral})

        # merge patterns across competitors
        if all_patterns:
            hook_totals = {}
            for p in all_patterns:
                for hook, count in p.get("hook_distribution", {}).items():
                    hook_totals[hook] = hook_totals.get(hook, 0) + count
            dominant = max(hook_totals, key=hook_totals.get) if hook_totals else "unknown"
            avg_dur = sum(p.get("avg_video_duration_seconds", 0) for p in all_patterns) / len(all_patterns)
            top_titles = [t for p in all_patterns for t in p.get("top_titles", [])[:2]]
            all_competitor_patterns = {
                "dominant_hook_pattern": dominant,
                "hook_distribution": hook_totals,
                "avg_video_duration_seconds": round(avg_dur),
                "top_titles": top_titles[:10],
            }

    report_data["competitors"] = enriched_competitors
    report_data["competitor_patterns"] = all_competitor_patterns

    # self-critique loop
    pass_status = "partial"
    for iteration in range(1, critique.max_iterations + 1):
        scores = critique.score(report_data)
        print(f"[youtube-analyst] Self-critique iteration {iteration}/{critique.max_iterations}: "
              f"integrity={scores['data_integrity']:.1f} specificity={scores['specificity']:.1f} "
              f"actionability={scores['actionability']:.1f} relevance={scores['competitive_relevance']:.1f}")

        if scores["passed"]:
            pass_status = "pass"
            break

        # patch weak dimensions
        if scores["specificity"] < critique.pass_score or scores["actionability"] < critique.pass_score:
            if not report_data.get("edit_suggestions"):
                report_data["edit_suggestions"] = [
                    "No retention curve data available yet. Upload more videos to enable cliff detection.",
                    "Focus on first 3 seconds: show the most surprising moment immediately.",
                    "Add text overlay at 15s mark to re-engage viewers who made it past the hook.",
                ]

    report_path = build_report(report_data, channel_name, status=pass_status)

    # log critique JSON
    critique.log(iteration, scores, report_path)
    print(f"[youtube-analyst] Done. Report: {report_path}")
    print(f"[youtube-analyst] Self-critique: {pass_status.upper()}")

    result = {
        "report_path": report_path,
        "critique_status": pass_status,
        "scores": {k: v for k, v in scores.items() if isinstance(v, (int, float))},
        "channel_kpis": report_data.get("channel_kpis", {}),
        "competitor_count": len(enriched_competitors),
    }
    print("\n[OUTPUT JSON]")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == "__main__":
    main()
