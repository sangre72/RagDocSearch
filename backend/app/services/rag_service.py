from sqlalchemy.orm import Session
from sqlalchemy import text

from app.providers.llm.base import BaseLLMProvider
from app.providers.embedding.base import BaseEmbeddingProvider
from app.providers.base import LLMMessage
from app.schemas import SearchResult


class RAGService:
    """RAG 서비스 - LLM과 Embedding Provider를 주입받아 사용"""

    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        embedding_provider: BaseEmbeddingProvider
    ):
        self.llm = llm_provider
        self.embeddings = embedding_provider

    async def search(
        self,
        query: str,
        db: Session,
        top_k: int = 5,
        document_ids: list[int] | None = None
    ) -> list[SearchResult]:
        """벡터 검색 수행"""
        # Generate query embedding
        query_embedding = await self.embeddings.embed_query(query)

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
        """RAG 기반 채팅"""
        # Search for relevant documents
        search_results = await self.search(
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

        # Create messages using Provider abstraction
        messages = [
            LLMMessage(
                role="system",
                content="""당신은 문서 검색 도우미입니다. 제공된 문서 내용을 기반으로 사용자의 질문에 답변해주세요.
답변할 때 다음 규칙을 따르세요:
1. 제공된 문서 내용만을 기반으로 답변하세요.
2. 문서에서 관련 정보를 찾을 수 없다면 솔직히 모른다고 말하세요.
3. 가능한 경우 출처(파일명, 페이지)를 언급하세요.
4. 답변은 명확하고 구조화된 형태로 제공하세요."""
            ),
            LLMMessage(
                role="user",
                content=f"""다음은 검색된 문서 내용입니다:

{context}

사용자 질문: {query}

위 문서 내용을 기반으로 질문에 답변해주세요."""
            )
        ]

        # Generate response using LLM Provider
        response = await self.llm.generate(messages)

        return response.content, search_results
