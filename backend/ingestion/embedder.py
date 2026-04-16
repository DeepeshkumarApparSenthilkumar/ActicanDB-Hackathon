# repomind/backend/ingestion/embedder.py
import httpx
from backend.config import get_settings

def embed_single(text: str) -> list[float]:
    s = get_settings()
    resp = httpx.post(
        f"{s.ollama_url}/api/embeddings",
        json={"model": s.embed_model, "prompt": text},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]

def embed_texts(texts: list[str]) -> list[list[float]]:
    return [embed_single(t) for t in texts]
