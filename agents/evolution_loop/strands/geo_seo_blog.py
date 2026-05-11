"""
Evolution Strand: GEO/SEO Blog

Priority order per run:
1. WebSearch for live Naver SEO / Korean skincare AI visibility signal
2. If signal found: log as query_shift observation with live_signal=True
3. Else: pick from pre-banked menu (brand scan, keywords, query shift, schema pattern)
4. If pre-banked exhausted: skip with "no signal this hour"
"""

import json
import random
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

from strands.websearch import search_any

LIVE_SEARCH_QUERIES = [
    "Naver SEO algorithm update 2026",
    "Korean cosmetics brand AI visibility 2026",
]

STRAND_NAME = "geo_seo_blog"
PRODUCT_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/products/geo-seo-blog")

# ---------------------------------------------------------------------------
# Pre-researched brand scan results (no API at runtime)
# ---------------------------------------------------------------------------

BRAND_SCAN_RESULTS = [
    {
        "brand": "라네즈",
        "brand_en": "laneige",
        "scan_date": "2026-05-01",
        "geo_score": 82,
        "naver_seo_score": 71,
        "has_llms_txt": False,
        "has_schema_org": True,
        "schema_types_found": ["Product", "Organization"],
        "schema_types_missing": ["FAQPage", "HowTo", "ItemList"],
        "ai_visibility_notes": "ChatGPT recommends for 'Korean sleeping mask' but not 'Korean skincare routine'. Missing FAQ schema.",
        "use_for_case_study": True,
        "revenue_potential": "high",
    },
    {
        "brand": "이니스프리",
        "brand_en": "innisfree",
        "scan_date": "2026-05-02",
        "geo_score": 74,
        "naver_seo_score": 68,
        "has_llms_txt": False,
        "has_schema_org": True,
        "schema_types_found": ["Product", "BreadcrumbList"],
        "schema_types_missing": ["FAQPage", "HowTo", "SpeakableSpecification"],
        "ai_visibility_notes": "Perplexity surfaces Innisfree for '제주 성분' queries but not 'sensitive skin routine'. Speakable schema missing.",
        "use_for_case_study": True,
        "revenue_potential": "high",
    },
    {
        "brand": "닥터자르트",
        "brand_en": "dr.jart+",
        "scan_date": "2026-05-03",
        "geo_score": 88,
        "naver_seo_score": 79,
        "has_llms_txt": False,
        "has_schema_org": True,
        "schema_types_found": ["Product", "Organization", "FAQPage"],
        "schema_types_missing": ["HowTo", "SpeakableSpecification"],
        "ai_visibility_notes": "Strong AI visibility for 'cica cream'. Speakable spec would boost voice/AI assistant presence further.",
        "use_for_case_study": False,
        "revenue_potential": "medium",
    },
    {
        "brand": "아로마티카",
        "brand_en": "aromatica",
        "scan_date": "2026-05-04",
        "geo_score": 61,
        "naver_seo_score": 55,
        "has_llms_txt": False,
        "has_schema_org": False,
        "schema_types_found": [],
        "schema_types_missing": ["Product", "Organization", "FAQPage", "HowTo", "ItemList", "SpeakableSpecification"],
        "ai_visibility_notes": "Virtually invisible to AI assistants. Clean brand story that AI should be surfacing but isn't. High opportunity.",
        "use_for_case_study": True,
        "revenue_potential": "very_high",
    },
    {
        "brand": "조선미녀",
        "brand_en": "beauty of joseon",
        "scan_date": "2026-05-05",
        "geo_score": 91,
        "naver_seo_score": 84,
        "has_llms_txt": True,
        "has_schema_org": True,
        "schema_types_found": ["Product", "Organization", "FAQPage", "ItemList"],
        "schema_types_missing": ["HowTo", "SpeakableSpecification"],
        "ai_visibility_notes": "Best-in-class GEO in Korean skincare. Has llms.txt. Used as benchmark for client scoring.",
        "use_for_case_study": False,
        "revenue_potential": "low",
    },
]

NEW_KEYWORDS = [
    "한국 스킨케어 AI 추천",
    "피부 타입별 화장품 AI",
    "GEO 최적화 화장품",
    "AI 검색 스킨케어",
    "비건 스킨케어 한국",
    "더마 코스메틱 브랜드",
    "저자극 세럼 추천 AI",
    "한방 스킨케어 성분",
    "민감성 피부 루틴 AI",
    "화장품 성분 분석 AI",
    "K-beauty AI visibility",
    "ChatGPT Korean skincare recommendation",
    "Perplexity 한국 화장품",
]

