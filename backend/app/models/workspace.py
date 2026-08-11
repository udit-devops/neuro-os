from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.db.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
class Workspace(Base):
    __tablename__ = "workspace"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="workspaces")
    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan", passive_deletes=True)

    @property
    def document_count(self) -> int:
        return len(self.documents)