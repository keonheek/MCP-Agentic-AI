# GEO/SEO 블로그 자동화 서비스

채널톡 + 카페24 + 네이버 스마트스토어 + 카카오 알림톡 + Make.com을 n8n self-host로 묶고 PIPA Tier P 옵션을 제공하는 한국 D2C 운영 통합자.

슬라이드가 아니라 작동하는 시스템을 인도합니다. (We deliver working systems, not slides.)

**대상:** 한국 스킨케어 D2C 브랜드
**목표:** ChatGPT, Perplexity, 네이버 검색에서 브랜드 노출 극대화

---

## 서비스 구성

### 1. GEO Scanner (무료 리드 마그넷)

브랜드 AI 검색 가시성 진단:
- GEO 점수 0-100점 (AI 가시성 60% + 네이버 노출 40%)
- PDF 진단 리포트
- 개선 권장사항 3가지

### 2. GEO/SEO 블로그 자동화 (유료 리텐션)

매월 4-8편 블로그 포스트를 AI 인용 최적화 + 네이버 SEO 구조로 납품합니다.

- 매주 금요일 납품
- 네이버 블로그 바로 붙여넣기 형식
- FAQ JSON-LD 스키마 포함
- 카카오톡으로 파일 전달

---

## 가격 (독립 서비스 기준)

| 플랜 | 편수 | 가격 |
|---|---|---|
| 기본 | 월 4편 | ₩500K 셋업 + ₩300K/월 |
| 프리미엄 | 월 8편 | ₩500K 셋업 + ₩500K/월 |

**에이전시 공통 4단계 번들 맥락:**
GEO/SEO Blog는 D2C STACK(₩5M) 또는 D2C STACK + PIPA Tier P(₩8M)에 번들로 포함될 수 있습니다.
단독 계약 시 위 독립 가격 기준이 적용됩니다.

---

## 실행

```bash
python demo/run_demo.py
python demo/run_demo.py --live
python tests/test_scanner_5_brands.py
python tests/test_blog_korean_keyword_density.py
python tests/test_geo_schema_validity.py
```

---

## geo-agency 재사용 현황

| 파일 | 재사용 방식 |
|---|---|
| `geo_report_pdf.py` | `report_generator.py`에서 import |
| `loop6_geo_monitor.py` | `publish_queue.py` 설계 패턴 참고 |
| `loop1_geo_score_sender.py` | `kakao_packager.py` 패턴 참고 |
| `geo_deliverables.py` | JSON-LD 생성 패턴 참고 |
