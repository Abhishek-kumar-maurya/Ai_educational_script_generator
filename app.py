import json
import os
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

from core.pipeline import run_pipeline
from core.pdf_processor import extract_pdf
from core.content_classifier import classify_content
from core.concept_extractor import extract_concepts
from llm.ollama_provider import OllamaProvider
from core.profiles import model_profile

load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
st.set_page_config(page_title="AI Educational Script Generator", page_icon="🎬", layout="wide")

st.title("🎬 AI-Assisted Educational Video Script Generator")
st.caption("Generate grounded, validated educational video scripts from lesson PDFs.")

with st.sidebar:
    st.header("Configuration")
    grade = st.text_input("Grade", value="2")
    duration = st.number_input("Target duration (minutes)", min_value=0.5, max_value=60.0, value=2.5, step=0.5)
    style = st.selectbox("Animation style", ["2D", "3D"])
    topic = st.text_input("Topic / page selection (optional)", value="")
    instructions = st.text_area("Additional instructions (optional)", height=120)
    model_name = st.text_input("Ollama model", value=os.getenv("MODEL_NAME", "llama3.1:8b"))
    profile = model_profile(model_name)
    st.caption(f"Performance profile: **{profile['name']}**")
    if profile["name"] == "fast":
        st.caption("Compact pipeline for low-RAM/local testing.")
    else:
        st.caption("Quality pipeline for stronger machines/models.")

uploaded = st.file_uploader("Upload lesson PDF", type=["pdf"])

if uploaded:
    if st.button("🔎 Analyze lesson", use_container_width=True):
        try:
            pdf = extract_pdf(uploaded.getvalue())
            classified = classify_content(pdf["pages"])
            concepts = extract_concepts(classified)
            st.session_state["analysis"] = {"pdf": pdf, "classified": classified, "concepts": concepts}
            st.success(f"Extracted {len(pdf['pages'])} pages and identified {len(concepts)} concepts.")
        except Exception as e:
            st.error(f"Analysis failed: {e}")

if uploaded and st.button("🚀 Generate validated script", type="primary", use_container_width=True):
    try:
        with st.status("Running AI workflow...", expanded=True) as status:
            provider = OllamaProvider(model_name=model_name)
            st.write(f"Using {model_name} ({provider.profile['name']} mode)")
            st.write("Extracting lesson and preparing grounded context...")
            if provider.profile["name"] == "fast":
                st.info("First generation can be slower while Ollama loads the model; later requests are faster.")
            st.write("Generating script...")
            result = run_pipeline(
                pdf_bytes=uploaded.getvalue(), grade=grade, target_minutes=float(duration),
                animation_style=style, topic=topic,
                additional_instructions=instructions, llm=provider,
            )
            status.update(label="Generation complete", state="complete")
        st.session_state["result"] = result
    except Exception as e:
        st.error(f"Generation failed: {e}")
        st.info("Tip: Qwen 1.5B may need a second attempt after its first model load. If this repeats, try the same generation again once Ollama is warm.")

result = st.session_state.get("result")
if result:
    st.subheader("Generated Script")
    rows = result["script"].get("scenes", [])
    table = [{
        "Time": f'{r["start_time"]}–{r["end_time"]}',
        "Visual / Animation": r["visual_animation"],
        "Voice-over / Dialogue": r["voiceover_dialogue"],
        "OTS / SFX": r["ots_sfx"],
    } for r in rows]
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.subheader("Evaluation")
    ev = result["evaluation"]
    cols = st.columns(4)
    for i, (k, v) in enumerate(ev["scores"].items()):
        cols[i % 4].metric(k.replace("_", " ").title(), f"{v}%")
    st.metric("Overall", f'{ev["overall"]}%')

    if ev.get("warnings"):
        st.warning("\n".join(f"• {w}" for w in ev["warnings"]))
    else:
        st.success("No validation warnings.")

    with st.expander("Pipeline details"):
        st.json(result["metadata"])

    st.download_button(
        "Download JSON", data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="generated_script.json", mime="application/json",
    )
