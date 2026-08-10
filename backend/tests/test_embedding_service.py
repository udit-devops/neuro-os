import json

import httpx
import pytest

from app.rag.embedding_service import (
    EmbeddingService,
    GeminiEmbeddingProvider,
    GroqEmbeddingProvider,
    OllamaEmbeddingProvider,
)
from app.rag.errors import ProcessingError, RetryableError
from app.core.config import settings


class RecordingProvider:
    def __init__(self, dimension: int | None = None) -> None:
        self.dimension = dimension or int(settings.EMBEDDING_DIMENSIONS)
        self.calls: list[tuple[list[str], str]] = []

    def embed_texts(self, texts, task_type: str = "RETRIEVAL_DOCUMENT"):
        self.calls.append((list(texts), task_type))
        return [[float(i + 1)] * self.dimension for i in range(len(texts))]


class FixedDimProvider:
    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def embed_texts(self, texts, task_type: str = "RETRIEVAL_DOCUMENT"):
        return [[1.0] * self.dimension for _ in texts]


class FakeEmbeddingData:
    def __init__(self, vectors: list[list[float]]) -> None:
        self.data = [type("Item", (), {"embedding": v, "index": i})() for i, v in enumerate(vectors)]


class FakeEmbeddingsAPI:
    def __init__(self, vectors: list[list[float]]) -> None:
        self.vectors = vectors
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeEmbeddingData(self.vectors)


class FakeGroq:
    def __init__(self, api_key: str | None = None) -> None:
        self.embeddings = FakeEmbeddingsAPI([])


def test_embed_documents_batches(monkeypatch):
    monkeypatch.setattr(settings, "EMBEDDING_BATCH_SIZE", 2)
    provider = RecordingProvider()
    service = EmbeddingService(provider=provider)
    vectors = service.embed_documents(["a", "b", "c", "d", "e"])
    assert len(vectors) == 5
    assert [len(call[0]) for call in provider.calls] == [2, 2, 1]
    assert all(task == "RETRIEVAL_DOCUMENT" for _, task in provider.calls)


def test_embed_query_uses_query_task():
    provider = RecordingProvider()
    service = EmbeddingService(provider=provider)
    vector = service.embed_query("question?")
    assert len(vector) == settings.EMBEDDING_DIMENSIONS
    assert provider.calls[0][1] == "RETRIEVAL_QUERY"


def test_empty_texts_no_provider_call():
    provider = RecordingProvider()
    service = EmbeddingService(provider=provider)
    assert service.embed_documents([]) == []
    assert provider.calls == []


def test_groq_provider_uses_groq_sdk(monkeypatch):
    monkeypatch.setattr(settings, "EMBEDDING_MODEL", "nomic-embed-text-v1.5")
    fake_groq = FakeGroq()
    fake_groq.embeddings = FakeEmbeddingsAPI([[0.1, 0.2], [0.3, 0.4]])

    provider = GroqEmbeddingProvider(api_key="test-key")
    provider.client = fake_groq

    vectors = provider.embed_texts(["one", "two"])

    assert vectors == [[0.1, 0.2], [0.3, 0.4]]
    assert fake_groq.embeddings.last_kwargs == {
        "model": "nomic-embed-text-v1.5",
        "input": ["one", "two"],
    }


def test_groq_provider_missing_key_raises_retryable(monkeypatch):
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    with pytest.raises(RetryableError):
        GroqEmbeddingProvider()


def test_gemini_provider_missing_key_raises_retryable(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    with pytest.raises(RetryableError):
        GeminiEmbeddingProvider()


def test_ollama_provider_posts_embeddings(monkeypatch):
    monkeypatch.setattr(settings, "EMBEDDING_MODEL", "nomic-embed-text")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/embeddings"
        assert json.loads(request.content) == {
            "model": "nomic-embed-text",
            "input": ["one", "two"],
            "encoding_format": "float",
        }
        return httpx.Response(
            200,
            json={
                "model": "nomic-embed-text",
                "data": [{"embedding": [0.1, 0.2]}, {"embedding": [0.3, 0.4]}],
            },
        )

    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434", transport=httpx.MockTransport(handler)
    )
    vectors = provider.embed_texts(["one", "two"])
    assert vectors == [[0.1, 0.2], [0.3, 0.4]]


def test_ollama_provider_sends_bearer_when_api_key_set():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(200, json={"data": [{"embedding": [1.0]}]})

    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434",
        api_key="secret",
        transport=httpx.MockTransport(handler),
    )
    provider.embed_texts(["x"])
    assert True


def test_ollama_provider_decodes_base64_embeddings(monkeypatch):
    import base64
    import struct

    vector = [0.25, -0.5, 1.0]
    encoded = base64.b64encode(struct.pack("<3f", *vector)).decode()
    monkeypatch.setattr(settings, "EMBEDDING_MODEL", "nomic-embed-text")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"embedding": encoded}]})

    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434", transport=httpx.MockTransport(handler)
    )
    assert provider.embed_texts(["x"]) == [[0.25, -0.5, 1.0]]


def test_ollama_provider_missing_base_url_raises_retryable(monkeypatch):
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "")
    with pytest.raises(RetryableError):
        OllamaEmbeddingProvider()


def test_ollama_provider_request_failure_raises_retryable():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    provider = OllamaEmbeddingProvider(
        base_url="http://ollama:11434", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(RetryableError):
        provider.embed_texts(["x"])


def test_dimension_mismatch_raises_processing_error(monkeypatch):
    monkeypatch.setattr(settings, "EMBEDDING_DIMENSIONS", 768)
    service = EmbeddingService(provider=FixedDimProvider(dimension=5))
    with pytest.raises(ProcessingError) as exc:
        service.embed_documents(["text"])
    assert "expected 768 dimensions" in str(exc.value)