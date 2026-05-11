"""
Model client wrappers for each LLM under test.
Each returns: {"text": str, "latency_ms": float, "input_tokens": int, "output_tokens": int}
"""
import os
import time
import requests

# 2026 public pricing per 1M tokens (input / output) in USD
MODEL_PRICING = {
    "solar-pro-3":           {"input": 2.00,  "output": 6.00},
    "gemini-2.5-flash":      {"input": 0.15,  "output": 0.60},
    "gpt-4o-mini":           {"input": 0.15,  "output": 0.60},
    "claude-haiku-4-5":      {"input": 0.80,  "output": 4.00},
}


def _cost_usd(model_key: str, input_tokens: int, output_tokens: int) -> float:
    p = MODEL_PRICING.get(model_key, {"input": 0, "output": 0})
    return (input_tokens * p["input"] + output_tokens * p["output"]) / 1_000_000


def call_solar(system_prompt: str, user_message: str) -> dict:
    api_key = os.getenv("UPSTAGE_API_KEY", "")
    if not api_key:
        return {"text": "[DRY MODE: UPSTAGE_API_KEY missing]", "latency_ms": 0,
                "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "dry": True}

    url = "https://api.upstage.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "solar-pro-3",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": 512,
    }

    t0 = time.perf_counter()
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    latency_ms = (time.perf_counter() - t0) * 1000

    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    inp = usage.get("prompt_tokens", 0)
    out = usage.get("completion_tokens", 0)

    return {
        "text": text,
        "latency_ms": round(latency_ms, 1),
        "input_tokens": inp,
        "output_tokens": out,
        "cost_usd": _cost_usd("solar-pro-3", inp, out),
        "dry": False,
    }


def call_gemini(system_prompt: str, user_message: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return {"text": "[DRY MODE: GEMINI_API_KEY missing]", "latency_ms": 0,
                "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "dry": True}

    try:
        from google import genai
        from google.genai import types as genai_types
    except ImportError:
        return {"text": "[ERROR: google-genai not installed. Run: pip install google-genai]",
                "latency_ms": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "dry": True}

    client = genai.Client(api_key=api_key)

    t0 = time.perf_counter()
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_message,
        config=genai_types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=512,
        ),
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    text = resp.text or ""
    usage = resp.usage_metadata
    inp = getattr(usage, "prompt_token_count", 0) or 0
    out = getattr(usage, "candidates_token_count", 0) or 0

    return {
        "text": text,
        "latency_ms": round(latency_ms, 1),
        "input_tokens": inp,
        "output_tokens": out,
        "cost_usd": _cost_usd("gemini-2.5-flash", inp, out),
        "dry": False,
    }


def call_gpt4o_mini(system_prompt: str, user_message: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return {"text": "[DRY MODE: OPENAI_API_KEY missing]", "latency_ms": 0,
                "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "dry": True}

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=512,
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    text = resp.choices[0].message.content
    inp = resp.usage.prompt_tokens
    out = resp.usage.completion_tokens

    return {
        "text": text,
        "latency_ms": round(latency_ms, 1),
        "input_tokens": inp,
        "output_tokens": out,
        "cost_usd": _cost_usd("gpt-4o-mini", inp, out),
        "dry": False,
    }


def call_claude_haiku(system_prompt: str, user_message: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        return {"text": "[DRY MODE: ANTHROPIC_API_KEY missing]", "latency_ms": 0,
                "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "dry": True}

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)

    t0 = time.perf_counter()
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    latency_ms = (time.perf_counter() - t0) * 1000

    text = resp.content[0].text
    inp = resp.usage.input_tokens
    out = resp.usage.output_tokens

    return {
        "text": text,
        "latency_ms": round(latency_ms, 1),
        "input_tokens": inp,
        "output_tokens": out,
        "cost_usd": _cost_usd("claude-haiku-4-5", inp, out),
        "dry": False,
    }


MODEL_REGISTRY = {
    "solar-pro-3":      call_solar,
    "gemini-2.5-flash": call_gemini,
    "gpt-4o-mini":      call_gpt4o_mini,
    "claude-haiku-4-5": call_claude_haiku,
}
