# Shopify Integration

API version: 2025-04 (stable)
Docs: https://shopify.dev/docs/api/admin-rest

## Required Credentials

| Credential | Where to Get |
|---|---|
| Shop domain | e.g. mybrand.myshopify.com |
| Access token | Shopify Admin > Apps > Create custom app > Install |
| Webhook secret | Same app settings page |

## Recommended: Custom App (not OAuth)

For agency client integrations, use Custom App tokens. No OAuth redirect, no public app approval needed.

1. Client opens Shopify Admin > Settings > Apps and sales channels > Develop apps.
2. Create custom app, set API scopes (see below).
3. Install app. Copy Admin API access token (shown once).
4. Copy webhook signing secret from Webhooks section.

## Required API Scopes

| Scope | Used for |
|---|---|
| read_orders | list_orders, get_order |
| read_customers | list_customers |
| write_webhooks | subscribe_webhook |

## Webhook Notes

- Shopify sends topic in `X-Shopify-Topic` header, not JSON body.
- Signature in `X-Shopify-Hmac-Sha256` header (Base64 HMAC-SHA256).
- Your endpoint must pass topic to `parse_webhook_event()` via `raw["_topic"]`.

## Rate Limits

- REST API: 2 requests/second (leaky bucket, burst to 40)
- Shopify-plus accounts get higher limits
- Use GraphQL for high-volume read operations

## Environment Variables

```
SHOPIFY_SHOP_DOMAIN=mybrand.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxx
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret
```
