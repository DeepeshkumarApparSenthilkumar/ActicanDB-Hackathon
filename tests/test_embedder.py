# repomind/tests/test_embedder.py
from unittest.mock import patch, MagicMock
from backend.ingestion.embedder import embed_texts, embed_single

FAKE_EMBEDDING = [0.1] * 768

def make_mock_response(embeddings):
    mock = MagicMock()
    mock.json.return_value = {"embeddings": embeddings}
    mock.raise_for_status.return_value = None
    return mock

def test_embed_single_returns_list():
    with patch("backend.ingestion.embedder.httpx.post") as mock_post:
        mock_post.return_value = make_mock_response([FAKE_EMBEDDING])
        result = embed_single("hello world")
        assert isinstance(result, list)
        assert len(result) == 768

def test_embed_texts_batch():
    with patch("backend.ingestion.embedder.httpx.post") as mock_post:
        mock_post.return_value = make_mock_response([FAKE_EMBEDDING, FAKE_EMBEDDING])
        results = embed_texts(["text one", "text two"])
        assert len(results) == 2
        assert all(len(e) == 768 for e in results)

def test_embed_single_calls_correct_model():
    with patch("backend.ingestion.embedder.httpx.post") as mock_post:
        mock_post.return_value = make_mock_response([FAKE_EMBEDDING])
        embed_single("test")
        call_kwargs = mock_post.call_args
        body = call_kwargs[1].get("json", call_kwargs[0][1] if len(call_kwargs[0]) > 1 else {})
        assert body["model"] == "nomic-embed-text"
