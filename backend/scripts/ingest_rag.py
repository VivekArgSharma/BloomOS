from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "data" / "rag_docs"
INDEX_DIR = ROOT / "data" / "faiss_index"
MANIFEST_PATH = INDEX_DIR / "manifest.json"


def chunk_text(text: str, chunk_size: int = 800) -> list[str]:
    cleaned = " ".join(text.split())
    return [cleaned[i : i + chunk_size] for i in range(0, len(cleaned), chunk_size) if cleaned[i : i + chunk_size]]


def main() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    pdf_files = sorted(DOCS_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No PDFs found. Add files to backend/data/rag_docs and rerun this script.")
        return

    manifest: dict[str, dict[str, int]] = {}
    for pdf_path in pdf_files:
        reader = PdfReader(str(pdf_path))
        combined_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        chunks = chunk_text(combined_text)
        manifest[pdf_path.name] = {"pages": len(reader.pages), "chunks": len(chunks)}

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Indexed {len(pdf_files)} PDF(s). Manifest saved to {MANIFEST_PATH}.")
    print("Next step: plug sentence-transformers + FAISS persistence into this script once your final corpus is ready.")


if __name__ == "__main__":
    main()
