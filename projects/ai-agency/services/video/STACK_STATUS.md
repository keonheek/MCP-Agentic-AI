# Service V: AI Video Ad Stack Status

Last updated: 2026-05-11

## Stack Readiness

| Tool | Status | Pricing | Key Secured |
|---|---|---|---|
| Higgsfield Pro | Pre-launch | Included in Pro plan at $99/mo (approx. 130,000원). No per-request surcharge for voice cloning. | NO |
| Veo 3 (Google) | Pre-launch | Approx. $0.35/second of generated video. 8-second clip: ~$2.80 (approx. 3,700원). Enterprise pricing available. | NO |
| ElevenLabs v3 | Pre-launch | Starter $5/mo (30K chars). Creator $22/mo (100K chars). Pro $99/mo (500K chars). Korean chars counted same as English. | NO |
| Suno Pro | Pre-launch | Pro plan $8/mo. 500 credits/day. 1 song = 10 credits. Commercial use included. | NO |

## Blockers

- **higgsfield_pro**: Plan 00 build / A1 blocker (per current-priorities.md)
- **elevenlabs_v3**: Same as Higgsfield - awaiting agency plan setup
- **veo_3**: Google Vertex AI account required, no active blocker except time
- **suno_pro**: Low priority, easy to acquire ($8/mo), no signup blocker

## Recent Changelog Entries

### Suno Pro (2026-03-01)
Suno v4 model launched with commercial license on Pro plan
Impact: V service can include original K-pop style BGM in ad videos. No royalty risk.

### ElevenLabs v3 (2026-02-20)
ElevenLabs v3 Korean language quality improvement
Impact: Primary voice-over tool for V service. Use for voiceover tracks, then sync to Higgsfield video.

### Higgsfield Pro (2026-03-15)
Korean voice cloning launched (Beta)
Impact: V service can now deliver full Korean voice-over + lip sync in one pipeline. Removes need for separate ElevenLabs call for standard cases.

## Korean Ad Observations

### 라네즈 (2026-05-01)
Hook: 첫 3초: 물방울 + 피부 클로즈업 + '수분이 이렇게 달라집니다'
AI elements: 보이스오버 (합성 추정), 배경음악 (생성 AI 추정), 일부 B-roll AI 생성 추정
Notes: AI 생성 여부 공개 안 함. 제품 실사 + AI 보이스오버 조합이 자연스러움.

### 코스알엑스 (2026-05-03)
Hook: 성분 분자 구조 애니메이션 + '이 성분 하나로 피부가 바뀌었습니다'
AI elements: 분자 구조 애니메이션 (Higgsfield/Runway 추정), ManyChat 자동 DM
Notes: ManyChat 자동화와 AI 비디오 결합. 댓글 키워드 DM이 리드 수집 효과적.
