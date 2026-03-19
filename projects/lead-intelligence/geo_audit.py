"""
GEO Audit Agent — Project B: Lead Intelligence

Checks each company's AI discoverability across seven dimensions:
  - Citability Score      (0-40): structured content on website
  - Crawler Access Score  (0-30): robots.txt GPTBot/ClaudeBot/PerplexityBot + llms.txt
  - Brand Mention Score   (0-30): Perplexity brand visibility
  - Schema.org Score      (0-20): JSON-LD structured data (Organization, FAQ, HowTo)
  - llms.txt Score        (0-10): LLM permissions file at site root (emerging standard)
  - Korean Presence Score (0-20): Naver profile (10), 사업자등록번호 (5), Kakao Map (5)
  - Share of Voice Score  (0-10): competitive AI citation vs industry peers

Total GEO score = sum of seven (max 150, normalized to /100 in audit_company_geo).
"""

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

for _p in [Path(__file__).parent / '.env', Path(__file__).parent.parent / '.env', Path(__file__).parent.parent.parent / '.env']:
    if _p.exists():
        load_dotenv(dotenv_path=_p)
        break

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    raise EnvironmentError("PERPLEXITY_API_KEY not found in .env")

HEADERS = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json",
}
PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar"

REQUEST_TIMEOUT = 8
ROBOTS_TIMEOUT = 5

# Schema.org types that matter for GEO (each found = +5 points, max 20)
SCHEMA_TYPES = ["Organization", "FAQPage", "HowTo", "Article", "Product", "LocalBusiness"]

# llms.txt scoring
LLMS_TXT_SCORE = 10  # full score if file exists at /llms.txt


def _perplexity_query(prompt: str) -> str:
    """Send a query to Perplexity sonar. Returns response text or empty string on failure."""
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    try:
        resp = requests.post(PERPLEXITY_URL, headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"    [perplexity error] {e}")
        return ""


def _find_website_url(corp_name: str) -> str | None:
    """Use Perplexity to find the company's official website URL."""
    prompt = f"{corp_name} 공식 홈페이지 site:kr OR site:com"
    response = _perplexity_query(prompt)
    if not response:
        return None

    # Extract first URL-looking token from the response
    import re
    urls = re.findall(r'https?://[^\s\)\]\,\"\']+', response)
    # Prefer .co.kr or .com domains that aren't social media or news
    skip_domains = {'naver', 'daum', 'google', 'kakao', 'instagram', 'facebook', 'linkedin', 'youtube'}
    for url in urls:
        # Strip non-ASCII and trailing non-URL chars (Korean/markdown artifacts)
        import re as _re
        url = _re.split(r'[^a-zA-Z0-9\-\.\/\:\?=&#%_~]', url)[0]
        url = url.rstrip('.,;)/\\')
        try:
            parsed = urlparse(url)
            host = parsed.netloc.lower()
        except ValueError:
            continue
        if host and '.' in host and not any(skip in host for skip in skip_domains):
            return url
    return None


def _score_citability(website_url: str | None) -> int:
    """
    Fetch website HTML and count content-rich paragraphs (>50 words).
    Score = min(block_count * 4, 40).
    Returns 10 if fetch fails or no URL.
    """
    if not website_url:
        return 10

    try:
        resp = requests.get(
            website_url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; LeadBot/1.0)"},
            allow_redirects=True,
        )
        if resp.status_code in (403, 429, 503):
            print(f"    [citability] {resp.status_code} — using default score 10")
            return 10
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"    [citability fetch error] {e}")
        return 10

    # Count paragraphs with >50 words (naive split on <p> tags or block separators)
    import re
    # Strip script/style blocks
    html = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Extract text between tags
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL | re.IGNORECASE)
    # Also capture divs with substantial text if paragraphs are sparse
    if len(paragraphs) < 3:
        paragraphs += re.findall(r'<div[^>]*>(.*?)</div>', html, flags=re.DOTALL | re.IGNORECASE)

    block_count = 0
    for p in paragraphs:
        # Strip HTML tags inside paragraph
        text = re.sub(r'<[^>]+>', ' ', p).strip()
        word_count = len(text.split())
        if word_count > 50:
            block_count += 1

    score = min(block_count * 4, 40)
    # Floor at 10 — if the page loaded, there's some basic web presence
    score = max(score, 10)
    print(f"    [citability] {block_count} rich blocks → {score}/40")
    return score


