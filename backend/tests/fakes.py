from app.core.config import settings


class FakeEmbeddingProvider:
    def __init__(self, dimension: int | None = None) -> None:
        self.dimension = dimension or int(settings.EMBEDDING_DIMENSIONS)
        self.calls = 0

    def embed_texts(self, texts, task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        self.calls += 1
        vectors = []
        for index, text in enumerate(texts):
            vector = [0.0] * self.dimension
            for char in text:
                vector[hash(char) % self.dimension] += 0.01
            vector[0] = float(index + 1)
            vectors.append(vector)
        return vectors