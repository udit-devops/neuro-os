import io
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import create_access_token
from app.main import app
from app.models.document import Document, ProcessingStatus
from app.services.storage_service import LocalStorageService
import app.api.documents.routes as document_routes
import app.services.storage_service as storage_module


@pytest.fixture
def client(db, owner, workspace, tmp_path, monkeypatch):
    token = create_access_token({"sub": str(owner.id)})
    test_storage = LocalStorageService(root=str(tmp_path / "blobs"))
    monkeypatch.setattr(document_routes, "storage_service", test_storage)
    monkeypatch.setattr(storage_module, "_storage", test_storage)

    with TestClient(app) as test_client:
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client, workspace, owner


def _upload(client, workspace, filename="notes.txt", content="hello world"):
    if not isinstance(content, bytes):
        content = content.encode("utf-8")
    files = {"file": (filename, io.BytesIO(content))}
    return client.post(f"/workspaces/{workspace.id}/documents/upload", files=files)


def test_upload_creates_document_and_enqueues(client, monkeypatch):
    test_client, workspace, _ = client
    calls = []
    monkeypatch.setattr(document_routes, "enqueue_document", lambda doc_id: calls.append(doc_id))

    response = _upload(test_client, workspace)

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "notes.txt"
    assert body["original_filename"] == "notes.txt"
    assert body["file_type"] == "text/plain"
    assert body["processing_status"] == ProcessingStatus.UPLOADED.value
    assert len(calls) == 1
    assert calls[0] == body["id"]


def test_upload_with_custom_title(client, monkeypatch):
    test_client, workspace, _ = client
    monkeypatch.setattr(document_routes, "enqueue_document", lambda doc_id: None)
    response = test_client.post(
        f"/workspaces/{workspace.id}/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"data"))},
        data={"title": "My Notes"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "My Notes"


def test_upload_rejects_unsupported_type(client):
    test_client, workspace, _ = client
    response = _upload(test_client, workspace, filename="virus.exe", content=b"MZ")
    assert response.status_code == 415


def test_upload_rejects_empty_file(client):
    test_client, workspace, _ = client
    response = _upload(test_client, workspace, content=b"")
    assert response.status_code == 400


def test_upload_rejects_oversized(client, monkeypatch):
    test_client, workspace, _ = client
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 0)
    response = _upload(test_client, workspace, content=b"x" * 10)
    assert response.status_code == 413


def test_upload_requires_auth(client):
    test_client, workspace, _ = client
    response = test_client.post(
        f"/workspaces/{workspace.id}/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"data"))},
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


def test_upload_stores_blob(client, db):
    test_client, workspace, _ = client
    response = _upload(test_client, workspace, content=b"stored bytes")
    document = db.query(Document).filter(Document.id == response.json()["id"]).first()
    storage = storage_module.get_storage_service()
    assert storage.exists(document.file_path)
    assert storage.read_bytes(document.file_path) == b"stored bytes"


def test_query_missing_keys_returns_503(client, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    test_client, workspace, _ = client
    response = test_client.post(
        f"/workspaces/{workspace.id}/query",
        json={"question": "What is the capital of France?"},
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_query_other_users_workspace_returns_404(client, db):
    test_client, workspace, owner = client
    from app.core.security import hash_password
    from app.models.users import User
    from app.models.workspace import Workspace
    other_user = User(
        email=f"other-{uuid4().hex}@example.com",
        full_name="Other User",
        is_active=True,
        hashed_password=hash_password("password"),
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)
    try:
        other = Workspace(name="someone else's ws", owner_id=other_user.id)
        db.add(other)
        db.commit()
        db.refresh(other)
        response = test_client.post(
            f"/workspaces/{other.id}/query",
            json={"question": "hello?"},
        )
        assert response.status_code == 404
        db.delete(other)
        db.commit()
    finally:
        db.delete(other_user)
        db.commit()