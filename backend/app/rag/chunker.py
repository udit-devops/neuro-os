from dataclasses import dataclass

from app.core.config import settings
from app.rag.text_cleaner import clean_text

_SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", " "]


@dataclass
class ChunkItem:
    index: int
    text: str
    char_count: int


def _merge(parts: list[str], sep: str, chunk_size: int, overlap: int) -> list[str]:
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = current + (sep + part if current else part)
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            tail = current[-overlap:] if current and overlap > 0 else ""
            current = tail + sep + part if tail else part
    if current:
        chunks.append(current)
    return chunks


def _recursive_split(text: str, separators: list[str], chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    for index, sep in enumerate(separators):
        parts = text.split(sep)
        if len(parts) > 1:
            merged = _merge(parts, sep, chunk_size, overlap)
            result: list[str] = []
            for piece in merged:
                if len(piece) > chunk_size and index + 1 < len(separators):
                    result.extend(_recursive_split(piece, separators[index + 1 :], chunk_size, overlap))
                else:
                    result.append(piece)
            return result

    return [text[start : start + chunk_size] for start in range(0, len(text), chunk_size - overlap)]


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[ChunkItem]:
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = min(overlap if overlap is not None else settings.CHUNK_OVERLAP, chunk_size // 2)
    cleaned = clean_text(text)
    pieces = _recursive_split(cleaned, _SEPARATORS, chunk_size, overlap)
    return [
        ChunkItem(index=index, text=piece, char_count=len(piece))
        for index, piece in enumerate(pieces)
        if piece and piece.strip()
    ]
