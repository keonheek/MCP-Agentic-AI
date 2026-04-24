"""
GEO Audit Outreach System — 강남 세무사 pipeline

Automates the full outreach loop:
  1. Run GEO audit on 20 hardcoded 강남 세무사 firms
  2. Generate a personalized 2-page PDF audit report per firm
  3. Generate a KakaoTalk DM (autoresearch loop, persuasiveness >= 8.0)
  4. Track everything in SQLite (outreach.db)

Usage:
    python projects/geo-agency/outreach.py                      # full pipeline, all 20 firms
    python projects/geo-agency/outreach.py --firm "세무법인 다솔"  # single firm
    python projects/geo-agency/outreach.py --list               # show tracker table
    python projects/geo-agency/outreach.py --update "세무법인 다솔" dm_sent 1
"""

import sys
import os
import json
import time
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime

# ── sys.path setup ────────────────────────────────────────────────────────────
_GEO_DIR = Path(__file__).parent
_LEAD_DIR = _GEO_DIR.parent / "lead-intelligence"
sys.path.insert(0, str(_GEO_DIR))
sys.path.insert(0, str(_LEAD_DIR))

# ── .env loading ──────────────────────────────────────────────────────────────
for _p in [_GEO_DIR / ".env", _GEO_DIR.parent / ".env", _GEO_DIR.parent.parent / ".env"]:
    if _p.exists():
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=_p)
        break

# ── API keys ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

if not ANTHROPIC_API_KEY:
    print("[ERROR] ANTHROPIC_API_KEY not set in .env")
    sys.exit(1)
if not PERPLEXITY_API_KEY:
    print("[ERROR] PERPLEXITY_API_KEY not set in .env")
    sys.exit(1)

import anthropic as _anthropic_sdk
_client = _anthropic_sdk.Anthropic(api_key=ANTHROPIC_API_KEY)

SONNET = "claude-sonnet-4-6"
HAIKU  = "claude-haiku-4-5-20251001"

DM_SCORE_THRESHOLD = 8.0
DM_MAX_ITERATIONS  = 5

# ── Hardcoded 20 강남 세무사 firms ────────────────────────────────────────────
FIRMS = [
    {"name": "세무법인 다솔",      "website": "https://www.dasoltax.com"},
    {"name": "세무법인 택스코리아", "website": "https://www.taxkorea.co.kr"},
    {"name": "강남세무법인",        "website": "https://www.gangnamtax.co.kr"},
    {"name": "세무법인 가나",       "website": "https://www.ganatax.co.kr"},
    {"name": "세무법인 정상",       "website": "https://www.jeongsangtax.co.kr"},
    {"name": "세무법인 한빛",       "website": "https://www.hanbittax.co.kr"},
    {"name": "세무법인 이현",       "website": "https://www.ihyuntax.co.kr"},
    {"name": "세무법인 광장",       "website": "https://www.bkl-tax.co.kr"},
    {"name": "세무법인 삼덕",       "website": "https://www.samduk.co.kr"},
    {"name": "세무법인 청솔",       "website": "https://www.cheongsolltax.co.kr"},
    {"name": "세무법인 지율",       "website": "https://www.jiyultax.co.kr"},
    {"name": "세무법인 우덕",       "website": "https://www.wooduktax.com"},
    {"name": "세무법인 대명",       "website": "https://www.daemungtax.co.kr"},
    {"name": "세무법인 한울",       "website": "https://www.hanuiltax.co.kr"},
    {"name": "세무법인 미래",       "website": "https://www.miraetax.co.kr"},
    {"name": "세무법인 유일",       "website": "https://www.yuilltax.co.kr"},
    {"name": "세무법인 나라",       "website": "https://www.naratax.co.kr"},
    {"name": "세무법인 신영",       "website": "https://www.shinyoungtax.co.kr"},
    {"name": "세무법인 하나로",     "website": "https://www.hanarotax.co.kr"},
    {"name": "세무법인 세종",       "website": "https://www.sejongltax.co.kr"},
]

