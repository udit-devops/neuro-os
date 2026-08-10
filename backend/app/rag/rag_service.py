from dataclasses import dataclass, asdict

from groq import Groq
from sqlalchemy.orm import Session

from app.core.config import settings
from app.rag.retrieval import RetrievalService
from app.rag.vector_store import RetrievedChunk

SYSTEM_PROMPT = (
    "You are an assistant that answers questions only from the provided context. "
    "Answer concisely and in the same language as the question. "
    "When you use a fact from a source, cite it inline as [1], [2], etc. "
    "If the context does not contain the answer, reply that you don't know. "
    "Never invent information outside of the context."
)


@dataclass
class RAGSource:
    document_id: int
    title: str
    chunk_index: int
    content: str
    score: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RAGAnswer:
    answer: str
    sources: list[RAGSource]

    def to_dict(self) -> dict:
        return {"answer": self.answer, "sources": [source.to_dict() for source in self.sources]}


class RAGUnavailableError(Exception):
    pass


class RAGService:
    def __init__(
        self,
        retrieval: RetrievalService | None = None,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        api_key = api_key or settings.GROQ_API_KEY
        if not api_key:
            raise RAGUnavailableError("GROQ_API_KEY is not configured; set it in .env to enable RAG")
        self.client = Groq(api_key=api_key)
        self.model = model or settings.LLM_MODEL
        self.retrieval = retrieval or RetrievalService()

    @staticmethod
    def _build_context(sources: list[RetrievedChunk]) -> str:
        return "\n\n".join(f"[{i + 1}] {source.content}" for i, source in enumerate(sources))

    def _answer_from_context(self, question: str, context: str, sources: list[RAGSource]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=0.2,
            max_tokens=800,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nContext:\n{context}\n\nAnswer:",
                },
            ],
        )
        return (completion.choices[0].message.content or "").strip()

    def answer(self, db: Session, workspace_id: int, question: str, top_k: int = 5) -> RAGAnswer:
        retrieved = self.retrieval.retrieve(db, workspace_id, question, top_k=top_k)
        sources = [
            RAGSource(
                document_id=chunk.document_id,
                title=chunk.title,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=round(chunk.score, 4),
            )
            for chunk in retrieved
        ]
        if not sources:
            return RAGAnswer(
                answer="I don't know — no relevant context was found in this workspace.",
                sources=[],
            )
        context = self._build_context(retrieved)
        answer_text = self._answer_from_context(question, context, sources)
        return RAGAnswer(answer=answer_text, sources=sources)