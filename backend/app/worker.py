import logging
import time

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import SessionLocal
from app.models.document import Document, ProcessingStatus
from app.rag.errors import ProcessingError, RetryableError
from app.services.document_processor import DocumentProcessor
from app.services.ingestion_queue import enqueue_document, pop_document

logger = logging.getLogger(__name__)


class IngestionWorker:
    def __init__(
        self,
        processor: DocumentProcessor | None = None,
        max_attempts: int | None = None,
    ) -> None:
        self.processor = processor or DocumentProcessor()
        self.max_attempts = max_attempts or settings.MAX_PROCESSING_ATTEMPTS
        self.max_error_length = 500

    def handle_document(self, document_id: int) -> None:
        db = SessionLocal()
        try:
            self.processor.process_document(db, document_id)
        except RetryableError as exc:
            self._retry_or_fail(db, document_id, str(exc))
        except (ProcessingError, ValueError, RuntimeError) as exc:
            self._fail(db, document_id, str(exc))
        except Exception as exc:
            logger.exception("unexpected error processing document=%s", document_id)
            self._retry_or_fail(db, document_id, f"unexpected error: {exc}")
        finally:
            db.close()

    def _retry_or_fail(self, db, document_id: int, error: str) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error("document %s disappeared during retry decision", document_id)
            return
        if document.processing_attempts < self.max_attempts:
            document.error_message = error[: self.max_error_length]
            db.commit()
            logger.warning(
                "document=%s failed (attempt %d/%d), re-enqueueing: %s",
                document_id,
                document.processing_attempts,
                self.max_attempts,
                error,
            )
            enqueue_document(document_id)
        else:
            self._fail(db, document_id, error)

    def _fail(self, db, document_id: int, error: str) -> None:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            logger.error("document %s disappeared before failure marking", document_id)
            return
        document.processing_status = ProcessingStatus.FAILED.value
        document.error_message = error[: self.max_error_length]
        db.commit()
        logger.error("document=%s permanently failed: %s", document_id, error)

    def run_once(self) -> int | None:
        document_id = pop_document()
        if document_id is not None:
            self.handle_document(document_id)
        return document_id

    def run(self) -> None:
        logger.info("ingestion worker started (queue=%s)", settings.INGESTION_QUEUE)
        while True:
            try:
                self.run_once()
            except KeyboardInterrupt:
                logger.info("ingestion worker stopped")
                return
            except Exception:
                logger.exception("worker loop error; backing off")
                time.sleep(1)


def main() -> None:
    setup_logging()
    IngestionWorker().run()


if __name__ == "__main__":
    main()
