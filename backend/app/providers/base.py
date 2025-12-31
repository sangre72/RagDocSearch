"""공통 타입 정의"""

from pydantic import BaseModel
from typing import Optional


class LLMConfig(BaseModel):
    """LLM Provider 공통 설정"""
    provider: str
    model_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class EmbeddingConfig(BaseModel):
    """Embedding Provider 공통 설정"""
    provider: str
    model_name: str
    dimension: int = 1536
    api_key: Optional[str] = None
    base_url: Optional[str] = None


class LLMMessage(BaseModel):
    """LLM 메시지"""
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMResponse(BaseModel):
    """LLM 응답"""
    content: str
    model: str
    usage: Optional[dict] = None
