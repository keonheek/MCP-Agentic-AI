"""
Self-critique loop for youtube-analyst reports.
Scores the report on 4 MECE dimensions (0-10 each).
Pass threshold and max iterations come from thresholds.yaml.
"""
import json
from datetime import date


class SelfCritique:
    def __init__(self, thresholds: dict):
        cfg = thresholds.get("self_critique", {})
        self.pass_score = cfg.get("pass_score", 8.0)
        self.max_iterations = cfg.get("max_iterations", 2)

    def score(self, report_data: dict) -> dict:
        scores = {
            "data_integrity": self._score_data_integrity(report_data),
            "specificity": self._score_specificity(report_data),
            "actionability": self._score_actionability(report_data),
            "competitive_relevance": self._score_competitive_relevance(report_data),
        }
        scores["passed"] = all(v >= self.pass_score for v in scores.values() if isinstance(v, float))
        scores["min_score"] = min(v for v in scores.values() if isinstance(v, float))
        return scores

    def _score_data_integrity(self, data: dict) -> float:
        kpis = data.get("channel_kpis", {})
        if not kpis:
            return 0.0
        competitors = data.get("competitors", [])
        score = 10.0
        # penalize missing KPIs
        critical_fields = ["views", "avg_view_duration_seconds", "avg_view_percentage"]
        missing = sum(1 for f in critical_fields if not kpis.get(f))
        score -= missing * 2.0
        # penalize too few competitors
        if len(competitors) < 3:
            score -= (3 - len(competitors)) * 2.0
        # penalize if no retention data
        if not data.get("retention_analysis"):
            score -= 2.0
        return max(0.0, score)

    def _score_specificity(self, data: dict) -> float:
        suggestions = data.get("edit_suggestions", [])
        if not suggestions:
            return 0.0
        score = 10.0
        vague_count = 0
        for s in suggestions:
            # vague if no number (time, %, count) in suggestion
            has_number = any(c.isdigit() for c in s)
            if not has_number:
                vague_count += 1
        score -= vague_count * 2.5
        return max(0.0, score)

    def _score_actionability(self, data: dict) -> float:
        suggestions = data.get("edit_suggestions", [])
        if not suggestions:
            return 0.0
        score = 10.0
        abstract_keywords = ["improve", "enhance", "optimize", "better", "consider", "개선", "향상"]
        abstract_count = sum(
            1 for s in suggestions
            if any(kw in s.lower() for kw in abstract_keywords) and not any(c.isdigit() for c in s)
        )
        score -= abstract_count * 2.0
        return max(0.0, score)

    def _score_competitive_relevance(self, data: dict) -> float:
        competitors = data.get("competitors", [])
        if not competitors:
            return 0.0
        score = 10.0
        niche = data.get("channel_niche", "")
        mismatched = 0
        for c in competitors:
            desc = (c.get("description", "") + c.get("title", "")).lower()
            niche_terms = ["드라마", "drama", "인터뷰", "interview", "번역", "translation", "밈", "meme", "팟캐스트", "podcast"]
            if not any(t in desc for t in niche_terms):
                mismatched += 1
        score -= mismatched * 1.5
        return max(0.0, min(10.0, score))

    def log(self, iteration: int, scores: dict, report_path: str):
        entry = {
            "iteration": iteration,
            "scores": {k: v for k, v in scores.items() if isinstance(v, (int, float))},
            "passed": scores.get("passed"),
            "date": date.today().isoformat(),
        }
        critique_path = report_path.replace(".md", "-critique.json")
        try:
            existing = json.loads(open(critique_path).read())
        except (FileNotFoundError, json.JSONDecodeError):
            existing = []
        existing.append(entry)
        with open(critique_path, "w") as f:
            json.dump(existing, f, indent=2)
        return critique_path
