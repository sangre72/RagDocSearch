from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import SearchQuery, SearchResponse, ChatQuery, ChatResponse
from app.services.rag_service import RAGService
from app.dependencies import get_llm_provider, get_embedding_provider
from app.providers.llm.base import BaseLLMProvider
from app.providers.embedding.base import BaseEmbeddingProvider

router = APIRouter(prefix="/search", tags=["search"])


def get_rag_service(
    llm_provider: BaseLLMProvider = Depends(get_llm_provider),
    embedding_provider: BaseEmbeddingProvider = Depends(get_embedding_provider)
) -> RAGService:
    """RAGService 의존성"""
    return RAGService(llm_provider, embedding_provider)


@router.post("", response_model=SearchResponse)
async def search_documents(
    query: SearchQuery,
    db: Session = Depends(get_db),
    rag_service: RAGService = Depends(get_rag_service)
):
    results = await rag_service.search(
        query=query.query,
        db=db,
        top_k=query.top_k,
        document_ids=query.document_ids
    )

    return SearchResponse(
        results=results,
        query=query.query
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_documents(
    query: ChatQuery,
    db: Session = Depends(get_db),
    rag_service: RAGService = Depends(get_rag_service)
):
    answer, sources = await rag_service.chat(
        query=query.query,
        db=db,
        top_k=query.top_k,
        document_ids=query.document_ids
    )

    return ChatResponse(
        answer=answer,
        sources=sources
    )
