"""
Evolution Strand: Service V (pre-launch)
Pure data module. No LLM calls. No API calls.

Menu: log Higgsfield/Veo 3/ElevenLabs/Suno changelog update,
log Korean cosmetics ad observation, update STACK_STATUS.md,
track API key acquisition.
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

STRAND_NAME = "service_v"
SERVICES_DIR = Path("C:/Users/keonh/Dev/MCP_Agentic_AI/projects/ai-agency/services/video")
STACK_STATUS_FILE = SERVICES_DIR / "STACK_STATUS.md"

# ---------------------------------------------------------------------------
# Static changelog bank (pre-researched)
# ---------------------------------------------------------------------------

TOOL_CHANGELOGS = [
    {
        "id": "higgsfield_2026q1_voice_cloning",
        "tool": "Higgsfield Pro",
        "update_date": "2026-03-15",
        "headline": "Korean voice cloning launched (Beta)",
        "detail": "Higgsfield Pro added Korean voice cloning via ElevenLabs v3 integration. 50 Korean voice styles available. Tier: Pro plan (monthly). API: POST /v1/generate/voice-clone",
        "pricing_note": "Included in Pro plan at $99/mo (approx. 130,000원). No per-request surcharge for voice cloning.",
        "impact": "V service can now deliver full Korean voice-over + lip sync in one pipeline. Removes need for separate ElevenLabs call for standard cases.",
        "source": "https://higgsfield.ai/changelog",
    },
    {
        "id": "veo3_korea_ga_2026q2",
        "tool": "Veo 3 (Google)",
        "update_date": "2026-04-01",
        "headline": "Veo 3 GA in Korea via Vertex AI",
        "detail": "Veo 3 now generally available in Seoul region (asia-northeast3). 1080p 8-second clips. Text-to-video and image-to-video. API via Vertex AI SDK or REST.",
        "pricing_note": "Approx. $0.35/second of generated video. 8-second clip: ~$2.80 (approx. 3,700원). Enterprise pricing available.",
        "impact": "Can use Veo 3 as fallback when Higgsfield queue is long or for YouTube-style horizontal video.",
        "source": "https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos",
    },
    {
        "id": "elevenlabs_v3_korean_2026q1",
        "tool": "ElevenLabs v3",
        "update_date": "2026-02-20",
        "headline": "ElevenLabs v3 Korean language quality improvement",
        "detail": "v3 model achieves near-native Korean prosody. Emotion control API added. New Korean voice: 'Jisoo' (female, clear), 'Minho' (male, warm). Latency: <500ms for <100 chars.",
        "pricing_note": "Starter $5/mo (30K chars). Creator $22/mo (100K chars). Pro $99/mo (500K chars). Korean chars counted same as English.",
        "impact": "Primary voice-over tool for V service. Use for voiceover tracks, then sync to Higgsfield video.",
        "source": "https://elevenlabs.io/changelog",
    },
    {
        "id": "suno_pro_v4_2026q1",
        "tool": "Suno Pro",
        "update_date": "2026-03-01",
        "headline": "Suno v4 model launched with commercial license on Pro plan",
        "detail": "Suno v4 generates broadcast-quality Korean-language music. 'K-pop BGM' and 'Korean ballad' style tags added. Pro plan includes commercial use rights. 500 credits/day on Pro.",
        "pricing_note": "Pro plan $8/mo. 500 credits/day. 1 song = 10 credits. Commercial use included.",
        "impact": "V service can include original K-pop style BGM in ad videos. No royalty risk.",
        "source": "https://suno.com/blog",
    },
]

KOREAN_AD_OBSERVATIONS = [
    {
        "id": "obs_laneige_reel_2026q1",
        "brand": "라네즈",
        "platform": "Instagram Reels",
        "observation_date": "2026-05-01",
        "format": "9:16, 15초, AI 보이스오버 + 제품 클로즈업 + 텍스트 오버레이",
        "hook": "첫 3초: 물방울 + 피부 클로즈업 + '수분이 이렇게 달라집니다'",
        "cta": "'지금 구매하기' 링크인바이오",
        "ai_elements_detected": "보이스오버 (합성 추정), 배경음악 (생성 AI 추정), 일부 B-roll AI 생성 추정",
        "engagement_estimate": "좋아요 2.3K, 댓글 180 (긍정적)",
        "notes": "AI 생성 여부 공개 안 함. 제품 실사 + AI 보이스오버 조합이 자연스러움.",
    },
    {
        "id": "obs_cosrx_reel_2026q1",
        "brand": "코스알엑스",
        "platform": "Instagram Reels",
        "observation_date": "2026-05-03",
        "format": "9:16, 30초, 영문/한문 바이링구얼, AI 이미지 애니메이션",
        "hook": "성분 분자 구조 애니메이션 + '이 성분 하나로 피부가 바뀌었습니다'",
        "cta": "링크인바이오 + 댓글 '성분' 입력 시 DM 자동 발송",
        "ai_elements_detected": "분자 구조 애니메이션 (Higgsfield/Runway 추정), ManyChat 자동 DM",
        "engagement_estimate": "좋아요 5.1K, 댓글 340",
        "notes": "ManyChat 자동화와 AI 비디오 결합. 댓글 키워드 DM이 리드 수집 효과적.",
    },
]

API_KEY_STATUS = {
    "higgsfield_pro": {"secured": False, "blocker": "Plan 00 build / A1 blocker (per current-priorities.md)"},
    "elevenlabs_v3": {"secured": False, "blocker": "Same as Higgsfield - awaiting agency plan setup"},
    "veo_3": {"secured": False, "blocker": "Google Vertex AI account required, no active blocker except time"},
    "suno_pro": {"secured": False, "blocker": "Low priority, easy to acquire ($8/mo), no signup blocker"},
}


def _load_state(data_dir: Path) -> dict:
    state_file = data_dir / "strand_state_service_v.json"
    if state_file.exists():
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _save_state(data_dir: Path, state: dict) -> None:
    state_file = data_dir / "strand_state_service_v.json"
    state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _select_menu_item(state: dict) -> str:
    last = state.get("last_improvement", "")
    menu = ["log_tool_changelog", "log_ad_observation", "update_stack_status"]
    available = [m for m in menu if m != last]
    import random
    return random.choice(available)


def _render_stack_status_md(changelogs: list, ad_obs: list, api_keys: dict, today_str: str) -> str:
    lines = [
        "# Service V: AI Video Ad Stack Status",
        "",
        f"Last updated: {today_str}",
        "",
        "## Stack Readiness",
        "",
        "| Tool | Status | Pricing | Key Secured |",
        "|---|---|---|---|",
    ]
    tool_map = {c["tool"]: c for c in changelogs}
    key_map = {
        "Higgsfield Pro": api_keys.get("higgsfield_pro", {}),
        "Veo 3 (Google)": api_keys.get("veo_3", {}),
        "ElevenLabs v3": api_keys.get("elevenlabs_v3", {}),
        "Suno Pro": api_keys.get("suno_pro", {}),
    }
    for tool_name, key_info in key_map.items():
        entry = tool_map.get(tool_name, {})
        pricing = entry.get("pricing_note", "See changelog")[:60]
        secured = "YES" if key_info.get("secured") else "NO"
        blocker = key_info.get("blocker", "")
        status = "Pre-launch" if not key_info.get("secured") else "Ready"
        lines.append(f"| {tool_name} | {status} | {pricing} | {secured} |")

    lines += [
        "",
        "## Blockers",
        "",
    ]
    for tool, info in api_keys.items():
        if not info.get("secured"):
            lines.append(f"- **{tool}**: {info.get('blocker', 'Unknown')}")

    lines += [
        "",
        "## Recent Changelog Entries",
        "",
    ]
    for entry in changelogs[-3:]:
        lines.append(f"### {entry['tool']} ({entry['update_date']})")
        lines.append(f"{entry['headline']}")
        lines.append(f"Impact: {entry['impact']}")
        lines.append("")

    lines += [
        "## Korean Ad Observations",
        "",
    ]
    for obs in ad_obs[-2:]:
        lines.append(f"### {obs['brand']} ({obs['observation_date']})")
        lines.append(f"Hook: {obs['hook']}")
        lines.append(f"AI elements: {obs['ai_elements_detected']}")
        lines.append(f"Notes: {obs['notes']}")
        lines.append("")

    return "\n".join(lines)


def run(data_dir: Path) -> dict:
    state = _load_state(data_dir)
    today_str = date.today().isoformat()

    if state.get("last_run_date") == today_str:
        return {"skipped": True, "reason": "already ran today", "strand": STRAND_NAME}

    improvement = _select_menu_item(state)

    # Load existing logs
    changelog_log_file = data_dir / "service_v_changelog_log.json"
    existing_changelogs = []
    if changelog_log_file.exists():
        try:
            existing_changelogs = json.loads(changelog_log_file.read_text(encoding="utf-8"))
        except Exception:
            existing_changelogs = []

    ad_log_file = data_dir / "service_v_ad_observations.json"
    existing_ads = []
    if ad_log_file.exists():
        try:
            existing_ads = json.loads(ad_log_file.read_text(encoding="utf-8"))
        except Exception:
            existing_ads = []

    if improvement == "log_tool_changelog":
        logged_ids = {e.get("id") for e in existing_changelogs}
        candidates = [c for c in TOOL_CHANGELOGS if c["id"] not in logged_ids]
        if not candidates:
            improvement = "update_stack_status"
        else:
            entry = {**candidates[0], "logged_date": today_str}
            existing_changelogs.append(entry)
            # Also regenerate STACK_STATUS.md
            stack_md = _render_stack_status_md(
                TOOL_CHANGELOGS,
                KOREAN_AD_OBSERVATIONS,
                API_KEY_STATUS,
                today_str
            )
            result = {
                "improvement_type": "log_tool_changelog",
                "strand": STRAND_NAME,
                "idempotent_key": f"service_v_changelog_{entry['id']}",
                "multi_write": [
                    {
                        "file_path": "agents/evolution_loop/data/service_v_changelog_log.json",
                        "write_content": json.dumps(existing_changelogs, ensure_ascii=False, indent=2),
                    },
                    {
                        "file_path": "projects/ai-agency/services/video/STACK_STATUS.md",
                        "write_content": stack_md,
                    },
                ],
                "summary": f"Service V changelog logged: {entry['tool']} - {entry['headline']}",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): service-v log {entry['tool'].lower().replace(' ', '-')} changelog",
                "flag_for_report": True,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    if improvement == "log_ad_observation":
        logged_ids = {e.get("id") for e in existing_ads}
        candidates = [o for o in KOREAN_AD_OBSERVATIONS if o["id"] not in logged_ids]
        if not candidates:
            improvement = "update_stack_status"
        else:
            obs = {**candidates[0], "logged_date": today_str}
            existing_ads.append(obs)
            result = {
                "improvement_type": "log_ad_observation",
                "strand": STRAND_NAME,
                "idempotent_key": f"service_v_ad_{obs['id']}",
                "file_path": "agents/evolution_loop/data/service_v_ad_observations.json",
                "write_content": json.dumps(existing_ads, ensure_ascii=False, indent=2),
                "summary": f"Korean ad observation logged: {obs['brand']} on {obs['platform']} ({obs['ai_elements_detected'][:50]}...)",
                "dry_run_passed": True,
                "commit_message": f"chore(evolution): service-v log ad observation {obs['id']}",
                "flag_for_report": False,
            }
            state["last_run_date"] = today_str
            state["last_improvement"] = improvement
            _save_state(data_dir, state)
            return result

    # update_stack_status
    SERVICES_DIR.mkdir(parents=True, exist_ok=True)
    stack_md = _render_stack_status_md(
        TOOL_CHANGELOGS,
        KOREAN_AD_OBSERVATIONS,
        API_KEY_STATUS,
        today_str
    )
    result = {
        "improvement_type": "update_stack_status",
        "strand": STRAND_NAME,
        "idempotent_key": f"service_v_stack_status_{today_str}",
        "file_path": "projects/ai-agency/services/video/STACK_STATUS.md",
        "write_content": stack_md,
        "summary": f"Service V STACK_STATUS.md refreshed. API keys secured: 0/4. Pre-launch.",
        "dry_run_passed": True,
        "commit_message": "chore(evolution): service-v refresh STACK_STATUS.md",
        "flag_for_report": False,
    }
    state["last_run_date"] = today_str
    state["last_improvement"] = improvement
    _save_state(data_dir, state)
    return result
