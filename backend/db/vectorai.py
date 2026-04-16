# repomind/backend/db/vectorai.py
"""
VectorStore wrapper backed by chromadb (local, persistent, no server required).

NOTE: The original plan assumed `from vectorai import VectorAIClient` (Actian VectorAI DB).
That package does not exist on PyPI. chromadb is used as a reliable local alternative;
if Actian provides a PostgreSQL-compatible endpoint later, only this file needs updating.
"""
from __future__ import annotations

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import get_settings


class VectorStore:
    """Persistent cosine-similarity vector store backed by chromadb."""

    def __init__(
        self,
        db_path: str | None = None,
        collection: str = "codebase",
        dim: int = 768,
    ) -> None:
        s = get_settings()
        path = db_path or s.db_path
        self._collection_name = collection
        self._dim = dim
        self._client = chromadb.PersistentClient(
            path=path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._col = self._client.get_or_create_collection(
            name=collection,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def insert(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        """Batch-insert code chunks and their embeddings."""
        if not chunks:
            return
        ids = [
            f"{c['file_path']}:{c['start_line']}:{c['end_line']}:{i}"
            for i, c in enumerate(chunks)
        ]
        metadatas = [
            {
                "file_path": c["file_path"],
                "language": c["language"],
                "content": c["content"],
                "start_line": c["start_line"],
                "end_line": c["end_line"],
                "chunk_type": str(c["chunk_type"]),
            }
            for c in chunks
        ]
        self._col.add(ids=ids, embeddings=embeddings, metadatas=metadatas)

    def search(self, query_vector: list[float], top_k: int = 8) -> list[dict]:
        """Return up to top_k nearest chunks with cosine similarity scores."""
        count = self._col.count()
        if count == 0:
            return []
        results = self._col.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, count),
        )
        output = []
        for meta, distance in zip(results["metadatas"][0], results["distances"][0]):
            output.append({**meta, "score": 1 - distance})
        return output

    def clear(self) -> None:
        """Drop and recreate the collection (removes all stored vectors)."""
        try:
            self._client.delete_collection(self._collection_name)
        except Exception:
            pass
        self._col = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )


# ------------------------------------------------------------------
# Singleton accessor
# ------------------------------------------------------------------

_store: VectorStore | None = None


def get_store() -> VectorStore:
    """Return the process-level singleton VectorStore."""
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
