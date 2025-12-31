"""Ollama Embedding Provider"""

import asyncio
import httpx

from app.providers.base import EmbeddingConfig
from .base import BaseEmbeddingProvider


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    """Ollama Embedding Provider - 로컬 임베딩 모델 사용"""

    provider_name = "ollama"

    # 모델별 차원 정보
    MODEL_DIMENSIONS = {
        "nomic-embed-text": 768,
        "mxbai-embed-large": 1024,
        "all-minilm": 384,
        "snowflake-arctic-embed": 1024,
    }

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"

        # 차원 설정
        self.dimension = self.MODEL_DIMENSIONS.get(
            config.model_name,
            config.dimension
        )

    async def _embed(self, text: str) -> list[float]:
        """단일 텍스트 임베딩"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.config.model_name,
                    "prompt": text,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["embedding"]

    async def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 임베딩"""
        return await self._embed(text)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """다중 문서 임베딩"""
        # 병렬 처리로 속도 향상
        tasks = [self._embed(text) for text in texts]
        embeddings = await asyncio.gather(*tasks)
        return list(embeddings)

    def get_available_models(self) -> list[str]:
        """Ollama에서 사용 가능한 임베딩 모델 목록"""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                # embedding 모델만 필터링 (이름에 embed가 포함된 경우)
                models = data.get("models", [])
                return [
                    m["name"] for m in models
                    if "embed" in m["name"].lower()
                ]
        except Exception:
            pass
        return list(self.MODEL_DIMENSIONS.keys())

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
