"""Embedding Provider 추상 기본 클래스"""

from abc import ABC, abstractmethod

from app.providers.base import EmbeddingConfig


class BaseEmbeddingProvider(ABC):
    """Embedding Provider 추상 기본 클래스"""

    provider_name: str = "base"
    dimension: int = 1536

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.dimension = config.dimension

    @abstractmethod
    async def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 임베딩"""
        pass

    @abstractmethod
    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """다중 문서 임베딩"""
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록 반환"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Provider 연결 상태 확인"""
        pass
