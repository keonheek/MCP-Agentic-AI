"""
publish_queue.py
Tracks blog post delivery status per client.
Wraps the monitoring pattern from geo-agency/loop6_geo_monitor.py.

State file: per-client JSON at clients/<brand>/publish_queue.json
"""

import sys
import json
from datetime import date, datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parents[2]
CLIENTS_DIR = HERE.parent.parent / "clients"

STATUS_OPTIONS = ["pending", "drafted", "delivered", "published", "overdue"]
DELIVERY_DAY = 4  # Friday = 4 (Monday = 0)


def _client_queue_path(brand_name: str) -> Path:
    safe = brand_name.replace(" ", "_").lower()
    return CLIENTS_DIR / safe / "publish_queue.json"


def load_queue(brand_name: str) -> list[dict]:
    path = _client_queue_path(brand_name)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_queue(brand_name: str, queue: list[dict]):
    path = _client_queue_path(brand_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def add_post(brand_name: str, topic: str, due_date: str = None) -> dict:
    """
    Adds a new post to the delivery queue.

    Args:
        brand_name: Client brand name
        topic: Blog post topic/title
        due_date: ISO date string (YYYY-MM-DD). Defaults to next Friday.

    Returns:
        The new post dict
    """
    if due_date is None:
        today = date.today()
        days_ahead = DELIVERY_DAY - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        due_date = str(today + timedelta(days=days_ahead))

    post = {
        "id": f"{brand_name}_{date.today().isoformat()}_{len(load_queue(brand_name)) + 1:03d}",
        "topic": topic,
        "status": "pending",
        "due_date": due_date,
        "created_at": str(date.today()),
        "delivered_at": None,
        "published_url": None,
        "notes": "",
    }
    queue = load_queue(brand_name)
    queue.append(post)
    save_queue(brand_name, queue)
    return post


def update_post_status(brand_name: str, post_id: str, status: str, published_url: str = None):
    """Updates status and optionally published_url of a post."""
    if status not in STATUS_OPTIONS:
        raise ValueError(f"Invalid status: {status}. Must be one of {STATUS_OPTIONS}")

    queue = load_queue(brand_name)
    for post in queue:
        if post["id"] == post_id:
            post["status"] = status
            if status == "delivered":
                post["delivered_at"] = str(date.today())
            if published_url:
                post["published_url"] = published_url
            break
    save_queue(brand_name, queue)


def get_pending_posts(brand_name: str) -> list[dict]:
    """Returns posts with status 'pending' or 'drafted'."""
    queue = load_queue(brand_name)
    return [p for p in queue if p["status"] in ("pending", "drafted")]


def get_overdue_posts(brand_name: str) -> list[dict]:
    """Returns posts past due date and not yet delivered."""
    today = date.today()
    queue = load_queue(brand_name)
    overdue = []
    for post in queue:
        if post["status"] in ("pending", "drafted"):
            due = datetime.fromisoformat(post["due_date"]).date()
            if due < today:
                post["status"] = "overdue"
                overdue.append(post)
    if overdue:
        save_queue(brand_name, queue)
    return overdue


def monthly_summary(brand_name: str, month: str = None) -> dict:
    """
    Returns delivery summary for a given month.

    Args:
        brand_name: Client brand
        month: YYYY-MM string. Defaults to current month.
    """
    if month is None:
        month = date.today().strftime("%Y-%m")

    queue = load_queue(brand_name)
    month_posts = [p for p in queue if p.get("due_date", "").startswith(month)]

    delivered = [p for p in month_posts if p["status"] in ("delivered", "published")]
    pending = [p for p in month_posts if p["status"] in ("pending", "drafted")]
    overdue = [p for p in month_posts if p["status"] == "overdue"]

    return {
        "brand": brand_name,
        "month": month,
        "total": len(month_posts),
        "delivered": len(delivered),
        "pending": len(pending),
        "overdue": len(overdue),
        "completion_rate": f"{round(len(delivered) / max(len(month_posts), 1) * 100)}%",
        "posts": month_posts,
    }


if __name__ == "__main__":
    # Smoke test
    brand = "글로우랩"
    post = add_post(brand, "비타민C 세럼 효과 완벽 가이드")
    print(f"Added: {post['id']} | Due: {post['due_date']}")
    summary = monthly_summary(brand)
    print(f"Monthly summary: {summary['delivered']}/{summary['total']} delivered")
