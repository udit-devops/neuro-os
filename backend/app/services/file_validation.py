import os
import re

from fastapi import HTTPException, status

from app.core.config import settings

ALLOWED_FILE_TYPES: dict[str, str] = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ALLOWED_MIME_TYPES = set(ALLOWED_FILE_TYPES.values())


class FileValidator:
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        safe = os.path.basename(filename.replace("\\", "/"))
        safe = safe.strip()
        safe = re.sub(r"[^\w.\- ]+", "_", safe)
        return safe

    @classmethod
    def validate(cls, filename: str, size: int) -> tuple[str, str]:
        """Return (safe_display_filename, file_type) or raise an HTTP error."""
        safe_name = cls.sanitize_filename(filename)
        if not safe_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="filename is required",
            )

        ext = os.path.splitext(safe_name)[1].lower()
        if ext not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"unsupported file type '{ext or '(none)'}'",
            )

        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if size > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"file exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit",
            )

        if size <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file is empty",
            )

        return safe_name, ALLOWED_FILE_TYPES[ext]
