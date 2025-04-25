from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class FileBase(BaseModel):
    name: str
    folder_id: Optional[UUID] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get("folder_id"):
            data["folder_id"] = str(data["folder_id"])
        return data


class FileCreate(FileBase):
    storage_path: str


class FileUpdate(FileBase):
    name: Optional[str] = None
    folder_id: Optional[UUID] = None


class FileInDB(FileBase):
    id: UUID
    user_id: UUID
    storage_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileModel(FileInDB):
    pass
