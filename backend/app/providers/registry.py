"""Provider Registry - Provider 등록 및 팩토리"""

from typing import Type
import httpx

from app.providers.base import LLMConfig, EmbeddingConfig
from app.providers.llm.base import BaseLLMProvider
from app.providers.embedding.base import BaseEmbeddingProvider

# LLM Providers
from app.providers.llm.openai import OpenAILLMProvider
from app.providers.llm.ollama import OllamaLLMProvider
from app.providers.llm.lmstudio import LMStudioLLMProvider
from app.providers.llm.huggingface import HuggingFaceLLMProvider
from app.providers.llm.google import GoogleLLMProvider
from app.providers.llm.xai import XAILLMProvider

# Embedding Providers
from app.providers.embedding.openai import OpenAIEmbeddingProvider
from app.providers.embedding.huggingface import HuggingFaceEmbeddingProvider
from app.providers.embedding.ollama import OllamaEmbeddingProvider


class ProviderRegistry:
    """Provider 등록 및 생성을 위한 Registry"""

    _llm_providers: dict[str, Type[BaseLLMProvider]] = {
        "openai": OpenAILLMProvider,
        "ollama": OllamaLLMProvider,
        "lmstudio": LMStudioLLMProvider,
        "huggingface": HuggingFaceLLMProvider,
        "google": GoogleLLMProvider,
        "xai": XAILLMProvider,
    }

    _embedding_providers: dict[str, Type[BaseEmbeddingProvider]] = {
        "openai": OpenAIEmbeddingProvider,
        "huggingface": HuggingFaceEmbeddingProvider,
        "ollama": OllamaEmbeddingProvider,
    }

    @classmethod
    def register_llm_provider(
        cls,
        name: str,
        provider_class: Type[BaseLLMProvider]
    ):
        """LLM Provider 등록"""
        cls._llm_providers[name] = provider_class

    @classmethod
    def register_embedding_provider(
        cls,
        name: str,
        provider_class: Type[BaseEmbeddingProvider]
    ):
        """Embedding Provider 등록"""
        cls._embedding_providers[name] = provider_class

    @classmethod
    def get_llm_provider(
        cls,
        config: LLMConfig
    ) -> BaseLLMProvider:
        """LLM Provider 인스턴스 생성"""
        provider_name = config.provider
        if provider_name not in cls._llm_providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}")
        return cls._llm_providers[provider_name](config)

    @classmethod
    def get_embedding_provider(
        cls,
        config: EmbeddingConfig
    ) -> BaseEmbeddingProvider:
        """Embedding Provider 인스턴스 생성"""
        provider_name = config.provider
        if provider_name not in cls._embedding_providers:
            raise ValueError(f"Unknown embedding provider: {provider_name}")
        return cls._embedding_providers[provider_name](config)

    @classmethod
    def list_llm_providers(cls) -> list[str]:
        """등록된 LLM Provider 목록"""
        return list(cls._llm_providers.keys())

    @classmethod
    def list_embedding_providers(cls) -> list[str]:
        """등록된 Embedding Provider 목록"""
        return list(cls._embedding_providers.keys())

    @classmethod
    def get_llm_provider_info(cls, provider_name: str) -> dict:
        """LLM Provider 정보 조회"""
        if provider_name not in cls._llm_providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

        provider_class = cls._llm_providers[provider_name]

        # LM Studio / Ollama는 실시간으로 로드된 모델 목록 조회
        models = []
        if provider_name == "lmstudio":
            models = cls._fetch_lmstudio_models()
        elif provider_name == "ollama":
            models = cls._fetch_ollama_models()
        else:
            models = (getattr(provider_class, "AVAILABLE_MODELS", [])
                      or getattr(provider_class, "DEFAULT_MODELS", []))

        return {
            "name": provider_name,
            "models": models,
            "is_local": provider_name in ["ollama", "lmstudio", "huggingface"],
            "requires_api_key": provider_name in ["openai", "google", "xai"],
        }

    @classmethod
    def _fetch_lmstudio_models(cls) -> list[str]:
        """LM Studio에서 로드된 모델 목록 조회"""
        from app.config import get_settings
        settings = get_settings()
        base_url = settings.lmstudio_base_url

        try:
            response = httpx.get(f"{base_url}/models", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return []

    @classmethod
    def _fetch_ollama_models(cls) -> list[str]:
        """Ollama에서 설치된 모델 목록 조회"""
        from app.config import get_settings
        settings = get_settings()
        base_url = settings.ollama_base_url

        try:
            response = httpx.get(f"{base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return []

    @classmethod
    def get_embedding_provider_info(cls, provider_name: str) -> dict:
        """Embedding Provider 정보 조회"""
        if provider_name not in cls._embedding_providers:
            raise ValueError(f"Unknown embedding provider: {provider_name}")

        provider_class = cls._embedding_providers[provider_name]
        model_dimensions = getattr(provider_class, "MODEL_DIMENSIONS", {})
        return {
            "name": provider_name,
            "models": list(model_dimensions.keys()),
            "dimensions": model_dimensions,
            "is_local": provider_name in ["huggingface", "ollama"],
            "requires_api_key": provider_name == "openai",
        }
