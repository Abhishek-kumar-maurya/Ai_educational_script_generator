# AI-Assisted Educational Video Script Generator

A local Streamlit prototype for the AVGC Studio internship assessment.

## What it does

PDF → extraction → content filtering → concept extraction → lightweight retrieval
→ adaptive AI generation → validation → optional repair → evaluation.

The generated result is shown as:

**Time | Visual / Animation | Voice-over / Dialogue | OTS / SFX**

## Adaptive model strategy

The application is model-agnostic and automatically selects a performance profile from the configured Ollama model name.

### Low-RAM / development mode

Examples: `qwen2.5:1.5b`, `qwen2.5:3b`

- Compact lesson context
- No separate planning LLM call
- Lower context/output limits
- Long cold-start timeout for slow laptops
- One validation/repair pass only when needed
- Ollama `keep_alive` keeps the model warm for subsequent requests

### Quality mode

Examples: `llama3.1:8b` or another larger instruction model

- Larger lesson context
- Separate planning + generation stages
- Larger context/output limits
- One repair pass only when validation identifies important issues

This means the same codebase can be tested on a low-end laptop and later deployed with a stronger model without rewriting the pipeline.

## Python compatibility

The project supports **Python 3.9+**. It intentionally avoids Python 3.10-only union type syntax such as `dict | None`.

## Stack

- Python 3.9+
- Streamlit
- PyMuPDF
- Ollama (local LLM)
- Pydantic
- python-dotenv
- Lightweight keyword retrieval foundation
- Deterministic validation/evaluation

## Setup (Windows)

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure:

```env
MODEL_NAME=qwen2.5:1.5b
OLLAMA_BASE_URL=http://localhost:11434
```

For final testing/deployment on a stronger machine, change only the model:

```env
MODEL_NAME=llama3.1:8b
```

Pull the selected model with Ollama, make sure Ollama is running, then:

```bat
streamlit run app.py
```

## Reliability / grounding choices

1. The PDF is processed before generation.
2. Activities/exercises/answer keys are filtered from primary teaching context.
3. Concepts are extracted before generation.
4. Retrieval limits the evidence sent to the model.
5. Required concepts and their source evidence are explicitly passed to generation.
6. The model receives a target narration word budget based on grade and duration.
7. The output is structured JSON and validated with Pydantic.
8. Timeline, narration duration, concept coverage, scene continuity, and OTS/SFX placeholders are checked deterministically.
9. A repair call is used only when important validation issues remain.
10. Evaluation scores reflect actual validation failures rather than always awarding high scores.
11. The LLM provider is abstracted so the model can be replaced.

## Current prototype limitations

The grounding check is deterministic and lightweight. A production version should add claim-level evidence matching, embedding retrieval, OCR for scanned PDFs, stronger semantic activity classification, and a more rigorous grade-level language evaluator.
