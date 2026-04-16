# repomind/tests/test_llm.py
from unittest.mock import patch, MagicMock
from backend.query.llm import build_prompt, stream_answer

CHUNKS = [
    {"file_path": "src/retry.py", "start_line": 12, "end_line": 45,
     "content": "def retry(fn, max=3):\n    for i in range(max):\n        try: return fn()\n        except: pass"},
]

def test_build_prompt_includes_chunk_content():
    prompt = build_prompt("How does retry work?", CHUNKS)
    assert "retry" in prompt
    assert "src/retry.py" in prompt
    assert "12" in prompt

def test_build_prompt_includes_question():
    prompt = build_prompt("How does retry work?", CHUNKS)
    assert "How does retry work?" in prompt

def test_stream_answer_yields_text():
    mock_stream = MagicMock()
    mock_event = MagicMock()
    mock_event.type = "content_block_delta"
    mock_event.delta = MagicMock()
    mock_event.delta.type = "text_delta"
    mock_event.delta.text = "The retry logic..."
    mock_stream.__enter__ = MagicMock(return_value=mock_stream)
    mock_stream.__exit__ = MagicMock(return_value=False)
    mock_stream.__iter__ = MagicMock(return_value=iter([mock_event]))

    with patch("backend.query.llm.anthropic.Anthropic") as MockAnthropic:
        MockAnthropic.return_value.messages.stream.return_value = mock_stream
        chunks_out = list(stream_answer("How does retry work?", CHUNKS))
        assert any("retry" in c.lower() for c in chunks_out)
