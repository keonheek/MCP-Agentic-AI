"""
client_config.py
Loads and validates per-client configuration from a JSON file.
"""

import json
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG = {
    "brand_name": "",
    "website_url": "",
    "naver_blog_url": "",
    "industry": "korean_skincare",
    "target_keywords": [],
    "contact_name": "",
    "kakao_id": "",
    "delivery_day": "friday",
    "posts_per_month": 4,
    "tier": "basic",
    "onboarded": False,
}


def load_client_config(config_path: Path) -> dict:
    """Load client config from JSON. Merges with defaults for missing keys."""
    if not config_path.exists():
        raise FileNotFoundError(f"Client config not found: {config_path}")
    raw = json.loads(config_path.read_text(encoding="utf-8"))
    merged = {**DEFAULT_CONFIG, **raw}
    return merged


def save_client_config(config: dict, config_path: Path):
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_demo_config(out_path: Path) -> dict:
    demo = {
        "brand_name": "글로우랩",
        "website_url": "https://glowlab.kr",
        "naver_blog_url": "https://blog.naver.com/glowlab",
        "industry": "korean_skincare",
        "target_keywords": ["비타민C 세럼", "수분크림 추천", "민감성 피부 화장품"],
        "contact_name": "김대표",
        "kakao_id": "glowlab_official",
        "delivery_day": "friday",
        "posts_per_month": 4,
        "tier": "basic",
        "onboarded": True,
        "brand_voice": "친근하고 전문적인 뷰티 전문가 톤",
    }
    save_client_config(demo, out_path)
    return demo
