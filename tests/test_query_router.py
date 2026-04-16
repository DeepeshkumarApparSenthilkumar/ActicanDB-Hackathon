# repomind/tests/test_query_router.py
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.main import app

client = TestClient(app)

FAKE_CHUNKS = [
    {"file_path": "auth.py", "content": "def login(): pass",
     "start_line": 1, "end_line": 1, "language": "python",
     "chunk_type": "function", "score": 0.9}
]

def test_query_returns_sse():
    with patch("backend.routers.query.search_codebase", return_value=FAKE_CHUNKS), \
         patch("backend.routers.query.stream_answer", return_value=iter(["auth ", "handles ", "login"])):
        resp = client.post("/query", json={"question": "how does auth work?"})
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

def test_query_missing_question():
    resp = client.post("/query", json={})
    assert resp.status_code == 422
