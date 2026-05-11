"""
run_demo.py
Side-by-side demo: same order paid event processed through all 4 platform adapters.

Loads demo_orders.json, normalizes each platform's payload via the respective adapter,
and prints a unified Order comparison table.

Run:
    python demo/run_demo.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cafe24.client import Cafe24Client
from src.imweb.client import ImwebClient
from src.smartstore.client import SmartStoreClient
from src.shopify.client import ShopifyClient
from src.unified import Order


DEMO_FILE = os.path.join(os.path.dirname(__file__), "demo_orders.json")


def null_transport(method, url, body):
    return {}


def load_demo():
    with open(DEMO_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_cafe24(raw: dict) -> Order:
    client = Cafe24Client("demo", "id", "secret", "tok", _mock_transport=null_transport)
    return client._normalize_order(raw)


def normalize_imweb(raw: dict) -> Order:
    client = ImwebClient("key", "secret", "tok", _mock_transport=null_transport)
    return client._normalize_order(raw)


def normalize_smartstore(raw: dict) -> Order:
    client = SmartStoreClient("id", "secret", "tok", _mock_transport=null_transport)
    return client._normalize_order(raw)


def normalize_shopify(raw: dict) -> Order:
    client = ShopifyClient("demo.myshopify.com", "tok", _mock_transport=null_transport)
    return client._normalize_order(raw)


def print_order_table(orders: list[tuple[str, Order]]):
    print("\n" + "=" * 80)
    print("  PLATFORM COMPARISON: Order Paid Event")
    print("=" * 80)

    fields = [
        ("order_id", "Order ID"),
        ("platform", "Platform"),
        ("customer_name", "Customer"),
        ("customer_email", "Email"),
        ("customer_phone", "Phone"),
        ("status", "Status"),
        ("total_price", "Total (KRW)"),
        ("created_at", "Created At"),
    ]

    label_width = 16
    col_width = 28

    header = f"{'Field':<{label_width}}" + "".join(f"{name:<{col_width}}" for _, name in [("", p) for p, _ in orders])
    print(f"\n{'Field':<{label_width}}" + "".join(f"{platform:<{col_width}}" for platform, _ in orders))
    print("-" * (label_width + col_width * len(orders)))

    for attr, label in fields:
        row = f"{label:<{label_width}}"
        for _, order in orders:
            val = str(getattr(order, attr, ""))
            if len(val) > col_width - 2:
                val = val[:col_width - 5] + "..."
            row += f"{val:<{col_width}}"
        print(row)

    print("-" * (label_width + col_width * len(orders)))
    print("\nAll 4 platforms produce the same Order shape.")
    print("Service A automation flows consume Order objects -- no platform-specific code needed.\n")


def main():
    demo = load_demo()
    print(f"\nScenario: {demo['scenario']}")
    print(f"Description: {demo['description']}")

    orders = [
        ("Cafe24", normalize_cafe24(demo["cafe24"])),
        ("Imweb", normalize_imweb(demo["imweb"])),
        ("SmartStore", normalize_smartstore(demo["smartstore"])),
        ("Shopify", normalize_shopify(demo["shopify"])),
    ]

    print_order_table(orders)

    print("Item counts per platform:")
    for platform, order in orders:
        print(f"  {platform}: {len(order.items)} item(s)")

    print("\nWebhook event flow simulation:")
    print("  1. Platform fires order.paid webhook to your endpoint")
    print("  2. verify_webhook_signature() validates HMAC")
    print("  3. parse_webhook_event() -> WebhookEvent")
    print("  4. Automation trigger: send Alimtalk via KakaoTalk Channel")
    print("  5. If customer contacts support: Channel.io handoff flow")
    print()


if __name__ == "__main__":
    main()
