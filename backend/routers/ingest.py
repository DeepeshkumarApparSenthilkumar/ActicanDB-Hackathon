# repomind/backend/routers/ingest.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.ingestion.walker import walk_repo
from backend.ingestion.chunker import chunk_file
from backend.ingestion.embedder import embed_texts
from backend.db.vectorai import get_store

router = APIRouter()

class IngestRequest(BaseModel):
    path: str

class IngestResponse(BaseModel):
    files_processed: int
    chunks_indexed: int

BATCH_SIZE = 32

@router.post("/ingest", response_model=IngestResponse)
def ingest_repo(req: IngestRequest) -> IngestResponse:
    store = get_store()
    store.clear()

    files = walk_repo(req.path)
    if not files:
        raise HTTPException(status_code=400, detail="No supported files found at path")

    all_chunks = []
    for f in files:
        all_chunks.extend(chunk_file(f["path"], f["content"], f["language"]))

    for i in range(0, len(all_chunks), BATCH_SIZE):
        batch = all_chunks[i : i + BATCH_SIZE]
        embeddings = embed_texts([c["content"] for c in batch])
        store.insert(batch, embeddings)

    return IngestResponse(files_processed=len(files), chunks_indexed=len(all_chunks))
