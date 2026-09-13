import re
from models.schemas import Script
from core.profiles import grade_wpm


def parse_seconds(t: str) -> int:
    m = re.match(r"^(\d+):(\d{2})$", str(t).strip())
    if not m:
        raise ValueError(f"Invalid time: {t}")
    return int(m.group(1)) * 60 + int(m.group(2))


def estimate_words(script: dict) -> int:
    return sum(len(s.get("voiceover_dialogue", "").split()) for s in script.get("scenes", []))


def _concept_key(name: str) -> str:
    words = re.findall(r"[a-zA-Z]{4,}", name.lower())
    stop = {"there", "their", "these", "those", "about", "parts", "such", "from", "with", "have", "that", "this"}
    return " ".join(w for w in words if w not in stop)[:4]


def deterministic_validate(script: dict, target_minutes: float, required_concepts: list[dict], grade: str = "5") -> dict:
    errors, warnings = [], []
    try:
        Script.model_validate(script)
    except Exception as e:
        errors.append(f"Schema validation failed: {e}")

    scenes = script.get("scenes", [])
    starts, ends = [], []
    try:
        for s in scenes:
            starts.append(parse_seconds(s["start_time"]))
            ends.append(parse_seconds(s["end_time"]))
        if not scenes or any(e <= s for s, e in zip(starts, ends)):
            errors.append("One or more scenes have invalid time ranges.")
        if scenes and any(b != a for a, b in zip(ends[:-1], starts[1:])):
            warnings.append("Scene time ranges are not contiguous.")
        total_seconds = max(ends) if ends else 0
    except (KeyError, ValueError) as e:
        errors.append(str(e))
        total_seconds = 0

    target_seconds = int(round(target_minutes * 60))
    tolerance = max(5, int(target_seconds * 0.05))
    if total_seconds > target_seconds + tolerance:
        warnings.append(f"Script timeline is {total_seconds}s vs target {target_seconds}s.")
    if total_seconds < max(1, target_seconds - tolerance):
        warnings.append(f"Script timeline is only {total_seconds}s vs target {target_seconds}s.")

    words = estimate_words(script)
    wpm = grade_wpm(grade)
    estimated_by_words = words / wpm * 60 if wpm else 0
    if abs(estimated_by_words - target_seconds) > max(12, target_seconds * 0.12):
        warnings.append(
            f"Narration is {words} words (~{round(estimated_by_words)}s at {wpm} wpm) "
            f"while the timeline is {total_seconds}s."
        )

    all_text = " ".join(
        (s.get("voiceover_dialogue", "") + " " + s.get("visual_animation", ""))
        for s in scenes
    ).lower()
    missing = []
    for c in required_concepts:
        key = _concept_key(c.get("name", ""))
        if key and key not in all_text:
            missing.append(c.get("name", "Unnamed concept"))
    if missing:
        warnings.append("Potentially missing concepts: " + "; ".join(missing[:8]))

    placeholders = [i + 1 for i, s in enumerate(scenes) if s.get("ots_sfx", "").strip() in {"...", "-", "none"}]
    if placeholders:
        warnings.append("Placeholder OTS/SFX found in scene(s): " + ", ".join(map(str, placeholders)))

    return {
        "valid_schema": not errors,
        "errors": errors,
        "warnings": warnings,
        "timeline_seconds": total_seconds,
        "target_seconds": target_seconds,
        "word_count": words,
        "target_word_count": round(target_minutes * wpm),
        "estimated_narration_seconds": round(estimated_by_words),
        "wpm": wpm,
    }
