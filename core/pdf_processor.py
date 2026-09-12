import io
import fitz

def extract_pdf(pdf_bytes: bytes) -> dict:
    doc = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
    pages = []
    for idx, page in enumerate(doc):
        text = page.get_text("text").strip()
        pages.append({"page": idx + 1, "text": text})
    nonempty = [p for p in pages if p["text"]]
    if not nonempty:
        raise ValueError("No extractable text found. The PDF may be scanned/image-only.")
    return {"page_count": len(pages), "pages": pages}
