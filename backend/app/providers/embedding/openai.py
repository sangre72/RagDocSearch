"""OpenAI Embedding Provider"""

from langchain_openai import OpenAIEmbeddings

from app.providers.base import EmbeddingConfig
from .base import BaseEmbeddingProvider


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI Embedding Provider"""

    provider_name = "openai"

    MODEL_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.dimension = self.MODEL_DIMENSIONS.get(config.model_name, 1536)
        self.client = OpenAIEmbeddings(
            model=config.model_name,
            openai_api_key=config.api_key,
        )

    async def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 임베딩"""
        return await self.client.aembed_query(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """다중 문서 임베딩"""
        return await self.client.aembed_documents(texts)

    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록 반환"""
        return list(self.MODEL_DIMENSIONS.keys())

    async def health_check(self) -> bool:
        """Provider 연결 상태 확인"""
        try:
            await self.embed_query("test")
            return True
        except Exception:
            return False
