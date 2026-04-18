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
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "The retry logic..."

    with patch("backend.query.llm.OpenAI") as MockOpenAI:
        mock_client = MockOpenAI.return_value
        mock_client.chat.completions.create.return_value = iter([mock_chunk])
        chunks_out = list(stream_answer("How does retry work?", CHUNKS))
        assert any("retry" in c.lower() for c in chunks_out)
