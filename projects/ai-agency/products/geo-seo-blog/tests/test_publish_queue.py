"""
test_publish_queue.py
Tests publish queue state management.
Uses a temp directory to avoid touching real client data.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))

import src.blog.publish_queue as pq

# Override CLIENTS_DIR to a temp location for testing
TEMP_DIR = Path(__file__).parent / "_temp_test_clients"


def setup():
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    # Patch the module-level CLIENTS_DIR
    pq.CLIENTS_DIR = TEMP_DIR


def teardown():
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)


def test_add_post_creates_entry():
    setup()
    brand = "테스트브랜드"
    post = pq.add_post(brand, "비타민C 세럼 가이드")
    assert post["topic"] == "비타민C 세럼 가이드"
    assert post["status"] == "pending"
    assert post["due_date"] is not None
    print(f"  Post created: {post['id']}")
    teardown()


def test_add_multiple_posts():
    setup()
    brand = "테스트브랜드"
    pq.add_post(brand, "포스트 1")
    pq.add_post(brand, "포스트 2")
    queue = pq.load_queue(brand)
    assert len(queue) == 2
    print(f"  Queue length: {len(queue)}")
    teardown()


def test_update_status_to_delivered():
    setup()
    brand = "테스트브랜드"
    post = pq.add_post(brand, "포스트 1")
    pq.update_post_status(brand, post["id"], "delivered")
    queue = pq.load_queue(brand)
    assert queue[0]["status"] == "delivered"
    assert queue[0]["delivered_at"] == str(date.today())
    print(f"  Status updated to delivered: {queue[0]['delivered_at']}")
    teardown()


def test_update_status_with_url():
    setup()
    brand = "테스트브랜드"
    post = pq.add_post(brand, "포스트 1")
    url = "https://blog.naver.com/testbrand/1"
    pq.update_post_status(brand, post["id"], "published", published_url=url)
    queue = pq.load_queue(brand)
    assert queue[0]["published_url"] == url
    print(f"  Published URL saved: {url}")
    teardown()


def test_get_pending_posts():
    setup()
    brand = "테스트브랜드"
    p1 = pq.add_post(brand, "포스트 1")
    p2 = pq.add_post(brand, "포스트 2")
    pq.update_post_status(brand, p1["id"], "delivered")
    pending = pq.get_pending_posts(brand)
    assert len(pending) == 1
    assert pending[0]["id"] == p2["id"]
    print(f"  Pending posts: {len(pending)}")
    teardown()


def test_monthly_summary():
    setup()
    brand = "테스트브랜드"
    month = date.today().strftime("%Y-%m")
    p1 = pq.add_post(brand, "포스트 1")
    p2 = pq.add_post(brand, "포스트 2")
    pq.update_post_status(brand, p1["id"], "delivered")
    summary = pq.monthly_summary(brand, month)
    assert summary["total"] == 2
    assert summary["delivered"] == 1
    assert summary["pending"] == 1
    print(f"  Monthly summary: {summary['delivered']}/{summary['total']} delivered ({summary['completion_rate']})")
    teardown()


def test_empty_queue_returns_empty_list():
    setup()
    brand = "새브랜드"
    queue = pq.load_queue(brand)
    assert queue == []
    print(f"  Empty queue: []")
    teardown()


def test_invalid_status_raises():
    setup()
    brand = "테스트브랜드"
    post = pq.add_post(brand, "포스트 1")
    try:
        pq.update_post_status(brand, post["id"], "invalid_status")
        assert False, "Should have raised ValueError"
    except ValueError:
        print(f"  Invalid status raises ValueError: PASS")
    teardown()


if __name__ == "__main__":
    print("=== Publish Queue Tests ===\n")
    test_add_post_creates_entry()
    print("test_add_post_creates_entry: PASS")
    test_add_multiple_posts()
    print("test_add_multiple_posts: PASS")
    test_update_status_to_delivered()
    print("test_update_status_to_delivered: PASS")
    test_update_status_with_url()
    print("test_update_status_with_url: PASS")
    test_get_pending_posts()
    print("test_get_pending_posts: PASS")
    test_monthly_summary()
    print("test_monthly_summary: PASS")
    test_empty_queue_returns_empty_list()
    print("test_empty_queue_returns_empty_list: PASS")
    test_invalid_status_raises()
    print("test_invalid_status_raises: PASS")
    print("\nAll publish queue tests passed.")
