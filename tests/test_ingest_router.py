# repomind/tests/test_ingest_router.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from backend.main import app

client = TestClient(app)

def test_ingest_returns_summary():
    with patch("backend.routers.ingest.walk_repo") as mock_walk, \
         patch("backend.routers.ingest.chunk_file") as mock_chunk, \
         patch("backend.routers.ingest.embed_texts") as mock_embed, \
         patch("backend.routers.ingest.get_store") as mock_store:

        mock_walk.return_value = [
            {"path": "a.py", "content": "def foo(): pass", "language": "python"}
        ]
        mock_chunk.return_value = [
            {"file_path": "a.py", "language": "python", "content": "def foo(): pass",
             "start_line": 1, "end_line": 1, "chunk_type": "function"}
        ]
        mock_embed.return_value = [[0.1] * 768]
        mock_store.return_value = MagicMock()

        resp = client.post("/ingest", json={"path": "/some/repo"})
        assert resp.status_code == 200
        body = resp.json()
        assert "files_processed" in body
        assert "chunks_indexed" in body

def test_ingest_missing_path():
    resp = client.post("/ingest", json={})
    assert resp.status_code == 422

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
