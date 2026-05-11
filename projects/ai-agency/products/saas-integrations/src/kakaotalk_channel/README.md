# KakaoTalk Channel Integration

API: Aligo Alimtalk API (Kakao Business reseller, simplest for new businesses)
Official Kakao: https://business.kakao.com/info/bizmessage/

## Two message types

| Type | Korean | Requires opt-in | Use case |
|---|---|---|---|
| Alimtalk | 알림톡 | No | Order confirmations, shipping, refunds |
| FriendTalk | 친구톡 | Yes (channel friend) | Marketing, promotions |

For e-commerce automation, always use Alimtalk first.

## Registration (Alimtalk sender approval)

1. Register business at https://business.kakao.com.
2. Create a KakaoTalk Channel (카카오톡 채널) in Kakao Business.
3. Apply for Alimtalk sender approval (사업자등록증 required, 2-5 business days).
4. Get Sender Key (발신 프로파일 키) after approval.
5. Register via Aligo (https://smartsms.aligo.in) or direct Kakao Bizmessage reseller.
6. Create and get approval for message templates (template review: 1-3 business days).

## Template format

Templates must be pre-approved. Use #{variable} syntax:

```
안녕하세요 #{name}님,
#{product_name} 주문이 확인되었습니다.
주문번호: #{order_id}
결제금액: #{amount}원
배송 시작 시 안내드리겠습니다.
```

## Rate Limits

| Limit | Value |
|---|---|
| Per second | 500 messages |
| Daily (default) | Negotiated with Kakao/reseller |

Always use send_alimtalk_bulk() for batch sends (max 1,000 per call).

## Environment Variables

```
KAKAO_API_KEY=your_aligo_api_key
KAKAO_USER_ID=your_aligo_user_id
KAKAO_SENDER_KEY=your_sender_profile_key
KAKAO_CHANNEL_ID=@your_channel_name
```
