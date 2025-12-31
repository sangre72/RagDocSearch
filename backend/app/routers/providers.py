"""Provider 관리 API"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.config import get_settings, Settings
from app.providers.registry import ProviderRegistry
from app.dependencies import ProviderManager

router = APIRouter(prefix="/providers", tags=["providers"])


# === 스키마 정의 ===

class ProviderInfo(BaseModel):
    name: str
    models: list[str]
    is_local: bool
    requires_api_key: bool


class EmbeddingProviderInfo(ProviderInfo):
    dimensions: dict[str, int] = {}


class ProviderListResponse(BaseModel):
    llm_providers: list[ProviderInfo]
    embedding_providers: list[EmbeddingProviderInfo]


class CurrentProviderResponse(BaseModel):
    llm_provider: str
    llm_model: str
    llm_temperature: float
    embedding_provider: str
    embedding_model: str
    embedding_dimension: int


class UpdateProviderRequest(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None
    embedding_provider: Optional[str] = None
    embedding_model: Optional[str] = None


class ProviderHealthResponse(BaseModel):
    llm: dict
    embedding: dict


# === API 엔드포인트 ===

@router.get("", response_model=ProviderListResponse)
async def list_providers():
    """사용 가능한 모든 Provider 목록"""
    llm_providers = []
    embedding_providers = []

    for name in ProviderRegistry.list_llm_providers():
        try:
            info = ProviderRegistry.get_llm_provider_info(name)
            llm_providers.append(ProviderInfo(**info))
        except Exception:
            pass

    for name in ProviderRegistry.list_embedding_providers():
        try:
            info = ProviderRegistry.get_embedding_provider_info(name)
            embedding_providers.append(EmbeddingProviderInfo(
                name=info["name"],
                models=info["models"],
                is_local=info["is_local"],
                requires_api_key=info["requires_api_key"],
                dimensions=info.get("dimensions", {}),
            ))
        except Exception:
            pass

    return ProviderListResponse(
        llm_providers=llm_providers,
        embedding_providers=embedding_providers
    )


@router.get("/current", response_model=CurrentProviderResponse)
async def get_current_provider(settings: Settings = Depends(get_settings)):
    """현재 활성화된 Provider 정보"""
    return CurrentProviderResponse(
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        llm_temperature=settings.llm_temperature,
        embedding_provider=settings.embedding_provider,
        embedding_model=settings.embedding_model,
        embedding_dimension=settings.embedding_dimension,
    )


@router.post("/update")
async def update_provider(
    request: UpdateProviderRequest,
    settings: Settings = Depends(get_settings)
):
    """Provider 런타임 변경 (주의: 서버 재시작 시 초기화됨)"""
    errors = []

    # LLM Provider 변경
    if request.llm_provider:
        if request.llm_provider not in ProviderRegistry.list_llm_providers():
            errors.append(f"Unknown LLM provider: {request.llm_provider}")
        else:
            settings.llm_provider = request.llm_provider
            if request.llm_model:
                settings.llm_model = request.llm_model
            ProviderManager.update_llm_provider(
                request.llm_provider,
                request.llm_model or settings.llm_model,
            )

    if request.llm_temperature is not None:
        settings.llm_temperature = request.llm_temperature
        ProviderManager.update_llm_provider(
            settings.llm_provider,
            settings.llm_model,
        )

    # Embedding Provider 변경
    if request.embedding_provider:
        if request.embedding_provider not in ProviderRegistry.list_embedding_providers():
            errors.append(f"Unknown embedding provider: {request.embedding_provider}")
        else:
            settings.embedding_provider = request.embedding_provider
            if request.embedding_model:
                settings.embedding_model = request.embedding_model
            ProviderManager.update_embedding_provider(
                request.embedding_provider,
                request.embedding_model or settings.embedding_model,
            )

    if errors:
        raise HTTPException(status_code=400, detail=errors)

    return {
        "message": "Provider updated successfully",
        "warning": "Changes will reset on server restart. Update .env for persistence.",
        "current": {
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
            "embedding_provider": settings.embedding_provider,
            "embedding_model": settings.embedding_model,
        }
    }


@router.get("/health")
async def check_provider_health(settings: Settings = Depends(get_settings)):
    """현재 Provider 연결 상태 확인"""
    llm_status = {
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "healthy": False,
        "error": None,
    }

    embedding_status = {
        "provider": settings.embedding_provider,
        "model": settings.embedding_model,
        "healthy": False,
        "error": None,
    }

    try:
        llm = ProviderManager.get_llm_provider(settings)
        llm_status["healthy"] = await llm.health_check()
    except Exception as e:
        llm_status["error"] = str(e)

    try:
        embedding = ProviderManager.get_embedding_provider(settings)
        embedding_status["healthy"] = await embedding.health_check()
    except Exception as e:
        embedding_status["error"] = str(e)

    return ProviderHealthResponse(
        llm=llm_status,
        embedding=embedding_status
    )


@router.get("/llm/{provider_name}/models")
async def get_llm_models(provider_name: str):
    """특정 LLM Provider의 사용 가능한 모델 목록"""
    try:
        info = ProviderRegistry.get_llm_provider_info(provider_name)
        return {"provider": provider_name, "models": info["models"]}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/embedding/{provider_name}/models")
async def get_embedding_models(provider_name: str):
    """특정 Embedding Provider의 사용 가능한 모델 목록"""
    try:
        info = ProviderRegistry.get_embedding_provider_info(provider_name)
        return {
            "provider": provider_name,
            "models": info["models"],
            "dimensions": info.get("dimensions", {}),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
