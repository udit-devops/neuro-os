from abc import ABC, abstractmethod
from io import BytesIO

from docx import Document as DocxDocument
from pypdf import PdfReader, errors as pypdf_errors

from app.rag.errors import ProcessingError


class Extractor(ABC):
    @abstractmethod
    def extract(self, data: bytes) -> str: ...


class PlainTextExtractor(Extractor):
    def extract(self, data: bytes) -> str:
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("latin-1", errors="replace")


class PdfExtractor(Extractor):
    def extract(self, data: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(data))
        except (pypdf_errors.PdfReadError, ValueError) as exc:
            raise ProcessingError("invalid or corrupt PDF") from exc
        pages = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
            except pypdf_errors.PdfReadError as exc:
                raise ProcessingError("failed to extract text from PDF") from exc
            pages.append(text)
        return "\n\n".join(pages)


class DocxExtractor(Extractor):
    def extract(self, data: bytes) -> str:
        try:
            document = DocxDocument(BytesIO(data))
        except Exception as exc:
            raise ProcessingError("invalid or corrupt DOCX") from exc
        parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
        return "\n\n".join(parts)


_EXTRACTORS: dict[str, Extractor] = {
    "text/plain": PlainTextExtractor(),
    "text/markdown": PlainTextExtractor(),
    "application/pdf": PdfExtractor(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocxExtractor(),
}


class ExtractionService:
    def extract(self, data: bytes, file_type: str) -> str:
        extractor = _EXTRACTORS.get(file_type)
        if extractor is None:
            raise ProcessingError(f"no extractor for file type '{file_type}'")
        text = extractor.extract(data)
        if not text or not text.strip():
            raise ProcessingError("no extractable text found in file")
        return text
