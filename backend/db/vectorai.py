from actian_vectorai import VectorAIClient, VectorParams, Distance, PointStruct
from backend.config import get_settings


class VectorStore:
    def __init__(self, host: str | None = None, collection: str = "codebase", dim: int = 768):
        s = get_settings()
        self._host = host or s.vectorai_host
        self._collection = collection
        self._dim = dim
        self._client = VectorAIClient(self._host)
        if not self._client.collections.exists(collection):
            self._client.collections.create(
                collection,
                vectors_config=VectorParams(size=dim, distance=Distance.Cosine),
            )
        self._next_id = self._client.points.count(collection)

    def insert(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        if not chunks:
            return
        points = [
            PointStruct(
                id=self._next_id + i,
                vector=vec,
                payload={
                    "file_path": chunk["file_path"],
                    "language": chunk["language"],
                    "content": chunk["content"],
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "chunk_type": str(chunk["chunk_type"]),
                },
            )
            for i, (chunk, vec) in enumerate(zip(chunks, embeddings))
        ]
        self._client.points.upsert(self._collection, points)
        self._next_id += len(chunks)

    def search(self, query_vector: list[float], top_k: int = 8) -> list[dict]:
        count = self._client.points.count(self._collection)
        if count == 0:
            return []
        results = self._client.points.search(
            self._collection,
            vector=query_vector,
            limit=min(top_k, count),
        )
        return [{**r.payload, "score": r.score} for r in results]

    def clear(self) -> None:
        try:
            self._client.collections.delete(self._collection)
        except Exception:
            pass
        self._client.collections.create(
            self._collection,
            vectors_config=VectorParams(size=self._dim, distance=Distance.Cosine),
        )
        self._next_id = 0

    def __del__(self):
        try:
            self._client.close()
        except Exception:
            pass


_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
    return _store
