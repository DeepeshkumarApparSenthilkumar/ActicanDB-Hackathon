# repomind/tests/test_vectorai.py
import pytest
import tempfile
from backend.db.vectorai import VectorStore


def test_insert_and_search():
    # ignore_cleanup_errors=True: chromadb holds HNSW file handles on Windows
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        store = VectorStore(db_path=tmp, collection="test", dim=4)
        chunks = [{"file_path": "a.py", "language": "python",
                   "content": "def foo(): pass", "start_line": 1,
                   "end_line": 1, "chunk_type": "function"}]
        embeddings = [[1.0, 0.0, 0.0, 0.0]]
        store.insert(chunks, embeddings)
        results = store.search([1.0, 0.0, 0.0, 0.0], top_k=5)
        assert len(results) == 1
        assert results[0]["file_path"] == "a.py"
        assert "score" in results[0]


def test_search_returns_score():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        store = VectorStore(db_path=tmp, collection="test2", dim=4)
        chunks = [{"file_path": "b.py", "language": "python",
                   "content": "def bar(): pass", "start_line": 5,
                   "end_line": 10, "chunk_type": "function"}]
        store.insert(chunks, [[0.0, 1.0, 0.0, 0.0]])
        results = store.search([0.0, 1.0, 0.0, 0.0], top_k=1)
        assert results[0]["score"] > 0.9


def test_clear_removes_data():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        store = VectorStore(db_path=tmp, collection="test3", dim=4)
        chunks = [{"file_path": "c.py", "language": "python",
                   "content": "x = 1", "start_line": 1,
                   "end_line": 1, "chunk_type": "block"}]
        store.insert(chunks, [[1.0, 0.0, 0.0, 0.0]])
        store.clear()
        results = store.search([1.0, 0.0, 0.0, 0.0], top_k=5)
        assert len(results) == 0
