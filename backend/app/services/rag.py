from __future__ import annotations

import json
from pathlib import Path

from app.core.config import Settings


class RagService:
    def __init__(self, settings: Settings) -> None:
        self.docs_path = Path(settings.rag_docs_path)
        self.index_path = Path(settings.faiss_index_path)
        self.manifest_path = self.index_path / "manifest.json"

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
        if not self.manifest_path.exists():
            return [
                "No RAG corpus has been ingested yet.",
                "Add PDFs to backend/data/rag_docs and run python scripts/ingest_rag.py.",
                f"Pending question for future grounding: {question}",
            ]

        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        docs = list(manifest.keys())[:3]
        return [
            f"RAG corpus ready with {len(manifest)} document(s).",
            f"Top local sources available: {', '.join(docs)}",
            "Full FAISS retrieval can be layered into this service once PDFs are added.",
        ]
