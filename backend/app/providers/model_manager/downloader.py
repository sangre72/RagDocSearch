"""HuggingFace 모델 다운로드 및 캐시 관리"""

import os
import shutil
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DownloadStatus:
    """다운로드 상태"""
    model_name: str
    status: str  # "pending", "downloading", "completed", "failed"
    progress: float = 0.0
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class CachedModel:
    """캐시된 모델 정보"""
    name: str
    path: str
    size_bytes: int
    downloaded_at: datetime


class ModelDownloader:
    """HuggingFace 모델 다운로드 및 캐시 관리"""

    # 추천 임베딩 모델 목록
    RECOMMENDED_EMBEDDING_MODELS = {
        "sentence-transformers/all-MiniLM-L6-v2": {
            "dimension": 384,
            "description": "⚡ 빠른 속도, 가벼운 용량 (영어 최적화, 다국어 기본 지원)",
            "size_mb": 90,
        },
        "sentence-transformers/all-mpnet-base-v2": {
            "dimension": 768,
            "description": "🏆 영어 문서 최고 성능 (영어 전용)",
            "size_mb": 420,
        },
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": {
            "dimension": 384,
            "description": "🌍 50개 언어 지원 (한국어 포함, 균형잡힌 성능)",
            "size_mb": 470,
        },
        "BAAI/bge-m3": {
            "dimension": 1024,
            "description": "🚀 최신 SOTA 모델 (한국어 우수, Dense+Sparse 검색)",
            "size_mb": 2200,
        },
        "intfloat/multilingual-e5-large": {
            "dimension": 1024,
            "description": "💪 대용량 다국어 모델 (한국어 우수, 높은 정확도)",
            "size_mb": 2200,
        },
    }

    # 추천 LLM 모델 목록 (HuggingFace Transformers 용)
    RECOMMENDED_LLM_MODELS = {
        "microsoft/phi-2": {
            "description": "⚡ 2.7B 경량 고성능 (영어 최적화, 코드 생성 우수)",
            "size_gb": 5.4,
        },
        "TinyLlama/TinyLlama-1.1B-Chat-v1.0": {
            "description": "🪶 1.1B 초경량 채팅 (빠른 응답, 저사양 PC)",
            "size_gb": 2.2,
        },
        "Qwen/Qwen2-1.5B-Instruct": {
            "description": "🇰🇷 1.5B 한국어 지원 (한중영 다국어, 균형잡힌 성능)",
            "size_gb": 3.0,
        },
    }

    _download_status: dict[str, DownloadStatus] = field(default_factory=dict)

    def __init__(self, cache_dir: str = "./models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._download_status: dict[str, DownloadStatus] = {}

    def _get_model_path(self, model_name: str) -> Path:
        """모델 저장 경로 반환"""
        safe_name = model_name.replace("/", "--")
        return self.cache_dir / safe_name

    def is_model_cached(self, model_name: str) -> bool:
        """모델이 캐시되어 있는지 확인"""
        model_path = self._get_model_path(model_name)
        return model_path.exists() and any(model_path.iterdir())

    def get_cached_models(self) -> list[CachedModel]:
        """캐시된 모델 목록 반환"""
        cached = []
        if not self.cache_dir.exists():
            return cached

        for model_dir in self.cache_dir.iterdir():
            if model_dir.is_dir():
                name = model_dir.name.replace("--", "/")
                size = sum(
                    f.stat().st_size
                    for f in model_dir.rglob("*")
                    if f.is_file()
                )
                mtime = datetime.fromtimestamp(model_dir.stat().st_mtime)
                cached.append(CachedModel(
                    name=name,
                    path=str(model_dir),
                    size_bytes=size,
                    downloaded_at=mtime,
                ))

        return cached

    def get_download_status(self, model_name: str) -> Optional[DownloadStatus]:
        """다운로드 상태 조회"""
        return self._download_status.get(model_name)

    def delete_model(self, model_name: str) -> bool:
        """캐시된 모델 삭제"""
        model_path = self._get_model_path(model_name)
        if model_path.exists():
            shutil.rmtree(model_path)
            return True
        return False

    def get_available_embedding_models(self) -> dict:
        """다운로드 가능한 임베딩 모델 목록"""
        return self.RECOMMENDED_EMBEDDING_MODELS

    def get_available_llm_models(self) -> dict:
        """다운로드 가능한 LLM 모델 목록"""
        return self.RECOMMENDED_LLM_MODELS

    async def download_embedding_model(
        self,
        model_name: str,
        progress_callback: Optional[callable] = None
    ) -> str:
        """임베딩 모델 다운로드 (sentence-transformers)"""
        from sentence_transformers import SentenceTransformer

        self._download_status[model_name] = DownloadStatus(
            model_name=model_name,
            status="downloading",
            started_at=datetime.now(),
        )

        try:
            model_path = self._get_model_path(model_name)

            # sentence-transformers가 자동으로 다운로드 처리
            model = SentenceTransformer(
                model_name,
                cache_folder=str(self.cache_dir),
            )

            self._download_status[model_name] = DownloadStatus(
                model_name=model_name,
                status="completed",
                progress=100.0,
                completed_at=datetime.now(),
            )

            return str(model_path)

        except Exception as e:
            self._download_status[model_name] = DownloadStatus(
                model_name=model_name,
                status="failed",
                error=str(e),
            )
            raise

    async def download_llm_model(
        self,
        model_name: str,
        progress_callback: Optional[callable] = None
    ) -> str:
        """LLM 모델 다운로드 (transformers)"""
        from huggingface_hub import snapshot_download

        self._download_status[model_name] = DownloadStatus(
            model_name=model_name,
            status="downloading",
            started_at=datetime.now(),
        )

        try:
            model_path = self._get_model_path(model_name)

            # huggingface_hub로 모델 다운로드
            snapshot_download(
                repo_id=model_name,
                local_dir=str(model_path),
                local_dir_use_symlinks=False,
            )

            self._download_status[model_name] = DownloadStatus(
                model_name=model_name,
                status="completed",
                progress=100.0,
                completed_at=datetime.now(),
            )

            return str(model_path)

        except Exception as e:
            self._download_status[model_name] = DownloadStatus(
                model_name=model_name,
                status="failed",
                error=str(e),
            )
            raise
