from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.workspace import Workspace
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.workspace_service import WorkspaceService


class DocumentService:

    def __init__(self) -> None:
        self.workspace_service = WorkspaceService()

    def _get_owned_workspace(self, db: Session, owner_id: int, workspace_id: int) -> Workspace:
        return self.workspace_service.get_workspace_by_id(db, owner_id, workspace_id)

    def create_document(self, db: Session, owner_id: int, workspace_id: int, data: DocumentCreate) -> Document:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        document = Document(
            title=data.title,
            original_filename=data.original_filename,
            file_path=data.file_path,
            file_size=data.file_size,
            file_type=data.file_type,
            workspace_id=workspace.id,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def upload_document(
        self,
        db: Session,
        owner_id: int,
        workspace_id: int,
        *,
        title: str,
        original_filename: str,
        storage_key: str,
        file_size: int,
        file_type: str,
    ) -> Document:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        document = Document(
            title=title,
            original_filename=original_filename,
            file_path=storage_key,
            file_size=file_size,
            file_type=file_type,
            workspace_id=workspace.id,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_documents(self, db: Session, owner_id: int, workspace_id: int, skip: int = 0, limit: int = 100) -> list[Document]:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        return (
            db.query(Document)
            .filter(Document.workspace_id == workspace.id)
            .order_by(Document.created_at.desc(), Document.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_document_by_id(self, db: Session, owner_id: int, workspace_id: int, document_id: int) -> Document:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        return self._get_document_in_workspace(db, workspace.id, document_id)

    def update_document(self, db: Session, owner_id: int, workspace_id: int, document_id: int, data: DocumentUpdate) -> Document:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        document = self._get_document_in_workspace(db, workspace.id, document_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(document, field, value)
        db.commit()
        db.refresh(document)
        return document

    def delete_document(self, db: Session, owner_id: int, workspace_id: int, document_id: int) -> dict:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        document = self._get_document_in_workspace(db, workspace.id, document_id)
        db.delete(document)
        db.commit()
        return {"message": "document deleted successfully"}

    def _get_document_in_workspace(self, db: Session, workspace_id: int, document_id: int) -> Document:
        document = (
            db.query(Document)
            .filter(Document.id == document_id, Document.workspace_id == workspace_id)
            .first()
        )
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="document not found",
            )
        return document