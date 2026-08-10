import pytest

from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document, ProcessingStatus
from app.rag.embedding_service import EmbeddingService
from app.rag.errors import ProcessingError
from app.services.document_processor import DocumentProcessor
from app.services.storage_service import LocalStorageService, StorageError


@pytest.fixture
def storage(tmp_path):
    return LocalStorageService(root=str(tmp_path / "blobs"))


def _make_processor(storage, provider):
    return DocumentProcessor(
        storage=storage,
        embeddings=EmbeddingService(provider=provider),
    )


def _new_document(db, workspace, key, file_type="text/plain"):
    doc = Document(
        title="Integration doc",
        original_filename="doc.txt",
        file_path=key,
        file_size=10,
        file_type=file_type,
        workspace_id=workspace.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def test_process_document_marks_completed(db, owner, workspace, fake_embedding_provider, storage):
    text = "\n\n".join(f"Section {i} about topic alpha beta gamma." for i in range(30))
    key = "ws1/doc.txt"
    storage.save_bytes(key, text.encode("utf-8"))
    doc = _new_document(db, workspace, key)

    _make_processor(storage, fake_embedding_provider).process_document(db, doc.id)

    db.refresh(doc)
    assert doc.processing_status == ProcessingStatus.COMPLETED.value
    assert doc.chunk_count > 1
    assert doc.processing_started_at is not None
    assert doc.processing_completed_at is not None
    chunks = db.query(Chunk).filter(Chunk.document_id == doc.id).all()
    assert len(chunks) == doc.chunk_count
    assert all(c.embedding is not None for c in chunks)
    assert all(c.workspace_id == workspace.id for c in chunks)


def test_reprocessing_is_idempotent(db, owner, workspace, fake_embedding_provider, storage):
    key = "ws1/doc2.txt"
    storage.save_bytes(key, b"repeated content here " * 200)
    doc = _new_document(db, workspace, key)

    processor = _make_processor(storage, fake_embedding_provider)
    processor.process_document(db, doc.id)
    first_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()
    processor.process_document(db, doc.id)
    second_count = db.query(Chunk).filter(Chunk.document_id == doc.id).count()

    assert first_count == second_count > 0


def test_missing_embeddings_leaves_no_chunks(db, owner, workspace, fake_embedding_provider, storage, monkeypatch):
    key = "ws1/doc3.txt"
    storage.save_bytes(key, b"some content " * 50)
    doc = _new_document(db, workspace, key)

    processor = _make_processor(storage, fake_embedding_provider)

    def boom(texts):
        raise ProcessingError("provider outage")

    monkeypatch.setattr(processor.embeddings, "embed_documents", boom)

    with pytest.raises(ProcessingError):
        processor.process_document(db, doc.id)

    assert db.query(Chunk).filter(Chunk.document_id == doc.id).count() == 0


def test_missing_file_raises(db, owner, workspace, fake_embedding_provider, storage):
    doc = _new_document(db, workspace, "ws1/ghost.txt")
    with pytest.raises((StorageError, ValueError)):
        _make_processor(storage, fake_embedding_provider).process_document(db, doc.id)