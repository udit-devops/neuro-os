from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.services.document_service import DocumentService

router = APIRouter(
    prefix="/workspaces",
    tags=["Documents"]
)

document_service = DocumentService()

@router.post("/{workspace_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    workspace_id: int,
    data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.create_document(db, current_user.id, workspace_id, data)

@router.get("/{workspace_id}/documents", response_model=list[DocumentResponse])
def get_documents(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
):
    return document_service.get_documents(db, current_user.id, workspace_id, skip, limit)

@router.get("/{workspace_id}/documents/{document_id}", response_model=DocumentResponse)
def get_document_by_id(
    workspace_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.get_document_by_id(db, current_user.id, workspace_id, document_id)

@router.put("/{workspace_id}/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    workspace_id: int,
    document_id: int,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.update_document(db, current_user.id, workspace_id, document_id, data)

@router.delete("/{workspace_id}/documents/{document_id}", response_model=dict)
def delete_document(
    workspace_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return document_service.delete_document(db, current_user.id, workspace_id, document_id)