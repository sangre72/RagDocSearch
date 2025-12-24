import os
import uuid
from pathlib import Path
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import Document, DocumentChunk

settings = get_settings()


class PDFService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def process_pdf(
        self,
        file_content: bytes,
        original_filename: str,
        db: Session
    ) -> Document:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.pdf"
        file_path = self.upload_dir / filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Read PDF
        reader = PdfReader(file_path)
        page_count = len(reader.pages)

        # Create document record
        document = Document(
            filename=filename,
            original_filename=original_filename,
            file_path=str(file_path),
            file_size=len(file_content),
            page_count=page_count
        )
        db.add(document)
        db.flush()

        # Extract text and create chunks
        all_chunks = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():
                chunks = self.text_splitter.split_text(text)
                for chunk_text in chunks:
                    all_chunks.append({
                        "text": chunk_text,
                        "page_number": page_num + 1
                    })

        # Generate embeddings
        texts = [chunk["text"] for chunk in all_chunks]
        embeddings = self.embeddings.embed_documents(texts)

        # Store chunks with embeddings
        for idx, (chunk, embedding) in enumerate(zip(all_chunks, embeddings)):
            chunk_record = DocumentChunk(
                document_id=document.id,
                chunk_index=idx,
                content=chunk["text"],
                embedding=embedding,
                page_number=chunk["page_number"]
            )
            db.add(chunk_record)

        db.commit()
        db.refresh(document)

        return document

    def delete_document(self, document: Document, db: Session):
        # Delete file
        if os.path.exists(document.file_path):
            os.remove(document.file_path)

        # Delete chunks
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete()

        # Delete document
        db.delete(document)
        db.commit()
