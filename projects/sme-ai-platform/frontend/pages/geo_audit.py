"""
GEO Audit page — /audit

Free tier: shows score + top 1 recommendation.
Paid tier: full report PDF download (access code gated).
"""
import httpx
import asyncio
import reflex as rx

BACKEND_URL = "http://localhost:8000"

# ─── State ───────────────────────────────────────────────────────────────────

class AuditState(rx.State):
    company_name: str = ""
    access_code: str = ""
    job_id: str = ""
    status: str = "idle"  # idle | running | done | error
    geo_score: int = 0
    website_url: str = ""
    top_rec: str = ""
    all_recs: list[str] = []
    pdf_path: str = ""
    error_msg: str = ""
    is_paid: bool = False

    @rx.event(background=True)
    async def run_audit(self):
        if not self.company_name.strip():
            async with self:
                self.error_msg = "회사명을 입력해주세요."
            return

        async with self:
            self.status = "running"
            self.error_msg = ""

        # POST to backend
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{BACKEND_URL}/audit/run",
                    json={"company_name": self.company_name.strip()},
                )
                resp.raise_for_status()
                data = resp.json()
                job_id = data["job_id"]

            async with self:
                self.job_id = job_id

            # Poll for result
            for _ in range(60):  # max 60 * 3s = 3 min
                await asyncio.sleep(3)
                async with httpx.AsyncClient(timeout=10) as client:
                    poll = await client.get(f"{BACKEND_URL}/audit/{job_id}")
                    poll.raise_for_status()
                    job = poll.json()

                if job.get("status") == "done":
                    result = job.get("result", {})
                    recs = job.get("recommendations", [])
                    async with self:
                        self.status = "done"
                        self.geo_score = result.get("geo_score", 0)
                        self.website_url = result.get("website_url") or ""
                        self.all_recs = recs
                        self.top_rec = recs[0] if recs else ""
                        self.pdf_path = job.get("pdf_path", "")
                    return

                if job.get("status") == "error":
                    async with self:
                        self.status = "error"
                        self.error_msg = job.get("error", "알 수 없는 오류")
                    return

            async with self:
                self.status = "error"
                self.error_msg = "시간 초과. 잠시 후 다시 시도해주세요."

        except Exception as e:
            async with self:
                self.status = "error"
                self.error_msg = str(e)

    def validate_access_code(self):
        VALID_CODES = {"DEMO2026", "GEO500K"}  # expand later via Supabase
        if self.access_code.strip().upper() in VALID_CODES:
            self.is_paid = True
        else:
            self.error_msg = "잘못된 액세스 코드입니다."


# ─── UI Components ────────────────────────────────────────────────────────────

def score_badge(score: int) -> rx.Component:
    color = rx.cond(score >= 70, "green", rx.cond(score >= 40, "yellow", "red"))
    label = rx.cond(score >= 70, "우수 (High)", rx.cond(score >= 40, "보통 (Medium)", "취약 (Low)"))
    return rx.hstack(
        rx.text(str(score), font_size="4rem", font_weight="800", color="#1b2a4a"),
        rx.text("/ 100", font_size="1.2rem", color="#64748b", align_self="flex-end", padding_bottom="0.6rem"),
        rx.badge(label, color_scheme=color, size="2", margin_left="1rem", align_self="flex-end", padding_bottom="0.4rem"),
        align="end",
    )


