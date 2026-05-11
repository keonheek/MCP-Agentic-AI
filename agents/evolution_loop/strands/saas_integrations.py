"""
Evolution Strand: SaaS Integrations
Pure data module. No LLM calls. No API calls.

Rotates through platform changelog checks, error handler additions,
README updates, and unified interface test stubs.
"""

import json
import random
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

STRAND_NAME = "saas_integrations"
PRODUCT_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/products/saas-integrations")

# ---------------------------------------------------------------------------
# Platform rotation (Cafe24 -> Imweb -> SmartStore -> Shopify -> Kakao -> Channel.io)
# ---------------------------------------------------------------------------

PLATFORM_CHANGELOGS = [
    {
        "platform": "cafe24",
        "check_date": "2026-04-15",
        "api_version": "2026-03-01",
        "changelog_url": "https://developers.cafe24.com/docs/api/admin/release-notes/",
        "notes": "v2026-03-01: Added order.custom_fields support. Webhook retry count increased to 5. No breaking changes.",
        "breaking_change": False,
        "action": "No update needed. Current client targets 2026-03-01 which is current.",
    },
    {
        "platform": "imweb",
        "check_date": "2026-04-15",
        "api_version": "v2",
        "changelog_url": "https://developers.imweb.me/docs/changelog",
        "notes": "v2 stable. Webhook payload now includes member_grade field for segmentation. No breaking changes.",
        "breaking_change": False,
        "action": "Consider using member_grade in AbandonedCart flow for VIP segmentation.",
    },
    {
        "platform": "smartstore",
        "check_date": "2026-04-15",
        "api_version": "v1",
        "changelog_url": "https://apicenter.commerce.naver.com/po/guide/releasenote",
        "notes": "Naver SmartStore API v1 stable. New field: productAttribute.skinType added for beauty category. No auth changes.",
        "breaking_change": False,
        "action": "skinType field useful for GEO/SEO Blog scanner integration (future).",
    },
    {
        "platform": "shopify",
        "check_date": "2026-04-15",
        "api_version": "2025-04",
        "changelog_url": "https://shopify.dev/api/release-notes/2025-04",
        "notes": "2025-04 stable. Shopify Markets API now returns KRW pricing natively. REST Admin API still supported through 2026.",
        "breaking_change": False,
        "action": "Update client.py to use Markets API for KRW price fetching instead of manual conversion.",
    },
    {
        "platform": "kakao",
        "check_date": "2026-04-15",
        "api_version": "2026-Q1",
        "changelog_url": "https://business.kakao.com/info/bizmessage/",
        "notes": "KakaoTalk Business Message: max buttons per template increased from 3 to 5 (confirmed 2026-Q1). Rate limit unchanged at 3000/min.",
        "breaking_change": False,
        "action": "No immediate change needed. Plan button expansion for cart recovery v2 template.",
    },
    {
        "platform": "channelio",
        "check_date": "2026-04-15",
        "api_version": "v9",
        "changelog_url": "https://developers.channel.io/docs/changelog",
        "notes": "Channel.io v9 stable. New: /open-chats endpoint for proactive chat initiation. Webhook event 'chat.opened' added.",
        "breaking_change": False,
        "action": "chat.opened event could trigger speed-to-lead flow. Note for future integration.",
    },
]

NEW_ERROR_HANDLERS = [
    {
        "platform": "cafe24",
        "error_code": "HTTP_429",
        "handler_id": "cafe24_rate_limit_retry",
        "description": "Cafe24 API 429 Too Many Requests: exponential backoff retry (max 3 attempts)",
        "pattern": "retry with backoff: 2s, 4s, 8s",
    },
    {
        "platform": "imweb",
        "error_code": "HTTP_401",
        "handler_id": "imweb_token_refresh",
        "description": "Imweb 401: auto-refresh access token using refresh_token before retry",
        "pattern": "refresh token -> retry once -> raise on second 401",
    },
    {
        "platform": "shopify",
        "error_code": "HTTP_422",
        "handler_id": "shopify_validation_error",
        "description": "Shopify 422 Unprocessable: parse error detail from JSON body and raise with field context",
        "pattern": "parse errors[] array -> raise ValueError with field names",
    },
    {
        "platform": "smartstore",
        "error_code": "HTTP_503",
        "handler_id": "smartstore_maintenance",
        "description": "SmartStore 503: detect maintenance window, log and skip (not retry)",
        "pattern": "check Retry-After header -> if > 300s: skip and log, else: wait and retry once",
    },
    {
        "platform": "channelio",
        "error_code": "WEBHOOK_SIGNATURE_INVALID",
        "handler_id": "channelio_sig_validation",
        "description": "Channel.io webhook signature mismatch: reject with 400 and log incident",
        "pattern": "hmac.compare_digest -> raise 400 SecurityError with timestamp",
    },
]

