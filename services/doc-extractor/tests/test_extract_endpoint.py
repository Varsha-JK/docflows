from __future__ import annotations
from datetime import datetime
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app


client = TestClient(app)


def test_extract_endpoint_return_types() -> None:
    pdf_path = Path(__file__).parent / "files" / "sample.pdf"

    files = {"file": ("sample.pdf", pdf_path.read_bytes(), "application/pdf")}
    resp = client.post("/extract", files=files)

    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert set(data.keys()) == {"document_metadata", "extraction_metadata", "content"}

    dm = data["document_metadata"]

    assert isinstance(dm["filename"], str)
    assert isinstance(dm["mime_type"], str)
    assert isinstance(dm["sha256"], str)
    assert len(dm["sha256"]) == 64
    assert isinstance(dm["version"], str)

    assert isinstance(dm["processed_on"], str)
    datetime.fromisoformat(dm["processed_on"].replace("Z", "+00:00"))

    em = data["extraction_metadata"]

    assert isinstance(em["extractor_version"], str)
    assert isinstance(em["service_used"], str)
    assert isinstance(em["warnings"], list)

    content = data["content"]

    assert isinstance(content["full_text"], str)
    assert isinstance(content["sections"], list)
