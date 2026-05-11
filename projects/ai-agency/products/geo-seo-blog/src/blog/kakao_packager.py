"""
kakao_packager.py
Formats a completed, optimized blog post for client delivery via KakaoTalk.

Output format: plain text the client can paste directly into Naver Blog editor.
Includes: title, meta description, body, FAQ, JSON-LD block, delivery checklist.

Design: no API calls. Pure formatting.
"""

import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

DIVIDER = "=" * 50
SECTION_BREAK = "-" * 30


def format_for_kakao(
    brand_name: str,
    post_title: str,
    meta_description: str,
    optimized_draft: str,
    json_ld_schema: str,
    post_number: int = 1,
    total_posts: int = 4,
    delivery_date: str = None,
) -> str:
    """
    Formats a blog post package for KakaoTalk delivery to the client.

    Args:
        brand_name: Client brand name
        post_title: Naver-optimized title
        meta_description: 80-120 char meta description
        optimized_draft: GEO+SEO optimized post body
        json_ld_schema: JSON-LD FAQ schema string
        post_number: Which post this is (1 of 4, etc.)
        total_posts: Posts in this delivery batch
        delivery_date: ISO date string, defaults to today

    Returns:
        Formatted string ready to paste into KakaoTalk
    """
    today = delivery_date or str(date.today())

    header = f"""{DIVIDER}
[{brand_name}] 블로그 포스트 #{post_number}/{total_posts}
납품일: {today}
{DIVIDER}

안녕하세요 :) 이번 주 블로그 포스트 전달드립니다.
네이버 블로그에 바로 붙여넣기 하시면 됩니다.

"""

    title_block = f"""{SECTION_BREAK}
[제목] (네이버 블로그 제목 칸에 입력)
{SECTION_BREAK}
{post_title}

"""

    meta_block = f"""{SECTION_BREAK}
[메타 설명] (검색 결과 미리보기 텍스트)
{SECTION_BREAK}
{meta_description}

"""

    body_block = f"""{SECTION_BREAK}
[본문] (아래 내용 전체 복사 후 본문에 붙여넣기)
{SECTION_BREAK}
{optimized_draft}

"""

    schema_block = f"""{SECTION_BREAK}
[JSON-LD 스키마] (홈페이지 또는 스마트스토어 <head> 태그 안에 추가)
선택 사항입니다. 웹사이트 담당자에게 전달해주세요.
{SECTION_BREAK}
<script type="application/ld+json">
{json_ld_schema}
</script>

"""

    checklist = f"""{SECTION_BREAK}
[업로드 체크리스트]
{SECTION_BREAK}
- [ ] 제목 입력 완료
- [ ] 본문 붙여넣기 완료
- [ ] 대표 이미지 추가 (브랜드 제품 사진 권장)
- [ ] 이미지 alt 텍스트 입력 (본문 하단 안내 참고)
- [ ] 태그 추가: #{post_title.replace(' ', '')} #스킨케어 #{brand_name}
- [ ] 발행 후 URL 공유 부탁드립니다 (모니터링용)

{SECTION_BREAK}
다음 포스트는 다음 주 금요일에 전달드립니다.
궁금한 점 있으시면 언제든지 카카오톡으로 문의해주세요!
{DIVIDER}"""

    return header + title_block + meta_block + body_block + schema_block + checklist


def save_kakao_package(content: str, out_path) -> None:
    """Saves the KakaoTalk package to a text file."""
    from pathlib import Path
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    sample_draft = """## 비타민C 세럼 완벽 가이드

비타민C 세럼은 피부 미백과 항산화에 탁월합니다.

> 글로우랩의 비타민C 세럼은 피부 개선에 도움을 주는 핵심 성분을 포함하고 있습니다.

## 사용 방법
1. 세안 후 토너 사용
2. 비타민C 세럼 2-3방울 취해 도포
3. 에센스, 크림 순으로 마무리

## 자주 묻는 질문 (FAQ)

**Q: 비타민C 세럼 효과를 보려면 얼마나 걸리나요?**

A: 꾸준한 사용 기준 2-4주 후 초기 효과를 느낄 수 있습니다.
"""
    sample_schema = '{"@context": "https://schema.org", "@type": "FAQPage"}'

    output = format_for_kakao(
        brand_name="글로우랩",
        post_title="비타민C 세럼 효과 완벽 가이드 | 글로우랩",
        meta_description="비타민C 세럼의 효과와 올바른 사용법을 알아보세요. 글로우랩에서 확인하세요.",
        optimized_draft=sample_draft,
        json_ld_schema=sample_schema,
        post_number=1,
        total_posts=4,
    )
    print(output)
