from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentBase(BaseModel):
    filename: str
    original_filename: str


class DocumentCreate(DocumentBase):
    file_path: str
    file_size: int
    page_count: Optional[int] = None


class DocumentResponse(DocumentBase):
    id: int
    file_size: int
    page_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    document_ids: Optional[list[int]] = None


class SearchResult(BaseModel):
    chunk_id: int
    document_id: int
    filename: str
    content: str
    page_number: Optional[int]
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    query: str


class ChatQuery(BaseModel):
    query: str
    document_ids: Optional[list[int]] = None
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    sources: list[SearchResult]


class UploadResponse(BaseModel):
    message: str
    document: DocumentResponse
