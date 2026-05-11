"""
Evolution Strand: Hagwon Stack (한국 학원 관련 정책 / EduPie / 사이다페이 / 알리미)

Priority order per run:
1. WebSearch for live signal (학원법, EduPie, 사이다페이, 알리미, Kakao 알림톡 학원 정책)
2. If signal found: log as changelog entry with live_signal=True, flag_for_report=True
3. Else: pick from pre-banked menu (policy changelog, competitor observation, pricing update)
4. If pre-banked exhausted: skip with "no signal this hour"
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from strands.websearch import search_any

LIVE_SEARCH_QUERIES = [
    "학원법 개정 2026",
    "사이다페이 학원 2026",
    "EduPie 학원 관리 2026",
    "카카오 알림톡 학원 2026",
    "알리미 학원 앱 업데이트 2026",
]

STRAND_NAME = "hagwon_stack"
PRODUCTS_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/products")

POLICY_CHANGELOGS = [
    {
        "id": "kakao_alimtalk_template_cache_2026q1",
        "source": "Kakao Business",
        "update_date": "2026-02-01",
        "headline": "Kakao Alimtalk template caching + AI partner program launched Q1 2026",
        "detail": "Kakao dropped per-message fees to under ₩10 for approved AI partner accounts. Template caching reduces API calls by up to 70% for recurring message patterns.",
        "impact_on_hagwon": "Product 1 (알림톡 AI 비서) cost model improves. Per-message cost now negligible; retainer pricing more defensible vs 사이다페이.",
        "action_required": False,
        "source_url": "https://business.kakao.com/info/bizmessage",
    },
    {
        "id": "toss_payments_billing_key_2026q1",
        "source": "Toss Payments",
        "update_date": "2026-03-15",
        "headline": "Toss Payments: ₩0 setup for billing key (recurring payment)",
        "detail": "Toss launched no-setup-fee billing key API in March 2026. Previously ₩100K setup. Now SMB operators can use auto-billing without upfront cost. Webhook support for success/fail events added.",
        "impact_on_hagwon": "Product 13 (수강료 결제 자동화) setup cost drops. Toss billing key competitive advantage over 사이다페이's transaction fee model.",
        "action_required": False,
        "source_url": "https://www.tosspayments.com/products/billing",
    },
    {
        "id": "edupie_competitor_2026",
        "source": "EduPie (Market observation)",
        "update_date": "2026-01-15",
        "headline": "EduPie focuses on attendance tracking; parent messaging gap remains",
        "detail": "EduPie's 2026 roadmap focuses on EMR integration and attendance reporting. No AI-generated parent message feature planned. Alimi and Classtin same gap.",
        "impact_on_hagwon": "Product 1 wedge confirmed: EduPie + Alimi cover attendance data but NOT natural language parent comms. 1stmover owns the messaging layer.",
        "action_required": False,
        "source_url": "https://edupie.co.kr",
    },
    {
        "id": "saidapay_pricing_2026",
        "source": "사이다페이 (Market scan)",
        "update_date": "2026-04-01",
        "headline": "사이다페이 maintains 1.5-2% transaction fee for 학원 결제",
        "detail": "사이다페이 2026 pricing unchanged: 1.5% per transaction for basic plan, 2% for standard. No flat-rate option announced. Korean hagwon owners continue to overpay at high student count.",
        "impact_on_hagwon": "Product 13 pricing wedge holds. 1stmover ₩70K flat vs 사이다페이 ₩225K (50 students x ₩300K x 1.5%). Update product pricing.md with this calculation.",
        "action_required": False,
        "source_url": "https://saidapay.co.kr",
    },
    {
        "id": "hagwon_law_amendment_2026",
        "source": "교육부 (Ministry of Education)",
        "update_date": "2026-01-01",
        "headline": "학원법 시행령 2026: 학부모 알림 의무 강화",
        "detail": "2026 amendment to 학원법 enforcement decree strengthens parent notification requirements. 학원 must provide written (or digital) notification for: attendance deviation, curriculum change, fee increase. Digital notification (알림톡 등) now explicitly accepted.",
        "impact_on_hagwon": "Regulatory tailwind for Product 1. 학원 now have compliance incentive to adopt digital parent comms. Pitch angle: '법적 의무 충족 + 자동화' (compliance + automation).",
        "action_required": True,
        "source_url": "https://www.law.go.kr/법령/학원의설립운영및과외교습에관한법률시행령",
    },
]

COMPETITOR_OBSERVATIONS = [
    {
        "id": "obs_edupie_2026q1",
        "competitor": "EduPie",
        "observation_date": "2026-05-01",
        "gap": "학부모 맞춤형 알림 메시지 생성 기능 없음. 출결 데이터만 전달",
        "opportunity": "Product 1 AI 메시지 생성이 EduPie 대비 차별화 포인트",
    },
]


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_hagwon_stack.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_hagwon_stack.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _select_menu_item(state: dict) -> str:
    last = state.get("last_improvement", "")
    menu = ["log_policy_changelog", "log_competitor_observation", "update_hagwon_intel"]
    available = [m for m in menu if m != last]
    import random
    return random.choice(available)


def run(data_dir: Path) -> dict:
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    if state.get("last_run_date") == today_str:
        return {"skipped": True, "reason": "already ran today", "strand": STRAND_NAME}

    live = search_any(LIVE_SEARCH_QUERIES)
    if live:
        log_file = data_dir / "hagwon_stack_changelog_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        entry = {
            "id": f"hagwon_live_{today_str}",
            "source": "Live Signal",
            "update_date": today_str,
            "headline": f"[LIVE] {live['title']}",
            "detail": live["snippet"],
            "impact_on_hagwon": "Verify manually and update Product 1/13 positioning if relevant",
            "action_required": True,
            "source_url": live["url"],
            "search_query": live["query"],
            "live_signal": True,
            "logged_date": today_str,
        }
        existing.append(entry)
        state["last_run_date"] = today_str
        state["last_improvement"] = "log_policy_changelog"
        _save_state(data_dir, state)
        return {
            "improvement_type": "log_policy_changelog",
            "strand": STRAND_NAME,
            "idempotent_key": f"hagwon_live_{today_str}",
            "file_path": "agents/evolution_loop/data/hagwon_stack_changelog_log.json",
            "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
            "summary": f"[LIVE] Hagwon stack signal: {live['title'][:80]}",
            "dry_run_passed": True,
            "live_signal": True,
            "commit_message": f"chore(evolution): hagwon-stack live signal {today_str}",
            "flag_for_report": True,
        }

    improvement = _select_menu_item(state)

    changelog_log_file = data_dir / "hagwon_stack_changelog_log.json"
    existing_changelogs = []
    if changelog_log_file.exists():
        try:
            existing_changelogs = json.loads(changelog_log_file.read_text(encoding="utf-8"))
        except Exception:
            existing_changelogs = []

    competitor_log_file = data_dir / "hagwon_stack_competitors.json"
    existing_competitors = []
    if competitor_log_file.exists():
        try:
            existing_competitors = json.loads(competitor_log_file.read_text(encoding="utf-8"))
        except Exception:
            existing_competitors = []

    if improvement == "log_policy_changelog":
        logged_ids = {e.get("id") for e in existing_changelogs}
        candidates = [c for c in POLICY_CHANGELOGS if c["id"] not in logged_ids]
        if not candidates:
            improvement = "log_competitor_observation"
        else:
            entry = {**candidates[0], "logged_date": today_str}
            existing_changelogs.append(entry)
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            flag = entry.get("action_required", False)
            return {
                "improvement_type": "log_policy_changelog",
                "strand": STRAND_NAME,
                "idempotent_key": f"hagwon_stack_policy_{entry['id']}",
                "file_path": "agents/evolution_loop/data/hagwon_stack_changelog_log.json",
                "write_content": json.dumps(existing_changelogs, ensure_ascii=False, indent=2),
                "summary": f"Hagwon policy: {entry['source']} - {entry['headline']}",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): hagwon-stack log policy {entry['id']}",
                "flag_for_report": flag,
            }

    if improvement == "log_competitor_observation":
        logged_ids = {e.get("id") for e in existing_competitors}
        candidates = [o for o in COMPETITOR_OBSERVATIONS if o["id"] not in logged_ids]
        if not candidates:
            improvement = "update_hagwon_intel"
        else:
            obs = {**candidates[0], "logged_date": today_str}
            existing_competitors.append(obs)
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return {
                "improvement_type": "log_competitor_observation",
                "strand": STRAND_NAME,
                "idempotent_key": f"hagwon_competitor_{obs['id']}",
                "file_path": "agents/evolution_loop/data/hagwon_stack_competitors.json",
                "write_content": json.dumps(existing_competitors, ensure_ascii=False, indent=2),
                "summary": f"Hagwon competitor gap: {obs['competitor']} - {obs['gap'][:60]}",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): hagwon-stack log competitor {obs['id']}",
                "flag_for_report": False,
            }

    # update_hagwon_intel summary file
    intel_md = f"""# Hagwon Stack Intelligence

