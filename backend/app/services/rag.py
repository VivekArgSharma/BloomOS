from __future__ import annotations

from pathlib import Path

from app.core.config import get_settings


class RagService:
    def __init__(self) -> None:
        settings = get_settings()
        self.docs_path = Path(settings.rag_docs_path)
        self.index_path = Path(settings.faiss_index_path)

    def status(self) -> dict[str, str | int]:
        docs = list(self.docs_path.glob("*.pdf")) if self.docs_path.exists() else []
        indexes = list(self.index_path.glob("*")) if self.index_path.exists() else []
        return {
            "docs_path": str(self.docs_path),
            "index_path": str(self.index_path),
            "pdf_count": len(docs),
            "index_file_count": len(indexes),
        }

    def grounding(self, question: str) -> list[str]:
        docs = list(self.docs_path.glob("*.pdf")) if self.docs_path.exists() else []
        if not docs:
            return [
                "No PDF manuals ingested yet.",
                "Drop plant care PDFs into backend/data/rag_docs and run the ingestion script.",
                f"Question captured for future grounding: {question}",
            ]
        return [
            f"RAG source folder contains {len(docs)} PDF file(s).",
            "The full ingestion pipeline is wired through backend/scripts/ingest_rag.py.",
            "Replace this placeholder retrieval method with FAISS-backed similarity search after your first ingest.",
        ]