def _score_crawler_access(website_url: str | None) -> int:
    """
    Fetch robots.txt and check for GPTBot, ClaudeBot, PerplexityBot rules.
    Base = 30. Each bot disallowed = -10.
    Returns 25 if robots.txt not found.
    """
    if not website_url:
        return 25

    parsed = urlparse(website_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        resp = requests.get(
            robots_url,
            timeout=ROBOTS_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if resp.status_code == 404:
            return 25
        resp.raise_for_status()
        content = resp.text.lower()
    except Exception as e:
        print(f"    [robots.txt error] {e}")
        return 25

    score = 30
    ai_bots = ["gptbot", "claudebot", "perplexitybot"]

    # Parse robots.txt blocks — find relevant user-agent blocks
    import re
    # Build a mapping: user-agent -> list of disallow rules
    blocks = re.split(r'\n\s*\n', content)
    current_agents = []
    disallowed_bots = set()

    for line in content.splitlines():
        line = line.strip()
        if line.startswith('user-agent:'):
            agent = line.split(':', 1)[1].strip()
            current_agents = [agent]
        elif line.startswith('disallow:'):
            disallow_path = line.split(':', 1)[1].strip()
            if disallow_path == '/' or disallow_path == '':
                # disallow: / means blocked; disallow: (empty) means allowed
                if disallow_path == '/':
                    for agent in current_agents:
                        if agent in ai_bots:
                            disallowed_bots.add(agent)

    for bot in ai_bots:
        if bot in disallowed_bots:
            score -= 10
            print(f"    [robots.txt] {bot} disallowed — -10")

    print(f"    [crawler access] score {score}/30")
    return max(score, 0)


def _score_brand_mention(corp_name: str) -> int:
    """
    Query Perplexity for brand visibility in AI/digital context.
    Returns 20 if mentioned, 5 if not, 10 if Perplexity fails.
    """
    prompt = f"{corp_name} 한국 기업 AI 도입 디지털전환"
    response = _perplexity_query(prompt)

    if not response:
        print(f"    [brand mention] Perplexity failed → 10")
        return 10

    # Check if company name appears in response
    if corp_name in response:
        print(f"    [brand mention] '{corp_name}' mentioned → 20")
        return 20
    else:
        print(f"    [brand mention] '{corp_name}' not found in response → 5")
        return 5


def _score_schema_org(website_url: str | None) -> int:
    """
    Fetch homepage HTML and check for schema.org JSON-LD structured data.
    Score = min(types_found * 5, 20).
    Returns 0 if no URL or fetch fails.
    """
    if not website_url:
        return 0

    try:
        resp = requests.get(
            website_url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; GEOBot/1.0)"},
            allow_redirects=True,
        )
        if resp.status_code not in (200, 301, 302):
            print(f"    [schema.org] HTTP {resp.status_code} — 0")
            return 0
        html = resp.text
    except Exception as e:
        print(f"    [schema.org fetch error] {e}")
        return 0

    import re, json as _json
    # Find all JSON-LD script blocks
    ld_blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.DOTALL | re.IGNORECASE,
    )

    found_types = set()
    for block in ld_blocks:
        try:
            data = _json.loads(block.strip())
            # Handle both single object and @graph arrays
            items = data if isinstance(data, list) else [data]
            for item in items:
                t = item.get("@type", "")
                types = t if isinstance(t, list) else [t]
                for schema_type in types:
                    if schema_type in SCHEMA_TYPES:
                        found_types.add(schema_type)
        except Exception:
            continue

    score = min(len(found_types) * 5, 20)
    print(f"    [schema.org] found: {list(found_types) or 'none'} → {score}/20")
    return score


