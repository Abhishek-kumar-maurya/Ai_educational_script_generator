def evaluate(script: dict, validation: dict, plan: dict) -> dict:
    warnings = validation["warnings"]
    scores = {
        "content_coverage": 100 if not any("missing concepts" in w.lower() for w in warnings) else 75,
        "factual_grounding": 90,
        "grade_appropriateness": 90,
        "storytelling": 90 if plan.get("story_or_situation") else 75,
        "hooks": 95 if script.get("scenes") else 0,
        "transitions": 90,
        "duration": 100 if validation["timeline_seconds"] <= 0 else (
            100 if not any("timeline is" in w.lower() for w in warnings) else 75
        ),
        "guideline_adherence": 90,
    }
    overall = round(sum(scores.values()) / len(scores))
    return {"scores": scores, "overall": overall, "warnings": warnings}
