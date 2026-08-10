import uuid

import pytest

from app.db.database import SessionLocal
from app.core.security import hash_password
from app.models.users import User
from app.models.workspace import Workspace
from tests.fakes import FakeEmbeddingProvider


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def owner(db):
    email = f"test-{uuid.uuid4().hex}@example.com"
    user = User(
        email=email,
        full_name="Test Owner",
        is_active=True,
        hashed_password=hash_password("correct horse battery staple"),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    db.query(Workspace).filter(Workspace.owner_id == user.id).delete()
    db.delete(user)
    db.commit()


@pytest.fixture
def workspace(db, owner):
    ws = Workspace(name=f"ws-{uuid.uuid4().hex[:8]}", description="test workspace", owner_id=owner.id)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    yield ws


@pytest.fixture
def fake_embedding_provider():
    return FakeEmbeddingProvider()