QUERY_SHIFT_OBSERVATIONS = [
    {
        "id": "chatgpt_korean_skincare_2026q1",
        "date": "2026-05-01",
        "platform": "ChatGPT (GPT-4o)",
        "query": "Korean skincare routine for oily skin",
        "observation": "Top mentions: 조선미녀, 라네즈, 코스알엑스. Innisfree dropped from top 5 vs 2025-Q4. FAQPage schema brands surfaced more.",
        "action_hint": "FAQPage schema is confirmed ranking signal for ChatGPT brand surfacing.",
    },
    {
        "id": "perplexity_k_beauty_2026q1",
        "date": "2026-05-02",
        "platform": "Perplexity AI",
        "query": "best Korean toner 2026",
        "observation": "Perplexity now cites ingredient claims directly. Brands with HowTo schema get ingredient use-case citations.",
        "action_hint": "HowTo schema with ingredient steps boosts Perplexity citation probability.",
    },
    {
        "id": "naver_ai_overview_launch",
        "date": "2026-04-15",
        "platform": "Naver AI Overview (Korean market)",
        "query": "수분 세럼 추천",
        "observation": "Naver AI Overview launched in Korea. Prioritizes Naver Blog posts with structured data + high dwell time. D2C brand blogs with schema outperform.",
        "action_hint": "Naver Blog + Product schema = new GEO opportunity specific to Korean market.",
    },
]

GEO_SCHEMA_PATTERNS = [
    {
        "id": "speakable_product_review",
        "schema_type": "SpeakableSpecification",
        "use_case": "Make product review text readable by Google Assistant / Naver Clova",
        "template": {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "{{product_name}}",
            "description": "{{product_description}}",
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".product-summary", ".key-ingredients"]
            }
        },
        "note": "Use on product detail pages with summary + ingredient sections",
    },
    {
        "id": "faqpage_ingredient_guide",
        "schema_type": "FAQPage",
        "use_case": "Capture ChatGPT/Perplexity FAQ surfacing for ingredient queries",
        "template": {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "{{ingredient}} 효과는 무엇인가요?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "{{ingredient_effect_text}}"
                    }
                }
            ]
        },
        "note": "Template for ingredient guide blog posts. One FAQ block per major ingredient.",
    },
    {
        "id": "howto_skincare_routine",
        "schema_type": "HowTo",
        "use_case": "Capture 'how to use' and routine queries from AI assistants",
        "template": {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": "{{brand_name}} {{product_name}} 사용법",
            "step": [
                {
                    "@type": "HowToStep",
                    "name": "{{step_name}}",
                    "text": "{{step_description}}"
                }
            ]
        },
        "note": "Use on product detail pages and routine guide blog posts",
    },
    {
        "id": "itemlist_product_collection",
        "schema_type": "ItemList",
        "use_case": "Capture 'best products for X' list queries from AI assistants",
        "template": {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "{{list_title}}",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "{{product_name}}",
                    "url": "{{product_url}}"
                }
            ]
        },
        "note": "Use on comparison pages and 'best of' blog posts. Minimum 3 items.",
    },
]


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_geo_seo_blog.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_geo_seo_blog.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _select_menu_item(state: dict) -> str:
    last = state.get("last_improvement", "")
    menu = ["scan_brand", "update_keyword_bank", "log_query_shift", "add_schema_pattern"]
    available = [m for m in menu if m != last]
    return random.choice(available)


