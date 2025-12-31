"""Google Gemini LLM Provider"""

from typing import AsyncIterator

from app.providers.base import LLMConfig, LLMMessage, LLMResponse
from .base import BaseLLMProvider


class GoogleLLMProvider(BaseLLMProvider):
    """Google Gemini LLM Provider"""

    provider_name = "google"

    AVAILABLE_MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro",
        "gemini-pro",
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.client = ChatGoogleGenerativeAI(
                model=config.model_name,
                google_api_key=config.api_key,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
            )
            self._available = True
        except ImportError:
            self._available = False
            self.client = None

    async def generate(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """동기 응답 생성"""
        if not self._available:
            raise RuntimeError(
                "langchain-google-genai not installed. "
                "Run: pip install langchain-google-genai"
            )

        langchain_messages = [
            (msg.role, msg.content) for msg in messages
        ]
        response = await self.client.ainvoke(langchain_messages)

        return LLMResponse(
            content=response.content,
            model=self.config.model_name,
        )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """스트리밍 응답 생성"""
        if not self._available:
            raise RuntimeError("langchain-google-genai not installed")

        langchain_messages = [
            (msg.role, msg.content) for msg in messages
        ]
        async for chunk in self.client.astream(langchain_messages):
            if chunk.content:
                yield chunk.content

    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록 반환"""
        return self.AVAILABLE_MODELS

    async def health_check(self) -> bool:
        """Provider 연결 상태 확인"""
        if not self._available:
            return False
        try:
            test_messages = [LLMMessage(role="user", content="hi")]
            await self.generate(test_messages)
            return True
        except Exception:
            return False
