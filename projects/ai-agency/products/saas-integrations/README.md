# SaaS Integrations

채널톡 + 카페24 + 네이버 스마트스토어 + 카카오 알림톡 + Make.com을 n8n self-host로 묶고 PIPA Tier P 옵션을 제공하는 한국 D2C 운영 통합자.

슬라이드가 아니라 작동하는 시스템을 인도합니다. (We deliver working systems, not slides.)

**₩200K/월 retainer = ops engineer 4시간 = 월 1회 장애 예방시 손익분기.**

Korean e-commerce platform connectors for Service A automation flows.

---

## Supported Platforms

| Platform | Market Share | Auth Method | Token Expiry |
|---|---|---|---|
| Cafe24 | 60% | OAuth 2.0 | 2 hours (refresh 14 days) |
| Imweb | 20% | API Key/Secret | 24 hours |
| Smart Store (Naver) | 15% | HMAC-signed client credentials | 30 minutes |
| Shopify | 5% | Custom App access token | Never |

Plus two supporting services:

| Service | Purpose |
|---|---|
| KakaoTalk Channel (Alimtalk) | Transactional notifications |
| Channel.io | Live chat + human handoff |

---

## Architecture

All platform clients extend `PlatformAdapter` (ABC in `src/unified.py`).
Every platform normalizes into the same `Order` and `Customer` dataclasses.

```
Webhook arrives -> verify_webhook_signature() -> parse_webhook_event()
    -> WebhookEvent -> automation trigger -> KakaoTalk Alimtalk send
```

---

## Quick Start

```bash
python demo/run_demo.py
python tests/test_cafe24_auth.py
python tests/test_unified_interface.py
```

---

## Business Documents

- `pricing.md` - 4-tier pricing + per-platform rates
- `sla.md` - Uptime guarantees, response times
- `proposal-template.md` - Client proposal (Korean)
- `onboarding.md` - Per-platform setup checklist (Korean)

---

## Environment Variables

```
CAFE24_MALL_ID=
CAFE24_CLIENT_ID=
CAFE24_CLIENT_SECRET=
CAFE24_ACCESS_TOKEN=
CAFE24_REFRESH_TOKEN=
IMWEB_API_KEY=
IMWEB_API_SECRET=
SMARTSTORE_APPLICATION_ID=
SMARTSTORE_APPLICATION_SECRET=
SHOPIFY_SHOP_DOMAIN=
SHOPIFY_ACCESS_TOKEN=
SHOPIFY_WEBHOOK_SECRET=
KAKAO_API_KEY=
KAKAO_SENDER_KEY=
KAKAO_CHANNEL_ID=
CHANNELIO_ACCESS_KEY=
CHANNELIO_CHANNEL_ID=
CHANNELIO_WEBHOOK_TOKEN=
```

---

## 요금제 (에이전시 공통 4단계)

에이전시 공통 4단계 요금제

| 티어 | 설치비 | 월 유지비 | 범위 |
|---|---|---|---|
| DEMO | ₩500K | 없음 | 1개 시나리오, 5일 납품 |
| STARTER | ₩2M | ₩200K | 3-5개 시나리오, Make-to-n8n 마이그레이션, 14일 납품 |
| D2C STACK | ₩5M | ₩500K | 화장품 D2C 풀스택 (카카오 + 카페24 + 이메일 + GPT + RFM) |
| D2C STACK + PIPA Tier P | ₩8M | ₩1M | 위 전체 + DB 분리 + 접근 제어 + 감사 |

₩200K/월 retainer = ops engineer 4시간 = 월 1회 장애 예방시 손익분기.

자세한 요금제: 
