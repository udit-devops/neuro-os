from pydantic import BaseModel, Field, field_validator
from datetime import datetime as DateTime

from app.models.document import ProcessingStatus


class DocumentCreate(BaseModel):
    title: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size: int = Field(default=0, ge=0)
    file_type: str | None = Field(default=None, max_length=100)

    @field_validator("title", "original_filename")
    @classmethod
    def strip_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("cannot be empty")
        return value


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    original_filename: str | None = Field(default=None, max_length=255)
    file_path: str | None = Field(default=None, max_length=500)
    file_size: int | None = Field(default=None, ge=0)
    file_type: str | None = Field(default=None, max_length=100)

    @field_validator("title", "original_filename")
    @classmethod
    def strip_non_empty(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("cannot be empty")
        return value


class DocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str | None = None
    workspace_id: int
    processing_status: ProcessingStatus
    error_message: str | None = None
    processing_started_at: DateTime | None = None
    processing_completed_at: DateTime | None = None
    chunk_count: int
    created_at: DateTime
    updated_at: DateTime