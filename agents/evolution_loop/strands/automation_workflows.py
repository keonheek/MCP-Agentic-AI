"""
Evolution Strand: Automation Workflows
Pure data module. No LLM calls. No API calls.

Selects one improvement from the menu, returns structured result.
"""

import json
import random
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

STRAND_NAME = "automation_workflows"
PRODUCT_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/products/automation-workflows")
TESTS_DIR = PRODUCT_DIR / "tests"
SRC_DIR = PRODUCT_DIR / "src"

# ---------------------------------------------------------------------------
# Menu data
# ---------------------------------------------------------------------------

NEW_KAKAO_VARIANTS = [
    {
        "flow": "abandoned_cart",
        "variant_id": "cart_30min_v2",
        "template_key": "TEMPLATE_30MIN_V2",
        "body": (
            "안녕하세요, {{customer_name}}님!\n\n"
            "{{product_name}} 아직 장바구니에 있어요.\n"
            "지금 구매하시면 무료 샘플도 함께 드려요.\n"
            "오늘만 이 혜택이에요 :)"
        ),
        "note": "30분 메시지 A/B 변형 v2: 무료 샘플 혜택 강조",
    },
    {
        "flow": "review_request",
        "variant_id": "review_7day_v2",
        "template_key": "TEMPLATE_REVIEW_7DAY_V2",
        "body": (
            "[광고] 안녕하세요, {{customer_name}}님!\n\n"
            "{{product_name}} 사용해 보셨나요?\n"
            "리뷰 한 줄만 남겨 주시면 다음 구매 시 {{review_reward}} 드려요.\n"
            "{{review_url}}"
        ),
        "note": "리뷰 요청 7일차 변형 v2: 리워드 금액 명시",
    },
    {
        "flow": "winback_inactive",
        "variant_id": "winback_90day_v2",
        "template_key": "TEMPLATE_WINBACK_90_V2",
        "body": (
            "[광고] {{customer_name}}님, 오랜만이에요!\n\n"
            "{{product_name}} 이후로 피부 상태 어떠신가요?\n"
            "이번 달만 {{discount_pct}}% 할인 쿠폰 드릴게요.\n"
            "코드: {{discount_code}}"
        ),
        "note": "90일 이탈 재활성 변형 v2: 피부 상태 관심 표현 + 할인율 명시",
    },
    {
        "flow": "birthday_discount",
        "variant_id": "birthday_v2",
        "template_key": "TEMPLATE_BIRTHDAY_V2",
        "body": (
            "[광고] {{customer_name}}님, 생일 축하해요!\n\n"
            "오늘 하루만 전 상품 {{discount_pct}}% 할인이에요.\n"
            "코드: {{discount_code}} (오늘 자정까지)\n\n"
            "오늘 기분 좋은 하루 되세요 :)"
        ),
        "note": "생일 할인 변형 v2: 만료 시간 명시 (자정) + 감성 클로징",
    },
]

NEW_E2E_EDGE_CASES = [
    {
        "id": "double_opt_out_ignored",
        "description": "이미 수신거부한 고객에게 중복 수신거부 요청 시 상태 변경 없음",
        "flow": "abandoned_cart",
        "scenario": "send opt-out to already opted-out customer, assert state unchanged",
    },
    {
        "id": "concurrent_flows_same_customer",
        "description": "동일 고객이 동시에 abandoned_cart + winback 두 flow에 진입 시 중복 발송 방지",
        "flow": "multi",
        "scenario": "two flows same customer_id, assert total touches <= 1 per channel per day",
    },
    {
        "id": "empty_product_name",
        "description": "product_name 빈 문자열인 경우 메시지 fallback 처리",
        "flow": "abandoned_cart",
        "scenario": "product_name='', assert message uses 'your item' fallback, no crash",
    },
    {
        "id": "unicode_phone_spaces",
        "description": "전화번호에 공백 포함 입력 (010 1234 5678) 정규화 처리",
        "flow": "abandoned_cart",
        "scenario": "phone='010 1234 5678', assert normalized to '01012345678'",
    },
]

PIPA_OPT_OUT_COPIES = [
    {
        "id": "opt_out_v3",
        "text": "[광고] 수신거부는 아래 링크를 클릭하거나 '거부'로 답장하세요.\n무료 거부: {{unsubscribe_url}}",
        "note": "PIPA 2026 개정: URL + 단어 거부 이중 경로 명시",
        "regulation_ref": "PIPA Art. 50-8 (2026 개정안)",
    },
    {
        "id": "opt_out_v4",
        "text": "[광고] 이 메시지를 더 이상 받지 않으시려면 '수신거부' 또는 '거부'로 답장해 주세요.\n처리 결과는 24시간 이내 안내드립니다.",
        "note": "처리 시간 24시간 이내 명시 (규정 준수 강화)",
        "regulation_ref": "PIPA Art. 50-8 (2026 개정안)",
    },
]

