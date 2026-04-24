"""
GEO Agency — 4-Agent Team Test

Simulates the full 4-agent pipeline using a dummy company:
  Auditor     → runs geo audit, saves audit_output.json
  Researcher  → runs before/after proof, saves evidence_output.json
  Critic      → cross-references both, saves critique_output.json
  Reporter    → reads critique approval, prints final report summary

Run:
    python test_agent_team.py

Uses: https://www.kakaocorp.com (Kakao — well-known, publicly accessible)
"""

import sys
import json
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── paths ────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent        # projects/geo-agency/
ROOT = HERE.parent.parent           # MCP_Agentic AI/
OUTPUT_DIR = HERE / "team_test_output"
OUTPUT_DIR.mkdir(exist_ok=True)

AUDIT_OUTPUT   = OUTPUT_DIR / "audit_output.json"
EVIDENCE_OUTPUT = OUTPUT_DIR / "evidence_output.json"
CRITIQUE_OUTPUT = OUTPUT_DIR / "critique_output.json"

# ── dummy target ──────────────────────────────────────────────────────────────
COMPANY_NAME     = "세무법인 엑스퍼트"
PRODUCT_CATEGORY = "세무 / 회계 서비스"
WEBSITE_URL      = "http://taxexpert.kr"

# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1: AUDITOR
# File territory: geo_audit.py, audit_output.json
# ─────────────────────────────────────────────────────────────────────────────
def run_auditor():
    print("\n" + "="*60)
    print("AGENT 1: AUDITOR")
    print("="*60)
    print(f"Target: {COMPANY_NAME} ({WEBSITE_URL})")
    print("Running 10-dimension GEO audit via lead-intelligence/geo_audit.py...")

    try:
        lead_intel_path = str(ROOT / "projects" / "lead-intelligence")
        if lead_intel_path not in sys.path:
            sys.path.insert(0, lead_intel_path)
        # Force reimport in case of stale module cache
        import importlib, importlib.util
        spec = importlib.util.spec_from_file_location(
            "geo_audit",
            ROOT / "projects" / "lead-intelligence" / "geo_audit.py"
        )
        geo_audit_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(geo_audit_mod)
        audit_single_company = geo_audit_mod.audit_single_company
        result = audit_single_company(COMPANY_NAME)  # signature: name only
    except Exception as e:
        print(f"[Auditor] geo_audit import failed: {e}")
        print("[Auditor] Using fallback mock audit result.")
        result = {
            "corp_name": COMPANY_NAME,
            "website_url": WEBSITE_URL,
            "geo_score": 52,
            "citability": 28,
            "ai_bot_access": 10,
            "ai_policy_file": 0,
            "org_schema": 8,
            "content_schema": 6,
            "naver_presence": 8,
            "kr_platform_sync": 5,
            "brand_sentiment": 12,
            "share_of_voice": 7,
            "recommendations": [
                "llms.txt 파일 루트에 추가",
                "FAQ 스키마 구조화 데이터 추가",
                "robots.txt에 GPTBot, ClaudeBot 허용 명시",
            ],
            "_source": "mock_fallback"
        }

    AUDIT_OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Auditor] GEO Score: {result.get('geo_score', 'N/A')}/100")
    print(f"[Auditor] Saved -> audit_output.json")
    print("[Auditor] >> Messaging Critic: audit complete")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2: RESEARCHER
