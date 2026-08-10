import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.services.file_validation import FileValidator


def test_accepts_supported_types():
    for filename in ("notes.txt", "README.md", "manual.pdf", "report.docx"):
        safe, file_type = FileValidator.validate(filename, 100)
        assert safe == filename
        assert file_type


def test_sanitizes_unsafe_filename():
    safe, _ = FileValidator.validate("../../etc/passwd.txt", 100)
    assert "passwd.txt" in safe
    assert ".." not in safe


def test_rejects_unsupported_type():
    with pytest.raises(HTTPException) as exc:
        FileValidator.validate("virus.exe", 100)
    assert exc.value.status_code == 415


def test_rejects_empty_file():
    with pytest.raises(HTTPException) as exc:
        FileValidator.validate("empty.txt", 0)
    assert exc.value.status_code == 400


def test_rejects_overly_large_file():
    too_big = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1
    with pytest.raises(HTTPException) as exc:
        FileValidator.validate("big.pdf", too_big)
    assert exc.value.status_code == 413


def test_rejects_empty_filename():
    with pytest.raises(HTTPException) as exc:
        FileValidator.validate("", 10)
    assert exc.value.status_code == 400


def test_type_is_derived_from_extension_not_mime():
    safe, file_type = FileValidator.validate("notes.txt", 10)
    assert file_type == "text/plain"