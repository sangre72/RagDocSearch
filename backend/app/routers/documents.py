from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse, DocumentListResponse, UploadResponse
from app.services.pdf_service import PDFService
from app.config import get_settings
from app.dependencies import get_embedding_provider
from app.providers.embedding.base import BaseEmbeddingProvider

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()


def get_pdf_service(
    embedding_provider: BaseEmbeddingProvider = Depends(get_embedding_provider)
) -> PDFService:
    """PDFService 의존성"""
    return PDFService(embedding_provider)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed ({settings.max_file_size} bytes)"
        )

    # Process PDF
    document = await pdf_service.process_pdf(
        file_content=content,
        original_filename=file.filename,
        db=db
    )

    return UploadResponse(
        message="Document uploaded and processed successfully",
        document=DocumentResponse.model_validate(document)
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.created_at.desc()).all()
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=len(documents)
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_service.delete_document(document, db)
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/reindex")
async def reindex_document(
    document_id: int,
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """문서 재인덱싱 (임베딩 재생성)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    updated_document = await pdf_service.reindex_document(document, db)
    return {
        "message": "Document reindexed successfully",
        "document": DocumentResponse.model_validate(updated_document)
    }


@router.post("/reindex-all")
async def reindex_all_documents(
    db: Session = Depends(get_db),
    pdf_service: PDFService = Depends(get_pdf_service)
):
    """모든 문서 재인덱싱"""
    documents = db.query(Document).all()
    reindexed = []

    for document in documents:
        try:
            updated = await pdf_service.reindex_document(document, db)
            reindexed.append(document.id)
        except Exception as e:
            # 개별 문서 실패 시 계속 진행
            pass

    return {
        "message": f"Reindexed {len(reindexed)} documents",
        "reindexed_ids": reindexed
    }
