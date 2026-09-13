from typing import Optional
from llm.base import LLMProvider
from core.profiles import grade_wpm


def generate_script(
    llm: LLMProvider,
    context: str,
    plan: Optional[dict],
    grade: str,
    duration: float,
    style: str,
    instructions: str,
    required_concepts: Optional[list] = None,
) -> dict:
    wpm = grade_wpm(grade)
    target_words = max(35, round(duration * wpm))
    lower = max(25, round(target_words * 0.85))
    upper = round(target_words * 1.08)

    # Keep the prompt compact because Ollama's num_ctx includes BOTH prompt and output.
    concepts_text = "\n".join(
        f"- {c['name']} (p.{c['source_page']}): {c['evidence'][:220]}"
        for c in (required_concepts or [])[:12]
    ) or "- Use only concepts explicitly supported by the lesson evidence."

    prompt = f"""You are an educational video script generator.
Generate ONE complete script using ONLY the supplied lesson evidence.
Do not add outside facts.

GRADE: {grade}
DURATION: {duration} minutes
NARRATION TARGET: {target_words} words; acceptable {lower}-{upper}
STYLE: {style}
EXTRA: {instructions or 'None'}

REQUIRED CONCEPTS (cover all that are supported):
{concepts_text}

LESSON EVIDENCE:
{context}

RULES:
- Use a curiosity hook and one connected learning journey.
- Preserve the lesson's meaning and terminology.
- Use simple, speakable, grade-appropriate language.
- Visuals must teach by highlighting, zooming, labeling, comparing, tracing, or demonstrating.
- OTS/SFX must be useful; never use "...".
- Do not teach activities, quizzes, or answer keys as core content.
- Keep narration within the target word range.
- Use 6-10 concise scenes for a 2-3 minute lesson; fewer for shorter videos.
- Make scene times contiguous from 00:00 to the target duration.
- Keep each visual description concise (one sentence) and each OTS/SFX concise.

OUTPUT JSON ONLY. No markdown. No explanation. Do not stop until the JSON is complete.
Schema:
{{"scenes":[{{"start_time":"00:00","end_time":"00:15","visual_animation":"...","voiceover_dialogue":"...","ots_sfx":"..."}}]}}
"""
    return llm.generate_json(prompt)