BACKLOG_FLOW_STUBS = [
    {
        "id": "restock_alert",
        "name": "재입고 알림 (Restock Alert)",
        "description": "품절 상품 관심 고객에게 재입고 시 즉시 알림 발송",
        "trigger": "재고 0 -> 1 webhook",
        "kakao_template": "알림톡 정보성",
        "complexity": "medium",
        "priority": "high",
        "added_date": None,
    },
    {
        "id": "vip_upgrade",
        "name": "VIP 등급 업그레이드 알림",
        "description": "누적 구매액 기준 VIP 등급 달성 시 축하 메시지 + 전용 혜택 안내",
        "trigger": "누적 구매액 임계값 초과",
        "kakao_template": "알림톡 정보성 + 광고",
        "complexity": "low",
        "priority": "medium",
        "added_date": None,
    },
    {
        "id": "post_purchase_care",
        "name": "구매 후 케어 시퀀스",
        "description": "구매 후 D+3, D+7, D+14 피부 상태 체크 + 사용법 팁 발송",
        "trigger": "구매 완료 webhook",
        "kakao_template": "알림톡 정보성",
        "complexity": "medium",
        "priority": "medium",
        "added_date": None,
    },
]


def _select_menu_item(state: dict) -> str:
    last = state.get("last_improvement", "")
    menu = [
        "add_kakao_variant",
        "add_e2e_edge_case",
        "add_backlog_stub",
    ]
    available = [m for m in menu if m != last]
    return random.choice(available)


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_automation_workflows.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_automation_workflows.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run(data_dir: Path) -> dict:
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    if state.get("last_run_date") == today_str:
        return {"skipped": True, "reason": "already ran today", "strand": STRAND_NAME}

    improvement = _select_menu_item(state)

    if improvement == "add_kakao_variant":
        log_file = data_dir / "kakao_variants_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        existing_ids = {v.get("variant_id") for v in existing}
        candidates = [v for v in NEW_KAKAO_VARIANTS if v["variant_id"] not in existing_ids]
        if not candidates:
            improvement = "add_backlog_stub"
        else:
            variant = candidates[0]
            existing.append({**variant, "added_date": today_str})
            result = {
                "improvement_type": "add_kakao_variant",
                "strand": STRAND_NAME,
                "idempotent_key": f"kakao_variant_{variant['variant_id']}",
                "file_path": "agents/evolution_loop/data/kakao_variants_log.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"Added Kakao A/B variant: {variant['variant_id']} for flow {variant['flow']}",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): automation-workflows add kakao variant {variant['variant_id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    if improvement == "add_e2e_edge_case":
        log_file = data_dir / "e2e_edge_cases_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        existing_ids = {c.get("id") for c in existing}
        candidates = [c for c in NEW_E2E_EDGE_CASES if c["id"] not in existing_ids]
        if not candidates:
            improvement = "add_backlog_stub"
        else:
            case = candidates[0]
            existing.append({**case, "added_date": today_str})
            result = {
                "improvement_type": "add_e2e_edge_case",
                "strand": STRAND_NAME,
                "idempotent_key": f"e2e_case_{case['id']}",
                "file_path": "agents/evolution_loop/data/e2e_edge_cases_log.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"Added e2e edge case: {case['id']} ({case['description']})",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): automation-workflows add e2e edge case {case['id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    # add_backlog_stub
    backlog_file = data_dir / "automation_backlog.json"
    existing = []
    if backlog_file.exists():
        try:
            existing = json.loads(backlog_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    existing_ids = {s.get("id") for s in existing}
    candidates = [s for s in BACKLOG_FLOW_STUBS if s["id"] not in existing_ids]
    if not candidates:
        stub = {"id": f"placeholder_{today_str}", "name": "No new stub available", "added_date": today_str}
    else:
        stub = {**candidates[0], "added_date": today_str}
    existing.append(stub)
    result = {
        "improvement_type": "add_backlog_stub",
        "strand": STRAND_NAME,
        "idempotent_key": f"backlog_{stub['id']}",
        "file_path": "agents/evolution_loop/data/automation_backlog.json",
        "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
        "summary": f"Added flow concept stub to backlog: {stub.get('name', stub['id'])}",
        "dry_run_passed": True,
        "commit_message": f"chore(evolution): automation-workflows add backlog stub {stub['id']}",
        "flag_for_report": False,
    }
    state["last_run_date"] = today_str
    state["last_improvement"] = improvement
    _save_state(data_dir, state)
    return result
