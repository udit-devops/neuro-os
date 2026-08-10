import pytest

from app.rag.rag_service import RAGService, RAGUnavailableError
from app.rag.vector_store import RetrievedChunk


class FakeCompletion:
    def __init__(self, content: str) -> None:
        self.message = type("Message", (), {"content": content})


class FakeChoices:
    def __init__(self, content: str) -> None:
        self.choices = [FakeCompletion(content)]


class FakeChatCompletions:
    def __init__(self) -> None:
        self.created = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        return FakeChoices("Short grounded answer. [1]")


class FakeChat:
    def __init__(self) -> None:
        self.completions = FakeChatCompletions()


class FakeGroq:
    def __init__(self, api_key: str | None = None) -> None:
        self.chat = FakeChat()


class FakeRetrieval:
    def __init__(self, results: list[RetrievedChunk] | None = None) -> None:
        self.results = results or []
        self.called_with = None

    def retrieve(self, db, workspace_id, query, top_k=5):
        self.called_with = (workspace_id, query, top_k)
        return self.results


def _source():
    return RetrievedChunk(
        chunk_id=1,
        document_id=42,
        title="Trusted Doc",
        chunk_index=0,
        content="The answer is forty-two.",
        score=0.87,
    )


def test_missing_key_raises_on_construction(monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "GROQ_API_KEY", "")
    with pytest.raises(RAGUnavailableError):
        RAGService(api_key="", retrieval=FakeRetrieval())


def test_answer_with_sources(monkeypatch):
    monkeypatch.setattr("app.rag.rag_service.Groq", FakeGroq)
    retrieval = FakeRetrieval([_source()])
    service = RAGService(api_key="test-key", retrieval=retrieval)

    result = service.answer(None, workspace_id=3, question="What is the answer?", top_k=5)

    assert "Short grounded answer" in result.answer
    assert len(result.sources) == 1
    assert result.sources[0].document_id == 42
    assert result.sources[0].score == 0.87
    assert retrieval.called_with == (3, "What is the answer?", 5)
    assert service.client.chat.completions.created


def test_answer_without_sources_skips_llm(monkeypatch):
    monkeypatch.setattr("app.rag.rag_service.Groq", FakeGroq)
    service = RAGService(api_key="test-key", retrieval=FakeRetrieval([]))

    result = service.answer(None, workspace_id=1, question="Anything", top_k=3)

    assert "no relevant context" in result.answer
    assert result.sources == []
    assert service.client.chat.completions.created == []


def test_answer_dict_shape(monkeypatch):
    monkeypatch.setattr("app.rag.rag_service.Groq", FakeGroq)
    service = RAGService(api_key="test-key", retrieval=FakeRetrieval([_source()]))
    payload = service.answer(None, workspace_id=1, question="Q", top_k=2).to_dict()
    assert set(payload) == {"answer", "sources"}
    assert payload["sources"][0]["document_id"] == 42