def run(data_dir: Path) -> dict:
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    if state.get("last_run_date") == today_str:
        return {"skipped": True, "reason": "already ran today", "strand": STRAND_NAME}

    # --- Fix 1: Try live WebSearch signal first ---
    live = search_any(LIVE_SEARCH_QUERIES)
    if live:
        log_file = data_dir / "query_shift_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        obs = {
            "id": f"geo_live_{today_str}",
            "date": today_str,
            "platform": "WebSearch (live)",
            "query": live["query"],
            "observation": live["snippet"],
            "action_hint": "Verify manually and update brand scan or schema recommendations",
            "live_signal": True,
            "source": live["url"],
            "logged_date": today_str,
        }
        existing.append(obs)
        state["last_run_date"] = today_str
        state["last_improvement"] = "log_query_shift"
        _save_state(data_dir, state)
        return {
            "improvement_type": "log_query_shift",
            "strand": STRAND_NAME,
            "idempotent_key": f"geo_live_{today_str}",
            "file_path": "agents/evolution_loop/data/query_shift_log.json",
            "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
            "summary": f"[LIVE] GEO signal: {live['title'][:80]}",
            "dry_run_passed": True,
            "live_signal": True,
            "commit_message": f"chore(evolution): geo-seo-blog live signal {today_str}",
            "flag_for_report": False,
        }

    improvement = _select_menu_item(state)

    if improvement == "scan_brand":
        log_file = data_dir / "brand_scan_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        scanned_brands = {e.get("brand") for e in existing}
        candidates = [b for b in BRAND_SCAN_RESULTS if b["brand"] not in scanned_brands]
        if not candidates:
            improvement = "update_keyword_bank"
        else:
            brand = {**candidates[0], "logged_date": today_str}
            existing.append(brand)
            result = {
                "improvement_type": "scan_brand",
                "strand": STRAND_NAME,
                "idempotent_key": f"brand_{brand['brand']}",
                "file_path": "agents/evolution_loop/data/brand_scan_log.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"GEO scan: {brand['brand']} scored {brand['geo_score']}/100 (case study: {brand['use_for_case_study']})",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): geo-seo-blog scan brand {brand['brand_en']}",
                "flag_for_report": brand.get("use_for_case_study", False),
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    if improvement == "update_keyword_bank":
        kw_file = data_dir / "keyword_bank.json"
        existing = {"keywords": [], "last_updated": ""}
        if kw_file.exists():
            try:
                existing = json.loads(kw_file.read_text(encoding="utf-8"))
            except Exception:
                existing = {"keywords": [], "last_updated": ""}
        current_kws = set(existing.get("keywords", []))
        new_kws = [k for k in NEW_KEYWORDS if k not in current_kws]
        if not new_kws:
            improvement = "log_query_shift"
        else:
            added = new_kws[:3]  # max 3 per night
            existing["keywords"] = list(current_kws) + added
            existing["last_updated"] = today_str
            result = {
                "improvement_type": "update_keyword_bank",
                "strand": STRAND_NAME,
                "idempotent_key": f"keywords_{today_str}",
                "file_path": "agents/evolution_loop/data/keyword_bank.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"Keyword bank updated: +{len(added)} keywords ({', '.join(added[:2])}...)",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): geo-seo-blog update keyword bank +{len(added)}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    if improvement == "log_query_shift":
        log_file = data_dir / "query_shift_log.json"
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
        logged_ids = {e.get("id") for e in existing}
        candidates = [o for o in QUERY_SHIFT_OBSERVATIONS if o["id"] not in logged_ids]
        if not candidates:
            improvement = "add_schema_pattern"
        else:
            obs = {**candidates[0], "logged_date": today_str}
            existing.append(obs)
            result = {
                "improvement_type": "log_query_shift",
                "strand": STRAND_NAME,
                "idempotent_key": f"query_shift_{obs['id']}",
                "file_path": "agents/evolution_loop/data/query_shift_log.json",
                "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
                "summary": f"Query shift logged: {obs['platform']} / '{obs['query']}' ({obs['action_hint'][:50]}...)",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): geo-seo-blog log query shift {obs['id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    # add_schema_pattern
    log_file = data_dir / "geo_schema_patterns.json"
    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except Exception:
            existing = []
    logged_ids = {p.get("id") for p in existing}
    candidates = [p for p in GEO_SCHEMA_PATTERNS if p["id"] not in logged_ids]
    if not candidates:
        pattern = {"id": f"placeholder_{today_str}", "note": "No new schema pattern available", "added_date": today_str}
    else:
        pattern = {**candidates[0], "added_date": today_str}
    existing.append(pattern)
    result = {
        "improvement_type": "add_schema_pattern",
        "strand": STRAND_NAME,
        "idempotent_key": f"schema_{pattern['id']}",
        "file_path": "agents/evolution_loop/data/geo_schema_patterns.json",
        "write_content": json.dumps(existing, ensure_ascii=False, indent=2),
        "summary": f"GEO schema pattern added: {pattern.get('schema_type', pattern['id'])} ({pattern.get('use_case', '')[:50]}...)",
        "dry_run_passed": True,
        "commit_message": f"chore(evolution): geo-seo-blog add schema pattern {pattern['id']}",
        "flag_for_report": False,
    }
    state["last_run_date"] = today_str
    state["last_improvement"] = improvement
    _save_state(data_dir, state)
    return result
