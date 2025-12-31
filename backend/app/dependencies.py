"""FastAPI 의존성 주입 설정"""

from typing import Optional
from fastapi import Depends

from app.config import Settings, get_settings
from app.providers.base import LLMConfig, EmbeddingConfig
from app.providers.registry import ProviderRegistry
from app.providers.llm.base import BaseLLMProvider
from app.providers.embedding.base import BaseEmbeddingProvider


class ProviderManager:
    """Provider 인스턴스 관리 (캐싱 및 상태 관리)"""

    _llm_provider: Optional[BaseLLMProvider] = None
    _embedding_provider: Optional[BaseEmbeddingProvider] = None
    _current_llm_config: Optional[LLMConfig] = None
    _current_embedding_config: Optional[EmbeddingConfig] = None

    @classmethod
    def get_llm_config(cls, settings: Settings) -> LLMConfig:
        """현재 설정에서 LLM Config 생성"""
        return LLMConfig(
            provider=settings.llm_provider,
            model_name=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.get_api_key_for_provider(settings.llm_provider),
            base_url=settings.get_base_url_for_provider(settings.llm_provider),
        )

    @classmethod
    def get_embedding_config(cls, settings: Settings) -> EmbeddingConfig:
        """현재 설정에서 Embedding Config 생성"""
        return EmbeddingConfig(
            provider=settings.embedding_provider,
            model_name=settings.embedding_model,
            dimension=settings.embedding_dimension,
            api_key=settings.get_api_key_for_provider(settings.embedding_provider),
            base_url=settings.get_base_url_for_provider(settings.embedding_provider),
        )

    @classmethod
    def get_llm_provider(cls, settings: Settings) -> BaseLLMProvider:
        """LLM Provider 인스턴스 반환 (캐싱)"""
        config = cls.get_llm_config(settings)

        # 설정 변경 시 재생성
        if cls._llm_provider is None or cls._current_llm_config != config:
            cls._llm_provider = ProviderRegistry.get_llm_provider(config)
            cls._current_llm_config = config

        return cls._llm_provider

    @classmethod
    def get_embedding_provider(cls, settings: Settings) -> BaseEmbeddingProvider:
        """Embedding Provider 인스턴스 반환 (캐싱)"""
        config = cls.get_embedding_config(settings)

        # 설정 변경 시 재생성
        if cls._embedding_provider is None or cls._current_embedding_config != config:
            cls._embedding_provider = ProviderRegistry.get_embedding_provider(config)
            cls._current_embedding_config = config

        return cls._embedding_provider

    @classmethod
    def update_llm_provider(
        cls,
        provider_name: str,
        model_name: str,
    ):
        """런타임에 LLM Provider 변경"""
        cls._llm_provider = None  # 재생성 트리거
        cls._current_llm_config = None

    @classmethod
    def update_embedding_provider(
        cls,
        provider_name: str,
        model_name: str,
    ):
        """런타임에 Embedding Provider 변경"""
        cls._embedding_provider = None  # 재생성 트리거
        cls._current_embedding_config = None

    @classmethod
    def reset(cls):
        """모든 Provider 캐시 초기화"""
        cls._llm_provider = None
        cls._embedding_provider = None
        cls._current_llm_config = None
        cls._current_embedding_config = None


# FastAPI 의존성 함수들
def get_llm_provider(
    settings: Settings = Depends(get_settings)
) -> BaseLLMProvider:
    """LLM Provider 의존성"""
    return ProviderManager.get_llm_provider(settings)


def get_embedding_provider(
    settings: Settings = Depends(get_settings)
) -> BaseEmbeddingProvider:
    """Embedding Provider 의존성"""
    return ProviderManager.get_embedding_provider(settings)
