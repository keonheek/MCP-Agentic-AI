# Google Forms 자동 생성 스크립트 — 사용 방법

## 준비물
- Google 계정
- 약 10분

---

## Step 1: Google Sheet 만들기

1. Google Drive에서 새 스프레드시트 만들기
2. 시트 이름: "Questions"
3. 1행에 헤더 입력:

| A | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Chapter | Question | A | B | C | D | Answer | Explanation |

---

## Step 2: 질문 데이터 붙여넣기

- `questions_sheet_data.tsv` 파일의 내용을 A2 셀부터 붙여넣기
- (파일 열고 전체 선택 → 복사 → 시트 A2 셀에 붙여넣기)

---

## Step 3: Apps Script 설치

1. 스프레드시트 상단 메뉴: **확장 프로그램 → Apps Script**
2. 기존 코드 전체 삭제
3. `create_forms.gs` 파일의 내용 전체 복사 → 붙여넣기
4. **저장** (Ctrl+S)

---

## Step 4: 스크립트 실행

1. 함수 선택 드롭다운에서 `createAllForms` 선택
2. **실행** 버튼 클릭
3. 처음 실행 시 권한 요청 → "허용"
4. 완료까지 약 2-3분 대기

---

## Step 5: 결과 확인

- Google Drive에 "경제학 개론 — 제N장" 폼 9개 자동 생성
- 각 폼: 퀴즈 모드 활성화, 오답 시 해설 표시
- 링크를 복사해서 카카오톡으로 전송
