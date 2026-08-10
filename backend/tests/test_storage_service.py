import pytest

from app.services.storage_service import (
    LocalStorageService,
    StorageError,
    generate_storage_key,
)

from app.services.storage_service import StorageService


def test_roundtrip(tmp_path):
    store = LocalStorageService(root=str(tmp_path / "root"))
    key = "ws1/abc123.txt"
    store.save_bytes(key, b"hello")
    assert store.exists(key)
    assert store.read_bytes(key) == b"hello"
    store.delete(key)
    assert not store.exists(key)


def test_nested_keys_create_directories(tmp_path):
    store = LocalStorageService(root=str(tmp_path / "root"))
    store.save_bytes("ws1/sub/dir/file.txt", b"data")
    assert store.exists("ws1/sub/dir/file.txt")


def test_generated_keys_are_scoped_and_unique(tmp_path):
    store = LocalStorageService(root=str(tmp_path / "root"))
    key = generate_storage_key(7, "my file.TXT")
    assert key.startswith("7/")
    assert key.endswith(".txt")
    assert generate_storage_key(7, "a.bin") != key


def test_rejects_path_traversal(tmp_path):
    store = LocalStorageService(root=str(tmp_path / "root"))
    with pytest.raises(StorageError):
        store.save_bytes("../escape.txt", b"x")
    with pytest.raises(StorageError):
        store.read_bytes("a/../../etc/passwd")


def test_missing_file_read_raises(tmp_path):
    store = LocalStorageService(root=str(tmp_path / "root"))
    with pytest.raises(StorageError):
        store.read_bytes("missing.txt")