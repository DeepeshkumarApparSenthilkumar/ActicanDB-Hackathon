# repomind/backend/ingestion/embedder.py
import httpx
from backend.config import get_settings

def embed_texts(texts: list[str]) -> list[list[float]]:
    s = get_settings()
    resp = httpx.post(
        f"{s.ollama_url}/api/embed",
        json={"model": s.embed_model, "input": texts},
        timeout=60.0,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"]

def embed_single(text: str) -> list[float]:
    return embed_texts([text])[0]
