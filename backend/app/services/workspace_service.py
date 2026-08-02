from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:

    def create_workspace(self, db: Session, owner_id: int, data: WorkspaceCreate) -> Workspace:
        workspace = Workspace(name=data.name, description=data.description, owner_id=owner_id)
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace

    def get_workspaces(self, db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[Workspace]:
        return (
            db.query(Workspace)
            .filter(Workspace.owner_id == owner_id)
            .order_by(Workspace.id.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_workspace_by_id(self, db: Session, owner_id: int, workspace_id: int) -> Workspace:
        return self._get_owned_workspace(db, owner_id, workspace_id)

    def update_workspace(self, db: Session, owner_id: int, workspace_id: int, data: WorkspaceUpdate) -> Workspace:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(workspace, field, value)
        db.commit()
        db.refresh(workspace)
        return workspace

    def delete_workspace(self, db: Session, owner_id: int, workspace_id: int) -> dict:
        workspace = self._get_owned_workspace(db, owner_id, workspace_id)
        db.delete(workspace)
        db.commit()
        return {"message": "workspace deleted successfully"}

    def _get_owned_workspace(self, db: Session, owner_id: int, workspace_id: int) -> Workspace:
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not workspace or workspace.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="workspace not found",
            )
        return workspace
