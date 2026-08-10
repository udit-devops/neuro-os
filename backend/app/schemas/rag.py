from pydantic import BaseModel, Field


class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class RAGSource(BaseModel):
    document_id: int
    title: str
    chunk_index: int
    content: str
    score: float


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[RAGSource]