def audit_form() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("무료 AI 가시성 진단", size="6", color="#1b2a4a", font_weight="700"),
            rx.text(
                "회사명을 입력하면 AI 시스템(ChatGPT, Perplexity, Claude)이 귀사를 어떻게 인식하는지 100점 만점으로 진단합니다.",
                color="#64748b",
                font_size="0.95rem",
            ),
            rx.hstack(
                rx.input(
                    placeholder="예: 스타벅스 코리아, 배민, 쿠팡...",
                    value=AuditState.company_name,
                    on_change=AuditState.set_company_name,
                    size="3",
                    width="100%",
                    border_radius="8px",
                ),
                rx.button(
                    rx.cond(
                        AuditState.status == "running",
                        rx.spinner(size="2"),
                        rx.text("진단 시작"),
                    ),
                    on_click=AuditState.run_audit,
                    color_scheme="teal",
                    size="3",
                    border_radius="8px",
                    disabled=AuditState.status == "running",
                ),
                width="100%",
                spacing="3",
            ),
            rx.cond(
                AuditState.error_msg != "",
                rx.callout(AuditState.error_msg, color="red", size="2"),
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="2rem",
        border="1px solid #e2e8f0",
        border_radius="16px",
        bg="white",
        max_width="640px",
        width="100%",
    )


def result_panel() -> rx.Component:
    return rx.cond(
        AuditState.status == "done",
        rx.box(
            rx.vstack(
                rx.heading(AuditState.company_name + " AI 가시성 진단 결과", size="5", color="#1b2a4a"),
                rx.cond(
                    AuditState.website_url != "",
                    rx.text("웹사이트: " + AuditState.website_url, color="#64748b", font_size="0.85rem"),
                ),
                score_badge(AuditState.geo_score),
                rx.divider(),
                rx.text("우선 개선 사항 (1순위)", font_weight="700", color="#1b2a4a"),
                rx.box(
                    rx.text(AuditState.top_rec, color="#334155", font_size="0.9rem", line_height="1.7"),
                    padding="1rem 1.2rem",
                    bg="#f0fdf9",
                    border_left="4px solid teal",
                    border_radius="8px",
                ),
                # Paid tier: show remaining recommendations + PDF
                rx.cond(
                    AuditState.is_paid,
                    rx.vstack(
                        rx.text("전체 개선 사항", font_weight="700", color="#1b2a4a"),
                        rx.foreach(
                            AuditState.all_recs[1:],
                            lambda rec: rx.box(
                                rx.text(rec, color="#334155", font_size="0.9rem", line_height="1.7"),
                                padding="0.8rem 1rem",
                                bg="#f8fafc",
                                border_left="3px solid #e2e8f0",
                                border_radius="6px",
                            ),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.text("전체 보고서 + 구현 키트를 받으려면 액세스 코드를 입력하세요.", color="#64748b", font_size="0.9rem"),
                            rx.hstack(
                                rx.input(
                                    placeholder="액세스 코드",
                                    value=AuditState.access_code,
                                    on_change=AuditState.set_access_code,
                                    size="2",
                                    width="180px",
                                ),
                                rx.button(
                                    "잠금 해제",
                                    on_click=AuditState.validate_access_code,
                                    color_scheme="teal",
                                    size="2",
                                ),
                                spacing="2",
                            ),
                            spacing="2",
                        ),
                        padding="1rem",
                        bg="#fffbeb",
                        border="1px dashed #f59e0b",
                        border_radius="8px",
                    ),
                ),
                spacing="4",
                align="start",
                width="100%",
            ),
            padding="2rem",
            border="1px solid #e2e8f0",
            border_radius="16px",
            bg="white",
            max_width="640px",
            width="100%",
        ),
        rx.box(),  # empty when not done
    )


def geo_audit_page() -> rx.Component:
    return rx.box(
        # Navbar
        rx.box(
            rx.hstack(
                rx.link("← 홈으로", href="/", color="#64748b", font_size="0.9rem"),
                rx.spacer(),
                rx.text("SME AI Platform", font_weight="700", color="teal"),
                padding="1rem 2rem",
                border_bottom="1px solid #e2e8f0",
                bg="white",
            )
        ),
        rx.vstack(
            rx.box(height="2rem"),
            audit_form(),
            result_panel(),
            rx.box(height="4rem"),
            align="center",
            width="100%",
            padding="0 1rem",
        ),
        bg="#f8fafc",
        min_height="100vh",
    )
