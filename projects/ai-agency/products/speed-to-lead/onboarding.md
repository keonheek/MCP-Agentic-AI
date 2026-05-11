# Speed-to-Lead 클라이언트 온보딩 체크리스트

_담당자: 1stmover 김건희_

---

## 사전 준비 (건희 진행)

- [ ] 클라이언트 슬러그 확정 (예: glow-lab, pure-skin)
- [ ] `clients/{slug}/config.yaml` 파일 생성
- [ ] Notion 클라이언트 DB에 신규 행 추가
- [ ] 계약 티어 확인 (DEMO / STARTER / D2C STACK / D2C STACK + PIPA)

---

## Step 1. 카카오톡 채널 API 설정 (클라이언트 진행, 약 30분)

1. center-pf.kakao.com 접속 후 로그인
2. "챗봇" -> "API형" -> API 메시지 토큰 발급
3. 발급된 토큰을 건희에게 카카오톡으로 전달
4. 웹훅 URL 입력: `https://[NGROK_DOMAIN]/webhook/[CLIENT_SLUG]`

---

## Step 2. 브랜드 설정 파일 구성 (건희 진행)

`clients/{slug}/config.yaml`:

```
brand_name: 브랜드명
brand_voice: 응답 톤
kakao_access_token: Step 1에서 받은 토큰
kakao_channel_id: 카카오 채널 ID
notion_db_id: 로그 저장용 Notion DB ID
product_catalog: 주요 제품 목록 (STARTER 이상)
faq: 자주 묻는 질문 (STARTER 이상)
owner_kakao_user_key: 에스컬레이션 알림 사장님 user_key
owner_phone: SMS 백업 연락처
```

---

## Step 3. Notion 대시보드 설정

속성: 고객ID, 문의내용, 카테고리, 신뢰도, 자동답변, 에스컬레이션, Eval점수, 처리시각

---

## Step 4. 서버 배포 및 테스트

```bash
cd projects/ai-agency/services/automation
python speed_to_lead.py
ngrok http 5000 --domain=[RESERVED_DOMAIN]
python test_webhook.py --slug [CLIENT_SLUG]
```

목표: 6/6 통과.

---

## Step 5. 실문의 테스트 (클라이언트 참여)

5개 문의 유형 직접 입력 후 90초 이내 자동응답 + Notion 기록 확인.

---

## Step 6. D2C STACK 이상 추가 항목

- n8n NCP 배포 확인
- 카페24/스마트스토어 웹훅 연동
- RFM 세그먼트 초기 설정
- PIPA Tier P: 국외 이전 고지 문구, DB 격리 확인

---

## 완료 기준

- [ ] 6/6 자동화 테스트 통과
- [ ] 실문의 5건 90초 이내 확인
- [ ] 에스컬레이션 알림 수신 확인
- [ ] Notion 대시보드 공유 완료
