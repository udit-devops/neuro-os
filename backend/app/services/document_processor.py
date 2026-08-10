import hashlib
import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document, ProcessingStatus
from app.rag.chunker import chunk_text
from app.rag.embedding_service import EmbeddingService
from app.rag.extractors import ExtractionService
from app.rag.text_cleaner import clean_text
from app.rag.vector_store import VectorStore
from app.services.storage_service import StorageService, get_storage_service

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(
        self,
        storage: StorageService | None = None,
        extraction: ExtractionService | None = None,
        embeddings: EmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        self.storage = storage or get_storage_service()
        self.extraction = extraction or ExtractionService()
        self.embeddings = embeddings or EmbeddingService()
        self.vector_store = vector_store or VectorStore()

    def process_document(self, db: Session, document_id: int) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"document {document_id} not found")

        document.processing_status = ProcessingStatus.PROCESSING.value
        document.processing_started_at = datetime.now(timezone.utc)
        document.processing_attempts += 1
        db.commit()

        logger.info("processing document=%s title=%r", document.id, document.title)
        raw = self.storage.read_bytes(document.file_path)
        text = self.extraction.extract(raw, document.file_type)
        text = clean_text(text)

        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("chunking produced no chunks")

        logger.info("document=%s generated %d chunks", document.id, len(chunks))

        vectors = self.embeddings.embed_documents([item.text for item in chunks])
        if len(vectors) != len(chunks):
            raise RuntimeError("embedding count does not match chunk count")

        rows = [
            Chunk(
                document_id=document.id,
                workspace_id=document.workspace_id,
                chunk_index=item.index,
                content=item.text,
                content_hash=hashlib.sha256(item.text.encode("utf-8")).hexdigest(),
                embedding=vector,
                char_count=item.char_count,
            )
            for item, vector in zip(chunks, vectors, strict=True)
        ]

        self.vector_store.delete_chunks_for_document(db, document.id)
        self.vector_store.insert_chunks(db, rows)

        document.processing_status = ProcessingStatus.COMPLETED.value
        document.chunk_count = len(chunks)
        document.processing_completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info("document=%s completed with %d chunks", document.id, len(chunks))
