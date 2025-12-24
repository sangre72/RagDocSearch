from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document
from app.schemas import DocumentResponse, DocumentListResponse, UploadResponse
from app.services.pdf_service import PDFService
from app.config import get_settings

router = APIRouter(prefix="/documents", tags=["documents"])
settings = get_settings()
pdf_service = PDFService()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
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
async def delete_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_service.delete_document(document, db)
    return {"message": "Document deleted successfully"}
