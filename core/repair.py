from core.validator import deterministic_validate


def repair_if_needed(llm, script, context, plan, grade, duration, style, instructions, required_concepts, max_attempts=1):
    history = []
    current = script
    for attempt in range(max_attempts + 1):
        validation = deterministic_validate(current, duration, required_concepts, grade)
        history.append(validation)
        hard_fail = bool(validation["errors"])
        important_warn = any(
            phrase in " ".join(validation["warnings"]).lower()
            for phrase in ("missing concepts", "timeline", "narration is", "placeholder")
        )
        if not hard_fail and not important_warn:
            return current, history
        if attempt == max_attempts:
            return current, history

        repair_prompt = f"""
Repair this educational video script using ONLY the supplied lesson evidence.
Do not add unsupported facts. Preserve all correct content.

GRADE: {grade}
TARGET DURATION: {duration} minutes
TARGET WORDS: {validation.get('target_word_count')}
STYLE: {style}

VALIDATION:
{validation}

REQUIRED CONCEPTS:
{required_concepts[:18]}

SCRIPT:
{current}

LESSON EVIDENCE:
{context}

Fix the validation issues, especially duration/word-count alignment, missing
required concepts, contiguous time ranges, and placeholder OTS/SFX.
Return ONLY the corrected JSON with the same scene schema.
"""
        current = llm.generate_json(repair_prompt)
    return current, history
