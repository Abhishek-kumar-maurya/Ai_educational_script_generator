# Technical Approach (assessment draft)

## Model

The prototype uses a locally runnable Llama instruction model through Ollama.
This follows the assessment preference for open-source/local/free approaches and
avoids mandatory paid API usage.

## Workflow

The system uses multiple stages: extraction, filtering, concept identification,
retrieval, planning, generation, validation, and repair. This reduces the risk
of treating the PDF as an undifferentiated prompt and makes failures observable.

## PDF extraction

PyMuPDF extracts page-level text and preserves page numbers. Pages are classified
using a lightweight rule layer to distinguish instructional material from obvious
activities, exercises, quizzes, and answer keys. A production version would add
OCR for scanned PDFs and stronger semantic classification.

## Grounding

The generator receives retrieved lesson evidence rather than the entire PDF by
default. The system also creates a concept checklist and checks whether required
concepts appear in the resulting script. A production implementation should add
claim-level evidence matching and semantic entailment checks.

## Guidelines

Guidelines are applied during planning and generation, then checked separately
during evaluation. The final script is not accepted solely because the model
claims it followed the rules.

## Validation

Pydantic validates output structure. Python checks timeline consistency, target
duration, word count and basic concept coverage. An evaluation stage scores
content coverage, grounding, grade appropriateness, storytelling, hook,
transitions, duration, and guideline adherence.

## Limitations

This prototype intentionally favors an 8–12 hour implementation scope. It does
not yet include robust OCR, production-grade vector retrieval, claim-level NLI,
or a comprehensive grade-language rubric.

## Production improvements

- OCR for image/scanned PDFs.
- Hybrid lexical + embedding retrieval.
- Claim extraction with source-page evidence.
- Entailment/grounding verifier.
- Versioned guideline profiles.
- Better curriculum/grade language models.
- Persistent project storage and audit logs.
- Human review/editing workflow.
- Export to production formats such as DOCX/CSV/SCORM-compatible packages.
