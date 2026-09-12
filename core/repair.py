from core.validator import deterministic_validate
from core.generator import generate_script


def repair_if_needed(llm, script, context, plan, grade, duration, style,
                     instructions, required_concepts, max_attempts=1):
    history = []
    current = script
    for attempt in range(max_attempts + 1):
        validation = deterministic_validate(current, duration, required_concepts)
        history.append(validation)
        if validation["valid_schema"] and not validation["errors"] and not validation["warnings"]:
            return current, history
        if attempt == max_attempts:
            return current, history

        repair_prompt = f"""
Repair the following educational video script.
Keep all supported content grounded in the lesson evidence.
Fix ONLY the issues identified by validation.
Do not add unsupported facts.
Target duration: {duration} minutes.
Grade: {grade}.
Animation style: {style}.

VALIDATION:
{validation}

SCRIPT:
{current}

LESSON EVIDENCE:
{context[:10000]}

Return only the corrected JSON using the same scene schema.
"""
        current = llm.generate_json(repair_prompt)
    return current, history