# File territory: before_after.py, evidence_output.json
# ─────────────────────────────────────────────────────────────────────────────
def run_researcher():
    print("\n" + "="*60)
    print("AGENT 2: RESEARCHER")
    print("="*60)
    print(f"Running before/after citation proof for '{COMPANY_NAME}'...")

    try:
        sys.path.insert(0, str(HERE))
        from before_after import generate_proof
        # Pass a minimal audit dict — Researcher doesn't wait for Auditor in parallel
        mock_audit = {"corp_name": COMPANY_NAME, "geo_score": 52, "website_url": WEBSITE_URL}
        mock_recs = ["llms.txt 파일 추가", "FAQ 스키마 추가"]
        proof = generate_proof(
            company_name=COMPANY_NAME,
            product_category=PRODUCT_CATEGORY,
            audit=mock_audit,
            recommendations=mock_recs,
        )
    except Exception as e:
        print(f"[Researcher] before_after failed: {e}")
        print("[Researcher] Using fallback mock evidence.")
        proof = {
            "company_name": COMPANY_NAME,
            "product_category": PRODUCT_CATEGORY,
            "before": f"AI 시스템은 '{COMPANY_NAME}'에 대해 일반적인 정보만 제공하며 구체적인 서비스나 경쟁력에 대한 언급이 부족합니다.",
            "after": f"[GEO 최적화 후] {COMPANY_NAME}은 국내 IT 플랫폼 분야에서 카카오톡, 카카오페이 등 핵심 서비스를 통해 AI 검색 시스템에서 명확히 인식됩니다.",
            "_source": "mock_fallback"
        }

    EVIDENCE_OUTPUT.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[Researcher] Before excerpt: {proof['before'][:120]}...")
    print(f"[Researcher] After excerpt:  {proof['after'][:120]}...")
    print(f"[Researcher] Saved -> evidence_output.json")
    print("[Researcher] >> Messaging Critic: evidence complete")
    return proof


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3: CRITIC
# File territory: critique_output.json
# Waits for Auditor + Researcher, cross-references, flags gaps
# ─────────────────────────────────────────────────────────────────────────────
def run_critic(audit: dict, evidence: dict):
    print("\n" + "="*60)
    print("AGENT 3: CRITIC")
    print("="*60)
    print("[Critic] Received messages from Auditor + Researcher. Cross-referencing...")

    flags = []
    approved = True

    geo_score = audit.get("geo_score", 0)
    brand_sentiment = audit.get("brand_sentiment", 0)
    before_text = evidence.get("before", "")
    after_text = evidence.get("after", "")

    # Check 1: High brand score but weak AI visibility?
    if brand_sentiment >= 10 and "찾을 수 없" in before_text:
        flags.append("INCONSISTENCY: Brand sentiment score is high but Perplexity found no citations. Possible scoring inflation.")
        approved = False

    # Check 2: After text should mention company name
    if COMPANY_NAME not in after_text and "카카오" not in after_text:
        flags.append("QUALITY ISSUE: After-text does not name the company — generic response, not citation-ready.")
        approved = False

    # Check 3: Audit has recommendations?
    recs = audit.get("recommendations", [])
    if len(recs) < 2:
        flags.append("COMPLETENESS: Fewer than 2 recommendations — audit may be incomplete.")

    # Check 4: Evidence has both before and after?
    if not before_text or not after_text:
        flags.append("MISSING: Before or After text is empty — evidence generation failed.")
        approved = False

    # Summarize
    critique = {
        "approved": approved,
        "flags": flags,
        "geo_score": geo_score,
        "brand_sentiment": brand_sentiment,
        "recommendations_count": len(recs),
        "evidence_quality": "ok" if (before_text and after_text) else "incomplete",
        "verdict": "APPROVED — proceed to Reporter" if approved else "BLOCKED — fix flags before reporting"
    }

    CRITIQUE_OUTPUT.write_text(json.dumps(critique, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[Critic] Verdict: {critique['verdict']}")
    if flags:
        for f in flags:
            print(f"  FLAG: {f}")
    else:
        print("  No flags raised.")
    print(f"[Critic] Saved -> critique_output.json")

    if approved:
        print("[Critic] >> Messaging Reporter: APPROVED, generate report")
    else:
        print("[Critic] >> Messaging Reporter: BLOCKED — do not generate report")
    return critique


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4: REPORTER (Haiku role — cheap, mechanical)
# File territory: geo_report_pdf.py, geo_deliverables.py, final PDFs
# Only runs if Critic approves
# ─────────────────────────────────────────────────────────────────────────────
def run_reporter(audit: dict, evidence: dict, critique: dict):
    print("\n" + "="*60)
    print("AGENT 4: REPORTER (Haiku)")
    print("="*60)

    if not critique.get("approved"):
        print("[Reporter] Message from Critic: BLOCKED. Halting report generation.")
        print("[Reporter] Flags to resolve:")
        for f in critique.get("flags", []):
            print(f"  - {f}")
        return None

    print("[Reporter] Critic approved. Generating report summary...")
    print(f"  Company:      {audit.get('corp_name', COMPANY_NAME)}")
    print(f"  GEO Score:    {audit.get('geo_score', 'N/A')}/100")
    print(f"  Top Recs:     {len(audit.get('recommendations', []))} items")
    print(f"  Evidence:     Before + After texts confirmed present")
    print()
    print("[Reporter] In production: calls geo_report_pdf.py + geo_deliverables.py")
    print("[Reporter] Outputs: 2-page PDF report + implementation kit (robots.txt, llms.txt, JSON-LD, checklist)")
    print("[Reporter] >> Pipeline complete. Ready to send to client.")

    summary = {
        "status": "complete",
        "company": audit.get("corp_name", COMPANY_NAME),
        "geo_score": audit.get("geo_score"),
        "report_generated": True,
        "kit_generated": True,
    }
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATOR — runs all 4 agents in sequence (parallel simulation)
# In real agent teams, Auditor + Researcher fire simultaneously
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*60)
    print("GEO AGENCY — 4-AGENT TEAM TEST")
    print(f"Target: {COMPANY_NAME} | {WEBSITE_URL}")
    print("="*60)
    print("Phase 1: Auditor + Researcher run in parallel (simulated sequentially)")
    print()

    t0 = time.time()

    # Phase 1: parallel (here sequential for test script)
    audit    = run_auditor()
    evidence = run_researcher()

    print(f"\nPhase 1 complete ({time.time()-t0:.1f}s). Forwarding to Critic...")

    # Phase 2: Critic gates the output
    critique = run_critic(audit, evidence)

    # Phase 3: Reporter (only if approved)
    result = run_reporter(audit, evidence, critique)

    # Final
    print("\n" + "="*60)
    print("PIPELINE SUMMARY")
    print("="*60)
    print(f"  Auditor:    {'OK' if audit else 'FAIL'}")
    print(f"  Researcher: {'OK' if evidence else 'FAIL'}")
    print(f"  Critic:     {'APPROVED' if critique.get('approved') else 'BLOCKED'}")
    print(f"  Reporter:   {'COMPLETE' if result else 'SKIPPED'}")
    print(f"  Total time: {time.time()-t0:.1f}s")
    print()
    print(f"Output files in: {OUTPUT_DIR}")
    print("  audit_output.json")
    print("  evidence_output.json")
    print("  critique_output.json")