from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from app.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ProcessingStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index(
            "ix_documents_workspace_created_id",
            "workspace_id",
            "created_at",
            "id",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    file_type = Column(String(100), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False)
    processing_status = Column(String(20), nullable=False, default=ProcessingStatus.UPLOADED.value, index=True)
    error_message = Column(Text, nullable=True)
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    chunk_count = Column(Integer, nullable=False, default=0)
    processing_attempts = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="documents")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan", passive_deletes=True)