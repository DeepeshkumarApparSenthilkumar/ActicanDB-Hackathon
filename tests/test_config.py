# repomind/tests/test_config.py
import os
from backend.config import Settings

def test_defaults():
    s = Settings()
    assert s.ollama_url == "http://localhost:11434"
    assert s.embed_model == "nomic-embed-text"
    assert s.embed_dim == 768
    assert s.llm_model == "meta/llama-3.1-70b-instruct"
    assert s.top_k == 8
    assert s.vectorai_host == "localhost:50051"

def test_override_via_env(monkeypatch):
    monkeypatch.setenv("TOP_K", "12")
    s = Settings()
    assert s.top_k == 12
