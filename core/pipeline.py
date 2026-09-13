from core.pdf_processor import extract_pdf
from core.content_classifier import classify_content
from core.concept_extractor import extract_concepts
from core.retriever import retrieve
from core.planner import build_plan
from core.generator import generate_script
from core.repair import repair_if_needed
from core.evaluator import evaluate
from core.profiles import model_profile


def _compact_context(selected, max_chars):
    chunks = []
    total = 0
    for p in selected:
        chunk = f"[Page {p['page']}]\n{p['text'].strip()}"
        remaining = max_chars - total
        if remaining <= 0:
            break
        chunks.append(chunk[:remaining])
        total += min(len(chunk), remaining)
    return "\n\n".join(chunks)


def run_pipeline(pdf_bytes, grade, target_minutes, animation_style, topic, additional_instructions, llm):
    profile = model_profile(llm.model_name)
    pdf = extract_pdf(pdf_bytes)
    classified = classify_content(pdf["pages"])
    instructional = [p for p in classified if p["content_type"] not in {"ACTIVITY_OR_EXERCISE", "ANSWER_KEY"}]
    concepts = extract_concepts(classified)

    query = topic or " ".join(c["name"] for c in concepts[:10])
    selected = retrieve(instructional, query, top_k=6 if profile["name"] == "fast" else 10)
    context = _compact_context(selected, profile["max_context_chars"])

    if profile["use_planner"]:
        plan = build_plan(llm, context, grade, target_minutes, animation_style, additional_instructions)
    else:
        plan = {
            "hook": "Use a curiosity question grounded in the lesson.",
            "learning_sequence": [c["name"] for c in concepts[:8]],
            "story_or_situation": "Use one simple relatable situation only if supported by the lesson.",
            "transitions": ["Now", "Next", "Let's look at"],
            "visual_strategy": ["Highlight and label the concept being explained."],
        }

    script = generate_script(
        llm, context, plan, grade, target_minutes, animation_style,
        additional_instructions, required_concepts=concepts,
    )

    repaired_script, validation_history = repair_if_needed(
        llm, script, context, plan, grade, target_minutes, animation_style,
        additional_instructions, concepts, max_attempts=profile["repair_attempts"]
    )
    validation = validation_history[-1]
    evaluation = evaluate(repaired_script, validation, plan)

    return {
        "script": repaired_script,
        "evaluation": evaluation,
        "metadata": {
            "pages": pdf["page_count"],
            "instructional_pages": len(instructional),
            "concept_count": len(concepts),
            "retrieved_pages": [p["page"] for p in selected],
            "validation_attempts": len(validation_history),
            "validation_history": validation_history,
            "performance_mode": profile["name"],
            "model": llm.model_name,
        },
    }
