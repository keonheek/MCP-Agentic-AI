"""
test_unified_interface.py
Tests that all platform clients satisfy the PlatformAdapter ABC contract,
and that Order/Customer dataclasses are consistent across platforms.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import hmac
import hashlib
import base64

from src.unified import PlatformAdapter, Order, Customer, WebhookEvent
from src.cafe24.client import Cafe24Client
from src.imweb.client import ImwebClient
from src.smartstore.client import SmartStoreClient
from src.shopify.client import ShopifyClient


# ------------------------------------------------------------------ #
# Shared mock helpers
# ------------------------------------------------------------------ #

MOCK_ORDER_RAW = {
    "order_id": "UNIFIED-001",
    "buyer": {"member_id": "M1", "name": "통합테스트", "email": "unified@test.com", "phone": "010-0000-0001"},
    "order_status": "paid",
    "order_price_amount": {"order_price": 50000},
    "items": [],
    "created_date": "2026-03-01T12:00:00+09:00",
}


def make_null_mock():
    """Returns minimal passing responses for each client."""
    def transport(method, url, body):
        return {}
    return transport


def make_order_mock(platform: str):
    """Mock that returns a platform-appropriate order response."""
    responses = {
        "cafe24": {
            ("GET", "/me"): {"mall": {}},
            ("GET", "/orders"): {"orders": [MOCK_ORDER_RAW]},
            ("GET", "/orders/UNIFIED-001"): {"order": MOCK_ORDER_RAW},
            ("GET", "/customers"): {"customers": []},
            ("POST", "/webhooks"): {"webhook": {}},
            ("GET", "/webhooks"): {"webhooks": []},
        },
        "imweb": {
            ("POST", "auth/token"): {"code": 200, "data": {"access_token": "tok"}},
            ("GET", "shop/orders"): {"code": 200, "data": {"list": []}},
            ("GET", "member/members"): {"code": 200, "data": {"list": []}},
            ("POST", "api/hook"): {"code": 200},
            ("GET", "api/hook"): {"code": 200, "data": {"list": []}},
        },
        "smartstore": {
            ("POST", "oauth2/token"): {"access_token": "tok", "expires_in": 1800},
            ("POST", "product-orders/query"): {"data": {"contents": []}},
            ("POST", "notification/register"): {"data": {}},
            ("GET", "notification/list"): {"data": []},
        },
        "shopify": {
            ("GET", "/shop.json"): {"shop": {"id": 1}},
            ("GET", "/orders.json"): {"orders": []},
            ("GET", "/customers.json"): {"customers": []},
            ("POST", "/webhooks.json"): {"webhook": {}},
            ("GET", "/webhooks.json"): {"webhooks": []},
        },
    }

    def transport(method, url, body):
        for (m, url_key), resp in responses[platform].items():
            if m == method and url_key in url:
                return resp
        return {}

    return transport


# ------------------------------------------------------------------ #
# ABC conformance tests
# ------------------------------------------------------------------ #

def test_cafe24_is_platform_adapter():
    client = Cafe24Client("mall", "id", "secret", "tok", _mock_transport=make_null_mock())
    assert isinstance(client, PlatformAdapter)


def test_imweb_is_platform_adapter():
    client = ImwebClient("key", "secret", "tok", _mock_transport=make_null_mock())
    assert isinstance(client, PlatformAdapter)


def test_smartstore_is_platform_adapter():
    client = SmartStoreClient("id", "secret", "tok", _mock_transport=make_null_mock())
    assert isinstance(client, PlatformAdapter)


def test_shopify_is_platform_adapter():
    client = ShopifyClient("domain.myshopify.com", "tok", _mock_transport=make_null_mock())
    assert isinstance(client, PlatformAdapter)


# ------------------------------------------------------------------ #
# Platform name tests
# ------------------------------------------------------------------ #

def test_platform_names():
    assert Cafe24Client("m", "i", "s", "t").platform_name == "cafe24"
    assert ImwebClient("k", "s", "t").platform_name == "imweb"
    assert SmartStoreClient("i", "s", "t").platform_name == "smartstore"
    assert ShopifyClient("d", "t").platform_name == "shopify"


# ------------------------------------------------------------------ #
# Order shape consistency
# ------------------------------------------------------------------ #

def test_order_dataclass_fields():
    """Order must have all required fields across all platforms."""
    o = Order(
        order_id="test",
        platform="test_platform",
        customer_id="c1",
        customer_name="테스트",
        customer_email="t@test.com",
        customer_phone="010-0000-0000",
        status="paid",
        total_price=50000,
        items=[],
        created_at="2026-01-01",
    )
    assert o.order_id == "test"
    assert o.platform == "test_platform"
    assert o.total_price == 50000
    assert isinstance(o.items, list)
    assert isinstance(o.raw, dict)


def test_customer_dataclass_fields():
    c = Customer(
        customer_id="c1",
        platform="cafe24",
        name="김건희",
        email="keonhee@test.com",
        phone="010-0000-0000",
        joined_at="2025-01-01",
        total_orders=3,
        total_spent=100000,
    )
    assert c.customer_id == "c1"
    assert c.total_spent == 100000
    assert isinstance(c.raw, dict)


def test_webhook_event_dataclass_fields():
    event = WebhookEvent(
        event_id="ev001",
        platform="cafe24",
        event_type="order_paid",
        payload={"order_id": "ORD001"},
    )
    assert event.event_id == "ev001"
    assert event.event_type == "order_paid"
    assert isinstance(event.received_at, float)


# ------------------------------------------------------------------ #
# Cross-platform list_orders returns same Order type
# ------------------------------------------------------------------ #

def test_cafe24_list_orders_returns_order_instances():
    client = Cafe24Client("mall", "id", "secret", "tok", _mock_transport=make_order_mock("cafe24"))
    orders = client.list_orders()
    assert all(isinstance(o, Order) for o in orders)


def test_imweb_list_orders_returns_order_instances():
    client = ImwebClient("key", "secret", "tok", _mock_transport=make_order_mock("imweb"))
    orders = client.list_orders()
    assert all(isinstance(o, Order) for o in orders)


def test_smartstore_list_orders_returns_order_instances():
    client = SmartStoreClient("id", "secret", "tok", _mock_transport=make_order_mock("smartstore"))
    client._token_expires_at = time.time() + 3600
    orders = client.list_orders()
    assert all(isinstance(o, Order) for o in orders)


def test_shopify_list_orders_returns_order_instances():
    client = ShopifyClient("d.myshopify.com", "tok", _mock_transport=make_order_mock("shopify"))
    orders = client.list_orders()
    assert all(isinstance(o, Order) for o in orders)


# ------------------------------------------------------------------ #
# health_check shape
# ------------------------------------------------------------------ #

def test_cafe24_health_check_shape():
    client = Cafe24Client("mall", "id", "secret", "tok", _mock_transport=make_order_mock("cafe24"))
    result = client.health_check()
    assert "platform" in result
    assert "status" in result
    assert result["platform"] == "cafe24"


if __name__ == "__main__":
    tests = [
        test_cafe24_is_platform_adapter,
        test_imweb_is_platform_adapter,
        test_smartstore_is_platform_adapter,
        test_shopify_is_platform_adapter,
        test_platform_names,
        test_order_dataclass_fields,
        test_customer_dataclass_fields,
        test_webhook_event_dataclass_fields,
        test_cafe24_list_orders_returns_order_instances,
        test_imweb_list_orders_returns_order_instances,
        test_smartstore_list_orders_returns_order_instances,
        test_shopify_list_orders_returns_order_instances,
        test_cafe24_health_check_shape,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed}/{passed+failed} passed")
