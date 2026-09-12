from collections import Counter
import re

def retrieve(pages: list[dict], query: str, top_k: int = 8) -> list[dict]:
    if not query.strip():
        return pages[:top_k]
    terms = set(re.findall(r"[a-zA-Z]{3,}", query.lower()))
    scored = []
    for p in pages:
        text_terms = re.findall(r"[a-zA-Z]{3,}", p["text"].lower())
        counts = Counter(text_terms)
        score = sum(counts[t] for t in terms)
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for score, p in scored[:top_k] if score > 0] or pages[:top_k]
