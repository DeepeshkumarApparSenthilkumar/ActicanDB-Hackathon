# repomind/tests/test_search.py
from unittest.mock import patch, MagicMock

def test_search_question_returns_chunks():
    mock_store = MagicMock()
    mock_store.search.return_value = [
        {"file_path": "src/auth.py", "content": "def login(): ...",
         "start_line": 10, "end_line": 20, "language": "python",
         "chunk_type": "function", "score": 0.9}
    ]
    with patch("backend.query.search.embed_single", return_value=[0.1]*768), \
         patch("backend.query.search.get_store", return_value=mock_store):
        from backend.query.search import search_codebase
        results = search_codebase("how does login work?", top_k=5)
        assert len(results) == 1
        assert results[0]["file_path"] == "src/auth.py"
        assert results[0]["score"] == 0.9
        mock_store.search.assert_called_once_with([0.1]*768, top_k=5)
