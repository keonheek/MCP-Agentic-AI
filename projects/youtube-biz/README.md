# YouTube Biz — 컨텐츠 자동화 사업

건희 + 영범 파트너십. 3채널 공통 코어 인프라.

## 현재 Phase

**Phase 0 (진행 중):** 계약 확정 + 인프라 셋업

| 항목 | 상태 |
|---|---|
| Sing It 계약 | 협상 중 |
| 영범 내부 계약 | 초안 (`config/partner-agreement.md`) |
| 인프라 구현 | 완료 |
| Smoke test | OK 33/37 (ffmpeg PATH 설정 필요) |

## 채널 로드맵

| Phase | 채널 | 상태 |
|---|---|---|
| 1 | Sing It 파트너십 (음악 번역 Shorts) | 준비 완료 |
| 2 | AI 자동화 채널 (Shorts + Stories) | 대기 |
| 3 | 한국 정치 롱폼 (시니어 타겟) | 대기 |

## 셋업

```bash
# 1. 패키지 설치
bash scripts/setup.sh

# 2. .env 파일에 API 키 입력
cp .env.example .env
# ANTHROPIC_API_KEY, YOUTUBE_CLIENT_ID 등 입력

# 3. ffmpeg 설치 (https://ffmpeg.org/download.html)
# PATH에 등록 필요

# 4. Smoke test
python scripts/run_phase0_smoketest.py

# 5. Dry run (실제 업로드 없이 파이프라인 검증)
python pipelines/singit_daily.py --dry-run

# 6. 실제 실행
python pipelines/singit_daily.py
```

## 디렉토리 구조

```
core/
  layer1_ingestion/   # 뉴스/트렌딩 수집
  layer2_intelligence/ # 채점 + 스크립트 + 품질 루프
  layer3_media/singit/ # 다운로드 + 편집 + 자막
  layer4_publishing/  # YouTube/Instagram 업로드
  layer5_crosspost/   # 크로스포스팅 (Phase 2)
  observability/      # UTM + Obsidian KPI 리포트
pipelines/            # 채널별 일일 실행 엔트리
data/                 # inbox, scripts, renders, archive
logs/                 # 파이프라인 실행 로그
config/               # 채널 설정, 소스, 훅 라이브러리
```

## Phase 1 KPI

| 지표 | 목표 |
|---|---|
| 주간 Shorts | 5개 이상 |
| 채널 구독자 | 1,000+ |
| Sing It 링크 CTR | 1.0%+ |
| 월 수익 (합산) | 100만원+ |
