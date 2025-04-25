from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class FolderBase(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class FolderCreate(FolderBase):
    pass


class FolderUpdate(FolderBase):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


class FolderInDB(FolderBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    subfolders: List["FolderInDB"] = []

    class Config:
        from_attributes = True


class Folder(FolderInDB):
    pass
