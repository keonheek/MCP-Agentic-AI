"""
brand_voice.py
Reads and formats client brand voice guidelines for use in LLM prompts.
"""

from pathlib import Path


TONE_PRESETS = {
    "expert": "전문적이고 신뢰감 있는 뷰티 전문가 톤. 성분 설명 시 근거 제시.",
    "friendly": "친근하고 대화체. 독자를 '우리'로 지칭. 유머 적절히 사용.",
    "luxury": "프리미엄 브랜드 톤. 절제된 표현, 품격 있는 어휘.",
    "educational": "교육적이고 정보 중심. 단계별 설명, 명확한 구조.",
    "default": "친근하고 전문적인 한국 스킨케어 브랜드 톤.",
}


def get_brand_voice_prompt(client_config: dict) -> str:
    """
    Returns a brand voice instruction string to inject into LLM system prompts.
    Reads from client_config['brand_voice'] or falls back to tone preset.
    """
    custom = client_config.get("brand_voice", "").strip()
    if custom:
        return custom

    tone_key = client_config.get("tone_preset", "default")
    return TONE_PRESETS.get(tone_key, TONE_PRESETS["default"])


def format_for_prompt(client_config: dict) -> str:
    """Full brand context block for LLM system prompt injection."""
    brand = client_config.get("brand_name", "브랜드")
    voice = get_brand_voice_prompt(client_config)
    keywords = client_config.get("target_keywords", [])
    kw_str = ", ".join(keywords) if keywords else "없음"

    return f"""[브랜드 정보]
브랜드명: {brand}
웹사이트: {client_config.get("website_url", "")}
톤앤매너: {voice}
핵심 키워드: {kw_str}
타겟 독자: 20-40대 한국 여성, 스킨케어에 관심 있는 소비자"""
