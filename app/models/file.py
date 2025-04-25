from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FileBase(BaseModel):
    name: str
    storage_path: str
    folder_id: Optional[UUID] = None


class FileCreate(FileBase):
    pass


class FileUpdate(FileBase):
    name: Optional[str] = None
    storage_path: Optional[str] = None
    folder_id: Optional[UUID] = None


class FileInDB(FileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileModel(FileInDB):
    pass
