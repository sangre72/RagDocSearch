from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str

    # Database
    database_url: str = "postgresql://localhost:5432/ragdoc"

    # Models
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"

    # Upload
    upload_dir: str = "./uploads"
    max_file_size: int = 10485760  # 10MB

    # Vector store
    collection_name: str = "documents"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
