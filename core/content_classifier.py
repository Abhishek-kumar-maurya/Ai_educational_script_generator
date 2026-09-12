import re

ACTIVITY_PATTERNS = [
    r"\bactivity\b", r"\bexercise\b", r"\bquiz\b", r"\bcheckpoint\b",
    r"\bthink and answer\b", r"\blet'?s talk\b", r"\bdiscuss\b",
    r"\bmatch the columns\b", r"\bfill in the blanks\b", r"\btick\b",
    r"\bcolour\b", r"\bcritical thinking\b"
]

def classify_text(text: str) -> str:
    low = text.lower()
    hits = sum(bool(re.search(p, low)) for p in ACTIVITY_PATTERNS)
    if hits >= 2:
        return "ACTIVITY_OR_EXERCISE"
    if re.search(r"\banswers?\b|\banswer key\b", low):
        return "ANSWER_KEY"
    if re.search(r"\brecap\b|\bwords to know\b", low):
        return "RECAP_REFERENCE"
    return "CORE_INSTRUCTION"

def classify_content(pages: list[dict]) -> list[dict]:
    return [{**p, "content_type": classify_text(p["text"])} for p in pages]
