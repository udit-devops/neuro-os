import os
import uuid
from abc import ABC, abstractmethod

from app.core.config import settings


class StorageError(Exception):
    pass


class StorageService(ABC):
    """Stores and retrieves uploaded blobs by a logical key."""

    @abstractmethod
    def save_bytes(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    def read_bytes(self, key: str) -> bytes: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def exists(self, key: str) -> bool: ...


class LocalStorageService(StorageService):
    def __init__(self, root: str | None = None) -> None:
        self.root = os.path.abspath(root or settings.STORAGE_LOCAL_ROOT)

    def _resolve(self, key: str) -> str:
        if not key or key.startswith("/") or ".." in key.split("/"):
            raise StorageError("invalid storage key")
        path = os.path.abspath(os.path.join(self.root, key))
        if os.path.commonpath([self.root, path]) != self.root:
            raise StorageError("storage key escapes storage root")
        return path

    def save_bytes(self, key: str, data: bytes) -> None:
        path = self._resolve(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)

    def read_bytes(self, key: str) -> bytes:
        path = self._resolve(key)
        if not os.path.exists(path):
            raise StorageError("file not found in storage")
        with open(path, "rb") as handle:
            return handle.read()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if os.path.exists(path):
            os.remove(path)

    def exists(self, key: str) -> bool:
        return os.path.exists(self._resolve(key))


def generate_storage_key(workspace_id: int, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return f"{workspace_id}/{uuid.uuid4().hex}{ext}"


_storage: StorageService | None = None


def get_storage_service() -> StorageService:
    global _storage
    if _storage is None:
        if settings.STORAGE_BACKEND == "s3":
            raise StorageError("S3 storage backend is not configured yet")
        _storage = LocalStorageService()
    return _storage


#wassup 