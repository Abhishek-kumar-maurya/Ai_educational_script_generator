import re
from models.schemas import Script

def parse_seconds(t: str) -> int:
    m = re.match(r"^(\d+):(\d{2})$", t.strip())
    if not m:
        raise ValueError(f"Invalid time: {t}")
    return int(m.group(1)) * 60 + int(m.group(2))

def estimate_words(script: dict) -> int:
    return sum(len(s["voiceover_dialogue"].split()) for s in script["scenes"])

def deterministic_validate(script: dict, target_minutes: float, required_concepts: list[dict]) -> dict:
    errors, warnings = [], []
    try:
        Script.model_validate(script)
    except Exception as e:
        errors.append(f"Schema validation failed: {e}")

    if script.get("scenes"):
        starts = [parse_seconds(s["start_time"]) for s in script["scenes"]]
        ends = [parse_seconds(s["end_time"]) for s in script["scenes"]]
        if any(e <= s for s, e in zip(starts, ends)) is False:
            errors.append("One or more scenes have invalid time ranges.")
        total_seconds = max(ends)
    else:
        total_seconds = 0

    target_seconds = int(target_minutes * 60)
    tolerance = max(10, int(target_seconds * 0.05))
    if total_seconds > target_seconds + tolerance:
        warnings.append(f"Script timeline is {total_seconds}s vs target {target_seconds}s.")

    words = estimate_words(script)
    # 130 wpm is used only as a rough sanity check; timeline remains authoritative.
    estimated_by_words = words / 130 * 60
    if abs(estimated_by_words - target_seconds) > max(30, target_seconds * 0.25):
        warnings.append("Narration word-count estimate and scene timeline differ materially.")

    # Simple evidence-presence check.
    all_text = " ".join(
        s["voiceover_dialogue"] + " " + s["visual_animation"] for s in script.get("scenes", [])
    ).lower()
    missing = []
    for c in required_concepts:
        name = c["name"].lower()
        key = " ".join(re.findall(r"[a-zA-Z]{4,}", name)[:4])
        if key and key not in all_text:
            missing.append(c["name"])
    if missing:
        warnings.append("Potentially missing concepts: " + "; ".join(missing[:8]))

    return {
        "valid_schema": not errors,
        "errors": errors,
        "warnings": warnings,
        "timeline_seconds": total_seconds,
        "word_count": words,
        "estimated_narration_seconds": round(estimated_by_words),
    }
