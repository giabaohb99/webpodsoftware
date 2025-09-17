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
    url: str

    class Config:
        orm_mode = True

class FileList(BaseModel):
    page: int
    limit: int
    total: int
    items: List[File]

# Thumbnail schemas
class ThumbnailBase(BaseModel):
    original_file_id: int
    width: int
    height: int
    quality: int = 80
    format: str = "webp"

class ThumbnailCreate(ThumbnailBase):
    file_url: str
    file_size: Optional[float] = None

class Thumbnail(ThumbnailBase):
    id: int
    file_url: str
    file_size: Optional[float] = None
    created_at: datetime
    last_accessed: Optional[datetime] = None
    access_count: int = 0

    class Config:
        orm_mode = True

class ThumbnailResponse(BaseModel):
    id: int
    width: int
    height: int
    format: str
    quality: int
    file_url: str
    file_size: Optional[float] = None
    created_at: datetime

    class Config:
        orm_mode = True

class ThumbnailUrl(BaseModel):
    """Simple thumbnail URL info for file responses"""
    width: int
    height: int
    url: str

class FileWithThumbnails(BaseModel):
    """File response with thumbnail URLs included"""
    id: int
    filename: str
    file_url: str
    content_type: Optional[str] = None
    file_extension: Optional[str] = None
    size: Optional[float] = None
    created_at: datetime
    url: str
    thumbnails: Optional[List[ThumbnailUrl]] = None

    class Config:
        orm_mode = True 