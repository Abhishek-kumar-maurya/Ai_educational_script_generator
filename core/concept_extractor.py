import json
from models.schemas import ConceptList

def extract_concepts(classified_pages: list[dict]) -> list[dict]:
    # Lightweight deterministic first pass. The AI stage can refine this list.
    concepts = []
    for p in classified_pages:
        if p["content_type"] in {"ACTIVITY_OR_EXERCISE", "ANSWER_KEY"}:
            continue
        text = p["text"]
        for line in text.splitlines():
            line = " ".join(line.split())
            if 20 <= len(line) <= 220 and (
                ":" in line or line.lower().startswith(("there are", "there is", "the ", "muscles", "bones", "joints"))
            ):
                concepts.append({"name": line[:90], "source_page": p["page"], "evidence": line})
    # Deduplicate while retaining evidence.
    seen = set()
    out = []
    for c in concepts:
        key = c["name"].lower()
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out[:40]
