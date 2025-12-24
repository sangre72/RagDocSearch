from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.config import get_settings
from app.models import Document, DocumentChunk
from app.schemas import SearchResult

settings = get_settings()


class RAGService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.7
        )

    def search(
        self,
        query: str,
        db: Session,
        top_k: int = 5,
        document_ids: list[int] | None = None
    ) -> list[SearchResult]:
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Build search query with cosine similarity
        base_query = """
            SELECT
                dc.id as chunk_id,
                dc.document_id,
                d.original_filename as filename,
                dc.content,
                dc.page_number,
                1 - (dc.embedding <=> :embedding::vector) as score
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
        """

        if document_ids:
            base_query += " WHERE dc.document_id = ANY(:doc_ids)"

        base_query += """
            ORDER BY dc.embedding <=> :embedding::vector
            LIMIT :limit
        """

        params = {
            "embedding": str(query_embedding),
            "limit": top_k
        }
        if document_ids:
            params["doc_ids"] = document_ids

        result = db.execute(text(base_query), params)
        rows = result.fetchall()

        return [
            SearchResult(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                filename=row.filename,
                content=row.content,
                page_number=row.page_number,
                score=float(row.score)
            )
            for row in rows
        ]

    async def chat(
        self,
        query: str,
        db: Session,
        top_k: int = 5,
        document_ids: list[int] | None = None
    ) -> tuple[str, list[SearchResult]]:
        # Search for relevant documents
        search_results = self.search(
            query=query,
            db=db,
            top_k=top_k,
            document_ids=document_ids
        )

        # Build context from search results
        context_parts = []
        for result in search_results:
            source_info = f"[{result.filename}"
            if result.page_number:
                source_info += f", 페이지 {result.page_number}"
            source_info += "]"
            context_parts.append(f"{source_info}\n{result.content}")

        context = "\n\n---\n\n".join(context_parts)

        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 문서 검색 도우미입니다. 제공된 문서 내용을 기반으로 사용자의 질문에 답변해주세요.
답변할 때 다음 규칙을 따르세요:
1. 제공된 문서 내용만을 기반으로 답변하세요.
2. 문서에서 관련 정보를 찾을 수 없다면 솔직히 모른다고 말하세요.
3. 가능한 경우 출처(파일명, 페이지)를 언급하세요.
4. 답변은 명확하고 구조화된 형태로 제공하세요."""),
            ("human", """다음은 검색된 문서 내용입니다:

{context}

사용자 질문: {question}

위 문서 내용을 기반으로 질문에 답변해주세요.""")
        ])

        # Generate response
        messages = prompt.format_messages(context=context, question=query)
        response = await self.llm.ainvoke(messages)

        return response.content, search_results
