"""Ollama LLM Provider"""

from typing import AsyncIterator
import httpx

from langchain_community.chat_models import ChatOllama

from app.providers.base import LLMConfig, LLMMessage, LLMResponse
from .base import BaseLLMProvider


class OllamaLLMProvider(BaseLLMProvider):
    """Ollama LLM Provider - 로컬 LLM 실행"""

    provider_name = "ollama"

    DEFAULT_MODELS = [
        "llama2",
        "llama3",
        "llama3.2",
        "mistral",
        "mixtral",
        "codellama",
        "phi",
        "gemma",
        "qwen",
        "qwen2.5",
    ]

    def __init__(self, config: LLMConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
        self.client = ChatOllama(
            model=config.model_name,
            base_url=self.base_url,
            temperature=config.temperature,
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
        langchain_messages = [
            (msg.role, msg.content) for msg in messages
        ]
        async for chunk in self.client.astream(langchain_messages):
            if chunk.content:
                yield chunk.content

    def get_available_models(self) -> list[str]:
        """Ollama에서 사용 가능한 모델 목록 조회"""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            pass
        return self.DEFAULT_MODELS

    async def health_check(self) -> bool:
        """Ollama 서버 연결 상태 확인"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/tags",
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception:
            return False
