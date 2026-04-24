"""
Loop 1 — Automated GEO Score Sender
Reads targets/targets.txt → runs GEO audit on each → generates personalized KakaoTalk DM drafts in Korean.
Output: outreach/YYYY-MM-DD-drafts.md

Usage:
    python loop1_geo_score_sender.py
    python loop1_geo_score_sender.py --targets targets/targets.txt
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import date
import anthropic

sys.stdout.reconfigure(encoding="utf-8")

# Resolve paths
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

for _p in [HERE / ".env", ROOT / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

sys.path.insert(0, str(ROOT / "projects" / "lead-intelligence"))
from geo_audit import audit_single_company

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def load_targets(path: Path) -> list[str]:
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def generate_dm_draft(url: str, score: int, weaknesses: list[str]) -> str:
    weakness_str = "\n".join(f"- {w}" for w in weaknesses[:2])
    prompt = f"""
You are 김건희, a Korean AI search optimization consultant. Write a short, friendly KakaoTalk DM (3-4 sentences max) in Korean to the owner of {url}.

Their GEO score (AI 검색 최적화 점수) is {score}/100. Their top weaknesses:
{weakness_str}

Rules:
- Start with a casual but professional greeting
- Mention the specific score and ONE specific weakness you found
- End with: "무료 진단 결과 전체 보내드릴까요? DM 주세요 :)"
- Do NOT mention "AI" as a buzzword — say "AI 검색" or "ChatGPT 같은 AI 도구"
- Keep it under 4 sentences
- Korean only

Output only the message text, nothing else.
"""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def run(targets_file: Path):
    urls = load_targets(targets_file)
    if not urls:
        print("[Loop 1] No targets found in", targets_file)
        print("Add URLs to", targets_file, "and re-run.")
        return

    print(f"[Loop 1] Processing {len(urls)} targets...")

    out_lines = [f"# GEO DM Drafts — {date.today()}\n"]
    out_lines.append(f"Generated from: {targets_file}\n")
    out_lines.append("---\n")

    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] Auditing {url}...")
        try:
            result = audit_single_company(url)
            score = result.get("geo_score", 0)
            # Extract top 2 weaknesses from dimension scores
            dims = result.get("geo_breakdown", {})
            sorted_dims = sorted(dims.items(), key=lambda x: x[1])
            weaknesses = [f"{k} ({v}/100)" for k, v in sorted_dims[:2]]

            dm = generate_dm_draft(url, score, weaknesses)

            out_lines.append(f"## {i}. {url}")
            out_lines.append(f"**GEO Score:** {score}/100")
            out_lines.append(f"**Top weaknesses:** {', '.join(weaknesses)}")
            out_lines.append(f"\n**DM Draft:**\n{dm}\n")
            out_lines.append("---\n")
            print(f"     Score: {score}/100 | DM generated")

        except Exception as e:
            out_lines.append(f"## {i}. {url}\n**ERROR:** {e}\n---\n")
            print(f"     ERROR: {e}")

    out_path = HERE / "outreach" / f"{date.today()}-drafts.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\n[Loop 1] Done. Drafts saved to: {out_path}")
    print(f"         Copy-paste from that file into KakaoTalk.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", default="targets/targets.txt")
    args = parser.parse_args()
    run(HERE / args.targets)
