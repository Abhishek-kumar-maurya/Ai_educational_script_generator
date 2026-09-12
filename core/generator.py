from typing import Optional

from llm.base import LLMProvider


def generate_script(llm: LLMProvider, context: str, plan: Optional[dict], grade: str,
                    duration: float, style: str, instructions: str) -> dict:
    ctx = getattr(llm, "options", {}).get("num_ctx", 8192)
    context_limit = 9000 if ctx <= 4096 else (11000 if ctx <= 6144 else 14000)
    context = context[:context_limit]
    plan_text = plan if plan else "Create the scene sequence directly from the lesson evidence."

    prompt = f"""
You are the script-generation stage of a reliable educational video workflow.
Generate a complete animated educational video script grounded ONLY in the
lesson evidence below.

GRADE: {grade}
TARGET DURATION MINUTES: {duration}
ANIMATION STYLE: {style}
ADDITIONAL INSTRUCTIONS: {instructions or "None"}

PLAN:
{plan_text}

LESSON EVIDENCE:
{context}

REQUIREMENTS:
- engaging opening hook
- age/grade-appropriate language
- natural transitions so scenes feel like one continuous lesson
- use curiosity/questions before explanations where appropriate
- use a relevant story/situation where appropriate
- visuals must explain concepts, not merely repeat narration
- no unsupported factual additions
- cover the important concepts supported by the evidence
- exclude activities, exercises and answer keys unless the user explicitly asks for them
- stay within target duration
- produce scenes with time ranges
- OTS/SFX may contain on-screen text, dialogue notes, or sound effects

Return ONLY valid JSON:
{{
  "scenes": [
    {{
      "start_time": "00:00",
      "end_time": "00:20",
      "visual_animation": "...",
      "voiceover_dialogue": "...",
      "ots_sfx": "..."
    }}
  ]
}}
"""
    return llm.generate_json(prompt)
