# Cafe24 Integration

API version: 2026-03-01
Docs: https://developers.cafe24.com/docs/api/admin/

## Required OAuth Scopes

| Scope | Used for |
|---|---|
| mall.read_order | list_orders, get_order |
| mall.read_customer | list_customers |
| mall.write_webhooks | subscribe_webhook, list_webhook_subscriptions |

## Auth Setup

1. Register app at https://developers.cafe24.com and get Client ID + Client Secret.
2. Set redirect URI to your callback endpoint (e.g. https://yourserver.com/auth/cafe24/callback).
3. Direct client to authorization URL:

```
https://{mall_id}.cafe24api.com/api/v2/oauth/authorize
  ?response_type=code
  &client_id={client_id}
  &redirect_uri={redirect_uri}
  &scope=mall.read_order,mall.read_customer,mall.write_webhooks
  &state={csrf_token}
```

4. Exchange code for tokens:

```
POST https://{mall_id}.cafe24api.com/api/v2/oauth/token
Authorization: Basic base64({client_id}:{client_secret})
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&code={code}&redirect_uri={redirect_uri}
```

5. Store `access_token` and `refresh_token`. Access tokens expire in 2 hours. Refresh tokens expire in 14 days.
6. Use `Cafe24Client.refresh_token()` before each batch job.

## Webhook Signature Verification

Cafe24 signs webhook requests with HMAC-SHA256 using your `client_secret`.
Header: `X-Cafe24-Signature`

Always verify before processing.

## Rate Limits (2026-03-01)

- 2 requests per second per mall
- 2,000 requests per hour per mall
- Batch endpoints have separate limits (documented per endpoint)

## Environment Variables

```
CAFE24_MALL_ID=mymall
CAFE24_CLIENT_ID=your_client_id
CAFE24_CLIENT_SECRET=your_client_secret
CAFE24_ACCESS_TOKEN=...
CAFE24_REFRESH_TOKEN=...
```