DB_PATH     = _GEO_DIR / "outreach.db"
OUTPUT_DIR  = _GEO_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Database ──────────────────────────────────────────────────────────────────

def init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS firms (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL UNIQUE,
            website       TEXT,
            geo_score     INTEGER,
            top_competitor TEXT,
            pdf_path      TEXT,
            dm_text       TEXT,
            dm_score      REAL,
            audit_sent    INTEGER DEFAULT 0,
            dm_sent       INTEGER DEFAULT 0,
            response      TEXT,
            status        TEXT    DEFAULT 'pending',
            created_at    TEXT,
            updated_at    TEXT
        )
    """)
    conn.commit()
    # Seed firms that don't exist yet
    now = datetime.now().isoformat(timespec="seconds")
    for f in FIRMS:
        conn.execute(
            "INSERT OR IGNORE INTO firms (name, website, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (f["name"], f["website"], now, now),
        )
    conn.commit()
    return conn


def _update_firm(conn: sqlite3.Connection, name: str, **kwargs):
    kwargs["updated_at"] = datetime.now().isoformat(timespec="seconds")
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [name]
    conn.execute(f"UPDATE firms SET {sets} WHERE name = ?", vals)
    conn.commit()


# ── Competitor lookup (세무사-specific) ───────────────────────────────────────

def _get_top_competitor(firm_name: str) -> str:
    """
    Queries Perplexity: 'ChatGPT에서 강남 세무사 추천 검색 시 상위 노출 세무법인'
    Extracts the first real 세무법인/세무사무소 name that is NOT firm_name.
    Falls back to '경쟁 세무법인' if extraction fails.
    """
    query = f"ChatGPT 또는 Perplexity에서 '강남 세무사 추천'을 검색하면 상위에 나오는 세무법인 또는 세무사무소 이름을 알려주세요. {firm_name}는 제외하고 실제 사무소 이름만 나열해주세요."
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": query}],
        "max_tokens": 300,
    }
    try:
        import requests
        resp = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]

        # Match Korean firm names with 세무 suffix patterns
        import re
        patterns = re.findall(
            r'(?:세무법인|세무사무소|세무사)\s*[\uAC00-\uD7A3]{1,8}|[\uAC00-\uD7A3]{1,8}\s*(?:세무법인|세무사무소|세무사)',
            text,
        )
        for p in patterns:
            p = p.strip()
            if p and firm_name not in p and len(p) > 3:
                print(f"    [competitor] {firm_name} → {p}")
                return p

        print(f"    [competitor] No match extracted, using fallback")
        return "경쟁 세무법인"
    except Exception as e:
        print(f"    [competitor error] {e}")
        return "경쟁 세무법인"


# ── Step 1: GEO audit + PDF ───────────────────────────────────────────────────

def run_audit(firm: dict, conn: sqlite3.Connection) -> dict:
    """
    Runs GEO audit via lead-intelligence/geo_audit.py,
    generates a PDF via geo_report_pdf.py, updates DB.
    Returns enriched audit dict.
    """
    from geo_audit import audit_single_company, generate_dynamic_recommendations
    from geo_report_pdf import generate_pdf
    from before_after import get_before

    name = firm["name"]
    print(f"\n{'='*60}")
    print(f"[Audit] {name}")

    audit = audit_single_company(name)
    breakdown = audit.get("geo_breakdown", {})
    recs = generate_dynamic_recommendations(breakdown, name)
    geo_score = audit.get("geo_score", 0)
    top_competitor = _get_top_competitor(name)

    print(f"  GEO score: {geo_score}/100 | top competitor: {top_competitor}")

    # Get "before" proof (what AI currently says)
    before = get_before(name, "세무/회계 서비스")

    # Generate PDF
    pdf_path = generate_pdf(audit, recs, before_text=before, output_dir=str(OUTPUT_DIR))
    print(f"  PDF saved: {pdf_path}")

    _update_firm(
        conn, name,
        geo_score=geo_score,
        top_competitor=top_competitor,
        pdf_path=str(pdf_path),
        audit_sent=1,
    )

    audit["_top_competitor"] = top_competitor
    return audit


# ── Step 2: KakaoTalk DM generator (autoresearch loop) ───────────────────────

def _draft_dm(firm_name: str, competitor: str, geo_score: int, feedback: str = "") -> str:
    """Sonnet drafts a KakaoTalk DM using the Hormozi hook."""
    feedback_block = f"\n\n이전 버전 개선 요청:\n{feedback}" if feedback else ""
    prompt = f"""강남 세무사 사무소 대표님께 보낼 KakaoTalk 첫 메시지를 작성해주세요.

