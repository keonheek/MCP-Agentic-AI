"""
Loop 6 — Self-Healing GEO Score Monitor
Reads crm/clients.json → runs GEO audit for each client → compares to last score →
flags drops > ALERT_THRESHOLD → saves reports/YYYY-MM-DD-health.md

Designed to run daily via CronCreate or `python loop6_geo_monitor.py`.

Usage:
    python loop6_geo_monitor.py
    python loop6_geo_monitor.py --alert-threshold 8

Requires:
    ANTHROPIC_API_KEY + PERPLEXITY_API_KEY in root .env
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import date, datetime

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

for _p in [HERE / ".env", ROOT / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

sys.path.insert(0, str(ROOT / "projects" / "lead-intelligence"))
from geo_audit import audit_single_company

CLIENTS_FILE = HERE / "crm" / "clients.json"
LOG_FILE = HERE / "reports" / "monitor_log.json"
ALERT_THRESHOLD = 8  # points drop triggers alert

DEMO_CLIENTS = [
    {
        "name": "데모 클라이언트",
        "url": "https://example.com",
        "tier": "demo",
        "contact": "N/A",
        "note": "Replace with real client URLs"
    }
]


def load_clients() -> list[dict]:
    if not CLIENTS_FILE.exists():
        CLIENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        CLIENTS_FILE.write_text(
            json.dumps(DEMO_CLIENTS, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"[Loop 6] Created demo clients file: {CLIENTS_FILE}")
        print("         Edit crm/clients.json to add real clients, then re-run.")
    return json.loads(CLIENTS_FILE.read_text(encoding="utf-8"))


def load_log() -> dict:
    if LOG_FILE.exists():
        return json.loads(LOG_FILE.read_text(encoding="utf-8"))
    return {}


def save_log(log: dict):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def run(alert_threshold: int = ALERT_THRESHOLD):
    today = str(date.today())
    clients = load_clients()
    log = load_log()

    print(f"[Loop 6] GEO Health Check — {today}")
    print(f"         {len(clients)} client(s) | alert threshold: -{alert_threshold} pts\n")

    report_lines = [
        f"# GEO 건강 리포트 — {today}\n",
        f"총 {len(clients)}개 클라이언트 | 알림 기준: -{alert_threshold}점 이상 하락\n",
        "---\n",
    ]

    alerts = []
    results = []

    for c in clients:
        url = c.get("url", "")
        name = c.get("name", url)
        tier = c.get("tier", "unknown")

        print(f"  Checking {name} ({url})...")

        try:
            audit = audit_single_company(url)
            score = audit.get("overall_score", 0)
            dims = audit.get("dimensions", {})

            # Compare to previous score
            prev = log.get(url, {})
            prev_score = prev.get("last_score")
            delta = (score - prev_score) if prev_score is not None else None
            delta_str = f"{'+' if delta >= 0 else ''}{delta}" if delta is not None else "첫 측정"

            # Update log entry
            log[url] = {
                "name": name,
                "last_score": score,
                "last_checked": today,
                "prev_score": prev_score,
                "delta": delta,
                "tier": tier,
            }

            # Detect drop
            is_alert = delta is not None and delta <= -alert_threshold
            status = "🚨 DROP" if is_alert else ("✅" if delta is None or delta >= 0 else "⚠️ MILD DROP")

            if is_alert:
                alerts.append({"name": name, "url": url, "score": score, "delta": delta})

            # Identify weakest dimension
            worst_dim = min(dims.items(), key=lambda x: x[1]) if dims else ("N/A", 0)

            result_line = (
                f"## {name}\n"
                f"- URL: {url}\n"
                f"- 현재 GEO 점수: **{score}/100** ({delta_str}점) {status}\n"
                f"- 가장 취약 항목: {worst_dim[0]} ({worst_dim[1]}/100)\n"
                f"- 등급: {tier}\n"
            )
            report_lines.append(result_line)
            results.append({"name": name, "score": score, "delta": delta_str, "status": status})
            print(f"     Score: {score}/100 | {delta_str}pts | {status}")

        except Exception as e:
            log[url] = {"name": name, "last_checked": today, "error": str(e)}
            report_lines.append(f"## {name}\n- **ERROR:** {e}\n")
            print(f"     ERROR: {e}")

    # Alert summary
    if alerts:
        report_lines.append("---\n## 🚨 알림 필요 클라이언트\n")
        for a in alerts:
            report_lines.append(
                f"- **{a['name']}** — {a['score']}/100 ({a['delta']}pts 하락) | {a['url']}\n"
                f"  → 즉시 원인 진단 후 클라이언트 연락 필요\n"
            )
    else:
        report_lines.append("---\n모든 클라이언트 점수 안정적. 알림 없음.\n")

    # Save log + report
    save_log(log)

    report_path = HERE / "reports" / f"{today}-health.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(f"\n[Loop 6] Done.")
    print(f"         Report: {report_path}")
    print(f"         Log:    {LOG_FILE}")
    if alerts:
        print(f"\n         ALERTS ({len(alerts)}): {', '.join(a['name'] for a in alerts)}")
    else:
        print("         No alerts.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--alert-threshold", type=int, default=ALERT_THRESHOLD,
                        help="Points drop that triggers an alert (default: 8)")
    args = parser.parse_args()
    run(alert_threshold=args.alert_threshold)
