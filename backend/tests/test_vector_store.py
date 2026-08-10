import pytest

from app.models.chunk import Chunk
from app.models.document import Document
from app.rag.vector_store import VectorStore
from app.rag.embedding_service import EmbeddingService
from tests.fakes import FakeEmbeddingProvider


@pytest.fixture
def indexed_document(db, owner, workspace, fake_embedding_provider):
    document = Document(
        title="Signal doc",
        original_filename="signal.txt",
        file_path="ws1/signal.txt",
        file_size=10,
        file_type="text/plain",
        workspace_id=workspace.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    texts = [
        "The quantum battery stores energy in entangled states.",
        "The zebra migration crosses the Serengeti each year.",
        "Rocket engines convert propellant into thrust.",
    ]
    vectors = EmbeddingService(provider=fake_embedding_provider).embed_documents(texts)
    rows = [
        Chunk(
            document_id=document.id,
            workspace_id=workspace.id,
            chunk_index=i,
            content=text,
            content_hash=f"h{i}",
            embedding=vector,
            char_count=len(text),
        )
        for i, (text, vector) in enumerate(zip(texts, vectors, strict=True))
    ]
    db.add_all(rows)
    db.commit()
    for row in rows:
        db.refresh(row)
    yield document, rows
    db.query(Chunk).filter(Chunk.document_id == document.id).delete()
    db.delete(document)
    db.commit()


def test_search_returns_scoped_results(db, owner, workspace, indexed_document, fake_embedding_provider):
    store = VectorStore()
    query_vec = EmbeddingService(provider=fake_embedding_provider).embed_query("entangled energy storage")
    results = store.search(db, workspace.id, query_vec, top_k=3)
    assert results
    assert results[0].document_id == indexed_document[0].id
    assert results[0].title == "Signal doc"
    assert 0.0 <= results[0].score <= 1.0
    assert all(r.workspace_id if hasattr(r, "workspace_id") else True for r in results)


def test_search_other_workspace_is_empty(db, owner, workspace, indexed_document, fake_embedding_provider):
    store = VectorStore()
    query_vec = EmbeddingService(provider=fake_embedding_provider).embed_query("anything")
    results = store.search(db, workspace.id + 5000, query_vec, top_k=5)
    assert results == []


def test_search_document_filter(db, owner, workspace, indexed_document, fake_embedding_provider):
    store = VectorStore()
    query_vec = EmbeddingService(provider=fake_embedding_provider).embed_query("anything")
    results = store.search(db, workspace.id, query_vec, top_k=5, document_id=indexed_document[0].id + 999)
    assert results == []


def test_delete_chunks_for_document(db, owner, workspace, indexed_document):
    store = VectorStore()
    store.delete_chunks_for_document(db, indexed_document[0].id)
    remaining = db.query(Chunk).filter(Chunk.document_id == indexed_document[0].id).count()
    assert remaining == 0