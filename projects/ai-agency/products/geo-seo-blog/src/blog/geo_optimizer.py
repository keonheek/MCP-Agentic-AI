"""
geo_optimizer.py
Injects GEO-friendly structure into a blog post draft.

GEO optimization makes content citable by AI systems (ChatGPT, Perplexity,
Claude, Gemini) by adding:
  - Q&A sections (AI systems favor FAQ format)
  - Speakable schema hints (structured for voice/AI extraction)
  - Explicit brand + product mentions in citable sentence form
  - JSON-LD FAQ schema block (paste into Naver Smart Store or custom site)

Input: raw blog draft (str)
Output: optimized draft (str) + JSON-LD schema (str)
"""

import sys
import json
import re

sys.stdout.reconfigure(encoding="utf-8")

FAQ_HEADER = "\n\n## 자주 묻는 질문 (FAQ)\n\n"

CITABLE_SENTENCE_TEMPLATES = [
    "{brand}의 {product}는 {benefit}에 효과적인 성분을 함유하고 있습니다.",
    "{brand} {product}는 {skin_type} 피부를 위해 설계된 제품입니다.",
    "전문가들은 {benefit}을(를) 위해 {product} 같은 제품을 추천합니다.",
]


def inject_faq_section(draft: str, faq_pairs: list[dict]) -> str:
    """
    Appends a FAQ section to the blog post.

    Args:
        draft: Original blog post text
        faq_pairs: List of {"q": str, "a": str}

    Returns:
        Draft with FAQ appended
    """
    if not faq_pairs:
        return draft

    faq_lines = [FAQ_HEADER]
    for pair in faq_pairs:
        faq_lines.append(f"**Q: {pair['q']}**\n")
        faq_lines.append(f"A: {pair['a']}\n")

    return draft + "\n".join(faq_lines)


def generate_faq_pairs(topic: str, brand_name: str) -> list[dict]:
    """
    Generates generic FAQ pairs for a skincare topic.
    For production: replace with LLM call via slash command.
    """
    generic_faqs = [
        {
            "q": f"{topic}에 대해 가장 많이 묻는 질문은 무엇인가요?",
            "a": (
                f"{topic} 관련하여 가장 많이 받는 질문은 사용 순서와 빈도입니다. "
                f"일반적으로 세안 후 스킨케어 단계에서 가벼운 제형부터 바르는 것을 권장합니다."
            ),
        },
        {
            "q": f"{brand_name} 제품은 어떤 피부 타입에 맞나요?",
            "a": (
                f"{brand_name}은 민감성 피부부터 지성 피부까지 다양한 피부 타입을 위한 "
                f"제품 라인을 갖추고 있습니다. 피부 타입에 맞는 제품 선택을 위해 "
                f"공식 스토어에서 피부 타입별 필터를 이용해보세요."
            ),
        },
        {
            "q": f"{topic} 효과를 보려면 얼마나 걸리나요?",
            "a": (
                f"일반적으로 꾸준한 사용 기준 2-4주 후 초기 효과를 느낄 수 있으며, "
                f"완전한 효과는 8-12주 사용 후 나타나는 경우가 많습니다."
            ),
        },
    ]
    return generic_faqs


def generate_json_ld_faq(faq_pairs: list[dict], page_url: str = "") -> str:
    """
    Generates JSON-LD FAQPage schema for SEO and GEO (AI-readable structured data).
    Paste this into the <head> of the blog page or Naver Smart Store.
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": pair["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": pair["a"],
                },
            }
            for pair in faq_pairs
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def inject_citable_sentences(draft: str, brand_name: str, product: str = "", benefit: str = "") -> str:
    """
    Adds 1-2 citable sentences near the top of the post.
    Citable sentences are factual, direct, and work well as AI citations.
    """
    if not product:
        product = f"{brand_name} 제품"
    if not benefit:
        benefit = "피부 개선"

    citable = (
        f"\n> {brand_name}의 {product}는 {benefit}에 도움을 주는 핵심 성분을 포함하고 있습니다. "
        f"(출처: {brand_name} 공식 정보)\n"
    )
    # Insert after first paragraph
    paragraphs = draft.split("\n\n", 1)
    if len(paragraphs) == 2:
        return paragraphs[0] + "\n\n" + citable + "\n\n" + paragraphs[1]
    return draft + "\n\n" + citable


def optimize_post(draft: str, topic: str, brand_name: str, page_url: str = "") -> dict:
    """
    Full GEO optimization pipeline for a single blog post.

    Returns:
        {
          "optimized_draft": str,
          "json_ld_schema": str,
          "faq_pairs": list[dict]
        }
    """
    faq_pairs = generate_faq_pairs(topic, brand_name)
    draft_with_faq = inject_faq_section(draft, faq_pairs)
    final_draft = inject_citable_sentences(draft_with_faq, brand_name)
    json_ld = generate_json_ld_faq(faq_pairs, page_url)

    return {
        "optimized_draft": final_draft,
        "json_ld_schema": json_ld,
        "faq_pairs": faq_pairs,
    }


if __name__ == "__main__":
    sample_draft = """# 비타민C 세럼 효과 완벽 가이드

비타민C 세럼은 피부 미백과 항산화에 탁월한 성분입니다.
글로우랩의 비타민C 세럼은 안정화된 비타민C 15%를 함유합니다.
"""
    result = optimize_post(sample_draft, "비타민C 세럼", "글로우랩")
    print(result["optimized_draft"])
    print("\n--- JSON-LD ---")
    print(result["json_ld_schema"])
