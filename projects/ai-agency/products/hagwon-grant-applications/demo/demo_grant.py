"""
Runnable demo: Government Grant Application Draft Agent

Usage:
    python demo/demo_grant.py --program "모두의창업" --mode analyze
    python demo/demo_grant.py --program "모두의창업" --business "AI 학원 자동화" --mode draft
    python demo/demo_grant.py --program "모두의창업" --mode export

Requires: OPENAI_API_KEY in environment for draft/analyze modes.
"""
import argparse
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


DEMO_BUSINESS_INFO = {
    "business_idea": "AI를 활용한 학원 학부모 소통 자동화",
    "target_customer": "1인-5인 운영 학원, 교습소 원장",
    "market_size": "전국 학원 수 7만개, 학원 SaaS 시장 규모 약 5000억원",
    "differentiation": "기존 EduPie/알리미는 출결만 처리, AI 자연어 메시지 생성은 없음",
    "revenue_model": "₩300K 설치 + ₩100K-150K/월 구독",
    "team": "AI 개발자 1인, 학원 운영 경험 1년",
    "timeline": "2026년 Q3 출시, Q4 50개 학원 목표",
    "budget_plan": "인건비 ₩3M, 서버비 ₩500K, 마케팅 ₩1.5M",
}


def analyze_program(program: str):
    """Show evaluation criteria for a program."""
    criteria = {
        "모두의창업": {
            "총점": "100점",
            "평가 항목": {
                "창업 동기 및 문제 인식": "20점",
                "시장성 및 사업 타당성": "25점",
                "차별성 및 혁신성": "25점",
                "팀 역량": "15점",
                "실현 가능성": "15점",
            },
            "핵심 키워드": ["AI", "디지털 전환", "소상공인", "자동화", "구체적 수치"],
            "탈락 이유 1위": "수치 없는 막연한 주장",
            "탈락 이유 2위": "시장 규모 근거 미흡",
        }
    }
    data = criteria.get(program, criteria["모두의창업"])
    print(f"\n[{program}] 평가 기준 분석")
    print(json.dumps(data, ensure_ascii=False, indent=2))


def draft_application(program: str, business_idea: str):
    """Generate draft (requires OPENAI_API_KEY)."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("[DEMO] OpenAI API 키 없음: 오프라인 예시 초안 출력")
        questions = [
            "Q1. 창업 동기 및 문제 인식",
            "Q2. 목표 고객 및 시장 규모",
            "Q3. 제품/서비스 차별점",
        ]
        for q in questions:
            print(f"\n{q}")
            print(f"[예시 답변] {business_idea}에 관한 답변입니다. (실제 서비스에서는 GPT-4o + 합격 사례 기반으로 생성)")
        return

    from draft_generator import generate_draft
    info = {**DEMO_BUSINESS_INFO, "business_idea": business_idea}
    draft = generate_draft(program, info)
    for q, a in draft.items():
        print(f"\n{q}")
        print(a)


def export_demo(program: str):
    """Export sample draft to file."""
    from docx_exporter import export_to_docx
    sample_draft = {
        "Q1. 창업 동기 및 문제 인식": "전국 7만개 학원 원장님들이 하루 1-2시간을 학부모 알림톡 작성에 쓰고 있습니다...",
        "Q2. 목표 고객 및 시장 규모": "1인-5인 운영 학원 약 5만개. 학원 SaaS 시장 규모 5000억원...",
    }
    path = export_to_docx(program, "데모_사업", sample_draft, "demo_output")
    print(f"[EXPORT] 파일 생성: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", default="모두의창업")
    parser.add_argument("--business", default="AI 학원 자동화")
    parser.add_argument("--mode", choices=["analyze", "draft", "export"], default="analyze")
    args = parser.parse_args()

    if args.mode == "analyze":
        analyze_program(args.program)
    elif args.mode == "draft":
        draft_application(args.program, args.business)
    elif args.mode == "export":
        export_demo(args.program)


if __name__ == "__main__":
    main()
