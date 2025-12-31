"""xAI Grok LLM Provider"""

from typing import AsyncIterator

from openai import AsyncOpenAI

from app.providers.base import LLMConfig, LLMMessage, LLMResponse
from .base import BaseLLMProvider


class XAILLMProvider(BaseLLMProvider):
    """xAI Grok LLM Provider - OpenAI 호환 API 사용"""

    provider_name = "xai"

    AVAILABLE_MODELS = [
        "grok-beta",
        "grok-2",
        "grok-2-mini",
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.client = AsyncOpenAI(
            base_url="https://api.x.ai/v1",
            api_key=config.api_key,
        )

    async def generate(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """동기 응답 생성"""
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=openai_messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage=response.usage.model_dump() if response.usage else None,
        )

    async def generate_stream(
        self,
        messages: list[LLMMessage],
        **kwargs
    ) -> AsyncIterator[str]:
        """스트리밍 응답 생성"""
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        stream = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=openai_messages,
            temperature=self.config.temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

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
