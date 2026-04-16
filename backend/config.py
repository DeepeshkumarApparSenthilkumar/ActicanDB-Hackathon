# repomind/backend/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text"
    embed_dim: int = 768
    llm_model: str = "claude-sonnet-4-6"
    top_k: int = 8
    db_path: str = "./repomind.db"
    anthropic_api_key: str = ""
    offline_mode: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