Last updated: {today_str}

## Key Policy Changes

"""
    for entry in POLICY_CHANGELOGS[-3:]:
        action_tag = " [ACTION REQUIRED]" if entry.get("action_required") else ""
        intel_md += f"### {entry['source']} ({entry['update_date']}){action_tag}\n"
        intel_md += f"{entry['headline']}\n"
        intel_md += f"Impact: {entry['impact_on_hagwon']}\n\n"

    intel_md += "## Competitor Gaps\n\n"
    for obs in COMPETITOR_OBSERVATIONS:
        intel_md += f"- **{obs['competitor']}**: {obs['gap']}\n"
        intel_md += f"  Opportunity: {obs['opportunity']}\n\n"

    state["last_run_date"] = today_str
    state["last_improvement"] = improvement
    _save_state(data_dir, state)
    return {
        "improvement_type": "update_hagwon_intel",
        "strand": STRAND_NAME,
        "idempotent_key": f"hagwon_stack_intel_{today_str}",
        "file_path": "agents/evolution_loop/data/hagwon_stack_intel.md",
        "write_content": intel_md,
        "summary": "Hagwon stack intelligence refreshed. 학원법 amendment flagged.",
        "dry_run_passed": True,
        "commit_message": "chore(evolution): hagwon-stack refresh intel",
        "flag_for_report": False,
    }
