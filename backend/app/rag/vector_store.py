from dataclasses import dataclass

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document


@dataclass
class RetrievedChunk:
    chunk_id: int
    document_id: int
    title: str
    chunk_index: int
    content: str
    score: float


class VectorStore:
    def insert_chunks(self, db: Session, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        db.add_all(chunks)
        db.commit()

    def delete_chunks_for_document(self, db: Session, document_id: int) -> None:
        db.execute(delete(Chunk).where(Chunk.document_id == document_id))
        db.commit()

    def search(
        self,
        db: Session,
        workspace_id: int,
        query_embedding: list[float],
        top_k: int,
        document_id: int | None = None,
    ) -> list[RetrievedChunk]:
        distance = Chunk.embedding.cosine_distance(query_embedding)
        query = (
            db.query(Chunk, Document.title, distance.label("distance"))
            .join(Document, Document.id == Chunk.document_id)
            .filter(
                Chunk.workspace_id == workspace_id,
                Chunk.embedding.isnot(None),
            )
        )
        if document_id is not None:
            query = query.filter(Chunk.document_id == document_id)
        rows = query.order_by(distance).limit(top_k).all()
        return [
            RetrievedChunk(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                title=title,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=max(0.0, 1.0 - dist),
            )
            for chunk, title, dist in rows
        ]
