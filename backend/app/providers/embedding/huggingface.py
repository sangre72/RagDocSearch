"""HuggingFace Embedding Provider"""

import asyncio
from typing import Optional

from app.providers.base import EmbeddingConfig
from .base import BaseEmbeddingProvider


class HuggingFaceEmbeddingProvider(BaseEmbeddingProvider):
    """HuggingFace Sentence Transformers Embedding Provider"""

    provider_name = "huggingface"

    # 모델별 차원 정보
    MODEL_DIMENSIONS = {
        "sentence-transformers/all-MiniLM-L6-v2": 384,
        "sentence-transformers/all-mpnet-base-v2": 768,
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
        "BAAI/bge-small-en-v1.5": 384,
        "BAAI/bge-base-en-v1.5": 768,
        "BAAI/bge-large-en-v1.5": 1024,
        "BAAI/bge-m3": 1024,
        "intfloat/multilingual-e5-small": 384,
        "intfloat/multilingual-e5-base": 768,
        "intfloat/multilingual-e5-large": 1024,
        "jhgan/ko-sroberta-multitask": 768,
    }

    def __init__(self, config: EmbeddingConfig):
        super().__init__(config)
        self._model = None
        self._model_loaded = False

        # 차원 설정
        self.dimension = self.MODEL_DIMENSIONS.get(
            config.model_name,
            config.dimension
        )

    def _load_model(self):
        """모델 지연 로딩"""
        if self._model_loaded:
            return

        try:
            from sentence_transformers import SentenceTransformer
            import torch

            # 디바이스 설정
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"

            self._model = SentenceTransformer(
                self.config.model_name,
                device=device,
            )
            self._model_loaded = True
        except ImportError:
            raise RuntimeError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )

    async def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 임베딩"""
        self._load_model()
        embedding = await asyncio.to_thread(
            self._model.encode,
            text,
            convert_to_numpy=True,
        )
        return embedding.tolist()

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """다중 문서 임베딩"""
        self._load_model()
        embeddings = await asyncio.to_thread(
            self._model.encode,
            texts,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()

    def get_available_models(self) -> list[str]:
        """사용 가능한 모델 목록 반환"""
        return list(self.MODEL_DIMENSIONS.keys())

    async def health_check(self) -> bool:
        """Provider 상태 확인"""
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False
