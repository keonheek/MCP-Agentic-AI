# Claude Project Template — AI 영상 광고 에이전시

이 폴더의 5개 파일을 Claude Project에 업로드하면 클라이언트별 foundational docs 생성 품질이 크게 높아진다.

## 설정 방법 (1회, ~5분)

1. claude.ai 접속 → 왼쪽 "Projects" → "New Project"
2. 이름: "Beauty D2C Foundational Docs"
3. "Project knowledge" 섹션에 이 폴더 5개 파일 모두 업로드:
   - 01-korean-dr-copy-reference.md
   - 02-schwartz-awareness-guide.md
   - 03-ad-law-risk-audit.md
   - 04-ltv-cac-template.md
   - 05-hormozi-offer-framework.md
4. Project URL을 .env 또는 setup.md에 기록

## 클라이언트별 사용법

새 클라이언트 시작 시:
1. 이 Project 열기
2. `clients/<slug>/voc-<slug>.json` 내용 붙여넣기
3. `/foundational-docs <slug>` 실행

## 주의

- 파일 내용 변경 시 Project에 재업로드 필요
- 한의원 ICP용은 별도 Project 생성 권장 (광고법 규정 다름)
