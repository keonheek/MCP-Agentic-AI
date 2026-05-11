"""
test_shopify_inventory.py
Tests for Shopify client -- orders, customers, webhooks, inventory topic.
All tests use mock transport -- no real API calls.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import hmac
import hashlib
import base64

from src.shopify.client import ShopifyClient
from src.shopify.webhooks import (
    ShopifyWebhookRouter,
    parse_shopify_payload,
    ORDERS_PAID,
    INVENTORY_UPDATE,
    CUSTOMERS_CREATE,
)
from src.unified import Order, Customer


def make_mock(responses: dict):
    def transport(method, url, body):
        sorted_resp = sorted(responses.items(), key=lambda x: len(x[0][1]), reverse=True)
        for (m, url_key), resp in sorted_resp:
            if m == method and url_key in url:
                return resp
        raise ValueError(f"No mock for {method} {url}")
    return transport


MOCK_SHOP = {"shop": {"id": 12345, "name": "Test Skincare Shop", "domain": "testbrand.myshopify.com"}}

MOCK_ORDERS = {
    "orders": [
        {
            "id": 5001,
            "email": "customer@test.com",
            "financial_status": "paid",
            "total_price": "67000.00",
            "created_at": "2026-02-01T11:00:00+09:00",
            "customer": {
                "id": 9001,
                "first_name": "최",
                "last_name": "지연",
                "email": "customer@test.com",
                "phone": "010-3333-4444",
            },
            "line_items": [
                {
                    "product_id": 111,
                    "variant_id": 222,
                    "title": "에센스 30ml",
                    "quantity": 1,
                    "price": "67000.00",
                }
            ],
        }
    ]
}

MOCK_SINGLE_ORDER = {
    "order": {
        "id": 5001,
        "email": "customer@test.com",
        "financial_status": "paid",
        "total_price": "67000.00",
        "created_at": "2026-02-01T11:00:00+09:00",
        "customer": {
            "id": 9001,
            "first_name": "최",
            "last_name": "지연",
            "email": "customer@test.com",
            "phone": "010-3333-4444",
        },
        "line_items": [],
    }
}

MOCK_CUSTOMERS = {
    "customers": [
        {
            "id": 9001,
            "first_name": "최",
            "last_name": "지연",
            "email": "customer@test.com",
            "phone": "010-3333-4444",
            "created_at": "2025-10-01T00:00:00+09:00",
            "orders_count": 4,
            "total_spent": "268000.00",
        }
    ]
}

MOCK_WEBHOOK_CREATE = {"webhook": {"id": 8001, "topic": "orders/paid", "address": "https://myserver.com/webhooks/shopify"}}
MOCK_WEBHOOK_LIST = {
    "webhooks": [
        {"id": 8001, "topic": "orders/paid", "address": "https://myserver.com/webhooks/shopify"}
    ]
}


def _make_client():
    mock = make_mock({
        ("GET", "/shop.json"): MOCK_SHOP,
        ("GET", "/orders.json"): MOCK_ORDERS,
        ("GET", "/orders/5001.json"): MOCK_SINGLE_ORDER,
        ("GET", "/customers.json"): MOCK_CUSTOMERS,
        ("POST", "/webhooks.json"): MOCK_WEBHOOK_CREATE,
        ("GET", "/webhooks.json"): MOCK_WEBHOOK_LIST,
    })
    return ShopifyClient(
        shop_domain="testbrand.myshopify.com",
        access_token="shpat_test_token",
        webhook_secret="shopify_webhook_secret",
        _mock_transport=mock,
    )


# ------------------------------------------------------------------ #
# Tests
# ------------------------------------------------------------------ #

def test_authenticate_returns_true():
    client = _make_client()
    assert client.authenticate() is True


def test_refresh_token_noop():
    """Shopify custom app tokens never expire."""
    client = _make_client()
    result = client.refresh_token()
    assert result is False


def test_list_orders_normalized():
    client = _make_client()
    orders = client.list_orders()
    assert len(orders) == 1
    o = orders[0]
    assert isinstance(o, Order)
    assert o.order_id == "5001"
    assert o.platform == "shopify"
    assert o.customer_name == "최 지연"
    assert o.total_price == 67000
    assert o.status == "paid"
    assert len(o.items) == 1
    assert o.items[0]["title"] == "에센스 30ml"


def test_get_order_normalized():
    client = _make_client()
    o = client.get_order("5001")
    assert isinstance(o, Order)
    assert o.customer_email == "customer@test.com"


def test_list_customers_normalized():
    client = _make_client()
    customers = client.list_customers()
    assert len(customers) == 1
    c = customers[0]
    assert isinstance(c, Customer)
    assert c.customer_id == "9001"
    assert c.total_orders == 4
    assert c.total_spent == 268000


def test_subscribe_webhook():
    client = _make_client()
    result = client.subscribe_webhook("orders/paid", "https://myserver.com/webhooks/shopify")
    assert result.get("webhook", {}).get("topic") == "orders/paid"


def test_list_webhook_subscriptions():
    client = _make_client()
    subs = client.list_webhook_subscriptions()
    assert len(subs) == 1
    assert subs[0]["topic"] == "orders/paid"


def test_verify_webhook_signature_valid():
    secret = "shopify_webhook_secret"
    payload = b'{"id":5001,"financial_status":"paid"}'
    sig = base64.b64encode(
        hmac.new(secret.encode(), payload, hashlib.sha256).digest()
    ).decode()
    client = ShopifyClient("testbrand.myshopify.com", "tok", webhook_secret=secret)
    assert client.verify_webhook_signature(payload, sig) is True


def test_verify_webhook_signature_invalid():
    client = ShopifyClient("testbrand.myshopify.com", "tok", webhook_secret="secret")
    assert client.verify_webhook_signature(b"body", "badsig") is False


def test_parse_webhook_event_with_topic():
    client = _make_client()
    raw = {"_topic": "orders/paid", "id": 5001, "financial_status": "paid"}
    event = client.parse_webhook_event(raw)
    assert event.platform == "shopify"
    assert event.event_type == "orders/paid"
    assert event.event_id == "5001"


def test_webhook_router_dispatches_inventory():
    router = ShopifyWebhookRouter()
    received = []
    router.on(INVENTORY_UPDATE, lambda p: received.append(p.topic))
    router.dispatch({"inventory_item_id": 111, "available": 0}, INVENTORY_UPDATE, "testbrand.myshopify.com")
    assert received == [INVENTORY_UPDATE]


def test_webhook_router_ignores_unregistered():
    router = ShopifyWebhookRouter()
    received = []
    router.on(ORDERS_PAID, lambda p: received.append(p))
    router.dispatch({"id": 1}, CUSTOMERS_CREATE)
    assert received == []


if __name__ == "__main__":
    tests = [
        test_authenticate_returns_true,
        test_refresh_token_noop,
        test_list_orders_normalized,
        test_get_order_normalized,
        test_list_customers_normalized,
        test_subscribe_webhook,
        test_list_webhook_subscriptions,
        test_verify_webhook_signature_valid,
        test_verify_webhook_signature_invalid,
        test_parse_webhook_event_with_topic,
        test_webhook_router_dispatches_inventory,
        test_webhook_router_ignores_unregistered,
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
