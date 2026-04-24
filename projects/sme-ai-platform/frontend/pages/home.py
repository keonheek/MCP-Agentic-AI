"""
Landing page — /
"""
import reflex as rx


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("SME AI Platform", font_weight="700", font_size="1.1rem", color="teal"),
            rx.spacer(),
            rx.link("무료 AI 진단", href="/audit", color="teal", font_weight="600"),
            padding="1rem 2rem",
            border_bottom="1px solid #e2e8f0",
            bg="white",
            position="sticky",
            top="0",
            z_index="10",
            width="100%",
        )
    )


def hero() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.badge("한국 소상공인 AI 자동화 전문", color_scheme="teal", size="2"),
            rx.heading(
                "AI가 당신의 사업을 모르고 있습니다",
                size="8",
                text_align="center",
                font_weight="800",
                color="#1b2a4a",
            ),
            rx.text(
                "지금 ChatGPT에게 귀사에 대해 물어보면 뭐라고 하나요? "
                "AI 가시성 진단으로 확인하고, 경쟁사보다 먼저 AI에 노출되세요.",
                text_align="center",
                color="#64748b",
                font_size="1.1rem",
                max_width="600px",
            ),
            rx.hstack(
                rx.link(
                    rx.button(
                        "무료 AI 가시성 진단 →",
                        size="4",
                        color_scheme="teal",
                        radius="full",
                    ),
                    href="/audit",
                ),
                justify="center",
            ),
            spacing="5",
            align="center",
            padding="5rem 2rem",
        ),
        bg="linear-gradient(135deg, #f8fafc 0%, #e0f7f7 100%)",
        width="100%",
    )


def services() -> rx.Component:
    items = [
        ("AI 가시성 진단", "ChatGPT, Perplexity, Claude가 귀사를 어떻게 인식하는지 100점 만점으로 측정합니다.", "🔍"),
        ("고객 팔로업 자동화", "구매 후 고객 연락처 리스트만 업로드하면 맞춤형 카카오 메시지를 자동 생성합니다.", "💬"),
        ("AI 문의 응답 시스템", "FAQ 업로드 한 번으로 고객 문의에 자동 초안 답변을 제공합니다.", "⚡"),
    ]
    return rx.box(
        rx.vstack(
            rx.heading("주요 서비스", size="6", color="#1b2a4a", font_weight="700"),
            rx.grid(
                *[
                    rx.box(
                        rx.vstack(
                            rx.text(icon, font_size="2rem"),
                            rx.text(title, font_weight="700", color="#1b2a4a"),
                            rx.text(desc, color="#64748b", font_size="0.9rem"),
                            spacing="2",
                            align="start",
                        ),
                        padding="1.5rem",
                        border="1px solid #e2e8f0",
                        border_radius="12px",
                        bg="white",
                        _hover={"border_color": "teal", "box_shadow": "0 4px 20px rgba(0,199,190,0.15)"},
                        transition="all 0.2s",
                    )
                    for icon, title, desc in items
                ],
                columns="3",
                spacing="4",
                width="100%",
            ),
            spacing="6",
            align="center",
            max_width="900px",
            margin="0 auto",
            padding="4rem 2rem",
        )
    )


def home() -> rx.Component:
    return rx.box(
        navbar(),
        hero(),
        services(),
        rx.box(
            rx.text(
                "© 2026 SME AI Platform · Keonhee Kim · AI 자동화 전문가",
                color="#94a3b8",
                font_size="0.85rem",
                text_align="center",
            ),
            padding="2rem",
            border_top="1px solid #e2e8f0",
        ),
        bg="#f8fafc",
        min_height="100vh",
    )
