# 파일 위치 안내 (영범용)

_매일 자동 업데이트됨. 마지막 업데이트: 2026-04-22_

이 파일은 우리 프로젝트의 파일 위치를 정리한 지도입니다.
어디에 뭐가 있는지 모를 때 여기를 먼저 보세요.

---

## 매일 자동 생성되는 파일

| 파일 종류 | 위치 | 생성 시간 |
|---------|-----|---------|
| YouTube 스크립트 (3개) | `projects/youtube-biz/channels/first-mover-ai/drafts/youtube/YYYY-MM-DD-scripts.json` | 매일 22:03 (KST) |
| Instagram 캐러셀 (5개) | `projects/youtube-biz/channels/first-mover-ai/drafts/instagram/YYYY-MM-DD-carousels.json` | 평일 07:07 (KST) |

**예시**: 오늘 (2026-04-22) YouTube 초안은 여기:
`projects/youtube-biz/channels/first-mover-ai/drafts/youtube/2026-04-22-scripts.json`

---

## 검토할 때 봐야 하는 파일

| 파일 | 위치 | 무엇 |
|------|-----|------|
| YouTube 파이프라인 메인 | `projects/youtube-biz/pipelines/first_mover_ai_youtube.py` | YouTube 자동 생성 스크립트 |
| Instagram 파이프라인 메인 | `projects/youtube-biz/pipelines/first_mover_ai_instagram.py` | Instagram 자동 생성 스크립트 |

---

## 설정 파일 (수정하지 마세요 — 건희에게 말씀해주세요)

| 파일 | 위치 | 무엇 |
|------|-----|------|
| 채널 설정 | `projects/youtube-biz/config/channels.yaml` | 채널 키, 타겟 |
| 점수 기준 | `projects/youtube-biz/config/thresholds.yaml` | 영상 선정 기준 |
| 훅 모음 | `projects/youtube-biz/config/hook-templates.json` | 스크립트 시작 멘트 |
| 파트너 계약서 | `projects/youtube-biz/config/partner-agreement.md` | 우리 계약 내용 |

---

## 매일 작업 흐름

1. **22:03** — YouTube 스크립트 3개가 자동으로 생성됨
2. **Discord 알림** — `#youtube-biz` 채널에 "오늘 YT 초안 준비 완료" 메시지
3. **검토** — 영범이 ClickUp 태스크 (`초안 준비` → `검토 중`)
4. **업로드** — 영상 편집 + 업로드 후 ClickUp 태스크 (`검토 중` → `업로드 완료`)
5. **Discord 알림** — ClickUp이 자동으로 "업로드 완료" 메시지 전송

---

## 질문이 있을 때

- **Discord** — 빠른 대화, 질문
- **ClickUp** — 태스크 상태 변경, 파일 위치 확인
- **이 파일 (FILE_MAP_KR.md)** — 파일이 어디 있는지 모를 때
