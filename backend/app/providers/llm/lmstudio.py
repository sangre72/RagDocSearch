"""LM Studio LLM Provider"""

from typing import AsyncIterator
import httpx

from openai import AsyncOpenAI

from app.providers.base import LLMConfig, LLMMessage, LLMResponse
from .base import BaseLLMProvider


class LMStudioLLMProvider(BaseLLMProvider):
    """LM Studio LLM Provider - OpenAI 호환 API 사용"""

    provider_name = "lmstudio"

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:1234/v1"
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key="lm-studio",  # LM Studio는 API 키 불필요
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
        """LM Studio에서 로드된 모델 목록 조회"""
        try:
            response = httpx.get(f"{self.base_url}/models", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["id"] for m in data.get("data", [])]
        except Exception:
            pass
        return []

    async def health_check(self) -> bool:
        """LM Studio 서버 연결 상태 확인"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception:
            return False
