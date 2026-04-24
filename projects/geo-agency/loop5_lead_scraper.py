"""
Loop 5 — KakaoTalk Lead Scraper + Enricher
Reads targets/raw.txt (business names/handles you paste after KakaoTalk sessions)
Enriches each: finds website, scores GEO vulnerability, ranks by opportunity.
Output: targets/YYYY-MM-DD-shortlist.md + appends top targets to targets/targets.txt (feeds Loop 1)

Usage:
    python loop5_lead_scraper.py
    # Run after each KakaoTalk open chat session
    # Paste business names into targets/raw.txt first

raw.txt format (one per line):
    카페봄봄
    스튜디오달빛
    https://instagram.com/someshop
    플로리스트정원
"""

import sys
import os
import re
import json
import time
from pathlib import Path
from datetime import date
import requests
import anthropic

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

for _p in [HERE / ".env", ROOT / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

RAW_FILE = HERE / "targets" / "raw.txt"
TARGETS_FILE = HERE / "targets" / "targets.txt"


def load_raw() -> list[str]:
    if not RAW_FILE.exists():
        RAW_FILE.write_text("# Paste business names or Instagram handles here, one per line\n", encoding="utf-8")
        return []
    lines = []
    for line in RAW_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            lines.append(line)
    return lines


def find_website(business_name: str) -> str:
    """Use Perplexity to find the business website."""
    if business_name.startswith("http"):
        return business_name

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "sonar",
        "messages": [
            {"role": "user", "content": f"Find the official website URL for Korean business: {business_name}. Return only the URL, nothing else. If no website, return 'none'."}
        ]
    }
    try:
        r = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body, timeout=15)
        text = r.json()["choices"][0]["message"]["content"].strip()
        # Extract URL
        match = re.search(r"https?://[^\s\"'>]+", text)
        if not match:
            return "none"
        url = re.sub(r"\[\d+\]", "", match.group(0))
        return url.rstrip("/,.")  or "none"
    except Exception:
        return "none"


def score_opportunity(business_name: str, url: str) -> dict:
    """Quick opportunity scoring without full GEO audit — just signals."""
    prompt = f"""
Score this Korean business as a GEO audit sales opportunity (1-10 each):

Business: {business_name}
Website: {url}

Dimensions:
1. website_quality: Does it look old, no-mobile, basic? (10 = very bad = high opportunity)
2. ai_invisibility: Likely invisible to ChatGPT/Perplexity? (10 = very likely = high opportunity)
3. local_business_type: Is this a local SME likely to pay for marketing help? (10 = perfect fit)
4. contact_ease: How easy to DM them? (10 = Instagram/KakaoTalk direct)

Output JSON only:
{{"website_quality": X, "ai_invisibility": X, "local_business_type": X, "contact_ease": X, "reason": "one sentence"}}
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    try:
        # Extract JSON
        match = re.search(r"\{.*\}", text, re.DOTALL)
        data = json.loads(match.group(0)) if match else {}
        avg = sum(v for k, v in data.items() if isinstance(v, (int, float))) / 4
        data["avg"] = round(avg, 1)
        return data
    except Exception:
        return {"avg": 5.0, "reason": "scoring failed"}


def append_to_targets(urls: list[str]):
    """Append new URLs to targets.txt without duplicates."""
    existing = set()
    if TARGETS_FILE.exists():
        for line in TARGETS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                existing.add(line)

    new_urls = [u for u in urls if u not in existing and u != "none"]
    if new_urls:
        with open(TARGETS_FILE, "a", encoding="utf-8") as f:
            for u in new_urls:
                f.write(u + "\n")
        print(f"  Added {len(new_urls)} new URLs to targets.txt (feeds Loop 1)")


def run():
    raw = load_raw()
    if not raw:
        print("[Loop 5] No entries in targets/raw.txt")
        print("Paste business names from KakaoTalk into that file and re-run.")
        return

    print(f"[Loop 5] Enriching {len(raw)} leads from raw.txt...")

    results = []
    for i, entry in enumerate(raw, 1):
        print(f"  [{i}/{len(raw)}] {entry}")

        url = find_website(entry)
        print(f"    Website: {url}")

        if url == "none":
            scores = {"avg": 3.0, "reason": "no website found"}
        else:
            scores = score_opportunity(entry, url)
        print(f"    Opportunity score: {scores.get('avg', '?')}/10 — {scores.get('reason', '')}")

        results.append({
            "name": entry,
            "url": url,
            "scores": scores,
            "avg": scores.get("avg", 0)
        })
        time.sleep(0.5)

    # Sort by opportunity score
    results.sort(key=lambda x: x["avg"], reverse=True)
    top5 = [r for r in results if r["url"] != "none"][:5]

    # Write shortlist
    out_lines = [f"# Lead Shortlist — {date.today()}\n", f"Enriched from: {RAW_FILE}\n", "---\n"]
    for rank, r in enumerate(results, 1):
        flag = " <-- DM TODAY" if r in top5 else ""
        out_lines.append(f"## {rank}. {r['name']}{flag}")
        out_lines.append(f"**Website:** {r['url']}")
        out_lines.append(f"**Opportunity Score:** {r['avg']}/10")
        out_lines.append(f"**Why:** {r['scores'].get('reason', '-')}\n")
        out_lines.append("---\n")

    out_path = HERE / "targets" / f"{date.today()}-shortlist.md"
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\n[Loop 5] Shortlist saved: {out_path}")

    # Feed top 5 into Loop 1's targets.txt
    top_urls = [r["url"] for r in top5]
    append_to_targets(top_urls)

    print(f"\n  Top 5 to DM today:")
    for r in top5:
        print(f"    {r['name']} — {r['url']} (score: {r['avg']})")


if __name__ == "__main__":
    run()
