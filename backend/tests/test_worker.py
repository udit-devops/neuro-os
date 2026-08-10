import pytest

from app.models.document import Document, ProcessingStatus
from app.rag.errors import ProcessingError, RetryableError
from app.services.ingestion_queue import enqueue_document, get_redis
import app.worker as worker_module
from app.worker import IngestionWorker


class RaisingProcessor:
    def __init__(self, exc: Exception) -> None:
        self.exc = exc

    def process_document(self, db, document_id: int) -> None:
        raise self.exc


class SucceedingProcessor:
    def process_document(self, db, document_id: int) -> None:
        doc = db.query(Document).filter(Document.id == document_id).first()
        doc.processing_status = ProcessingStatus.COMPLETED.value
        db.commit()


def _new_document(db, workspace):
    doc = Document(
        title="Worker doc",
        original_filename="w.txt",
        file_path="ws1/w.txt",
        file_size=5,
        file_type="text/plain",
        workspace_id=workspace.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def test_success_path_marks_completed(db, owner, workspace, monkeypatch):
    doc = _new_document(db, workspace)
    calls = []
    monkeypatch.setattr(worker_module, "enqueue_document", lambda doc_id: calls.append(doc_id))
    worker = IngestionWorker(processor=SucceedingProcessor())
    worker.handle_document(doc.id)
    db.refresh(doc)
    assert doc.processing_status == ProcessingStatus.COMPLETED.value
    assert calls == []


def test_permanent_error_marks_failed_without_retry(db, owner, workspace, monkeypatch):
    doc = _new_document(db, workspace)
    calls = []
    monkeypatch.setattr(worker_module, "enqueue_document", lambda doc_id: calls.append(doc_id))
    worker = IngestionWorker(processor=RaisingProcessor(ProcessingError("corrupt pdf")))

    worker.handle_document(doc.id)

    db.refresh(doc)
    assert doc.processing_status == ProcessingStatus.FAILED.value
    assert doc.error_message == "corrupt pdf"
    assert calls == []


def test_retryable_error_re_enqueues_while_attempts_remain(db, owner, workspace, monkeypatch):
    doc = _new_document(db, workspace)
    doc.processing_attempts = 1
    db.commit()

    calls = []
    monkeypatch.setattr(worker_module, "enqueue_document", lambda doc_id: calls.append(doc_id))
    worker = IngestionWorker(processor=RaisingProcessor(RetryableError("network flake")))

    worker.handle_document(doc.id)

    db.refresh(doc)
    assert doc.processing_status == ProcessingStatus.UPLOADED.value
    assert doc.processing_attempts == 1
    assert doc.error_message == "network flake"
    assert calls == [doc.id]


def test_retryable_error_gives_up_at_max_attempts(db, owner, workspace, monkeypatch):
    doc = _new_document(db, workspace)
    doc.processing_attempts = 3
    db.commit()

    calls = []
    monkeypatch.setattr(worker_module, "enqueue_document", lambda doc_id: calls.append(doc_id))
    worker = IngestionWorker(processor=RaisingProcessor(RetryableError("flaky")), max_attempts=3)

    worker.handle_document(doc.id)

    db.refresh(doc)
    assert doc.processing_status == ProcessingStatus.FAILED.value
    assert calls == []


def test_enqueue_uses_queue_and_document_id(db, owner, workspace, monkeypatch):
    doc = _new_document(db, workspace)
    monkeypatch.setattr(worker_module.settings, "INGESTION_QUEUE", "test:ingestion")
    enqueue_document(doc.id)
    popped = get_redis().brpop("test:ingestion", timeout=1)
    assert popped[1] == str(doc.id)