# 플랫폼별 온보딩 체크리스트

클라이언트 계약 체결 후 실행 순서.

---

## Cafe24

**클라이언트 준비**
- [ ] Cafe24 관리자 로그인
- [ ] 우리 개발자 앱 설치 허용
- [ ] 권한 동의: 주문 조회, 회원 조회, 웹훅 관리

**에이전시 진행**
- [ ] OAuth 인증 코드 수신 확인
- [ ] Access Token / Refresh Token 교환 완료
- [ ] 웹훅 등록: order_paid, member_join
- [ ] 테스트 주문으로 웹훅 수신 확인

---

## Imweb

**클라이언트 준비**
- [ ] Settings -> Developer -> API 메뉴 접속
- [ ] API Key, API Secret 발급 후 에이전시에 전달
- [ ] 권한 체크: 주문 읽기, 회원 읽기, 웹훅 관리, 상품 읽기

**에이전시 진행**
- [ ] 토큰 인증 테스트
- [ ] 웹훅 등록: order.pay, member.create
- [ ] 24시간 토큰 자동 갱신 스케줄러 설정

---

## 스마트스토어 (Naver Commerce API)

**클라이언트 준비**
- [ ] Commerce API 신청 (사업자등록증 필요, 심사 2-5 영업일)
- [ ] Application ID, Application Secret 발급 후 전달

**에이전시 진행**
- [ ] 서명 기반 인증 테스트
- [ ] 알림 등록: PAYMENT_DONE, PURCHASE_DECIDED
- [ ] 30분 토큰 자동 갱신 스케줄러 확인

---

## Shopify

**클라이언트 준비**
- [ ] Settings -> Apps -> Develop apps
- [ ] API scopes: read_orders, read_customers, write_webhooks
- [ ] Admin API access token + Webhook signing secret 에이전시에 전달

**에이전시 진행**
- [ ] Access token 유효성 확인 (GET /shop.json)
- [ ] 웹훅 등록: orders/paid, customers/create

---

## 카카오톡 채널 (알림톡)

**클라이언트 준비**
- [ ] 카카오 비즈니스 계정 생성 (business.kakao.com)
- [ ] 알림톡 발신자 승인 신청 (사업자등록증 필요, 2-5 영업일)
- [ ] 발신 프로파일 키 발급 후 전달

**에이전시 진행**
- [ ] 알림톡 템플릿 작성 및 심사 제출
- [ ] 템플릿 승인 후 테스트 발송

---

## 채널톡

**클라이언트 준비**
- [ ] Settings -> Developers -> API에서 Channel Access Secret, Channel ID, 웹훅 서명 토큰 전달

**에이전시 진행**
- [ ] API 접속 테스트
- [ ] 웹훅 등록: userChatCreated, messageCreated
- [ ] 자동 응답 흐름 + 담당자 핸드오프 설정

---

## 최종 Go-Live 체크리스트

- [ ] 모든 플랫폼 웹훅 수신 확인 완료
- [ ] 알림톡 템플릿 승인 완료
- [ ] 실서비스 테스트 주문 1건 엔드투엔드 완료
- [ ] 클라이언트 담당자 운영 가이드 전달
- [ ] 레테이너 첫 달 입금 확인
