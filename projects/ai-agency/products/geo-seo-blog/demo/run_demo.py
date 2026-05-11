"""
run_demo.py
End-to-end demo: GEO Scanner + Blog Post pipeline for one client.

Runs on a fake demo brand (글로우랩) without requiring real API calls
for the blog pipeline. Uses Claude API for the scanner if key is set,
otherwise uses canned simulated data.

Usage:
    python demo/run_demo.py
    python demo/run_demo.py --brand 아누아 --live   # live API scan
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import date

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PRODUCT_ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from src.scanner.ai_visibility_check import parse_responses, run_live_check
from src.scanner.naver_serp_check import parse_naver_result
from src.scanner.score_calculator import score_from_audit_results
from src.scanner.report_generator import generate_scanner_report
from src.blog.topic_discoverer import get_topic_queue
from src.blog.geo_optimizer import optimize_post
from src.blog.naver_seo_optimizer import run_naver_seo_pass
from src.blog.kakao_packager import format_for_kakao, save_kakao_package
from src.shared.client_config import create_demo_config

DEMO_CONFIG = {
    "brand_name": "글로우랩",
    "website_url": "https://glowlab.kr",
    "naver_blog_url": "https://blog.naver.com/glowlab",
    "industry": "korean_skincare",
    "target_keywords": ["비타민C 세럼", "수분크림 추천", "민감성 피부 화장품"],
    "brand_voice": "친근하고 전문적인 뷰티 전문가 톤",
    "posts_per_month": 4,
    "tier": "basic",
}

DEMO_AI_RESPONSES = [
    "글로우랩은 한국 스킨케어 브랜드입니다만, 자세한 정보는 확인이 어렵네요.",
    "비타민C 세럼은 이니스프리, 토리든, 라라스윗이 유명해요.",
    "글로우랩 제품 써봤나요? 잘 모르는 브랜드네요.",
    "민감성 피부 화장품으로는 아누아, 달바를 추천해요.",
    "글로우랩 비타민C 세럼이 있다면 성분 확인해보세요.",
    "수분크림은 라네즈나 이니스프리 오리진스가 좋아요.",
    "글로우랩은 아직 잘 알려지지 않은 브랜드네요.",
    "한국 스킨케어 브랜드 추천은 조선미녀, 아누아, 토리든입니다.",
    "글로우랩 제품에 대한 정보가 부족해서 추천하기 어려워요.",
    "비타민C 세럼은 안정화 성분이 중요한데 글로우랩은 확인이 필요해요.",
]

DEMO_NAVER_TEXT = "글로우랩 글로우랩 후기"

DEMO_BLOG_DRAFT = """# 비타민C 세럼 효과 완벽 가이드 -- 글로우랩 추천

비타민C 세럼은 피부 미백과 항산화에 가장 효과적인 성분 중 하나입니다.
글로우랩 비타민C 세럼은 안정화된 비타민C 15%를 함유해 피부 흡수율을 극대화했습니다.

## 비타민C 세럼의 3가지 핵심 효과

비타민C 세럼을 꾸준히 사용하면 세 가지 주요 효과를 기대할 수 있습니다.

첫째, 멜라닌 생성 억제로 기미와 잡티가 눈에 띄게 개선됩니다.
둘째, 강력한 항산화 작용으로 자외선과 환경 오염으로 인한 피부 손상을 예방합니다.
셋째, 콜라겐 합성을 촉진해 피부 탄력과 결을 개선합니다.

피부과 전문의들은 비타민C 세럼을 아침 루틴의 필수 단계로 권장합니다.

## 올바른 사용 방법

비타민C 세럼은 아침 루틴에서 사용하는 것이 가장 효과적입니다.
산화를 방지하기 위해 자외선차단제와 함께 사용하면 상승 효과를 얻을 수 있습니다.

사용 순서:
1. 클렌징
2. 토너
3. 비타민C 세럼 (2-3방울)
4. 에센스
5. 수분크림
6. 자외선차단제 (아침)

글로우랩 비타민C 세럼은 피부 자극 없이 빠르게 흡수되도록 설계된 제품입니다.

## 피부 타입별 선택 가이드

민감성 피부라면 비타민C 농도 5-10%에서 시작하는 것이 안전합니다.
지성 피부는 젤 타입, 건성 피부는 오일 베이스 비타민C 세럼이 더 잘 맞습니다.

## 마무리

