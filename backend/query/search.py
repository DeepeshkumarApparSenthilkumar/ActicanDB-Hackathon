# repomind/backend/query/search.py
from backend.ingestion.embedder import embed_single
from backend.db.vectorai import get_store
from backend.config import get_settings

def search_codebase(question: str, top_k: int | None = None) -> list[dict]:
    s = get_settings()
    k = top_k or s.top_k
    query_vec = embed_single(question)
    store = get_store()
    return store.search(query_vec, top_k=k)
