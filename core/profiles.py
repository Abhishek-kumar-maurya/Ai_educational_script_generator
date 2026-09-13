import re


def model_profile(model_name: str) -> dict:
    """Choose safe generation settings from the configured model.

    The app remains model-agnostic: small local models use a compact, fast
    pipeline while larger models get the richer planning/repair pipeline.
    """
    name = (model_name or "").lower()
    small = any(x in name for x in ("1.5b", "1b", "2b", "3b", "4b"))
    if small:
        return {
            "name": "fast",
            "max_context_chars": 4800,
            "num_ctx": 4096,
            "num_predict": 1900,
            "temperature": 0.15,
            "timeout": 900,
            "use_planner": False,
            "repair_attempts": 1,
        }
    return {
        "name": "quality",
        "max_context_chars": 18000,
        "num_ctx": 8192,
        "num_predict": 2400,
        "temperature": 0.15,
        "timeout": 900,
        "use_planner": True,
        "repair_attempts": 1,
    }


def grade_wpm(grade: str) -> int:
    """Conservative narration speed for educational video planning."""
    m = re.search(r"\d+", str(grade))
    g = int(m.group()) if m else 5
    if g <= 3:
        return 110
    if g <= 6:
        return 120
    if g <= 8:
        return 130
    return 140
