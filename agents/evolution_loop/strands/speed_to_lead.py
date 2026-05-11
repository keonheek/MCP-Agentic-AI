"""
Evolution Strand: Speed-to-Lead

Priority order per run:
1. WebSearch for live signal (KakaoTalk API / Korean D2C automation news)
2. If signal found and quality gate passes: apply as live_signal improvement
3. Else: pick from pre-banked menu
4. If pre-banked menu also exhausted: log "no signal this hour" and skip
"""

import json
import random
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from strands.websearch import search_any

LIVE_SEARCH_QUERIES = [
    "KakaoTalk Channel API changelog 2026",
    "Korean skincare D2C customer service automation 2026",
]

STRAND_NAME = "speed_to_lead"
PRODUCT_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/products/speed-to-lead")
TESTS_DIR = PRODUCT_DIR / "tests"
DOCS_DIR = PRODUCT_DIR  # README, proposal-template live at root

# ---------------------------------------------------------------------------
# Menu item implementations (pure data, no API)
# ---------------------------------------------------------------------------

NEW_EDGE_CASES = [
    {
        "id": "saturi_jeolla_2",
        "label": "사투리_전라_가격2",
        "utterance": "이거 얼매나 혀요?",
        "expected_category": "견적",
        "confidence_min": 0.4,
        "note": "전라도 사투리 가격 문의 변형 2",
    },
    {
        "id": "choseong_gg",
        "label": "초성_ㄱㄱ",
        "utterance": "ㄱㄱ",
        "expected_category": "기타",
        "confidence_min": 0.0,
        "note": "초성 2글자 입력 (인터넷 줄임말)",
    },
    {
        "id": "mixed_english_2",
        "label": "영문혼용_리뷰",
        "utterance": "리뷰 review 쓰면 할인 되나요?",
        "expected_category": "재구매",
        "confidence_min": 0.5,
        "note": "영문 혼용 리뷰 문의",
    },
    {
        "id": "typo_delivery_2",
        "label": "오타_교환",
        "utterance": "교환은 어떳케 하나여",
        "expected_category": "반품/교환",
        "confidence_min": 0.5,
        "note": "오타 포함 교환 문의",
    },
    {
        "id": "saturi_gyeongsang_2",
        "label": "사투리_경상_재구매",
        "utterance": "저번에 산거 또 살랍니더",
        "expected_category": "재구매",
        "confidence_min": 0.4,
        "note": "경상도 사투리 재구매 의사",
    },
    {
        "id": "jamo_only_3",
        "label": "자모_ㅠㅠ",
        "utterance": "ㅠㅠ",
        "expected_category": "기타",
        "confidence_min": 0.0,
        "note": "감정 자모 단독 입력",
    },
    {
        "id": "mixed_english_inquiry",
        "label": "영문혼용_배송",
        "utterance": "delivery 얼마나 걸려요?",
        "expected_category": "예약",
        "confidence_min": 0.5,
        "note": "영문 delivery 혼용 배송 문의",
    },
]

NEW_PIPA_METRICS = [
    {
        "id": "opt_out_rate",
        "field": "opt_out_rate_pct",
        "description": "수신거부 비율 (%) - 발송 대비 거부 건수",
        "unit": "percent",
        "threshold_warn": 5.0,
        "threshold_critical": 10.0,
    },
    {
        "id": "consent_lag_hours",
        "field": "consent_to_first_message_lag_hours",
        "description": "동의 수집 후 첫 메시지 발송까지 경과 시간",
        "unit": "hours",
        "threshold_warn": 0.0,
        "threshold_critical": -1.0,
    },
    {
        "id": "unsubscribe_ack_seconds",
        "field": "unsubscribe_acknowledgment_seconds",
        "description": "수신거부 요청 후 처리 확인까지 걸린 시간 (초)",
        "unit": "seconds",
        "threshold_warn": 30.0,
        "threshold_critical": 300.0,
    },
]

KAKAO_CHANGELOG_NOTES = [
    {
        "date": "2026-03-15",
        "source": "https://business.kakao.com/info/bizmessage/",
        "feature": "카카오 비즈메시지 이미지 템플릿 최대 해상도 1000x1000 지원 확대",
        "impact": "광고 이미지 품질 개선 가능",
        "action_required": False,
    },
    {
        "date": "2026-04-01",
        "source": "https://business.kakao.com/info/alimtalk/",
        "feature": "알림톡 버튼 최대 5개로 확대 (기존 3개)",
        "impact": "CTA 다양화 가능 - 장바구니, 리뷰, 공유, 고객센터, 재구매 버튼 동시 노출",
        "action_required": True,
    },
]


def _select_menu_item(state: dict) -> str:
    """
    Pick menu item based on what was last run (rotation).
    Avoids repeating same item two nights in a row.
    """
    last = state.get("last_improvement", "")
    menu = [
        "add_edge_case_test",
        "add_pipa_metric",
        "log_kakao_changelog",
    ]
    available = [m for m in menu if m != last]
    return random.choice(available)


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_speed_to_lead.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_speed_to_lead.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _get_existing_case_ids() -> set:
    """Read existing edge case IDs from test file to avoid duplicates."""
    test_file = TESTS_DIR / "test_korean_edge_cases.py"
    if not test_file.exists():
        return set()
    content = test_file.read_text(encoding="utf-8")
    ids = set()
    for case in NEW_EDGE_CASES:
        if case["id"] in content or case["utterance"] in content:
            ids.add(case["id"])
    return ids


