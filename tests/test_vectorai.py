# repomind/tests/test_vectorai.py
from unittest.mock import MagicMock, patch, call
import pytest


def make_mock_client(point_count=0):
    client = MagicMock()
    client.collections.exists.return_value = False
    client.points.count.return_value = point_count

    def fake_search(collection, vector, limit):
        payload = {"file_path": "a.py", "language": "python", "content": "def foo(): pass",
                   "start_line": 1, "end_line": 1, "chunk_type": "function"}
        result = MagicMock()
        result.payload = payload
        result.score = 0.95
        return [result]

    client.points.search.side_effect = fake_search
    return client


CHUNKS = [{"file_path": "a.py", "language": "python", "content": "def foo(): pass",
            "start_line": 1, "end_line": 1, "chunk_type": "function"}]
EMBEDDINGS = [[0.1] * 768]


def test_insert_calls_upsert():
    with patch("backend.db.vectorai.VectorAIClient", return_value=make_mock_client()):
        from backend.db import vectorai as vmod
        vmod._store = None
        store = vmod.VectorStore(host="localhost:50051", collection="test", dim=768)
        store.insert(CHUNKS, EMBEDDINGS)
        store._client.points.upsert.assert_called_once()
        args = store._client.points.upsert.call_args[0]
        assert args[0] == "test"
        assert len(args[1]) == 1


def test_search_returns_chunks_with_score():
    with patch("backend.db.vectorai.VectorAIClient", return_value=make_mock_client(point_count=1)):
        from backend.db import vectorai as vmod
        vmod._store = None
        store = vmod.VectorStore(host="localhost:50051", collection="test2", dim=768)
        results = store.search([0.1] * 768, top_k=5)
        assert len(results) == 1
        assert results[0]["file_path"] == "a.py"
        assert results[0]["score"] == 0.95


def test_clear_recreates_collection():
    with patch("backend.db.vectorai.VectorAIClient", return_value=make_mock_client()):
        from backend.db import vectorai as vmod
        vmod._store = None
        store = vmod.VectorStore(host="localhost:50051", collection="test3", dim=768)
        store.clear()
        store._client.collections.delete.assert_called_once_with("test3")
        assert store._next_id == 0


def test_search_empty_collection_returns_empty():
    with patch("backend.db.vectorai.VectorAIClient", return_value=make_mock_client(point_count=0)):
        from backend.db import vectorai as vmod
        vmod._store = None
        store = vmod.VectorStore(host="localhost:50051", collection="test4", dim=768)
        results = store.search([0.1] * 768, top_k=5)
        assert results == []
