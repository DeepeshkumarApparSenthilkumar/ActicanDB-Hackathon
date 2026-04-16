# repomind/backend/routers/query.py
from fastapi import APIRouter
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from backend.query.search import search_codebase
from backend.query.llm import stream_answer
from backend.config import get_settings
import json

router = APIRouter()

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
async def query_codebase(req: QueryRequest):
    s = get_settings()
    chunks = search_codebase(req.question, top_k=s.top_k)

    async def event_generator():
        yield {"event": "sources", "data": json.dumps(chunks)}
        for token in stream_answer(req.question, chunks):
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
