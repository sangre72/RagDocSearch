"""모델 다운로드 및 관리 API"""

import asyncio
from typing import Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.providers.model_manager.downloader import ModelDownloader, DownloadStatus

router = APIRouter(prefix="/models", tags=["models"])
settings = get_settings()

# 전역 다운로더 인스턴스
downloader = ModelDownloader(cache_dir=settings.huggingface_cache_dir)

# 다운로드 작업 상태 저장
download_tasks: dict[str, DownloadStatus] = {}


# === 스키마 ===

class DownloadRequest(BaseModel):
    model_name: str
    model_type: str = "embedding"  # "embedding" or "llm"


class CachedModelInfo(BaseModel):
    name: str
    path: str
    size_bytes: int
    size_mb: float
    downloaded_at: str


class AvailableModel(BaseModel):
    name: str
    description: str
    size_mb: float
    dimension: Optional[int] = None


# === API 엔드포인트 ===

@router.get("/available/embedding")
async def get_available_embedding_models():
    """다운로드 가능한 임베딩 모델 목록"""
    models = downloader.get_available_embedding_models()
    return {
        "models": [
            AvailableModel(
                name=name,
                description=info["description"],
                size_mb=info["size_mb"],
                dimension=info["dimension"],
            )
            for name, info in models.items()
        ]
    }


@router.get("/available/llm")
async def get_available_llm_models():
    """다운로드 가능한 LLM 모델 목록"""
    models = downloader.get_available_llm_models()
    return {
        "models": [
            AvailableModel(
                name=name,
                description=info["description"],
                size_mb=info["size_gb"] * 1024,
            )
            for name, info in models.items()
        ]
    }


@router.get("/cached")
async def get_cached_models():
    """캐시된 모델 목록"""
    cached = downloader.get_cached_models()
    return {
        "models": [
            CachedModelInfo(
                name=m.name,
                path=m.path,
                size_bytes=m.size_bytes,
                size_mb=round(m.size_bytes / (1024 * 1024), 2),
                downloaded_at=m.downloaded_at.isoformat(),
            )
            for m in cached
        ]
    }


@router.post("/download")
async def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """모델 다운로드 시작 (백그라운드)"""
    model_name = request.model_name

    # 이미 캐시된 경우
    if downloader.is_model_cached(model_name):
        return {
            "status": "already_cached",
            "message": f"Model {model_name} is already downloaded",
        }

    # 이미 다운로드 중인 경우
    status = downloader.get_download_status(model_name)
    if status and status.status == "downloading":
        return {
            "status": "downloading",
            "message": f"Model {model_name} is already being downloaded",
        }

    # 백그라운드로 다운로드 시작
    async def download_task():
        try:
            if request.model_type == "embedding":
                await downloader.download_embedding_model(model_name)
            else:
                await downloader.download_llm_model(model_name)
        except Exception as e:
            download_tasks[model_name] = DownloadStatus(
                model_name=model_name,
                status="failed",
                error=str(e),
            )

    background_tasks.add_task(asyncio.create_task, download_task())

    return {
        "status": "started",
        "message": f"Download started for {model_name}",
        "model_name": model_name,
    }


@router.get("/download/{model_name}/status")
async def get_download_status(model_name: str):
    """다운로드 상태 조회"""
    # 캐시 확인
    if downloader.is_model_cached(model_name):
        return {
            "model_name": model_name,
            "status": "completed",
            "progress": 100.0,
        }

    # 다운로드 상태 확인
    status = downloader.get_download_status(model_name)
    if status:
        return {
            "model_name": model_name,
            "status": status.status,
            "progress": status.progress,
            "error": status.error,
        }

    return {
        "model_name": model_name,
        "status": "not_found",
        "message": "No download status found for this model",
    }


@router.get("/download/{model_name}/stream")
async def stream_download_status(model_name: str):
    """다운로드 상태 SSE 스트리밍"""
    async def event_generator():
        while True:
            # 캐시 확인
            if downloader.is_model_cached(model_name):
                yield {
                    "event": "complete",
                    "data": '{"status": "completed", "progress": 100}'
                }
                break

            # 다운로드 상태 확인
            status = downloader.get_download_status(model_name)
            if status:
                if status.status == "failed":
                    yield {
                        "event": "error",
                        "data": f'{{"status": "failed", "error": "{status.error}"}}'
                    }
                    break
                elif status.status == "completed":
                    yield {
                        "event": "complete",
                        "data": '{"status": "completed", "progress": 100}'
                    }
                    break
                else:
                    yield {
                        "event": "progress",
                        "data": f'{{"status": "{status.status}", "progress": {status.progress}}}'
                    }

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())


@router.delete("/{model_name}")
async def delete_model(model_name: str):
    """캐시된 모델 삭제"""
    # URL 인코딩된 슬래시 처리
    model_name = model_name.replace("--", "/")

    if not downloader.is_model_cached(model_name):
        raise HTTPException(
            status_code=404,
            detail=f"Model {model_name} not found in cache"
        )

    success = downloader.delete_model(model_name)
    if success:
        return {"message": f"Model {model_name} deleted successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete model {model_name}"
        )


@router.get("/check/{model_name}")
async def check_model(model_name: str):
    """모델 캐시 상태 확인"""
    # URL 인코딩된 슬래시 처리
    model_name = model_name.replace("--", "/")

    is_cached = downloader.is_model_cached(model_name)
    return {
        "model_name": model_name,
        "is_cached": is_cached,
    }