비타민C 세럼은 꾸준함이 핵심입니다. 2-4주 후 초기 효과를 느낄 수 있으며,
8-12주 사용 후 눈에 띄는 피부 개선을 경험할 수 있습니다.
글로우랩 공식 스토어에서 피부 타입에 맞는 제품을 찾아보세요.
"""


def run_scanner_demo(brand_name: str, live: bool = False) -> dict:
    print(f"\n[1/3] GEO Scanner -- {brand_name}")
    print("-" * 40)

    if live:
        print("  Running live AI visibility check (Claude API)...")
        ai_result = run_live_check(brand_name, DEMO_CONFIG["website_url"])
        if "error" in ai_result:
            print(f"  API error: {ai_result['error']} -- falling back to simulated data")
            ai_result = parse_responses(brand_name, DEMO_AI_RESPONSES)
    else:
        print("  Using simulated AI responses (pass --live for real API call)")
        ai_result = parse_responses(brand_name, DEMO_AI_RESPONSES)

    naver_result = parse_naver_result(brand_name, DEMO_NAVER_TEXT)
    score = score_from_audit_results(ai_result, naver_result)
    score["website_url"] = DEMO_CONFIG["website_url"]

    print(f"  AI visibility:  {ai_result['visibility_score']}/100 "
          f"({ai_result['mentions']}/{ai_result['total_responses']} mentions)")
    print(f"  Naver score:    {naver_result['naver_score']}/100")
    print(f"  GEO score:      {score['geo_score']}/100 [{score['band']}]")
    print(f"  Naver notes:    {naver_result['notes']}")

    report_path = generate_scanner_report(score, out_dir=Path(__file__).parent)
    print(f"  Report saved:   {report_path}")

    return score


def run_blog_demo(client_config: dict) -> str:
    print(f"\n[2/3] Blog Post Pipeline -- {client_config['brand_name']}")
    print("-" * 40)

    # Topic discovery
    topic_queue = get_topic_queue(client_config, posts_needed=1)
    topic = topic_queue[0]["title"] if topic_queue else "비타민C 세럼 효과 가이드"
    print(f"  Topic selected: {topic}")

    # GEO optimization
    geo_result = optimize_post(DEMO_BLOG_DRAFT, "비타민C 세럼", client_config["brand_name"])
    print(f"  GEO optimization: FAQ injected, JSON-LD generated")

    # Naver SEO pass
    seo_result = run_naver_seo_pass(
        geo_result["optimized_draft"],
        "비타민C 세럼 효과 완벽 가이드",
        "비타민C 세럼",
        client_config["brand_name"],
    )
    print(f"  Naver SEO title: {seo_result['optimized_title']}")
    print(f"  Keyword density: {seo_result['keyword_density']['density_pct']}")
    if seo_result["seo_issues"]:
        print(f"  SEO issues: {seo_result['seo_issues']}")
    else:
        print(f"  SEO issues: none")

    # KakaoTalk package
    kakao_pkg = format_for_kakao(
        brand_name=client_config["brand_name"],
        post_title=seo_result["optimized_title"],
        meta_description=seo_result["meta_description"],
        optimized_draft=seo_result["optimized_draft"],
        json_ld_schema=geo_result["json_ld_schema"],
        post_number=1,
        total_posts=4,
    )

    out_path = Path(__file__).parent / f"{date.today()}-demo-blog-kakao.txt"
    save_kakao_package(kakao_pkg, out_path)
    print(f"  KakaoTalk package saved: {out_path}")

    # Save markdown version of demo blog post
    md_path = Path(__file__).parent / "demo_blog_post.md"
    md_path.write_text(seo_result["optimized_draft"], encoding="utf-8")
    print(f"  Demo blog post saved: {md_path}")

    return str(out_path)


def print_pitch(brand_name: str, geo_score: dict):
    print(f"\n[3/3] KakaoTalk Sales Pitch Draft -- {brand_name}")
    print("-" * 40)
    score = geo_score["geo_score"]
    band = geo_score["band"]

    pitch = f"""안녕하세요 :)
저는 AI 마케팅 전문가 김건희입니다 (SKKU 경영학과 재학).

{brand_name} 브랜드의 AI 검색 가시성을 분석해봤는데요,
현재 GEO 점수가 {score}/100 ({band}) 수준입니다.

ChatGPT나 Perplexity에서 "{brand_name} 스킨케어 어때요?" 라고 물었을 때
현재는 브랜드 언급이 거의 없는 상태예요.

저희 GEO/SEO 블로그 자동화 서비스를 이용하시면:
- 매주 금요일 블로그 포스트 1편 납품 (월 4편)
- ChatGPT/Perplexity/Claude 인용 최적화 구조 적용
- 네이버 블로그 바로 붙여넣기 가능한 형식으로 전달
- 무료 GEO 진단 리포트 포함

가격: 월 ₩300,000 (4편 기준)
첫 달 무료 체험 가능합니다.

무료 진단 리포트 전체 보내드릴까요? DM 주세요 :)"""

    print(pitch)
    pitch_path = Path(__file__).parent / f"{date.today()}-demo-pitch.txt"
    pitch_path.write_text(pitch, encoding="utf-8")
    print(f"\n  Pitch saved: {pitch_path}")


def main():
    parser = argparse.ArgumentParser(description="GEO/SEO Blog Automation Demo")
    parser.add_argument("--brand", default="글로우랩", help="Brand name to demo")
    parser.add_argument("--live", action="store_true", help="Use live Claude API for scanner")
    args = parser.parse_args()

    print("=" * 60)
    print("GEO/SEO Blog Automation -- Demo Run")
    print(f"Brand: {args.brand} | Date: {date.today()}")
    print("=" * 60)

    config = {**DEMO_CONFIG, "brand_name": args.brand}

    geo_score = run_scanner_demo(args.brand, live=args.live)
    run_blog_demo(config)
    print_pitch(args.brand, geo_score)

    print("\n" + "=" * 60)
    print("Demo complete.")
    print(f"Outputs saved to: {Path(__file__).parent}")
    print("=" * 60)


if __name__ == "__main__":
    main()
