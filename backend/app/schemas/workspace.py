from pydantic import BaseModel
from datetime import datetime as DateTime

class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None

class WorkspaceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class WorkspaceResponse(BaseModel):
    model_config ={
        "from_attributes": True
    }
    id:int
    name:str
    description:str | None = None
    updated_at:DateTime
    created_at:DateTime
    owner_id:int

