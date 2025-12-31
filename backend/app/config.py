from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, Literal


class Settings(BaseSettings):
    # === LLM Provider 설정 ===
    llm_provider: Literal[
        "openai", "ollama", "lmstudio", "huggingface", "google", "xai"
    ] = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7

    # === Embedding Provider 설정 ===
    embedding_provider: Literal["openai", "huggingface", "ollama"] = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # === Provider별 API Keys ===
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None

    # === Provider별 Base URLs ===
    ollama_base_url: str = "http://localhost:11434"
    lmstudio_base_url: str = "http://localhost:1234/v1"

    # === HuggingFace 모델 관리 ===
    huggingface_cache_dir: str = "./models"
    huggingface_device: str = "cpu"  # "cpu", "cuda", "mps"

    # === Database ===
    database_url: str = "postgresql+psycopg://localhost:5432/ragdoc"

    # === Upload ===
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB

    # === Vector store ===
    collection_name: str = "documents"

    class Config:
        env_file = ".env"
        extra = "ignore"

    def get_api_key_for_provider(self, provider: str) -> Optional[str]:
        """Provider별 API 키 반환"""
        key_map = {
            "openai": self.openai_api_key,
            "google": self.google_api_key,
            "xai": self.xai_api_key,
            "huggingface": self.huggingface_api_key,
        }
        return key_map.get(provider)

    def get_base_url_for_provider(self, provider: str) -> Optional[str]:
        """Provider별 Base URL 반환"""
        url_map = {
            "ollama": self.ollama_base_url,
            "lmstudio": self.lmstudio_base_url,
        }
        return url_map.get(provider)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
