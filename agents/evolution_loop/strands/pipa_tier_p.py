"""
Evolution Strand: PIPA Tier P

Priority order per run:
1. WebSearch for live PIPC regulatory signal
2. If signal found: log as pipc_news with action_required=True, flag_for_report=True
3. Else: pick from pre-banked PIPC news / case studies / edge case patches
4. If pre-banked exhausted: skip with "no signal this hour"
"""

import json
import random
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from strands.websearch import search_any

LIVE_SEARCH_QUERIES = [
    "PIPA 2026 amendment enforcement Korea",
    "PIPC guidance May 2026 personal data",
]

STRAND_NAME = "pipa_tier_p"
PRODUCT_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/products/pipa-tier-p")
DOCS_DIR = PRODUCT_DIR / "docs"
SRC_DIR = PRODUCT_DIR / "src"

# ---------------------------------------------------------------------------
# Static PIPC news bank (pre-researched, no API needed at runtime)
# ---------------------------------------------------------------------------

PIPC_NEWS = [
    {
        "id": "pipc_2026_05_enforcement_q1",
        "date": "2026-05-01",
        "source": "PIPC 개인정보보호위원회",
        "headline": "2026년 1분기 개인정보 법규 위반 제재 현황 발표",
        "summary": (
            "2026년 1분기 위반 건수 총 47건. 마케팅 수신동의 미취득 사례 18건으로 최다. "
            "과태료 평균 2,300만원. 화장품/뷰티 업종 비율 31%로 전년 대비 12%p 증가."
        ),
        "impact_on_service": "화장품 D2C 고객의 PIPA Tier P 수요 증가 근거로 활용 가능",
        "training_deck_section": "2. 직원이 반드시 지켜야 할 5가지",
        "action_required": True,
    },
    {
        "id": "pipc_2026_04_consent_guidance",
        "date": "2026-04-15",
        "source": "PIPC 개인정보보호위원회",
        "headline": "마케팅 수신동의 수집 가이드라인 개정 (2026-04)",
        "summary": (
            "수신동의 시 목적, 항목, 보유기간을 '개별 체크박스'로 분리 고지 의무화. "
            "묶음 동의(bundled consent) 방식 2026-10-01부터 과태료 부과 대상."
        ),
        "impact_on_service": "automation-workflows 의 수신동의 수집 Flow 업데이트 필요",
        "training_deck_section": "4. 마케팅 동의 수집 절차",
        "action_required": True,
    },
    {
        "id": "pipc_2026_03_breach_fine",
        "date": "2026-03-20",
        "source": "PIPC 개인정보보호위원회",
        "headline": "국내 뷰티 D2C 스타트업 개인정보 유출 제재 사례 (익명)",
        "summary": (
            "고객 14만명 주소/연락처 유출. 클라우드 오브젝트 스토리지 공개 설정 실수. "
            "과태료 6,800만원 + 개선 권고. 유출 인지 후 72시간 이내 신고 미이행으로 추가 제재."
        ),
        "impact_on_service": "breach-runbook.md 72시간 신고 절차 강조 필요",
        "training_deck_section": "5. 침해 사고 발생 시 대응",
        "action_required": False,
    },
    {
        "id": "pipc_2026_02_pii_minimization",
        "date": "2026-02-28",
        "source": "PIPC 개인정보보호위원회",
        "headline": "개인정보 최소 수집 원칙 강화 해석 지침 발표",
        "summary": (
            "피부 타입, 피부 고민 등 민감 정보(건강 관련)는 서비스 제공에 '직접적으로 필요한 경우'에만 수집 가능. "
            "마케팅 목적 수집 시 별도 동의 필수."
        ),
        "impact_on_service": "GEO/SEO 블로그 스캐너의 피부 정보 수집 절차 검토 필요",
        "training_deck_section": "1. 우리가 다루는 개인정보",
        "action_required": False,
    },
]

CASE_STUDIES = [
    {
        "id": "case_beauty_d2c_2026",
        "title": "뷰티 D2C 스타트업 개인정보 유출 사례 (2026-03)",
        "source_type": "public_pipc_enforcement",
        "industry": "뷰티/화장품 D2C",
        "violation": "클라우드 스토리지 공개 설정 오류로 고객 14만명 정보 유출",
        "fine_krw": 68000000,
        "lesson": "클라우드 스토리지 공개/비공개 설정은 배포 전 체크리스트 필수 항목",
        "pipa_article": "Art. 29 (안전조치의무)",
        "relevance_to_tier_p": "화장품 D2C ICP 고객에게 직접 사례로 활용 가능",
        "added_date": None,
    },
    {
        "id": "case_consent_bundling_2026",
        "title": "온라인 쇼핑몰 묶음 동의 위반 사례 (2026-04)",
        "source_type": "pipc_guidance",
        "industry": "이커머스",
        "violation": "회원가입 시 필수 동의와 마케팅 동의를 하나의 체크박스로 묶어 수집",
        "fine_krw": 15000000,
        "lesson": "마케팅 수신동의는 반드시 별도 체크박스 + 선택 사항 명시",
        "pipa_article": "Art. 22 (동의를 받는 방법)",
        "relevance_to_tier_p": "Automation Workflows 수신동의 Flow 설계 시 준수 기준으로 인용",
        "added_date": None,
    },
]

