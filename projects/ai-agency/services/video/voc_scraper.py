"""
VoC Scraper — Korean cosmetics consumer language extractor.

Sources (no login required):
  1. 파우더룸 (powderm.co.kr) — product reviews
  2. Naver Blog public search
  3. Naver Shopping review search
  4. Fallback: Naver Search API (NAVER_CLIENT_ID + NAVER_CLIENT_SECRET)
  5. Fallback: manual paste

Usage:
  python voc_scraper.py --brand 토리든 --slug torriden
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Force UTF-8 on Windows consoles (cp949 default breaks Korean print output)
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[4]  # MCP_Agentic_AI root
load_dotenv(ROOT / ".env")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.8",
    "Accept-Charset": "utf-8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

REQUEST_TIMEOUT = 10
SLEEP_BETWEEN = 1.5  # polite crawl delay (seconds)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get(url: str, params: dict | None = None, extra_headers: dict | None = None) -> requests.Response | None:
    """GET with retry on connection errors. Returns None if all attempts fail."""
    hdrs = {**HEADERS, **(extra_headers or {})}
    for attempt in range(2):
        try:
            resp = requests.get(url, params=params, headers=hdrs, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp
        except requests.exceptions.HTTPError as e:
            print(f"  [HTTP {e.response.status_code}] {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  [연결 오류 attempt {attempt+1}] {e}")
            time.sleep(2)
    return None


def _text_chunks(soup: BeautifulSoup, tags: list[str]) -> list[str]:
    """Extract non-empty text from given tags."""
    chunks = []
    for tag in tags:
        for el in soup.find_all(tag):
            t = el.get_text(separator=" ", strip=True)
            if t and len(t) > 10:
                chunks.append(t)
    return chunks


# ---------------------------------------------------------------------------
# Source 1: 파우더룸
# ---------------------------------------------------------------------------


def scrape_powderm(brand_name: str) -> list[str]:
    """Scrape review text from 파우더룸 search results page."""
    print(f"[파우더룸] '{brand_name}' 검색 중...")
    url = "https://www.powderm.co.kr/search"
    resp = _get(url, params={"query": brand_name})
    if not resp:
        print("  [파우더룸] 응답 없음 — 건너뜀")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    # 파우더룸 search results: review cards have class variations — try broad selectors
    phrases = []

    # Product review cards
    for el in soup.select("div.review-content, p.review-text, span.txt, div.content, li.item-review"):
        t = el.get_text(separator=" ", strip=True)
        if t and len(t) > 15:
            phrases.append(t)

    # Fallback: grab all paragraph-like text from body
    if not phrases:
        phrases = _text_chunks(soup, ["p", "li", "span"])
        # Filter Korean-heavy strings (at least 30% Korean characters)
        phrases = [p for p in phrases if _korean_ratio(p) >= 0.3]

    print(f"  [파우더룸] {len(phrases)}개 문장 수집")
    return phrases[:200]


# ---------------------------------------------------------------------------
# Source 2: Naver Blog public search
# ---------------------------------------------------------------------------


def scrape_naver_blog(brand_name: str) -> list[str]:
    """Scrape Naver Blog search result snippets (public, no login)."""
    print(f"[Naver Blog] '{brand_name} 후기' 검색 중...")
    url = "https://search.naver.com/search.naver"
    params = {"where": "blog", "query": f"{brand_name} 후기"}
    resp = _get(url, params=params)
    if not resp:
        print("  [Naver Blog] 응답 없음 — 건너뜀")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    phrases = []

    # Naver blog result snippets
    for el in soup.select(
        "a.title_link, div.dsc_wrap, div.api_txt_lines, span.sub_txt, div.total_wrap a"
    ):
        t = el.get_text(separator=" ", strip=True)
        if t and len(t) > 15 and _korean_ratio(t) >= 0.3:
            phrases.append(t)

    # Broader fallback
    if not phrases:
        for el in soup.select("li.bx, div.view_wrap"):
            t = el.get_text(separator=" ", strip=True)
            if t and len(t) > 15:
                phrases.append(t[:500])

    print(f"  [Naver Blog] {len(phrases)}개 문장 수집")
    return phrases[:200]


# ---------------------------------------------------------------------------
# Source 3: Naver Shopping review search
# ---------------------------------------------------------------------------


def scrape_naver_shopping(brand_name: str) -> list[str]:
    """Scrape Naver Shopping review search result snippets."""
    print(f"[Naver Shopping] '{brand_name} 리뷰' 검색 중...")
    url = "https://search.naver.com/search.naver"
    params = {"where": "nexearch", "query": f"{brand_name} 리뷰"}
    resp = _get(url, params=params)
    if not resp:
        print("  [Naver Shopping] 응답 없음 — 건너뜀")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    phrases = []

    for el in soup.select(
        "div.review_area, p.review_text, span.review_text, div.api_txt_lines, "
        "div.product_comment, a.title_link, div.dsc_wrap"
    ):
        t = el.get_text(separator=" ", strip=True)
        if t and len(t) > 15 and _korean_ratio(t) >= 0.3:
            phrases.append(t)

    # Fallback
    if not phrases:
        for el in soup.select("div.g_inner, li.bx"):
            t = el.get_text(separator=" ", strip=True)
            if t and len(t) > 15:
                phrases.append(t[:500])

    print(f"  [Naver Shopping] {len(phrases)}개 문장 수집")
    return phrases[:200]


# ---------------------------------------------------------------------------
# Fallback: Naver Search API
# ---------------------------------------------------------------------------


def naver_api_search(brand_name: str, search_type: str = "blog") -> list[str]:
    """
    Use Naver Search API to fetch blog/cafe post descriptions.
    search_type: 'blog' | 'cafearticle'
    Requires NAVER_CLIENT_ID + NAVER_CLIENT_SECRET in .env.
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        return []

    print(f"[Naver API] {search_type} 검색 중: '{brand_name} 후기'")
    url = f"https://openapi.naver.com/v1/search/{search_type}.json"
    params = {"query": f"{brand_name} 후기", "display": 100, "sort": "sim"}
    hdrs = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    resp = _get(url, params=params, extra_headers=hdrs)
    if not resp:
        print(f"  [Naver API/{search_type}] 실패")
        return []

    data = resp.json()
    items = data.get("items", [])
    phrases = []
    for item in items:
        # Strip HTML tags from description
        desc = BeautifulSoup(item.get("description", ""), "html.parser").get_text()
        title = BeautifulSoup(item.get("title", ""), "html.parser").get_text()
        for text in [title, desc]:
            if text and len(text) > 10:
                phrases.append(text.strip())

    print(f"  [Naver API/{search_type}] {len(phrases)}개 문장 수집")
    return phrases


