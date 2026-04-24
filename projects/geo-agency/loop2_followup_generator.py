"""
Loop 2 — KakaoTalk Response Monitor + Follow-Up Generator
Reads crm/leads.json → generates follow-up drafts based on lead status.
Output: crm/followups-YYYY-MM-DD.md

Lead status options:
  - new         : just added, no contact yet
  - contacted   : DM sent, waiting for reply
  - replied     : they responded, need follow-up
  - interested  : showed interest, move toward close
  - no_response : no reply after 3+ days
  - closed_won  : converted to client
  - closed_lost : declined

Usage:
    python loop2_followup_generator.py
    # Runs daily via CronCreate (9am)
"""

import sys
import os
import json
from pathlib import Path
from datetime import date, datetime, timedelta
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
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

LEADS_FILE = HERE / "crm" / "leads.json"
OUT_DIR = HERE / "crm"


def load_leads() -> list[dict]:
    if not LEADS_FILE.exists():
        return []
    data = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
    return data.get("leads", [])


def days_since(date_str: str) -> int:
    try:
        d = datetime.fromisoformat(date_str).date()
        return (date.today() - d).days
    except Exception:
        return 0


def generate_message(lead: dict, message_type: str) -> str:
    name = lead.get("name", "사장님")
    business = lead.get("business", "")
    url = lead.get("url", "")
    score = lead.get("geo_score", "?")
    last_message = lead.get("last_message", "")

    prompts = {
        "follow_up": f"""
You are 김건희, Korean AI search consultant. Write a short KakaoTalk follow-up (2-3 sentences, Korean) for a lead who replied showing interest.

Lead info: {name}, business: {business}, URL: {url}, GEO score: {score}/100
Their last message: "{last_message}"

Next step: offer to send the full free audit report and schedule a 15-min call.
Korean only. Casual-professional tone. No emojis except :)
Output only the message text.
""",
        "re_engage": f"""
You are 김건희, Korean AI search consultant. Write a gentle re-engagement KakaoTalk message (2 sentences, Korean) for a lead who hasn't replied in 3+ days.

Lead info: {name}, business: {business}, GEO score: {score}/100

Remind them of the free audit offer. Create light urgency (only taking 3 free audits this week).
Korean only. Warm tone. Output only the message text.
""",
        "onboarding": f"""
You are 김건희, Korean AI search consultant. Write a warm welcome KakaoTalk message (3-4 sentences, Korean) for a new paying client.

Client info: {name}, business: {business}

Thank them, confirm next steps (you'll send implementation checklist within 24 hours), and give your KakaoTalk availability.
Korean only. Professional but warm. Output only the message text.
"""
    }

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompts[message_type]}]
    )
    return response.content[0].text.strip()


def run():
    leads = load_leads()
    if not leads:
        print("[Loop 2] No leads in crm/leads.json yet.")
        print("Add leads manually — see README for format.")
        return

    actionable = [
        l for l in leads
        if l.get("status") in ("replied", "interested", "no_response", "closed_won")
    ]

    print(f"[Loop 2] {len(leads)} total leads, {len(actionable)} need follow-up today")

    out_lines = [f"# Follow-Up Drafts — {date.today()}\n", "---\n"]
    count = 0

    for lead in actionable:
        status = lead.get("status")
        name = lead.get("name", "Unknown")

        if status in ("replied", "interested"):
            msg_type = "follow_up"
            label = "Follow-up (replied)"
        elif status == "no_response" and days_since(lead.get("last_contact", "")) >= 3:
            msg_type = "re_engage"
            label = "Re-engagement (3+ days silent)"
        elif status == "closed_won":
            msg_type = "onboarding"
            label = "Onboarding (new client!)"
        else:
            continue

        print(f"  Generating {label} for {name}...")
        try:
            msg = generate_message(lead, msg_type)
            out_lines.append(f"## {name} — {lead.get('business', '')}")
            out_lines.append(f"**Status:** {status} | **Type:** {label}")
            out_lines.append(f"\n**Message:**\n{msg}\n")
            out_lines.append("---\n")
            count += 1
        except Exception as e:
            print(f"  ERROR for {name}: {e}")

    out_path = OUT_DIR / f"followups-{date.today()}.md"
    out_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\n[Loop 2] Done. {count} follow-ups saved to: {out_path}")


if __name__ == "__main__":
    run()
