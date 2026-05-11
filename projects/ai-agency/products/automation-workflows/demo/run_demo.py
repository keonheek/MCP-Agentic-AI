"""
5-flow demo walkthrough.

Run:
    python demo/run_demo.py

Shows all 5 flows firing for their respective customer scenarios.
All Kakao sends are mocked (no real API calls).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
import logging
from datetime import datetime, timedelta, date

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

from src.flows.abandoned_cart import AbandonedCartState, run_touch as cart_run
from src.flows.review_request import ReviewState, run_touch as review_run, submit_review
from src.flows.restock_alert import register_alert, trigger_restock
from src.flows.birthday_discount import BirthdayCustomer, run_daily_batch
from src.flows.winback_inactive import WinbackState, run_touch as winback_run
from src.kakao_sender import reset_daily_counts

DEMO_DATA_PATH = os.path.join(os.path.dirname(__file__), "demo_customers.json")


def load_demo_data() -> dict:
    with open(DEMO_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def print_separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  FLOW: {title}")
    print(f"{'='*60}")


def demo_abandoned_cart(customer: dict, brand: dict) -> None:
    print_separator("장바구니 이탈 복구 (Abandoned Cart)")
    minutes_ago = customer.get("cart_abandoned_minutes_ago", 35)
    state = AbandonedCartState(
        customer_id=customer["customer_id"],
        customer_name=customer["name"],
        customer_phone=customer["phone"],
        customer_email=customer["email"],
        product_name=customer["product"],
        product_url=brand["product_url"],
        brand_name=brand["name"],
        cart_abandoned_at=datetime.utcnow() - timedelta(minutes=minutes_ago),
        discount_code=f"CART10-{customer['customer_id']}",
    )
    state = cart_run(state, mock=True)
    if minutes_ago >= 1440:
        state.cart_abandoned_at = datetime.utcnow() - timedelta(hours=25)
        state = cart_run(state, mock=True)
    print(f"  Touches sent: {state.touches_sent}")


def demo_review_request(customer: dict, brand: dict) -> None:
    print_separator("구매 후 리뷰 요청 (Review Request)")
    state = ReviewState(
        customer_id=customer["customer_id"],
        customer_name=customer["name"],
        customer_phone=customer["phone"],
        product_name=customer["product"],
        review_url=brand["review_url"],
        brand_ig=brand["instagram"],
        founder_phone=brand["founder_phone"],
        delivered_at=datetime.utcnow() - timedelta(days=customer.get("delivered_days_ago", 8)),
    )
    state = review_run(state, mock=True)
    if customer.get("scenario") == "review_request_negative":
        state = submit_review(state, "별로예요. 환불하고 싶어요.")
    else:
        state = submit_review(state, "완전 좋아요! 재구매 확정이에요. 별5점!")
    state = review_run(state, mock=True)
    print(f"  Sentiment: {state.sentiment} | IG requested: {state.ig_requested} | Escalated: {state.escalated}")


def demo_restock(customers: list[dict], brand: dict) -> None:
    print_separator("재입고 알림 (Restock Alert)")
    restock_customers = [c for c in customers if c.get("scenario") == "restock_alert"]
    for c in restock_customers:
        product_id = c.get("restock_product_id", "PROD-001")
        register_alert(product_id, c["customer_id"], c["name"], c["phone"])
        print(f"  Registered: {c['name']} for {c['product']}")

    product_id = restock_customers[0].get("restock_product_id") if restock_customers else "PROD-001"
    count = trigger_restock(product_id, restock_customers[0]["product"], brand["product_url"], mock=True)
    print(f"  Restock alerts sent: {count}")


def demo_birthday(customers: list[dict], brand: dict) -> None:
    print_separator("생일 쿠폰 (Birthday Discount)")
    today = date(2026, 5, 11)
    birthday_customers = [
        BirthdayCustomer(
            customer_id=c["customer_id"],
            customer_name=c["name"],
            customer_phone=c["phone"],
            birthday=date.fromisoformat(c["birthday"]).replace(year=2026),
            brand_name=brand["name"],
            discount_code=f"BDAY15-{c['customer_id']}",
        )
        for c in customers if c.get("scenario") == "birthday_discount"
    ]
    # Override birthday to be exactly 7 days from demo date for demo effect
    for bc in birthday_customers:
        bc.birthday = date(2026, 5, 18)
    sent = run_daily_batch(birthday_customers, today=today, mock=True)
    print(f"  Birthday messages sent today: {sent}")


def demo_winback(customers: list[dict], brand: dict) -> None:
    print_separator("휴면 고객 복구 (Win-Back)")
    winback_customers = [c for c in customers if c.get("scenario") == "winback_inactive"]
    for c in winback_customers:
        state = WinbackState(
            customer_id=c["customer_id"],
            customer_name=c["name"],
            customer_phone=c["phone"],
            brand_name=brand["name"],
            product_url=brand["product_url"],
            last_purchase_at=datetime.utcnow() - timedelta(days=c.get("days_inactive", 91)),
        )
        for _ in range(3):
            state = winback_run(state, mock=True)
        print(f"  {c['name']} touches sent: {state.touches_sent}")


def main() -> None:
    print("\n스킨로직 x 1stmover AI 자동화 데모")
    print("5개 자동화 플로우 시연")

    reset_daily_counts()
    data = load_demo_data()
    brand = data["brand"]
    customers = data["customers"]

    cart_customers = [c for c in customers if c.get("scenario", "").startswith("abandoned_cart")]
    for c in cart_customers:
        demo_abandoned_cart(c, brand)

    review_customers = [c for c in customers if "review" in c.get("scenario", "")]
    for c in review_customers:
        demo_review_request(c, brand)

    demo_restock(customers, brand)
    demo_birthday(customers, brand)
    demo_winback(customers, brand)

    print("\n" + "="*60)
    print("  데모 완료. 모든 Kakao 발송은 Mock (실제 발송 없음)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
