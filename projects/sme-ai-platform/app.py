"""
SME AI Platform — FastHTML frontend

Run with: python app.py
Serves at: http://localhost:5001
"""
import httpx
import asyncio
from fasthtml.common import *

BACKEND_URL = "http://localhost:8000"

# ─── App setup ────────────────────────────────────────────────────────────────

css = Style("""
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8fafc; color: #1b2a4a; }

/* Navbar */
.navbar { background: white; border-bottom: 1px solid #e2e8f0; padding: 1rem 2rem; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 10; }
.navbar .logo { font-weight: 700; font-size: 1.1rem; color: #00c7be; text-decoration: none; }
.navbar a { color: #00c7be; font-weight: 600; text-decoration: none; font-size: 0.95rem; }
.navbar a:hover { text-decoration: underline; }

/* Hero */
.hero { background: linear-gradient(135deg, #f8fafc 0%, #e0f7f7 100%); padding: 5rem 2rem; text-align: center; }
.hero .badge { display: inline-block; background: #e0f7f7; color: #00c7be; font-size: 0.8rem; font-weight: 600; padding: 0.3rem 0.8rem; border-radius: 999px; margin-bottom: 1.5rem; }
.hero h1 { font-size: 2.8rem; font-weight: 800; color: #1b2a4a; margin-bottom: 1rem; line-height: 1.2; }
.hero p { font-size: 1.1rem; color: #64748b; max-width: 580px; margin: 0 auto 2rem; line-height: 1.7; }
.btn-primary { display: inline-block; background: #00c7be; color: white; font-weight: 600; padding: 0.85rem 2rem; border-radius: 999px; text-decoration: none; font-size: 1rem; transition: background 0.2s; }
.btn-primary:hover { background: #009e96; }

/* Services */
.services { padding: 4rem 2rem; max-width: 900px; margin: 0 auto; }
.services h2 { font-size: 1.8rem; font-weight: 700; text-align: center; margin-bottom: 2.5rem; }
.cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }
.card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; transition: all 0.2s; }
.card:hover { border-color: #00c7be; box-shadow: 0 4px 20px rgba(0,199,190,0.15); }
.card .icon { font-size: 2rem; margin-bottom: 0.75rem; }
.card h3 { font-size: 1rem; font-weight: 700; margin-bottom: 0.5rem; }
.card p { font-size: 0.875rem; color: #64748b; line-height: 1.6; }

/* Audit page */
.audit-page { max-width: 640px; margin: 3rem auto; padding: 0 1.5rem; }
.audit-box { background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2rem; margin-bottom: 1.5rem; }
.audit-box h2 { font-size: 1.4rem; font-weight: 700; margin-bottom: 0.5rem; }
.audit-box .sub { color: #64748b; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1.5rem; }
.input-row { display: flex; gap: 0.75rem; }
.input-row input { flex: 1; padding: 0.7rem 1rem; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 0.95rem; outline: none; }
.input-row input:focus { border-color: #00c7be; }
.input-row button { background: #00c7be; color: white; font-weight: 600; padding: 0.7rem 1.5rem; border: none; border-radius: 8px; cursor: pointer; font-size: 0.95rem; white-space: nowrap; }
.input-row button:hover { background: #009e96; }
.input-row button:disabled { background: #94a3b8; cursor: not-allowed; }

/* Result */
.result-box { background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2rem; }
.score-row { display: flex; align-items: flex-end; gap: 1rem; margin: 1rem 0; }
.score-num { font-size: 4rem; font-weight: 800; line-height: 1; }
.score-denom { font-size: 1.1rem; color: #64748b; padding-bottom: 0.5rem; }
.badge-score { padding: 0.3rem 0.9rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; align-self: flex-end; padding-bottom: 0.55rem; }
.badge-high { background: #dcfce7; color: #16a34a; }
.badge-mid { background: #fef9c3; color: #ca8a04; }
.badge-low { background: #fee2e2; color: #dc2626; }
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.2rem 0; }
.rec-label { font-weight: 700; margin-bottom: 0.6rem; }
.rec-box { background: #f0fdf9; border-left: 4px solid #00c7be; border-radius: 8px; padding: 1rem 1.2rem; font-size: 0.9rem; line-height: 1.7; color: #334155; }
.website-tag { font-size: 0.82rem; color: #64748b; margin-top: 0.3rem; }
.error-box { background: #fee2e2; border-radius: 8px; padding: 0.75rem 1rem; color: #dc2626; font-size: 0.9rem; margin-top: 0.75rem; }
.running-msg { color: #64748b; font-size: 0.9rem; padding: 1rem 0; }

/* Paywall */
.paywall { background: #fffbeb; border: 1px dashed #f59e0b; border-radius: 8px; padding: 1.2rem; margin-top: 1rem; }
.paywall p { font-size: 0.9rem; color: #64748b; margin-bottom: 0.75rem; }
.code-row { display: flex; gap: 0.6rem; }
.code-row input { padding: 0.5rem 0.8rem; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 0.9rem; width: 160px; }
.code-row button { background: #00c7be; color: white; padding: 0.5rem 1rem; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 600; }

/* Footer */
.footer { text-align: center; padding: 2rem; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 0.85rem; margin-top: 3rem; }
""")

