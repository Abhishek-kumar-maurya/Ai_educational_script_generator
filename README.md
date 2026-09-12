# AI-Assisted Educational Video Script Generator

A local Streamlit prototype for the AVGC Studio internship assessment.

## What it does

PDF → extraction → content filtering → concept extraction → lightweight retrieval
→ multi-stage AI planning → script generation → validation → repair → evaluation.

The generated result is shown as:

**Time | Visual / Animation | Voice-over / Dialogue | OTS / SFX**

## Stack

- Python 3.11+
- Streamlit
- PyMuPDF
- Ollama (local LLM)
- Pydantic
- Lightweight keyword/TF-IDF-style retrieval foundation
- Python deterministic validation

## Setup

### 1. Create a virtual environment

Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Ollama

Install Ollama from its official installer, then pull a local instruction model.

For a low-RAM development laptop, use a small model:

```bash
ollama pull qwen2.5:1.5b
```

For a stronger machine/final deployment, you can use:

```bash
ollama pull llama3.1:8b
```

Make sure Ollama is running.

### Adaptive performance mode

The app uses `PERFORMANCE_MODE=auto` by default. It detects the configured
model size from its name and changes the workflow automatically:

- **<= 4B models:** fast mode — one generation call, smaller context/output
  limits, and no expensive repair LLM call. This is intended for low-RAM
  development machines.
- **> 4B models:** quality mode — planning + generation and one repair attempt
  when validation requires it. This is intended for stronger machines.

You can override this with `PERFORMANCE_MODE=fast` or
`PERFORMANCE_MODE=quality`. The model remains configurable through
`MODEL_NAME`; no application code needs to change when switching models.

The Ollama adapter also uses a long cold-start timeout, one retry, and a short
`keep_alive` period so the first request can load a model without being
incorrectly reported as a connection failure.

### 4. Run

```bash
streamlit run app.py
```

## Architecture

```text
PDF Upload
   ↓
PyMuPDF Extraction
   ↓
Content Classification
   ↓
Concept Extraction
   ↓
Relevant Content Retrieval
   ↓
AI Planning
   ↓
AI Script Generation
   ↓
Schema + Duration + Coverage Validation
   ↓
Repair Loop (max 2)
   ↓
Evaluation
   ↓
Final 4-column Script
```

## Reliability choices

1. The PDF is processed before generation.
2. Activities/exercises/answer keys are filtered from the primary generation context.
3. Concepts are extracted before script generation.
4. Retrieval limits the evidence sent to the generator.
5. Generation is structured JSON and validated with Pydantic.
6. Duration and word-count checks are deterministic.
7. Concept coverage is checked.
8. A repair loop is used when validation fails.
9. Evaluation is separate from generation.
10. The LLM provider is abstracted so the model can be replaced.

## Important prototype limitation

The current grounding check is intentionally lightweight. A production system
should add claim-level evidence matching (for example, embedding retrieval and
NLI/LLM claim verification), better scanned-PDF OCR, stronger semantic activity
classification, and a more rigorous grade-level language evaluator.

## Paid API policy

The default prototype uses a local Ollama model, so there is no per-script API
cost. If an external model adapter is added, document model choice, token usage,
and estimated cost per generated script.

## Demo flow

1. Start Ollama.
2. Start Streamlit.
3. Upload the supplied lesson PDF.
4. Select grade, duration, 2D/3D, and topic/page if needed.
5. Generate.
6. Show the pipeline metadata.
7. Show the four-column script.
8. Show evaluation scores and any repair/validation history.