def _score_llms_txt(website_url: str | None) -> int:
    """
    Check if the site has an llms.txt file at the root (emerging LLM permissions standard).
    Returns LLMS_TXT_SCORE (10) if found and non-empty, 0 otherwise.
    """
    if not website_url:
        return 0

    parsed = urlparse(website_url)
    llms_url = f"{parsed.scheme}://{parsed.netloc}/llms.txt"

    try:
        resp = requests.get(
            llms_url,
            timeout=ROBOTS_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        if resp.status_code == 200 and len(resp.text.strip()) > 10:
            print(f"    [llms.txt] found at {llms_url} → {LLMS_TXT_SCORE}/10")
            return LLMS_TXT_SCORE
        else:
            print(f"    [llms.txt] not found (HTTP {resp.status_code}) → 0")
            return 0
    except Exception as e:
        print(f"    [llms.txt error] {e} → 0")
        return 0


def _score_korean_presence(corp_name: str, website_url: str | None) -> int:
    """
    Check Korean-specific GEO signals:
      - Naver Business Profile presence (10 pts): Perplexity query for 네이버 플레이스/지도 listing
      - 사업자등록번호 on website (5 pts): fetch homepage, look for 10-digit business registration number
      - Kakao Map listing (5 pts): Perplexity query for 카카오맵 listing

    Max = 20 pts.
    """
    score = 0

    # 1. Naver Business Profile
    naver_prompt = f"{corp_name} 네이버 플레이스 OR 네이버 지도 등록 기업"
    naver_resp = _perplexity_query(naver_prompt)
    if naver_resp and corp_name in naver_resp:
        score += 10
        print(f"    [korean] Naver profile found → +10")
    else:
        print(f"    [korean] Naver profile not found → 0")

    # 2. 사업자등록번호 on website
    if website_url:
        try:
            import re
            resp = requests.get(
                website_url,
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": "Mozilla/5.0"},
                allow_redirects=True,
            )
            if resp.status_code == 200:
                # Korean business registration number: 10 digits in xxx-xx-xxxxx format
                if re.search(r'\d{3}-\d{2}-\d{5}', resp.text):
                    score += 5
                    print(f"    [korean] 사업자등록번호 found on website → +5")
                else:
                    print(f"    [korean] 사업자등록번호 not found → 0")
        except Exception as e:
            print(f"    [korean] website fetch for 사업자등록번호 error: {e}")

    # 3. Kakao Map listing
    kakao_prompt = f"{corp_name} 카카오맵 OR 카카오 지도"
    kakao_resp = _perplexity_query(kakao_prompt)
    if kakao_resp and corp_name in kakao_resp:
        score += 5
        print(f"    [korean] Kakao Map found → +5")
    else:
        print(f"    [korean] Kakao Map not found → 0")

    print(f"    [korean presence] total → {score}/20")
    return score


def _score_share_of_voice(corp_name: str) -> dict:
    """
    Competitive Share of Voice: query Perplexity for the company's industry/category,
    check how often the target company is cited vs competitors.

    Returns {"sov_score": int 0-10, "competitors_found": list[str], "cited": bool}
    """
    # First find the industry context
    industry_prompt = f"{corp_name} 경쟁사 OR 동종업계 OR 업종 한국 기업"
    industry_resp = _perplexity_query(industry_prompt)

    if not industry_resp:
        print(f"    [sov] Perplexity failed → 0")
        return {"sov_score": 0, "competitors_found": [], "cited": False}

    # Check if target company is mentioned in the competitor context
    cited = corp_name in industry_resp

    # Extract other company names mentioned (crude heuristic: Korean corp suffixes)
    import re
    corp_patterns = re.findall(r'[\uAC00-\uD7A3]+(?:주식회사|㈜|코리아|전자|중공업|화학|제약|물산|건설|에너지|반도체|소재)?', industry_resp)
    competitors = [c for c in corp_patterns if c != corp_name and len(c) > 1][:5]

    sov_score = 7 if cited else 2
    print(f"    [sov] '{corp_name}' cited in competitor context: {cited} → {sov_score}/10")
    print(f"    [sov] Competitors mentioned: {competitors[:3]}")

    return {"sov_score": sov_score, "competitors_found": competitors, "cited": cited}


def audit_company_geo(company: dict) -> dict:
    """
    Takes company dict with at minimum: corp_name, readiness_score.
    Returns company dict + {
        "geo_score": int,
        "geo_breakdown": {"citability": int, "crawler_access": int, "brand_mention": int},
        "website_url": str or None
    }
    """
    corp_name = company["corp_name"]
    print(f"\n[GEO Audit] {corp_name}")

    # Step 1: Find website URL
    print(f"  Finding website URL...")
    website_url = _find_website_url(corp_name)
    print(f"  URL: {website_url}")

    # Step 2: Run seven checks
    print(f"  Check 1 — Citability...")
    citability = _score_citability(website_url)

    print(f"  Check 2 — Crawler Access...")
    crawler_access = _score_crawler_access(website_url)

    print(f"  Check 3 — Brand Mention...")
    brand_mention = _score_brand_mention(corp_name)

    print(f"  Check 4 — Schema.org structured data...")
    schema_score = _score_schema_org(website_url)

    print(f"  Check 5 — llms.txt...")
    llms_score = _score_llms_txt(website_url)

    print(f"  Check 6 — Korean Presence (Naver/사업자등록번호/Kakao)...")
    korean_score = _score_korean_presence(corp_name, website_url)

    print(f"  Check 7 — Share of Voice (competitive AI citation)...")
    sov_data = _score_share_of_voice(corp_name)
    sov_score = sov_data["sov_score"]

    # Raw total out of 150, normalize to /100
    raw_total = citability + crawler_access + brand_mention + schema_score + llms_score + korean_score + sov_score
    geo_score = round(raw_total / 150 * 100)

    result = {**company}
    result["geo_score"] = geo_score
    result["geo_breakdown"] = {
        "citability": citability,
        "crawler_access": crawler_access,
        "brand_mention": brand_mention,
        "schema_org": schema_score,
        "llms_txt": llms_score,
        "korean_presence": korean_score,
        "share_of_voice": sov_score,
    }
    result["sov_competitors"] = sov_data.get("competitors_found", [])
    result["sov_cited"] = sov_data.get("cited", False)
    result["website_url"] = website_url

    print(
        f"  GEO Score: {geo_score}/100 (raw {raw_total}/150 | "
        f"citability={citability}, crawler={crawler_access}, brand={brand_mention}, "
        f"schema={schema_score}, llms={llms_score}, korean={korean_score}, sov={sov_score})"
    )
    return result


def audit_single_company(company_name: str) -> dict:
    """
    Audit any company by name only — no DART data required.
    Works for startups, SMEs, any company with a website.
    Returns a full GEO audit dict compatible with audit_company_geo() output.
    """
    company = {"corp_name": company_name, "readiness_score": None}
    return audit_company_geo(company)


def generate_dynamic_recommendations(breakdown: dict, corp_name: str = "") -> list[str]:
    """
    Generate company-specific recommendations based on which dimensions scored low.
    Returns 3-5 actionable recommendations in Korean, ordered by impact.
    """
    recs = []

    # Priority 1: Crawler access (quick win, high impact)
    crawler = breakdown.get("crawler_access", 30)
    if crawler < 20:
        recs.append(
            f"robots.txt에 GPTBot, ClaudeBot, PerplexityBot 허용 규칙 추가 "
            f"(현재 {crawler}/30점 — AI 크롤러가 웹사이트에 접근하지 못하면 AI 추천에 포함될 수 없습니다)"
        )

    # Priority 2: llms.txt (5-minute fix, immediate signal)
    llms = breakdown.get("llms_txt", 0)
    if llms == 0:
        recs.append(
            "웹사이트 루트에 llms.txt 파일 생성 — AI 시스템에 콘텐츠 접근을 명시적으로 허용하는 신규 표준입니다. "
            "5분 내 적용 가능하며, AI 검색 결과 노출에 직접적인 영향을 줍니다"
        )

    # Priority 3: Schema.org (technical but high-leverage)
    schema = breakdown.get("schema_org", 0)
    if schema < 10:
        recs.append(
            "홈페이지에 Organization JSON-LD 구조화 데이터 추가 — "
            "AI 시스템이 기업명, 설립연도, 주요 제품, 위치 정보를 정확히 인식할 수 있게 합니다. "
            "FAQPage 스키마도 함께 추가하면 AI 질의 응답에 직접 인용됩니다"
        )

    # Priority 4: Citability (content quality)
    citability = breakdown.get("citability", 40)
    if citability < 20:
        recs.append(
            "주요 페이지(회사 소개, 제품/서비스)에 50단어 이상의 구체적 텍스트 블록 추가 — "
            "AI 시스템은 구조화된 긴 문단을 인용합니다. 현재 웹사이트는 AI가 인용할 만한 콘텐츠가 부족합니다"
        )

    # Priority 5: Korean presence (Naver/Kakao ecosystem)
    korean = breakdown.get("korean_presence", 20)
    if korean < 10:
        recs.append(
            "네이버 비즈니스 프로필 및 카카오맵 등록/업데이트 — "
            "한국 AI 생태계(네이버 클로바, 카카오 i)에서의 가시성을 높이고, "
            "사업자등록번호를 웹사이트에 표시하여 신뢰도를 강화하세요"
        )

    # Priority 6: Brand mention (content strategy)
    brand = breakdown.get("brand_mention", 30)
    if brand < 10:
        recs.append(
            f"'{corp_name}' 브랜드가 AI 검색에서 거의 언급되지 않습니다. "
            "업계 관련 질문에 대한 답변이 될 수 있는 전문 콘텐츠(블로그, 사례 연구, 백서)를 발행하세요"
        )

    # Priority 7: Share of Voice
    sov = breakdown.get("share_of_voice", 10)
    if sov < 5:
        recs.append(
            "경쟁사 대비 AI 인용 빈도가 낮습니다. 업계 키워드(제품명, 서비스 카테고리)에서 "
            "AI 시스템이 귀사를 추천하도록 '답변형 콘텐츠'(질문-답변, 비교 분석, 가이드) 전략이 필요합니다"
        )

    # If somehow everything scores well, give general advice
    if not recs:
        recs = [
            "전체적으로 높은 점수입니다. 월간 SoV(Share of Voice) 모니터링을 통해 경쟁사 대비 AI 가시성을 유지하세요",
            "분기별 콘텐츠 업데이트로 AI 시스템의 최신 정보 반영을 유도하세요",
            "신규 제품/서비스 출시 시 구조화된 페이지를 즉시 추가하여 AI 인덱싱 속도를 높이세요",
        ]

    return recs[:5]


def run_geo_audit(companies: list[dict]) -> list[dict]:
    """Run GEO audit on all companies. Adds 2s sleep between companies."""
    results = []
    for i, company in enumerate(companies):
        audited = audit_company_geo(company)
        results.append(audited)
        if i < len(companies) - 1:
            time.sleep(2)
    print(f"\nGEO audit complete: {len(results)} companies processed.")
    return results


if __name__ == "__main__":
    sample_companies = [
        {
            "corp_code": "000001",
            "corp_name": "현대모비스",
            "revenue_bn_krw": 320.0,
            "operating_profit_bn_krw": 48.0,
            "operating_margin_pct": 15.0,
            "year": 2024,
            "financials_history": [
                {"year": 2022, "revenue_bn_krw": 210.0, "operating_profit_bn_krw": 25.0, "operating_margin_pct": 11.9},
                {"year": 2024, "revenue_bn_krw": 320.0, "operating_profit_bn_krw": 48.0, "operating_margin_pct": 15.0},
            ],
            "readiness_score": 72.5,
            "score_breakdown": {
                "financial_health": 22.5,
                "growth_trajectory": 25.0,
                "size_signal": 10.0,
                "dart_disclosure": 15.0,
            },
        },
        {
            "corp_code": "000002",
            "corp_name": "솔브레인",
            "revenue_bn_krw": 180.0,
            "operating_profit_bn_krw": 36.0,
            "operating_margin_pct": 20.0,
            "year": 2024,
            "financials_history": [
                {"year": 2022, "revenue_bn_krw": 140.0, "operating_profit_bn_krw": 28.0, "operating_margin_pct": 20.0},
                {"year": 2024, "revenue_bn_krw": 180.0, "operating_profit_bn_krw": 36.0, "operating_margin_pct": 20.0},
            ],
            "readiness_score": 80.0,
            "score_breakdown": {
                "financial_health": 30.0,
                "growth_trajectory": 20.0,
                "size_signal": 15.0,
                "dart_disclosure": 15.0,
            },
        },
    ]

    print("Running GEO audit on 2 sample companies...\n")
    results = run_geo_audit(sample_companies)

    print("\n--- GEO Audit Results ---")
    for r in results:
        print(
            f"{r['corp_name']} | GEO: {r['geo_score']}/100 | "
            f"Citability: {r['geo_breakdown']['citability']} | "
            f"Crawler: {r['geo_breakdown']['crawler_access']} | "
            f"Brand: {r['geo_breakdown']['brand_mention']} | "
            f"URL: {r['website_url']}"
        )
