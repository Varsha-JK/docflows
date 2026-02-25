from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile
from typing import Any, Dict, List
import hashlib
from datetime import date
from docling.document_converter import DocumentConverter
import tempfile

from .models import ExtractResponse


app = FastAPI(title="docflow extractor", version="0.1.0")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
async def extract(file: UploadFile = File(...)) -> Dict[str, Any]:
    # Basic validation
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=415, detail="Only PDF uploads are supported.")
    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Empty file.")
    doc_content = ""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
        converter = DocumentConverter()
        doc_content = converter.convert(tmp_path).document

    sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    file_version = "1.0"

    # STUB response (no Docling yet). This matches your Output Contract (v0).
    return {
        "document_metadata": {
            "filename": file.filename,
            "processed_on": date.today(),
            "mime_type": file.content_type,
            "pages": None,
            "sha256": sha256,
            "version": file_version,
        },
        "extraction_metadata": {
            "extractor_version": app.version,
            "service_used": "docling",
            "service_version": doc_content.version,
            "warnings": [],
        },
        "content": {
            "full_text": doc_content.export_to_text(),
            "sections": [],  # later: [{path, heading, level, page_start, page_end, text}, ...]
        },
    }