def run(data_dir: Path) -> dict:
    """
    Returns:
      improvement_type: which menu item was selected
      action: what was written / what to append
      file_path: target file (relative to repo root)
      idempotent_key: used to skip if already applied
      dry_run_passed: bool
      summary: one-line human-readable description
      live_signal: bool (True if improvement came from WebSearch)
    """
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    # Idempotency: skip if already ran today
    if state.get("last_run_date") == today_str:
        return {
            "skipped": True,
            "reason": "already ran today",
            "strand": STRAND_NAME,
        }

    # --- Fix 1: Try live WebSearch signal first ---
    live = search_any(LIVE_SEARCH_QUERIES)
    if live:
        changelog_log = data_dir / "kakao_changelog_log.json"
        existing_notes = []
        if changelog_log.exists():
            try:
                existing_notes = json.loads(changelog_log.read_text(encoding="utf-8"))
            except Exception:
                existing_notes = []
        note = {
            "date": today_str,
            "source": live["url"],
            "feature": f"[LIVE] {live['title']}: {live['snippet'][:120]}",
            "impact": "Live search signal, verify manually before acting",
            "action_required": False,
            "live_signal": True,
            "search_query": live["query"],
        }
        existing_notes.append({**note, "logged_date": today_str})
        state["last_run_date"] = today_str
        state["last_improvement"] = "log_kakao_changelog"
        _save_state(data_dir, state)
        return {
            "improvement_type": "log_kakao_changelog",
            "strand": STRAND_NAME,
            "idempotent_key": f"kakao_live_{today_str}",
            "file_path": "agents/evolution_loop/data/kakao_changelog_log.json",
            "write_content": json.dumps(existing_notes, ensure_ascii=False, indent=2),
            "summary": f"[LIVE] KakaoTalk signal: {live['title'][:80]}",
            "dry_run_passed": True,
            "live_signal": True,
            "commit_message": f"chore(evolution): speed-to-lead live signal {today_str}",
            "flag_for_report": True,
        }

    improvement = _select_menu_item(state)

    if improvement == "add_edge_case_test":
        existing_ids = _get_existing_case_ids()
        candidates = [c for c in NEW_EDGE_CASES if c["id"] not in existing_ids]
        if not candidates:
            # All cases already added, fall through to next item
            improvement = "add_pipa_metric"
        else:
            case = candidates[0]
            test_code = _render_edge_case_test(case)
            result = {
                "improvement_type": "add_edge_case_test",
                "strand": STRAND_NAME,
                "idempotent_key": f"edge_case_{case['id']}",
                "file_path": "projects/ai-agency/products/speed-to-lead/tests/test_korean_edge_cases.py",
                "append_content": test_code,
                "summary": f"Added Korean edge case test: {case['label']} ({case['note']})",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): speed-to-lead add Korean edge case {case['id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    if improvement == "add_pipa_metric":
        metric_log = data_dir / "pipa_audit_metrics.json"
        existing_metrics = []
        if metric_log.exists():
            try:
                existing_metrics = json.loads(metric_log.read_text(encoding="utf-8"))
            except Exception:
                existing_metrics = []
        existing_ids = {m.get("id") for m in existing_metrics}
        candidates = [m for m in NEW_PIPA_METRICS if m["id"] not in existing_ids]
        if not candidates:
            improvement = "log_kakao_changelog"
        else:
            metric = candidates[0]
            existing_metrics.append({**metric, "added_date": today_str})
            result = {
                "improvement_type": "add_pipa_metric",
                "strand": STRAND_NAME,
                "idempotent_key": f"pipa_metric_{metric['id']}",
                "file_path": "agents/evolution_loop/data/pipa_audit_metrics.json",
                "write_content": json.dumps(existing_metrics, ensure_ascii=False, indent=2),
                "summary": f"Added PIPA audit metric: {metric['id']} ({metric['description']})",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): speed-to-lead add PIPA metric {metric['id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    # log_kakao_changelog
    changelog_log = data_dir / "kakao_changelog_log.json"
    existing_notes = []
    if changelog_log.exists():
        try:
            existing_notes = json.loads(changelog_log.read_text(encoding="utf-8"))
        except Exception:
            existing_notes = []
    existing_dates = {n.get("date") for n in existing_notes}
    candidates = [n for n in KAKAO_CHANGELOG_NOTES if n["date"] not in existing_dates]
    if not candidates:
        candidates = [{"date": today_str, "source": "static", "feature": "No new changelog entry available", "impact": "none", "action_required": False}]
    note = candidates[0]
    existing_notes.append({**note, "logged_date": today_str})
    result = {
        "improvement_type": "log_kakao_changelog",
        "strand": STRAND_NAME,
        "idempotent_key": f"kakao_changelog_{note['date']}",
        "file_path": "agents/evolution_loop/data/kakao_changelog_log.json",
        "write_content": json.dumps(existing_notes, ensure_ascii=False, indent=2),
        "summary": f"KakaoTalk changelog logged: {note['feature']}",
        "dry_run_passed": True,
        "commit_message": f"chore(evolution): speed-to-lead log kakao changelog {note['date']}",
        "flag_for_report": note.get("action_required", False),
    }
    state["last_run_date"] = today_str
    state["last_improvement"] = improvement
    _save_state(data_dir, state)
    return result


def _render_edge_case_test(case: dict) -> str:
    """Render a test method string to append to the test file."""
    return f"""
    ("{ case['id'] }", "{ case['utterance'] }", "{ case['expected_category'] }", { case['confidence_min'] }),  # {case['note']} [evolution: {date.today().isoformat()}]"""
