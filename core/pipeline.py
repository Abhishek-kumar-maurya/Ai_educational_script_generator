import os

from core.pdf_processor import extract_pdf
from core.content_classifier import classify_content
from core.concept_extractor import extract_concepts
from core.retriever import retrieve
from core.planner import build_plan
from core.generator import generate_script
from core.repair import repair_if_needed
from core.evaluator import evaluate


def _performance_mode(llm) -> str:
    """Return fast for small local models, quality for larger models.

    Override with PERFORMANCE_MODE=fast|quality|auto. Auto is the default and
    uses a single generation call for <=2B models to reduce RAM pressure and
    latency, while larger models retain the planning stage for quality.
    """
    requested = os.getenv("PERFORMANCE_MODE", "auto").lower().strip()
    if requested in {"fast", "quality"}:
        return requested
    options = getattr(llm, "options", {})
    return "fast" if options.get("num_ctx", 8192) <= 6144 else "quality"


def run_pipeline(pdf_bytes, grade, target_minutes, animation_style, topic,
                 additional_instructions, llm, progress_callback=None):
    def progress(message):
        if progress_callback:
            progress_callback(message)

    progress("Extracting PDF content...")
    pdf = extract_pdf(pdf_bytes)
    classified = classify_content(pdf["pages"])
    instructional = [
        p for p in classified
        if p["content_type"] not in {"ACTIVITY_OR_EXERCISE", "ANSWER_KEY"}
    ]

    progress("Identifying important lesson concepts...")
    concepts = extract_concepts(classified)
    query = topic or " ".join(c["name"] for c in concepts[:8])
    selected = retrieve(instructional, query, top_k=8)
    context = "\n\n".join(f"[Page {p['page']}]\n{p['text']}" for p in selected)

    mode = _performance_mode(llm)
    progress("Preparing AI generation...")

    # On <=2B models, one strong generation call is substantially cheaper than
    # planner + generator + repair calls and is more reliable on 3-4 GB RAM.
    plan = {}
    if mode == "quality":
        progress("Building lesson scene plan...")
        plan = build_plan(
            llm, context, grade, target_minutes, animation_style,
            additional_instructions
        )

    progress("Generating the educational video script...")
    script = generate_script(
        llm, context, plan, grade, target_minutes, animation_style,
        additional_instructions
    )

    progress("Validating duration, schema and concept coverage...")
    max_repair_attempts = 0 if mode == "fast" else 1
    repaired_script, validation_history = repair_if_needed(
        llm, script, context, plan, grade, target_minutes, animation_style,
        additional_instructions, concepts, max_attempts=max_repair_attempts
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
            "performance_mode": mode,
            "model": getattr(llm, "model_name", "unknown"),
        },
    }
