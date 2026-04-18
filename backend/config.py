# repomind/backend/config.py
import os
from pydantic_settings import BaseSettings
from functools import lru_cache

_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text"
    embed_dim: int = 768
    llm_model: str = "meta/llama-3.1-70b-instruct"
    top_k: int = 8
    vectorai_host: str = "localhost:50051"
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    offline_mode: bool = False

    class Config:
        env_file = _ENV_FILE

@lru_cache
def get_settings() -> Settings:
    return Settings()
