from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class FileBase(BaseModel):
    filename: str
    file_url: str
    content_type: Optional[str] = None
    file_extension: Optional[str] = None
    size: Optional[float] = None

class FileCreate(FileBase):
    pass

class File(FileBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class FileList(BaseModel):
    page: int
    limit: int
    total: int
    items: List[File] 