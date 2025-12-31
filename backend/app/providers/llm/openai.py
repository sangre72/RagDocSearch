"""OpenAI LLM Provider"""

from typing import AsyncIterator

from langchain_openai import ChatOpenAI

from app.providers.base import LLMConfig, LLMMessage, LLMResponse
from .base import BaseLLMProvider


class OpenAILLMProvider(BaseLLMProvider):
    """OpenAI LLM Provider"""

    provider_name = "openai"

    AVAILABLE_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = ChatOpenAI(
            model=config.model_name,
            api_key=config.api_key,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """동기 응답 생성"""
        langchain_messages = [
            (msg.role, msg.content) for msg in messages
        ]
        response = await self.client.ainvoke(langchain_messages)

        usage = None
        if hasattr(response, 'response_metadata'):
            usage = response.response_metadata.get('usage')

        return LLMResponse(
            content=response.content,
            model=self.config.model_name,
            usage=usage,
        )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """스트리밍 응답 생성"""
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
        try:
            test_messages = [LLMMessage(role="user", content="hi")]
            await self.generate(test_messages)
            return True
        except Exception:
            return False
