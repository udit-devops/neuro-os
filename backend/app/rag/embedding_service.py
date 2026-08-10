import base64
import struct
from abc import ABC, abstractmethod

import httpx
from google import genai
from google.genai import types
from groq import Groq

from app.core.config import settings
from app.rag.errors import ProcessingError, RetryableError

TASK_DOCUMENT = "RETRIEVAL_DOCUMENT"
TASK_QUERY = "RETRIEVAL_QUERY"

_EMBEDDING_DIMENSION_MISMATCH = (
    "embedding provider returned {actual}-dimensional vectors, but expected {expected} dimensions "
    "(EMBEDDING_DIMENSIONS); set EMBEDDING_MODEL to a model matching the configured dimensions"
)


def _decode_base64_embedding(value: str) -> list[float]:
    raw = base64.b64decode(value)
    return list(struct.unpack(f"<{len(raw) // 4}f", raw))


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str], task_type: str) -> list[list[float]]: ...


class GroqEmbeddingProvider(EmbeddingProvider):
    """Uses the same GROQ_API_KEY as the chat completions, so one key covers both."""

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or settings.GROQ_API_KEY
        if not api_key:
            raise RetryableError(
                "GROQ_API_KEY is not configured; set it in .env to enable embeddings"
            )
        self.client = Groq(api_key=api_key)

    def embed_texts(self, texts: list[str], task_type: str = TASK_DOCUMENT) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = self.client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=texts,
            )
        except Exception as exc:
            raise RetryableError(f"embedding provider request failed: {exc}") from exc
        return [item.embedding for item in response.data]


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Optional alternative provider when EMBEDDING_PROVIDER=gemini."""

    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or settings.GEMINI_API_KEY
        if not api_key:
            raise RetryableError(
                "GEMINI_API_KEY is not configured; set it in .env to use Gemini embeddings"
            )
        self.client = genai.Client(api_key=api_key)

    def embed_texts(self, texts: list[str], task_type: str = TASK_DOCUMENT) -> list[list[float]]:
        if not texts:
            return []
        try:
            response = self.client.models.embed_content(
                model=settings.EMBEDDING_MODEL,
                contents=texts,
                config=types.EmbedContentConfig(
                    task_type=task_type,
                    output_dimensionality=settings.EMBEDDING_DIMENSIONS,
                ),
            )
        except Exception as exc:
            raise RetryableError(f"embedding provider request failed: {exc}") from exc
        return [embedding.values for embedding in response.embeddings]


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Local embeddings via Ollama's OpenAI-compatible endpoint; no API key required."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        base_url = base_url or settings.OLLAMA_BASE_URL
        api_key = api_key or settings.OLLAMA_API_KEY
        if not base_url:
            raise RetryableError(
                "OLLAMA_BASE_URL is not configured; install Ollama (https://ollama.com) "
                "and set it in .env"
            )
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._transport = transport

    def embed_texts(self, texts: list[str], task_type: str = TASK_DOCUMENT) -> list[list[float]]:
        if not texts:
            return []
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": texts,
            "encoding_format": "float",
        }
        try:
            with httpx.Client(timeout=60.0, transport=self._transport) as client:
                response = client.post(
                    f"{self.base_url}/v1/embeddings",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
        except RetryableError:
            raise
        except Exception as exc:
            raise RetryableError(f"embedding provider request failed: {exc}") from exc
        vectors = []
        for item in data["data"]:
            embedding = item["embedding"]
            if isinstance(embedding, str):
                embedding = _decode_base64_embedding(embedding)
            vectors.append(list(embedding))
        return vectors


def get_embedding_provider() -> EmbeddingProvider:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "ollama":
        return OllamaEmbeddingProvider()
    if provider == "gemini":
        return GeminiEmbeddingProvider()
    return GroqEmbeddingProvider()


class EmbeddingService:
    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self.provider = provider or get_embedding_provider()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._batched(texts, TASK_DOCUMENT)

    def embed_query(self, text: str) -> list[float]:
        vectors = self._batched([text], TASK_QUERY)
        return vectors[0]

    def _batched(self, texts: list[str], task_type: str) -> list[list[float]]:
        batch_size = settings.EMBEDDING_BATCH_SIZE
        vectors: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            vectors.extend(
                self.provider.embed_texts(texts[start : start + batch_size], task_type=task_type)
            )
        for vector in vectors:
            if len(vector) != settings.EMBEDDING_DIMENSIONS:
                raise ProcessingError(
                    _EMBEDDING_DIMENSION_MISMATCH.format(
                        actual=len(vector),
                        expected=settings.EMBEDDING_DIMENSIONS,
                    )
                )
        return vectors