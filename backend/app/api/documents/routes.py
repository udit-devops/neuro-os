from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.users import User
from app.rag.errors import RetryableError
from app.rag.rag_service import RAGService, RAGUnavailableError
from app.schemas.document import DocumentUpdate, DocumentResponse
from app.schemas.rag import RAGQueryRequest, RAGQueryResponse
from app.services.document_service import DocumentService
from app.services.file_validation import FileValidator
from app.services.ingestion_queue import enqueue_document
from app.services.storage_service import generate_storage_key, get_storage_service

router = APIRouter(
    prefix="/workspaces",
    tags=["Documents"],
)

document_service = DocumentService()
storage_service = get_storage_service()


def _require_owned_workspace(owner_id: int, workspace_id: int, db: Session) -> None:
    document_service.workspace_service.get_workspace_by_id(db, owner_id, workspace_id)


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
    document = document_service.get_document_by_id(db, current_user.id, workspace_id, document_id)
    result = document_service.delete_document(db, current_user.id, workspace_id, document_id)
    try:
        storage_service.delete(document.file_path)
    except Exception:
        pass
    return result


@router.post("/{workspace_id}/query", response_model=RAGQueryResponse)
def query_workspace(
    workspace_id: int,
    data: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_owned_workspace(current_user.id, workspace_id, db)
    try:
        answer = RAGService().answer(db, workspace_id, data.question, data.top_k)
    except (RAGUnavailableError, RetryableError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return answer.to_dict()


@router.post("/{workspace_id}/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: int,
    file: UploadFile,
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = await file.read()
    safe_name, file_type = FileValidator.validate(file.filename or "", len(data))
    storage_key = generate_storage_key(workspace_id, safe_name)
    storage_service.save_bytes(storage_key, data)

    document = document_service.upload_document(
        db,
        current_user.id,
        workspace_id,
        title=title or safe_name,
        original_filename=safe_name,
        storage_key=storage_key,
        file_size=len(data),
        file_type=file_type,
    )
    enqueue_document(document.id)
    return document