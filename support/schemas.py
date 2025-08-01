from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List, Dict, Union
from datetime import datetime

class SupportBase(BaseModel):
    title: str
    content: str
    email: EmailStr  # Email của người gửi support
    fullname: Optional[str] = None  # Tên đầy đủ của người gửi
    support_type: str = "general"  # general, recruitment, technical
    source_type: Optional[str] = None  # story, user, etc.
    source_id: Optional[int] = None
    file_ids: Optional[List[int]] = None  # Có thể là string "1,2,3" hoặc list [1,2,3]

class SupportCreate(BaseModel):
    title: str
    content: str
    email: EmailStr  # Email của người gửi support
    fullname: Optional[str] = None  # Tên đầy đủ của người gửi
    support_type: str = "general"  # general, recruitment, technical
    source_type: Optional[str] = None  # story, user, etc.
    source_id: Optional[int] = None
    file_ids: Optional[List[int]] = None  # Có thể là string "1,2,3" hoặc list [1,2,3]

class SupportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    email: Optional[EmailStr] = None
    fullname: Optional[str] = None
    support_type: Optional[str] = None
    source_type: Optional[str] = None
    source_id: Optional[int] = None
    file_ids: Optional[List[int]] = None
    status: Optional[str] = None

class SupportStatusUpdate(BaseModel):
    status: str  # pending, in_progress, resolved, rejected
    note: Optional[str] = None  # Ghi chú khi thay đổi status

class Support(SupportBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    files: Optional[List[Dict[str, str]]] = None

    model_config = ConfigDict(from_attributes=True)

class SupportPage(BaseModel):
    page: int
    limit: int
    total: int
    items: List[Support] 

class SupportResponse(BaseModel):
    id: int
    title: str
    content: str
    email: EmailStr
    fullname: Optional[str] = None
    support_type: str
    source_type: Optional[str] = None
    source_id: Optional[int] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    files: Optional[List[Dict[str, Union[int, str]]]] = None  # ✅ array obj như yêu cầu

    class Config:
        orm_mode = True