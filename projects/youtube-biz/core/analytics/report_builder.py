"""
Builds the final research/*.md report from structured analysis data.
"""
from datetime import date
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parents[4] / "research"
RESEARCH_DIR.mkdir(exist_ok=True)


def build_report(data: dict, channel_name: str, status: str = "pass") -> str:
    today = date.today().isoformat()
    slug = channel_name.lower().replace(" ", "-")
    path = RESEARCH_DIR / f"{today}-youtube-{slug}.md"

    kpis = data.get("channel_kpis", {})
    competitors = data.get("competitors", [])
    retention = data.get("retention_analysis", {})
    suggestions = data.get("edit_suggestions", [])
    competitor_patterns = data.get("competitor_patterns", {})

    warn_banner = ""
    if status == "partial":
        warn_banner = "> [!WARNING] Self-critique score below threshold after 2 iterations. Review critique JSON for details.\n\n"

    # staleness info
    config_modified = data.get("config_modified_days_ago", "unknown")
    competitor_cache_age = data.get("competitor_cache_age_days", "unknown")

    lines = [
        f"# YouTube Analysis Report — {channel_name}",
        f"_Generated: {today}_",
        "",
        warn_banner,
        "## Data Freshness",
        f"- `thresholds.yaml` last modified: {config_modified} days ago",
        f"- Competitor cache age: {competitor_cache_age} days",
        "",
        "---",
        "",
        "## Channel KPIs",
        f"_Last {kpis.get('period_days', 30)} days_",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Views | {kpis.get('views', 'N/A'):,} |",
        f"| Watch Time | {kpis.get('watch_time_minutes', 0):,.0f} min |",
        f"| Avg View Duration | {kpis.get('avg_view_duration_seconds', 0):.0f}s |",
        f"| Avg View % | {kpis.get('avg_view_percentage', 0):.1f}% |",
        f"| Subs Gained | {kpis.get('subscribers_gained', 'N/A')} |",
        f"| Est. Revenue | ${kpis.get('estimated_revenue_usd', 0):.2f} |",
        f"| CPM | ${kpis.get('cpm', 0):.2f} |",
        f"| Playback CPM | ${kpis.get('playback_based_cpm', 0):.2f} |",
        "",
        "---",
        "",
        "## Retention Analysis",
    ]

    cliffs = retention.get("cliffs", [])
    hook_drop = retention.get("hook_drop_pct")
    hook_alert = retention.get("hook_alert", False)

    if hook_drop is not None:
        alert_label = " ALERT" if hook_alert else ""
        lines.append(f"- **Hook zone drop:** {hook_drop:.1f}%{alert_label}")
    if cliffs:
        lines.append(f"- **Retention cliffs detected:** {len(cliffs)}")
        for c in cliffs[:3]:
            lines.append(f"  - {c['elapsed_seconds']}s: -{c['drop_pct']:.1f}% ({c['severity']})")
    else:
        lines.append("- No significant retention cliffs detected.")

    lines += [
        "",
        "---",
        "",
        "## Actionable Edit Suggestions",
    ]
    for i, s in enumerate(suggestions, 1):
        lines.append(f"{i}. {s}")

    lines += [
        "",
        "---",
        "",
        "## Competitor Analysis",
        f"_Auto-discovered {len(competitors)} competitors_",
        "",
    ]
    for comp in competitors:
        lines.append(f"### {comp.get('title', 'Unknown')}")
        lines.append(f"- Subscribers: {comp.get('subscriber_count', 0):,}")
        lines.append(f"- Avg view velocity: {comp.get('avg_view_velocity', 0):.1f} views/hr")
        viral = comp.get("viral_videos", [])
        if viral:
            lines.append(f"- Top viral video: **{viral[0].get('title', '')}** ({viral[0].get('view_count', 0):,} views)")
        lines.append("")

    if competitor_patterns:
        lines += [
            "## Competitor Patterns",
            f"- Dominant hook type: **{competitor_patterns.get('dominant_hook_pattern', 'N/A')}**",
            f"- Avg video length: {competitor_patterns.get('avg_video_duration_seconds', 0):.0f}s",
            "- Top titles:",
        ]
        for t in competitor_patterns.get("top_titles", [])[:5]:
            lines.append(f"  - {t}")

    lines += [
        "",
        "---",
        "",
        f"_Self-critique status: {status.upper()}_",
    ]

    content = "\n".join(lines)
    path.write_text(content, encoding="utf-8")
    print(f"[ReportBuilder] Saved: {path}")
    return str(path)
