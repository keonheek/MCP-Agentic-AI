"""
Retention cliff detector.
Takes a retention curve (list of {elapsed_ratio, retained_pct}) and finds
points where viewership drops sharply within a short window.
"""


class RetentionCliffDetector:
    def __init__(self, thresholds: dict):
        self.cliff_drop = thresholds.get("retention", {}).get("cliff_drop_pct", 5.0)
        self.hook_window = thresholds.get("retention", {}).get("hook_window_seconds", 15)
        self.hook_max_drop = thresholds.get("retention", {}).get("hook_max_drop_pct", 30.0)
        self.target_apv_shorts = thresholds.get("retention", {}).get("target_apv_shorts", 75.0)

    def detect(self, curve: list[dict], video_duration_seconds: float = 60.0) -> dict:
        if not curve:
            return {"cliffs": [], "hook_drop_pct": None, "status": "no_data"}

        cliffs = []
        for i in range(1, len(curve)):
            drop = curve[i - 1]["retained_pct"] - curve[i]["retained_pct"]
            if drop >= self.cliff_drop:
                elapsed_seconds = curve[i]["elapsed_ratio"] * video_duration_seconds
                cliffs.append({
                    "elapsed_seconds": round(elapsed_seconds),
                    "elapsed_ratio": curve[i]["elapsed_ratio"],
                    "drop_pct": round(drop, 2),
                    "retained_after": round(curve[i]["retained_pct"], 2),
                    "severity": "critical" if drop >= self.cliff_drop * 3 else "major" if drop >= self.cliff_drop * 1.5 else "minor",
                })

        # hook zone analysis
        hook_ratio = self.hook_window / max(video_duration_seconds, 1)
        hook_points = [p for p in curve if p["elapsed_ratio"] <= hook_ratio]
        if len(hook_points) >= 2:
            hook_drop = hook_points[0]["retained_pct"] - hook_points[-1]["retained_pct"]
        elif hook_points:
            hook_drop = 100.0 - hook_points[-1]["retained_pct"]
        else:
            hook_drop = None

        return {
            "cliffs": sorted(cliffs, key=lambda x: x["drop_pct"], reverse=True),
            "hook_drop_pct": round(hook_drop, 2) if hook_drop is not None else None,
            "hook_alert": hook_drop is not None and hook_drop > self.hook_max_drop,
            "total_cliffs": len(cliffs),
        }

    def generate_edit_suggestions(self, cliff_result: dict, video_duration_seconds: float) -> list[str]:
        suggestions = []
        if cliff_result.get("hook_alert"):
            drop = cliff_result["hook_drop_pct"]
            suggestions.append(
                f"Hook zone ({self.hook_window}s): {drop:.1f}% drop -- exceeds {self.hook_max_drop}% threshold. "
                f"Rewrite opening: lead with the payoff first, not context."
            )

        for cliff in cliff_result.get("cliffs", [])[:3]:
            t = cliff["elapsed_seconds"]
            d = cliff["drop_pct"]
            sev = cliff["severity"]
            if sev == "critical":
                suggestions.append(
                    f"{t}s mark ({d:.1f}% drop, critical): Add pattern interrupt here -- "
                    f"zoom cut, text overlay, or direct address to camera."
                )
            elif sev == "major":
                suggestions.append(
                    f"{t}s mark ({d:.1f}% drop, major): Pacing issue. "
                    f"Cut dead air or static framing at this point."
                )
            else:
                suggestions.append(
                    f"{t}s mark ({d:.1f}% drop, minor): Minor drop -- "
                    f"consider adding B-roll or subtitle emphasis here."
                )

        if not suggestions:
            suggestions.append("No significant retention cliffs detected. Maintain current edit pacing.")

        return suggestions