목표: 무료 GEO(AI 검색 가시성) 진단 리포트 전달 동의 받기

핵심 정보:
- 대상: {firm_name} 대표님
- 경쟁사 (AI에서 먼저 노출): {competitor}
- 현재 AI 가시성 점수: {geo_score}/100

Hormozi hook 구조:
1. ChatGPT/Perplexity 검색 시 경쟁사가 먼저 나온다는 사실로 시작
2. {firm_name}는 안 나온다는 문제 제기
3. 무료 진단 리포트 제안으로 마무리

제약:
- 150자 이하 (KakaoTalk 첫 메시지 특성)
- 구어체, 자연스럽고 부담 없는 톤
- 영업 티 최소화 — 진짜 도움이 되고 싶다는 뉘앙스
- 발신자: SKKU 재학생 김건희{feedback_block}

메시지만 출력하세요 (다른 설명 없이)."""

    resp = _client.messages.create(
        model=SONNET,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def _score_dm(dm_text: str, firm_name: str) -> tuple[float, str]:
    """Haiku scores the DM on persuasiveness only. Returns (score, feedback)."""
    prompt = f"""다음 KakaoTalk 메시지를 평가하고 JSON으로만 응답하세요.

대상: {firm_name} 세무사 대표
메시지:
{dm_text}

평가 기준:
- persuasiveness (0-10): 대표님이 "무료 리포트 보내주세요"라고 답장할 가능성

