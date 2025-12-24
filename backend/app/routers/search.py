from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SearchQuery, SearchResponse, ChatQuery, ChatResponse
from app.services.rag_service import RAGService

router = APIRouter(prefix="/search", tags=["search"])
rag_service = RAGService()


@router.post("", response_model=SearchResponse)
async def search_documents(query: SearchQuery, db: Session = Depends(get_db)):
    results = rag_service.search(
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
async def chat_with_documents(query: ChatQuery, db: Session = Depends(get_db)):
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
