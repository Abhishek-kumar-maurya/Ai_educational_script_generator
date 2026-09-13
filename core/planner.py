from llm.base import LLMProvider


def build_plan(llm: LLMProvider, context: str, grade: str, duration: float, style: str, instructions: str) -> dict:
    prompt = f"""
You are the planning stage of an educational video script system.
Create a concise connected scene plan using ONLY the supplied lesson evidence.

GRADE: {grade}
TARGET MINUTES: {duration}
ANIMATION STYLE: {style}
ADDITIONAL INSTRUCTIONS: {instructions or 'None'}

LESSON EVIDENCE:
{context}

Return JSON with:
{{
  "hook": "...",
  "learning_sequence": ["..."],
  "story_or_situation": "...",
  "transitions": ["..."],
  "visual_strategy": ["..."]
}}

Do not introduce facts not supported by the lesson evidence.
"""
    return llm.generate_json(prompt)