{{"persuasiveness": <score>, "feedback": "<개선 포인트 한 줄>"}}"""

    resp = _client.messages.create(
        model=HAIKU,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    try:
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        score = float(data.get("persuasiveness", 5.0))
        feedback = data.get("feedback", "")
        return score, feedback
    except Exception as e:
        print(f"    [haiku parse error] {e} | raw: {raw[:100]}")
        return 7.0, ""


def generate_dm(firm_name: str, competitor: str, geo_score: int) -> tuple[str, float]:
    """
    Autoresearch loop: draft → score → improve until persuasiveness >= 8.0.
    Returns (dm_text, final_score).
    """
    print(f"\n[DM] Generating KakaoTalk message for {firm_name}...")
    dm = _draft_dm(firm_name, competitor, geo_score)
    score, feedback = _score_dm(dm, firm_name)
    iteration = 1
    print(f"  Iter {iteration}: score={score:.1f} | {dm[:60]}...")

    while score < DM_SCORE_THRESHOLD and iteration < DM_MAX_ITERATIONS:
        print(f"  Score {score} < {DM_SCORE_THRESHOLD} — improving (iter {iteration + 1})...")
        dm = _draft_dm(firm_name, competitor, geo_score, feedback=feedback)
        score, feedback = _score_dm(dm, firm_name)
        iteration += 1
        print(f"  Iter {iteration}: score={score:.1f} | {dm[:60]}...")

    print(f"  Final score: {score:.1f}/10 after {iteration} iteration(s)")
    return dm, score


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_outreach(conn: sqlite3.Connection, firm_name: str | None = None, dm_only: bool = False):
    """Process one firm by name, or all 20 if firm_name is None.
    dm_only=True: skip audit, re-generate DMs only for firms with audit_sent=1.
    """
    if firm_name:
        targets = [f for f in FIRMS if f["name"] == firm_name]
        if not targets:
            print(f"[ERROR] Firm not found in list: {firm_name}")
            print(f"Available: {[f['name'] for f in FIRMS]}")
            return
    else:
        targets = FIRMS

    for i, firm in enumerate(targets):
        name = firm["name"]
        try:
            if dm_only:
                # Load existing audit data from DB
                row = conn.execute(
                    "SELECT geo_score, top_competitor FROM firms WHERE name = ?", (name,)
                ).fetchone()
                if not row or row[0] is None:
                    print(f"\n[Skip] {name} — no audit data, run without --dm-only first")
                    continue
                geo_score, competitor = row
                # Re-fetch a real competitor name (old one was generic)
                competitor = _get_top_competitor(name)
                _update_firm(conn, name, top_competitor=competitor)
            else:
                audit = run_audit(firm, conn)
                competitor = audit.get("_top_competitor", "경쟁 세무법인")
                geo_score  = audit.get("geo_score", 0)

            dm, dm_score = generate_dm(name, competitor, geo_score)

            _update_firm(conn, name, dm_text=dm, dm_score=dm_score, status="ready")

            print(f"\n[Done] {name}")
            print(f"  GEO score:  {geo_score}/100")
            print(f"  Competitor: {competitor}")
            print(f"  DM score:   {dm_score:.1f}/10")
            print(f"  DM text:    {dm}")

        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            _update_firm(conn, name, status="error")

        if i < len(targets) - 1:
            print("\n[Sleep 2s before next firm...]")
            time.sleep(2)


# ── CLI helpers ───────────────────────────────────────────────────────────────

def show_list(conn: sqlite3.Connection):
    sys.stdout.reconfigure(encoding="utf-8")
    rows = conn.execute("""
        SELECT name, geo_score, top_competitor, dm_score,
               audit_sent, dm_sent, status, pdf_path
        FROM firms ORDER BY id
    """).fetchall()

    header = f"{'#':>2}  {'Name':<18} {'GEO':>4}  {'DM Score':>8}  {'Audit':>5}  {'DM':>5}  {'Status':<12}  Top Competitor"
    print(header)
    print("-" * 90)
    for idx, (name, geo, competitor, dm_score, a_sent, d_sent, status, pdf) in enumerate(rows, 1):
        geo_str  = f"{geo}/100" if geo is not None else "---"
        dm_str   = f"{dm_score:.1f}" if dm_score is not None else "---"
        comp_str = (competitor or "")[:20]
        st       = status or "pending"
        print(f"{idx:>2}  {name:<18} {geo_str:>6}  {dm_str:>8}  {'Y' if a_sent else 'N':>5}  {'Y' if d_sent else 'N':>5}  {st:<12}  {comp_str}")


def update_field(conn: sqlite3.Connection, firm_name: str, field: str, value: str):
    allowed = {"dm_sent", "audit_sent", "response", "status"}
    if field not in allowed:
        print(f"[ERROR] Field '{field}' not updatable. Allowed: {allowed}")
        return
    # Coerce booleans
    if field in ("dm_sent", "audit_sent"):
        value = int(value)
    _update_firm(conn, firm_name, **{field: value})
    print(f"[Updated] {firm_name} | {field} = {value}")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="GEO Audit Outreach — 강남 세무사")
    parser.add_argument("--firm",    help="Process only this firm by exact name")
    parser.add_argument("--list",    action="store_true", help="Show tracker table")
    parser.add_argument("--dm-only", action="store_true", help="Skip audits, re-generate DMs only (uses existing audit data)")
    parser.add_argument(
        "--update", nargs=3, metavar=("FIRM", "FIELD", "VALUE"),
        help="Update a field: --update '세무법인 다솔' dm_sent 1"
    )
    args = parser.parse_args()

    conn = init_db()

    if args.list:
        show_list(conn)
    elif args.update:
        update_field(conn, args.update[0], args.update[1], args.update[2])
    else:
        run_outreach(conn, firm_name=args.firm, dm_only=args.dm_only)

    conn.close()
