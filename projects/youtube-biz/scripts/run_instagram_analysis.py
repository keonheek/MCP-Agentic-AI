"""
Instagram Competitor Analysis Runner
Usage: python scripts/run_instagram_analysis.py

Scrapes evolving.ai, ai.trend.kr, ddalkak (+ any extras)
Outputs: data/instagram_analysis_YYYY-MM-DD.{json,md}
"""
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from core.analytics.instagram_competitor_scraper import run

ACCOUNTS = ["evolving.ai", "ai.trend.kr", "ai_newpd", "trenddalkak.ai"]
N_POSTS = 12
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")


def build_report(results: list[dict]) -> str:
    lines = [
        f"# Instagram Competitor Analysis — {TODAY}",
        "",
        "**목적:** 매거진형 vs 교육형 포지셔닝 결정",
        "",
        "---",
        "",
        "## 계정 비교 요약",
        "",
        "| 계정 | 팔로워 | 릴스% | 카드뉴스% | 평균 좋아요 | 참여율 | 캡션길이 | 포지셔닝 |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for r in results:
        u = r["username"]
        if "error" in r:
            lines.append(f"| @{u} | 오류: {r['error'][:50]} | - | - | - | - | - | - |")
            continue
        p = r["profile"]
        m = r.get("metrics", {})
        followers = f"{p['followers']:,}" if p.get("followers") else "N/A"
        lines.append(
            f"| @{u} "
            f"| {followers} "
            f"| {m.get('reel_pct', '-')}% "
            f"| {m.get('carousel_pct', '-')}% "
            f"| {m.get('avg_likes', '-'):,} "
            f"| {m.get('avg_engagement_rate_pct', '-')}% "
            f"| {m.get('avg_caption_length', '-')}자 "
            f"| **{m.get('positioning', 'N/A')}** |"
        )

    lines += ["", "---", ""]

    for r in results:
        u = r["username"]
        if "error" in r:
            lines.append(f"## @{u} — 수집 실패\n{r['error']}\n")
            continue

        p = r["profile"]
        m = r.get("metrics", {})
        lines += [
            f"## @{u}",
            f"**{p.get('full_name', '')}**  ",
            f"팔로워 {p.get('followers', 0):,} | 게시물 {p.get('post_count', 0):,} | 팔로잉 {p.get('following', 0):,}",
        ]
        if p.get("bio"):
            lines.append(f"> {p['bio'][:200]}")
        if p.get("link_in_bio"):
            lines.append(f"링크: {p['link_in_bio']}")
        lines.append("")

        if m:
            lines += [
                f"| 지표 | 수치 |",
                f"|---|---|",
                f"| 릴스 비율 | {m.get('reel_pct')}% |",
                f"| 카드뉴스 비율 | {m.get('carousel_pct')}% |",
                f"| 이미지 비율 | {m.get('image_pct')}% |",
                f"| 평균 좋아요 | {m.get('avg_likes'):,} |",
                f"| 평균 댓글 | {m.get('avg_comments'):,} |",
                f"| 평균 참여율 | {m.get('avg_engagement_rate_pct')}% |",
                f"| 평균 캡션 길이 | {m.get('avg_caption_length')}자 |",
                f"| 주간 게시 빈도 | {m.get('posts_per_week', 'N/A')}개/주 |",
                f"| 분석 게시물 수 | {m.get('posts_analyzed')} |",
                f"| **포지셔닝 판정** | **{m.get('positioning')}** (edu={m.get('edu_score')}, mag={m.get('mag_score')}) |",
                "",
            ]

        # Recent posts sample
        posts = r.get("posts", [])[:3]
        if posts:
            lines.append("**최근 게시물 샘플:**\n")
            for i, post in enumerate(posts, 1):
                caption_preview = (post.get("caption") or "")[:100].replace("\n", " ")
                lines.append(
                    f"{i}. [{post['type']}] 좋아요 {post.get('likes', 0):,} | "
                    f"댓글 {post.get('comments', 0):,} | "
                    f"_{caption_preview}_"
                )
            lines.append("")

        lines.append("---\n")

    # Strategic Recommendation
    lines += [
        "## 전략 권고",
        "",
    ]

    valid = [r for r in results if "error" not in r and r.get("metrics")]
    main_competitor = next((r for r in valid if r["username"] == "ai.trend.kr"), None)
    benchmark = next((r for r in valid if r["username"] == "evolving.ai"), None)

    if benchmark:
        m = benchmark["metrics"]
        lines.append(
            f"**evolving.ai (벤치마크):** {benchmark['profile']['followers']:,}명 팔로워, "
            f"참여율 {m['avg_engagement_rate_pct']}%. 한국어 시장 미도달 → 한국어 틈새 기회 있음."
        )
        lines.append("")

    if main_competitor:
        m = main_competitor["metrics"]
        positioning = m["positioning"]
        lines.append(f"**ai.trend.kr 포지셔닝: {positioning}형**")
        lines.append("")

        if positioning == "magazine":
            lines += [
                "ai.trend.kr이 매거진형(트렌드 집계, 짧은 캡션, 릴스 중심)이라면:",
                "- **교육형으로 차별화 추천**: '어떻게 쓰는가'를 가르치는 콘텐츠",
                "- 카드뉴스 중심 + 긴 캡션(저장 유도) + 튜토리얼 시리즈",
                "- 참여율 기준: ai.trend.kr보다 높아야 광고주 단가 프리미엄 가능",
            ]
        elif positioning == "educational":
            lines += [
                "ai.trend.kr이 교육형이라면:",
                "- **더 깊은 교육 콘텐츠로 틈새 공략**: 실습 중심, 코드/프롬프트 공개",
                "- 또는 **매거진형으로 차별화**: 빠른 트렌드 리포트, 릴스 집중",
                "- 핵심은 참여율(저장률)에서 앞서는 것",
            ]
        else:
            lines += [
                "ai.trend.kr이 혼합형이라면:",
                "- 교육 또는 매거진 하나를 명확히 선택해 포지셔닝 강화",
                "- '선택과 집중'이 알고리즘 친화적",
            ]
        lines.append("")

    lines += [
        "**핵심 판단 기준:**",
        "- 참여율 1% 이상 = 건강한 계정",
        "- 카드뉴스 저장률 > 릴스 조회수 → 교육형 수요 있음",
        "- 교육형: 협찬 단가 프리미엄 + 강의/커뮤니티 수익 가능",
        "- 매거진형: 빠른 팔로워 성장, 협찬 물량 많음",
        "",
        f"_분석 기준: 최근 {N_POSTS}개 게시물 | 생성: {TODAY}_",
    ]

    return "\n".join(lines)


def main():
    print(f"=== Instagram Competitor Analysis ({TODAY}) ===")
    print(f"Accounts: {', '.join(ACCOUNTS)}")
    print(f"Posts per account: {N_POSTS}\n")

    results = run(ACCOUNTS, n_posts=N_POSTS)

    # Save JSON
    json_path = DATA_DIR / f"instagram_analysis_{TODAY}.json"
    json_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"\nJSON saved: {json_path}")

    # Save Markdown report
    report = build_report(results)
    md_path = DATA_DIR / f"instagram_analysis_{TODAY}.md"
    md_path.write_text(report, encoding="utf-8")
    print(f"Report saved: {md_path}")

    # Print report to console
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
