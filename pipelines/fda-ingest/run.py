import json
from pathlib import Path
import httpx

EXTRACTOR_URL = "http://localhost:8000/extract"
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/extracted")

RAW_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


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

        data = call_extractor(pdf_path)

        sha = data["document_metadata"]["sha256"]
        out_path = OUT_DIR / f"{sha}.json"

        out_path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8",
        )

        print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