app, rt = fast_app(hdrs=[css])

# ─── In-memory job store (shared with background tasks) ───────────────────────
_jobs: dict[str, dict] = {}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def navbar(back=False):
    left = A("← 홈으로", href="/") if back else A("SME AI Platform", href="/", cls="logo")
    right = A("무료 AI 진단 →", href="/audit") if not back else A("SME AI Platform", href="/", cls="logo")
    return Div(left, right, cls="navbar")


def score_badge_html(score: int):
    if score >= 70:
        label, cls = "우수 (High)", "badge-score badge-high"
    elif score >= 40:
        label, cls = "보통 (Medium)", "badge-score badge-mid"
    else:
        label, cls = "취약 (Low)", "badge-score badge-low"

    color = "#16a34a" if score >= 70 else ("#ca8a04" if score >= 40 else "#dc2626")
    return Div(
        Span(str(score), cls="score-num", style=f"color:{color}"),
        Span("/ 100", cls="score-denom"),
        Span(label, cls=cls),
        cls="score-row",
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

@rt("/")
def get():
    return Html(
        Head(Title("SME AI Platform"), Meta(charset="utf-8"), Meta(name="viewport", content="width=device-width,initial-scale=1")),
        Body(
            navbar(),
            Div(
                Span("한국 소상공인 AI 자동화 전문", cls="badge"),
                H1("AI가 당신의 사업을 모르고 있습니다"),
                P("지금 ChatGPT에게 귀사에 대해 물어보면 뭐라고 하나요? "
                  "AI 가시성 진단으로 확인하고, 경쟁사보다 먼저 AI에 노출되세요."),
                A("무료 AI 가시성 진단 →", href="/audit", cls="btn-primary"),
                cls="hero",
            ),
            Div(
                H2("주요 서비스"),
                Div(
                    Div(Div("🔍", cls="icon"), H3("AI 가시성 진단"), P("ChatGPT, Perplexity, Claude가 귀사를 어떻게 인식하는지 100점 만점으로 측정합니다."), cls="card"),
                    Div(Div("💬", cls="icon"), H3("고객 팔로업 자동화"), P("구매 후 고객 리스트만 업로드하면 맞춤형 카카오 메시지를 자동 생성합니다."), cls="card"),
                    Div(Div("⚡", cls="icon"), H3("AI 문의 응답"), P("FAQ 업로드 한 번으로 고객 문의에 자동 초안 답변을 제공합니다."), cls="card"),
                    cls="cards",
                ),
                cls="services",
            ),
            Footer(P("© 2026 SME AI Platform · Keonhee Kim · AI 자동화 전문가"), cls="footer"),
        )
    )


@rt("/audit")
def get():
    return Html(
        Head(Title("AI 가시성 진단"), Meta(charset="utf-8"), Meta(name="viewport", content="width=device-width,initial-scale=1")),
        Body(
            navbar(back=True),
            Div(
                Div(
                    H2("무료 AI 가시성 진단"),
                    P("회사명을 입력하면 AI 시스템(ChatGPT, Perplexity, Claude)이 귀사를 어떻게 인식하는지 100점 만점으로 진단합니다.", cls="sub"),
                    Form(
                        Div(
                            Input(name="company_name", placeholder="예: 스타벅스 코리아, 배민, 쿠팡...", required=True, id="company-input"),
                            Button("진단 시작", type="submit", id="submit-btn"),
                            cls="input-row",
                        ),
                        hx_post="/audit/start",
                        hx_target="#result-area",
                        hx_swap="innerHTML",
                        hx_indicator="#submit-btn",
                    ),
                    Div(id="result-area"),
                    cls="audit-box",
                ),
                cls="audit-page",
            ),
            Script("""
                document.body.addEventListener('htmx:beforeRequest', function(e) {
                    document.getElementById('submit-btn').disabled = true;
                    document.getElementById('submit-btn').textContent = '진단 중...';
                    document.getElementById('result-area').innerHTML = '<p class="running-msg">AI 시스템을 분석하고 있습니다. 약 30~60초 소요됩니다...</p>';
                });
                document.body.addEventListener('htmx:afterRequest', function(e) {
                    document.getElementById('submit-btn').disabled = false;
                    document.getElementById('submit-btn').textContent = '진단 시작';
                });
            """),
        )
    )


@rt("/audit/start")
async def post(company_name: str):
    """HTMX endpoint: runs audit synchronously and returns result HTML."""
    if not company_name.strip():
        return Div("회사명을 입력해주세요.", cls="error-box")

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                f"{BACKEND_URL}/audit/run",
                json={"company_name": company_name.strip()},
            )
            resp.raise_for_status()
            job_id = resp.json()["job_id"]
    except Exception as e:
        return Div(f"백엔드 연결 오류: {e}", cls="error-box")

    # Poll until done (max 3 min)
    for _ in range(60):
        await asyncio.sleep(3)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                poll = await client.get(f"{BACKEND_URL}/audit/{job_id}")
                poll.raise_for_status()
                job = poll.json()
        except Exception:
            continue

        if job.get("status") == "done":
            result = job.get("result", {})
            recs = job.get("recommendations", [])
            score = result.get("geo_score", 0)
            website = result.get("website_url") or ""
            top_rec = recs[0] if recs else "추천 사항이 없습니다."

            return Div(
                H2(f"{company_name} AI 가시성 진단 결과"),
                P(f"웹사이트: {website}", cls="website-tag") if website else "",
                score_badge_html(score),
                Hr(cls="divider"),
                P("우선 개선 사항 (1순위)", cls="rec-label"),
                Div(top_rec, cls="rec-box"),
                # Paywall for remaining recs
                Div(
                    P("전체 보고서 + 구현 키트를 받으려면 액세스 코드를 입력하세요."),
                    Form(
                        Div(
                            Input(name="access_code", placeholder="액세스 코드", id="code-input"),
                            Input(name="job_id", value=job_id, type="hidden"),
                            Button("잠금 해제", type="submit"),
                            cls="code-row",
                        ),
                        hx_post="/audit/unlock",
                        hx_target="#unlock-area",
                        hx_swap="innerHTML",
                    ),
                    Div(id="unlock-area"),
                    cls="paywall",
                ),
                cls="result-box",
            )

        if job.get("status") == "error":
            return Div(f"오류: {job.get('error', '알 수 없는 오류')}", cls="error-box")

    return Div("시간 초과. 잠시 후 다시 시도해주세요.", cls="error-box")


@rt("/audit/unlock")
async def post(access_code: str, job_id: str):
    VALID_CODES = {"DEMO2026", "GEO500K"}
    if access_code.strip().upper() not in VALID_CODES:
        return Div("잘못된 액세스 코드입니다.", cls="error-box", style="margin-top:0.5rem")

    # Fetch full results from backend
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            poll = await client.get(f"{BACKEND_URL}/audit/{job_id}")
            job = poll.json()
    except Exception as e:
        return Div(f"오류: {e}", cls="error-box")

    recs = job.get("recommendations", [])
    if len(recs) <= 1:
        return P("추가 권고사항이 없습니다.", style="color:#64748b;font-size:0.9rem;margin-top:0.5rem")

    return Div(
        P("전체 개선 사항", cls="rec-label", style="margin-top:1rem"),
        *[Div(rec, cls="rec-box", style="margin-bottom:0.5rem") for rec in recs[1:]],
    )


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    serve(port=5001)