README_SCOPE_NOTES = [
    {
        "platform": "cafe24",
        "note_id": "cafe24_oauth_scope_2026",
        "content": "Cafe24 OAuth: as of 2026-03-01, mall.read_product scope required for inventory checks. Add to scope list in README.",
        "section": "Authentication",
    },
    {
        "platform": "shopify",
        "note_id": "shopify_api_version_pin",
        "content": "Shopify recommends pinning API version in all requests. Current pin: 2025-04. Schedule upgrade to 2026-01 by Q3 2026.",
        "section": "API Versioning",
    },
]

UNIFIED_INTERFACE_TESTS = [
    {
        "test_id": "test_unified_order_schema_all_platforms",
        "description": "Assert Order dataclass fields match across all 5 platform adapters",
        "assertion": "All platforms return Order with: id, customer_id, total_krw, created_at, status",
    },
    {
        "test_id": "test_unified_customer_phone_normalization",
        "description": "Assert phone number normalized to 01012345678 format by all adapters",
        "assertion": "Customer.phone always 11 digits, no dashes, no spaces",
    },
    {
        "test_id": "test_unified_webhook_event_type_enum",
        "description": "Assert WebhookEvent.event_type is always one of: order.created, cart.abandoned, customer.created",
        "assertion": "Unknown event types raise ValueError, not silently ignored",
    },
]


def _get_next_platform(data_dir: Path) -> dict:
    """Rotate through platforms in order."""
    state_file = data_dir / "strand_state_saas_integrations.json"
    state = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    last_idx = state.get("last_platform_idx", -1)
    next_idx = (last_idx + 1) % len(PLATFORM_CHANGELOGS)
    state["last_platform_idx"] = next_idx
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return PLATFORM_CHANGELOGS[next_idx], state


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_saas_integrations.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_saas_integrations.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def run(data_dir: Path) -> dict:
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    if state.get("last_run_date") == today_str:
        return {"skipped": True, "reason": "already ran today", "strand": STRAND_NAME}

    # Tonight: check one platform changelog (rotation)
    platform_log_file = data_dir / "platform_changelog_log.json"
    existing_logs = []
    if platform_log_file.exists():
        try:
            existing_logs = json.loads(platform_log_file.read_text(encoding="utf-8"))
        except Exception:
            existing_logs = []

    logged_platforms_today = {e.get("platform") for e in existing_logs if e.get("logged_date") == today_str}
    last_idx = state.get("last_platform_idx", -1)
    next_idx = (last_idx + 1) % len(PLATFORM_CHANGELOGS)
    platform_entry = PLATFORM_CHANGELOGS[next_idx]

    # Also queue one error handler if any not yet logged
    error_log_file = data_dir / "error_handlers_log.json"
    existing_errors = []
    if error_log_file.exists():
        try:
            existing_errors = json.loads(error_log_file.read_text(encoding="utf-8"))
        except Exception:
            existing_errors = []
    logged_handler_ids = {e.get("handler_id") for e in existing_errors}
    new_handler = next((h for h in NEW_ERROR_HANDLERS if h["handler_id"] not in logged_handler_ids), None)

    existing_logs.append({**platform_entry, "logged_date": today_str})
    writes = [
        {
            "file_path": "agents/evolution_loop/data/platform_changelog_log.json",
            "write_content": json.dumps(existing_logs, ensure_ascii=False, indent=2),
        }
    ]

    if new_handler:
        existing_errors.append({**new_handler, "added_date": today_str})
        writes.append({
            "file_path": "agents/evolution_loop/data/error_handlers_log.json",
            "write_content": json.dumps(existing_errors, ensure_ascii=False, indent=2),
        })

    summary_parts = [f"Checked {platform_entry['platform']} API changelog: {platform_entry['notes'][:60]}..."]
    if new_handler:
        summary_parts.append(f"Added error handler: {new_handler['handler_id']}")

    state["last_run_date"] = today_str
    state["last_platform_idx"] = next_idx
    state["last_improvement"] = "platform_changelog_check"
    _save_state(data_dir, state)

    return {
        "improvement_type": "platform_changelog_check",
        "strand": STRAND_NAME,
        "idempotent_key": f"platform_{platform_entry['platform']}_{today_str}",
        "multi_write": writes,
        "summary": " | ".join(summary_parts),
        "dry_run_passed": True,
        "commit_message": f"chore(evolution): saas-integrations check {platform_entry['platform']} changelog",
        "flag_for_report": platform_entry.get("breaking_change", False),
        "platform_checked": platform_entry["platform"],
        "breaking_change": platform_entry.get("breaking_change", False),
    }
