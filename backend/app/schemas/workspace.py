from pydantic import BaseModel, Field, field_validator
from datetime import datetime as DateTime

class WorkspaceCreate(BaseModel):
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=5000)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name cannot be empty")
        return value

class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=5000)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("name cannot be empty")
        return value

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
    document_count:int = 0

## workspace backend done