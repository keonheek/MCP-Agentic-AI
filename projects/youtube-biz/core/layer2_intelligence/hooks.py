"""
Layer 2: 훅 라이브러리 관리
실적 데이터 기반으로 훅 점수 업데이트 + 신규 훅 추가
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
HOOKS_PATH = BASE_DIR / "config" / "hook-templates.json"


def load_hooks() -> dict:
    with open(HOOKS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_hooks(data: dict):
    with open(HOOKS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_hook_score(channel: str, hook_id: str, ctr: float, views: int):
    data = load_hooks()
    hooks = data.get(channel, {}).get("hooks", [])
    for hook in hooks:
        if hook["id"] == hook_id:
            prev_score = hook.get("score") or 0
            prev_uses = hook.get("uses", 0)
            # 가중 이동평균 (새 데이터 30%)
            hook["score"] = prev_score * 0.7 + ctr * 0.3 if prev_score else ctr
            hook["uses"] = prev_uses + 1
            hook["last_views"] = views
    save_hooks(data)
    print(f"[Hooks] {channel}/{hook_id} 점수 업데이트 완료")


def get_best_hooks(channel: str, top_n: int = 3) -> list[dict]:
    data = load_hooks()
    hooks = data.get(channel, {}).get("hooks", [])
    scored = [h for h in hooks if h.get("score") is not None]
    unscored = [h for h in hooks if h.get("score") is None]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return (scored + unscored)[:top_n]


def add_hook(channel: str, hook_id: str, template: str):
    data = load_hooks()
    if channel not in data:
        data[channel] = {"hooks": []}
    data[channel]["hooks"].append({
        "id": hook_id,
        "template": template,
        "score": None,
        "uses": 0,
    })
    save_hooks(data)
    print(f"[Hooks] 신규 훅 추가: {channel}/{hook_id}")


if __name__ == "__main__":
    print("Best Sing It hooks:", get_best_hooks("singit"))
