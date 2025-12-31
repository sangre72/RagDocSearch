"""LLM Provider 추상 기본 클래스"""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.providers.base import LLMConfig, LLMMessage, LLMResponse


class BaseLLMProvider(ABC):
    """LLM Provider 추상 기본 클래스"""

    provider_name: str = "base"

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """동기 응답 생성"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """스트리밍 응답 생성"""
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록 반환"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Provider 연결 상태 확인"""
        pass
