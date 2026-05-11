"""
Notion Logger -- per-inquiry log writer for Speed-to-Lead.

Writes one Notion page per inquiry to the client's designated database.
Wraps the existing log_to_notion function from speed_to_lead.py and adds
a structured audit trail field for PIPA Tier P clients.

Usage:
    from src.notion_logger import log_inquiry

    log_inquiry(
        inquiry="세럼 가격이 어떻게 되나요?",
        user_key="abc123xyz",
        category="견적",
        confidence=0.92,
        reply="안녕하세요...",
        escalated=False,
        eval_score=9.5,
        config=client_config,
        pii_redacted=True,      # Tier P only
        audit_note="",          # optional free text
    )
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger("speed_to_lead.notion_logger")


def log_inquiry(
    inquiry: str,
    user_key: str,
    category: str,
    confidence: float,
    reply: str,
    escalated: bool,
    eval_score: float,
    config: dict,
    pii_redacted: bool = False,
    audit_note: str = "",
) -> None:
    """
    Write a single inquiry record to the client's Notion database.

    For Tier P clients, appends two extra properties:
        - PII 제거 여부 (checkbox)
        - 감사 메모 (rich_text)

    Falls back gracefully if Notion credentials are absent.
    """
    notion_token = config.get("notion_token") or os.getenv("NOTION_TOKEN")
    db_id = config.get("notion_db_id")

    if not notion_token or not db_id:
        logger.warning("Notion credentials missing -- skipping log")
        return

    try:
        from notion_client import Client as NotionClient
    except ImportError:
        logger.error("notion-client not installed -- pip install notion-client")
        return

    notion = NotionClient(auth=notion_token)
    brand_name = config.get("brand_name", "브랜드")
    now = datetime.now(timezone.utc).isoformat()

    properties: dict = {
        "고객ID": {"title": [{"text": {"content": user_key[:12] + "..."}}]},
        "문의내용": {"rich_text": [{"text": {"content": inquiry[:2000]}}]},
        "카테고리": {"select": {"name": category}},
        "신뢰도": {"number": round(confidence, 2)},
        "자동답변": {"rich_text": [{"text": {"content": reply[:2000]}}]},
        "에스컬레이션": {"checkbox": escalated},
        "Eval점수": {"number": round(eval_score, 1)},
        "브랜드": {"rich_text": [{"text": {"content": brand_name}}]},
        "처리시각": {"date": {"start": now}},
    }

    # Tier P audit fields
    tier = config.get("tier", "pro")
    if str(tier).lower().replace("-", "_") == "tier_p":
        properties["PII제거여부"] = {"checkbox": pii_redacted}
        if audit_note:
            properties["감사메모"] = {
                "rich_text": [{"text": {"content": audit_note[:500]}}]
            }

    try:
        notion.pages.create(
            parent={"database_id": db_id},
            properties=properties,
        )
        logger.info(f"Notion log created for {brand_name}")
    except Exception as e:
        logger.error(f"Notion log failed: {e}")
