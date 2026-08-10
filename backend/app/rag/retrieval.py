from sqlalchemy.orm import Session

from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import RetrievedChunk, VectorStore


class RetrievalService:
    def __init__(
        self,
        embeddings: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.embeddings = embeddings or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        db: Session,
        workspace_id: int,
        query: str,
        top_k: int = 5,
        document_id: int | None = None,
    ) -> list[RetrievedChunk]:
        query_embedding = self.embeddings.embed_query(query)
        return self.vector_store.search(
            db,
            workspace_id=workspace_id,
            query_embedding=query_embedding,
            top_k=top_k,
            document_id=document_id,
        )