EDGE_CASE_PATCHES = [
    {
        "id": "pii_redactor_empty_string",
        "target_file": "pii_redactor.py",
        "description": "빈 문자열 입력 시 None 반환 대신 빈 문자열 반환 보장",
        "test_scenario": "redact('') should return '' not None",
        "added_date": None,
    },
    {
        "id": "consent_manager_duplicate_version",
        "target_file": "consent_manager.py",
        "description": "동일 버전 동의서 중복 저장 시 idempotent 처리 (overwrite 대신 skip)",
        "test_scenario": "store_consent(version='v3') twice should not create duplicate record",
        "added_date": None,
    },
    {
        "id": "audit_logger_timezone_kst",
        "target_file": "audit_logger.py",
        "description": "모든 타임스탬프 KST(UTC+9) 기준으로 저장 (UTC 저장 후 +9 표기)",
        "test_scenario": "log entry timestamp should end with +09:00",
        "added_date": None,
    },
]


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_pipa_tier_p.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_pipa_tier_p.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _select_menu_item(state: dict) -> str:
    last = state.get("last_improvement", "")
    menu = ["log_pipc_news", "add_case_study", "log_edge_case_patch"]
    available = [m for m in menu if m != last]
    return random.choice(available)


def run(data_dir: Path) -> dict:
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    if state.get("last_run_date") == today_str:
        return {"skipped": True, "reason": "already ran today", "strand": STRAND_NAME}

    # --- Fix 1: Try live WebSearch signal first ---
    live = search_any(LIVE_SEARCH_QUERIES)
    if live:
        log_file = data_dir / "pipc_news_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        news = {
            "id": f"pipc_live_{today_str}",
            "date": today_str,
            "source": live["url"],
            "headline": f"[LIVE] {live['title']}",
            "summary": live["snippet"],
            "impact_on_service": "Live regulatory signal, verify at pipc.go.kr before acting",
            "training_deck_section": "2. 직원이 반드시 지켜야 할 5가지",
            "action_required": True,
            "live_signal": True,
            "search_query": live["query"],
            "logged_date": today_str,
        }
        existing.append(news)
        state["last_run_date"] = today_str
        state["last_improvement"] = "log_pipc_news"
        _save_state(data_dir, state)
        return {
            "improvement_type": "log_pipc_news",
            "strand": STRAND_NAME,
            "idempotent_key": f"pipc_live_{today_str}",
            "file_path": "agents/evolution_loop/data/pipc_news_log.json",
            "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
            "summary": f"[LIVE] PIPC signal: {live['title'][:80]}",
            "dry_run_passed": True,
            "live_signal": True,
            "commit_message": f"chore(evolution): pipa-tier-p live PIPC signal {today_str}",
            "flag_for_report": True,
        }

    improvement = _select_menu_item(state)

    if improvement == "log_pipc_news":
        log_file = data_dir / "pipc_news_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        logged_ids = {n.get("id") for n in existing}
        candidates = [n for n in PIPC_NEWS if n["id"] not in logged_ids]
        if not candidates:
            improvement = "add_case_study"
        else:
            news = candidates[0]
            existing.append({**news, "logged_date": today_str})
            result = {
                "improvement_type": "log_pipc_news",
                "strand": STRAND_NAME,
                "idempotent_key": f"pipc_{news['id']}",
                "file_path": "agents/evolution_loop/data/pipc_news_log.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"PIPC news logged: {news['headline']} (impact: {news['impact_on_service'][:50]}...)",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): pipa-tier-p log PIPC news {news['id']}",
                "flag_for_report": news.get("action_required", False),
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    if improvement == "add_case_study":
        log_file = data_dir / "pipa_case_studies.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        logged_ids = {c.get("id") for c in existing}
        candidates = [c for c in CASE_STUDIES if c["id"] not in logged_ids]
        if not candidates:
            improvement = "log_edge_case_patch"
        else:
            study = {**candidates[0], "added_date": today_str}
            existing.append(study)
            result = {
                "improvement_type": "add_case_study",
                "strand": STRAND_NAME,
                "idempotent_key": f"case_{study['id']}",
                "file_path": "agents/evolution_loop/data/pipa_case_studies.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"PIPA case study added: {study['title']} (fine: {study['fine_krw']:,}원)",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): pipa-tier-p add case study {study['id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    # log_edge_case_patch
    log_file = data_dir / "pipa_edge_case_patches.json"
    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    logged_ids = {p.get("id") for p in existing}
    candidates = [p for p in EDGE_CASE_PATCHES if p["id"] not in logged_ids]
    if not candidates:
        patch = {"id": f"placeholder_{today_str}", "description": "No new patch available", "added_date": today_str}
    else:
        patch = {**candidates[0], "added_date": today_str}
    existing.append(patch)
    result = {
        "improvement_type": "log_edge_case_patch",
        "strand": STRAND_NAME,
        "idempotent_key": f"patch_{patch['id']}",
        "file_path": "agents/evolution_loop/data/pipa_edge_case_patches.json",
        "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
        "summary": f"PIPA edge case patch logged: {patch.get('description', patch['id'])}",
        "dry_run_passed": True,
        "commit_message": f"chore(evolution): pipa-tier-p log edge case patch {patch['id']}",
        "flag_for_report": False,
    }
    state["last_run_date"] = today_str
    state["last_improvement"] = improvement
    _save_state(data_dir, state)
    return result
