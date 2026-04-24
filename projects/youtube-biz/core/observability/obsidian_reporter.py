"""
Observability: Obsidian daily note에 KPI 요약 자동 append
기존 mcp__obsidian__append_to_note 패턴 재사용
"""
import json
import os
from datetime import datetime
from pathlib import Path

VAULT_PATH = Path(os.getenv("OBSIDIAN_VAULT_PATH", r"C:\Users\keonh\Claude_obs"))
DAILY_NOTES_DIR = VAULT_PATH / "Daily Notes"


def format_kpi_section(summary: dict) -> str:
    date = summary.get("date", datetime.now().strftime("%Y-%m-%d"))
    totals = summary.get("totals", {})
    videos = summary.get("videos", [])

    lines = [
        f"\n## YouTube Biz KPI ({date})",
        f"- 총 뷰: {totals.get('views', 0):,}",
        f"- 좋아요: {totals.get('likes', 0):,}",
        f"- 공유: {totals.get('shares', 0):,}",
    ]

    if videos:
        lines.append("\n### 영상별 실적")
        for v in videos:
            vid = v.get("video_id", "?")
            views = v.get("views", 0)
            if isinstance(views, (int, float)):
                lines.append(f"- [{vid}](https://youtu.be/{vid}): {views:,}뷰")

    lines.append("")
    return "\n".join(lines)


def append_to_daily_note(content: str, date_str: str = None) -> bool:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    note_path = DAILY_NOTES_DIR / f"{date_str}.md"

    try:
        DAILY_NOTES_DIR.mkdir(parents=True, exist_ok=True)
        with open(note_path, "a", encoding="utf-8") as f:
            f.write(content)
        print(f"[Reporter] Obsidian daily note 업데이트: {note_path}")
        return True
    except Exception as e:
        print(f"[WARN] Obsidian 업데이트 실패: {e}")
        return False


def run_daily_report(utm_summary_path: str = None, date_str: str = None) -> bool:
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    logs_dir = Path(__file__).resolve().parents[3] / "logs"
    if utm_summary_path is None:
        utm_summary_path = str(logs_dir / f"{date_str}-utm-summary.json")

    try:
        with open(utm_summary_path, encoding="utf-8") as f:
            summary = json.load(f)
    except FileNotFoundError:
        summary = {"date": date_str, "totals": {}, "videos": []}
    except Exception as e:
        print(f"[WARN] UTM 요약 파일 읽기 실패: {e}")
        summary = {"date": date_str, "totals": {}, "videos": []}

    content = format_kpi_section(summary)
    return append_to_daily_note(content, date_str)


if __name__ == "__main__":
    success = run_daily_report()
    print("성공" if success else "실패")