# ---------------------------------------------------------------------------
# Fallback: Manual paste
# ---------------------------------------------------------------------------


def manual_paste_fallback(brand_name: str) -> list[str]:
    """Ask user to paste raw review text when all scraping fails."""
    print(f"\n[수동 입력] '{brand_name}' 자동 수집 실패. 리뷰 텍스트를 직접 붙여넣어주세요.")
    print("종료하려면 빈 줄 후 'END' 입력:\n")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip().upper() == "END":
            break
        lines.append(line)
    return lines if lines else []


# ---------------------------------------------------------------------------
# Korean character ratio filter
# ---------------------------------------------------------------------------


def _korean_ratio(text: str) -> float:
    if not text:
        return 0.0
    korean_chars = sum(1 for c in text if "가" <= c <= "힣")
    return korean_chars / len(text)


# ---------------------------------------------------------------------------
# Claude analysis
# ---------------------------------------------------------------------------


def analyze_with_claude(brand_name: str, raw_phrases: list[str]) -> dict:
    """
    Send raw phrases to claude-sonnet-4-6 to extract top 30 VoC phrases
    with categories: pain_points, triggers, fears, desired_outcomes.
    """
    if not ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY가 .env에 없습니다.")

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Limit input to avoid token overflow: join up to 400 phrases, each truncated
    sample = raw_phrases[:400]
    joined = "\n".join(f"- {p[:300]}" for p in sample)

    prompt = f"""당신은 한국 화장품 브랜드 '{brand_name}'의 소비자 리서처입니다.
아래는 온라인 커뮤니티와 블로그에서 수집한 실제 소비자 언어 원문입니다.

[원문 데이터]
{joined}

위 데이터를 분석하여 JSON 형식으로 다음을 추출하세요:

1. top_30: 소비자가 실제로 사용한 표현 상위 30개
   - phrase: 실제 소비자 언어 (원문 그대로 또는 유사 표현 통합)
   - frequency: 유사 표현 등장 횟수 (추정)
   - sentiment: "positive" | "negative" | "neutral"
   - category: "texture" | "effect" | "scent" | "price" | "packaging" | "skin_concern" | "ingredient" | "other"

2. pain_points: 소비자가 느끼는 불편/문제점 (리스트, 최대 10개)
3. triggers: 구매를 결정하게 만드는 요인 (리스트, 최대 10개)
4. fears: 구매를 망설이게 하는 두려움 (리스트, 최대 10개)
5. desired_outcomes: 소비자가 원하는 결과/기대 효과 (리스트, 최대 10개)

반드시 유효한 JSON만 반환하세요. 설명 없이 JSON만.

형식:
{{
  "top_30": [
    {{"phrase": "...", "frequency": 5, "sentiment": "negative", "category": "texture"}},
    ...
  ],
  "pain_points": ["...", ...],
  "triggers": ["...", ...],
  "fears": ["...", ...],
  "desired_outcomes": ["...", ...]
}}"""

    print("[Claude] VoC 분석 중...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_output = message.content[0].text.strip()

    # Strip markdown code fences if present
    if raw_output.startswith("```"):
        lines = raw_output.split("\n")
        raw_output = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

    try:
        result = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"  [경고] JSON 파싱 실패: {e}")
        print(f"  Raw output preview: {raw_output[:500]}")
        result = {
            "top_30": [],
            "pain_points": [],
            "triggers": [],
            "fears": [],
            "desired_outcomes": [],
            "raw_claude_output": raw_output,
        }

    print(f"  [Claude] top_30 {len(result.get('top_30', []))}개 추출 완료")
    return result


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run(brand_name: str, slug: str, raw_only: bool = False) -> Path:
    print(f"\n=== VoC 수집 시작: {brand_name} ({slug}) ===\n")

    # --- Scrape all sources ---
    raw_phrases: list[str] = []
    sources_used: list[str] = []

    # Source 1: 파우더룸
    powderm_results = scrape_powderm(brand_name)
    if powderm_results:
        raw_phrases.extend(powderm_results)
        sources_used.append("powderm")
    time.sleep(SLEEP_BETWEEN)

    # Source 2: Naver Blog
    blog_results = scrape_naver_blog(brand_name)
    if blog_results:
        raw_phrases.extend(blog_results)
        sources_used.append("naver_blog")
    time.sleep(SLEEP_BETWEEN)

    # Source 3: Naver Shopping
    shopping_results = scrape_naver_shopping(brand_name)
    if shopping_results:
        raw_phrases.extend(shopping_results)
        sources_used.append("naver_shopping")
    time.sleep(SLEEP_BETWEEN)

    # Fallback 1: Naver API (blog)
    if len(raw_phrases) < 20:
        print("[Fallback] 수집량 부족 — Naver API 시도")
        api_results = naver_api_search(brand_name, "blog")
        if api_results:
            raw_phrases.extend(api_results)
            sources_used.append("naver_api_blog")
        time.sleep(SLEEP_BETWEEN)

        # Naver API (cafe)
        cafe_results = naver_api_search(brand_name, "cafearticle")
        if cafe_results:
            raw_phrases.extend(cafe_results)
            sources_used.append("naver_api_cafe")

    # Fallback 2: Manual paste
    if len(raw_phrases) < 10:
        print(f"\n[경고] 자동 수집 결과가 너무 적습니다 ({len(raw_phrases)}개).")
        manual = manual_paste_fallback(brand_name)
        if manual:
            raw_phrases.extend(manual)
            sources_used.append("manual")

    # Deduplicate while preserving order
    seen = set()
    unique_phrases = []
    for p in raw_phrases:
        key = p[:80]  # dedupe by first 80 chars
        if key not in seen:
            seen.add(key)
            unique_phrases.append(p)

    print(f"\n총 수집: {len(unique_phrases)}개 고유 문장 (중복 제거 후)")

    if not unique_phrases:
        print("[오류] 수집된 데이터가 없습니다. 종료합니다.")
        sys.exit(1)

    # --- Claude analysis (skipped in --raw-only) ---
    if raw_only:
        print("[--raw-only] Claude API 호출 건너뜀. 분석은 세션에서 수행.")
        analysis = {"top_30": [], "pain_points": [], "triggers": [], "fears": [], "desired_outcomes": []}
    else:
        analysis = analyze_with_claude(brand_name, unique_phrases)

    # --- Build output ---
    output = {
        "brand_slug": slug,
        "brand_name": brand_name,
        "scraped_at": datetime.utcnow().isoformat() + "Z",
        "sources": sources_used,
        "raw_phrase_count": len(unique_phrases),
        "raw_phrases": unique_phrases[:500],  # cap storage at 500
        "top_30": analysis.get("top_30", []),
        "pain_points": analysis.get("pain_points", []),
        "triggers": analysis.get("triggers", []),
        "fears": analysis.get("fears", []),
        "desired_outcomes": analysis.get("desired_outcomes", []),
    }

    # --- Save ---
    client_dir = ROOT / "projects" / "ai-agency" / "clients" / slug
    client_dir.mkdir(parents=True, exist_ok=True)
    output_path = client_dir / f"voc-{slug}.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n[완료] 저장됨: {output_path}")
    print(f"  sources: {sources_used}")
    print(f"  raw phrases: {len(unique_phrases)}")
    print(f"  top_30: {len(output['top_30'])}개")
    print(f"  pain_points: {len(output['pain_points'])}개")

    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Korean cosmetics VoC scraper. Extracts top 30 consumer phrases per brand."
    )
    parser.add_argument("--brand", required=True, help="Brand name in Korean. e.g. 토리든")
    parser.add_argument(
        "--slug",
        required=True,
        help="Brand slug (lowercase English). e.g. torriden. Used for output filename and folder.",
    )
    parser.add_argument(
        "--raw-only",
        action="store_true",
        help="Skip Claude API analysis. Save raw_phrases only. Use when analyzing in-session.",
    )
    args = parser.parse_args()

    output_path = run(brand_name=args.brand, slug=args.slug, raw_only=args.raw_only)
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
