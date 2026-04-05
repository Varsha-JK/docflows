import json
from pathlib import Path
import httpx
import logging
import os
import hashlib
from core.registry import DocumentRegistry

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
import sys


DSN = os.getenv(
    "REGISTRY_DSN",
    "postgresql://ingestion_user:ingestion_pass@localhost:5432/ingestion",
)
registry = DocumentRegistry(DSN)

EXTRACTOR_URL = "http://localhost:8000/extract"
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/extracted")

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def call_extractor(pdf_path: Path) -> dict:
    with httpx.Client(timeout=120.0) as client:
        files = {
            "file": (
                pdf_path.name,
                pdf_path.read_bytes(),
                "application/pdf",
            )
        }

        response = client.post(EXTRACTOR_URL, files=files)
        response.raise_for_status()
        return response.json()


def main():
    pdfs = sorted(RAW_DIR.glob("*.pdf"))

    if not pdfs:
        print(f"No PDFs found in {RAW_DIR}")
        return

    for pdf_path in pdfs:
        print(f"Processing: {pdf_path.name}")

        sha = compute_sha256(pdf_path)

        if registry.is_processed(sha):
            print(f"  → Skipping, already processed")
            continue

        doc_id = registry.register(sha256=sha, filename=pdf_path.name)
        registry.mark_processing(doc_id)

        try:
            data = call_extractor(pdf_path)

            out_path = OUT_DIR / f"{sha}.json"

            out_path.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )

            print(f"Saved → {out_path}")
            registry.mark_done(doc_id)
        except Exception as e:
            registry.mark_failed(doc_id, error=str(e))
            print(f"  → Failed: {e}")


if __name__ == "__main__":
    main()
