"""
Logs alimtalk send events to Notion database.
"""
import os
from datetime import datetime
import requests

NOTION_TOKEN = os.environ.get("NOTION_API_KEY", "")
NOTION_DB_ID = os.environ.get("HAGWON_NOTION_DB_ID", "")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def log_to_notion(record: dict) -> bool:
    """Append a send record to the Notion alimtalk log database."""
    if not NOTION_TOKEN or not NOTION_DB_ID:
        print(f"[NOTION LOG] {record}")
        return True

    payload = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "학생": {"title": [{"text": {"content": record.get("student", "")}}]},
            "이벤트": {"select": {"name": record.get("event_type", "기타")}},
            "메시지": {"rich_text": [{"text": {"content": record.get("message", "")[:500]}}]},
            "상태": {"select": {"name": record.get("status", "unknown")}},
            "발송일시": {"date": {"start": datetime.utcnow().isoformat()}},
        },
    }

    resp = requests.post(
        "https://api.notion.com/v1/pages",
        json=payload,
        headers=HEADERS,
        timeout=10,
    )
    return resp.ok
