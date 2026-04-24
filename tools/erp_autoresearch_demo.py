import os, json, anthropic
from dotenv import load_dotenv
load_dotenv()

SCORER = "claude-haiku-4-5-20251001"
GENERATOR = "claude-sonnet-4-6"
THRESHOLD = 8.0
MAX_ITER = 5

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

context = """
Target: Korean 세무사 (tax accountant) running a small firm in 강남.
Currently tracking client quotes and follow-ups in Excel.
We are offering: ERP system (quote tracker + client log) built in 4 weeks, 1.5M KRW.
Channel: KakaoTalk cold DM.
Language: Korean. Casual-professional tone.
Goal: Get them to say "send me the free audit" or "tell me more".
"""

initial = """안녕하세요 대표님,

저는 AI 기반 업무 자동화를 개발하는 김건희입니다.
세무사 사무소에서 견적 관리나 고객 이력 추적을 엑셀로 하고 계신 분들이 많아서 연락드렸습니다.

저희는 4주 안에 견적서 관리 + 고객 로그 시스템을 개발해드리고 있습니다.
관심 있으시면 말씀해 주세요.

감사합니다."""


def score(content):
    prompt = f"""Score this Korean cold KakaoTalk outreach message (0-10 per dimension). Return ONLY valid JSON.

Context: {context}

Message:
{content}

Return:
{{
  "relevance": <0-10, does it speak to their exact pain?>,
  "personalization": <0-10, does it feel targeted not generic?>,
  "persuasiveness": <0-10, does it create urgency or desire to respond?>,
  "feedback": "<one sentence: the single biggest thing to improve>"
}}"""
    r = client.messages.create(
        model=SCORER, max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = r.content[0].text.strip()
    if raw.startswith("```"):
        raw = "\n".join(raw.splitlines()[1:-1])
    return json.loads(raw)


def improve(content, scores):
    prompt = f"""Improve this Korean KakaoTalk cold outreach message based on feedback. Return ONLY the improved message, nothing else.

Context: {context}
Scores: relevance={scores["relevance"]}/10, personalization={scores["personalization"]}/10, persuasiveness={scores["persuasiveness"]}/10
Feedback: {scores["feedback"]}

Current message:
{content}"""
    r = client.messages.create(
        model=GENERATOR, max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text.strip()


print("=== AUTORESEARCH: ERP Cold Outreach (KakaoTalk) ===")
print(f"Target: {THRESHOLD}/10 avg | Dimensions: relevance, personalization, persuasiveness")
print(f"Scorer: Haiku (cheap) | Generator: Sonnet")
print()
print("--- INITIAL MESSAGE ---")
print(initial)
print()

content = initial
final_scores = {}

for i in range(MAX_ITER):
    scores = score(content)
    avg = (scores["relevance"] + scores["personalization"] + scores["persuasiveness"]) / 3
    scores["avg"] = round(avg, 2)
    final_scores = scores

    print(f"--- Iteration {i+1} ---")
    print(f"relevance={scores['relevance']} | personalization={scores['personalization']} | persuasiveness={scores['persuasiveness']} | avg={avg:.2f}")
    print(f"Feedback: {scores['feedback']}")
    print()

    if avg >= THRESHOLD:
        print(f"THRESHOLD {THRESHOLD} REACHED at iteration {i+1}.")
        break

    if i < MAX_ITER - 1:
        content = improve(content, scores)
        print("Improved message:")
        print(content)
        print()

print("=" * 50)
print("FINAL MESSAGE:")
print(content)
print()
print(f"Final scores: relevance={final_scores['relevance']} | personalization={final_scores['personalization']} | persuasiveness={final_scores['persuasiveness']} | avg={final_scores['avg']}/10")
