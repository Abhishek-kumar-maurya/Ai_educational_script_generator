import re


def _has_any(text: str, terms) -> bool:
    low = text.lower()
    return any(t in low for t in terms)


def evaluate(script: dict, validation: dict, plan: dict) -> dict:
    warnings = validation["warnings"]
    scenes = script.get("scenes", [])
    first_voice = scenes[0].get("voiceover_dialogue", "") if scenes else ""
    all_voice = " ".join(s.get("voiceover_dialogue", "") for s in scenes)
    all_visual = " ".join(s.get("visual_animation", "") for s in scenes)
    ots = [s.get("ots_sfx", "").strip() for s in scenes]

    missing = any("missing concepts" in w.lower() for w in warnings)
    duration_issue = any(x in w.lower() for w in warnings for x in ("timeline", "narration is"))
    placeholder = any(x in {"", "...", "none", "-"} for x in ots)

    hook = 95 if _has_any(first_voice, ["?", "imagine", "can you", "what if", "let's", "today"]) else 65
    transitions = 90 if _has_any(all_voice, ["now", "next", "but", "so", "let's", "because"]) else 70
    visual_teaching = 95 if _has_any(all_visual, ["highlight", "zoom", "label", "compare", "trace", "show", "appear", "animate"]) else 70
    storytelling = 90 if plan.get("story_or_situation") else 75

    if missing:
        coverage = 55
    else:
        coverage = 92 if len(scenes) >= 5 else 82

    grounding = 92 if not any("unsupported" in w.lower() for w in warnings) else 60
    grade_score = 90 if all(len(s.split()) <= 24 for s in all_voice.split(".") if s.strip()) else 75

    target = max(1, validation.get("target_seconds", 1))
    actual = validation.get("timeline_seconds", 0)
    timeline_ratio = actual / target
    word_ratio = validation.get("estimated_narration_seconds", 0) / target
    duration_score = max(0, round(100 - abs(timeline_ratio - 1) * 160 - abs(word_ratio - 1) * 120))
    if duration_issue:
        duration_score = min(duration_score, 55)

    guideline = 95 if not placeholder and visual_teaching >= 90 else 75

    scores = {
        "content_coverage": coverage,
        "factual_grounding": grounding,
        "grade_appropriateness": grade_score,
        "storytelling": storytelling,
        "hooks": hook,
        "transitions": transitions,
        "duration": duration_score,
        "guideline_adherence": guideline,
    }
    overall = round(sum(scores.values()) / len(scores))
    return {"scores": scores, "overall": overall, "warnings": warnings}
