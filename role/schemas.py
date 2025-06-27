from pydantic import BaseModel
from typing import Optional, List

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleOut(RoleBase):
    id: int
    class Config:
        from_attributes = True

class UserRoleBase(BaseModel):
    user_id: int
    role_id: int

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleOut(UserRoleBase):
    id: int
    class Config:
        from_attributes = True

# Danh sách quyền mẫu
DEFAULT_ROLES = [
    {"name": "employee_manager", "description": "Quản lý nhân viên"},
    {"name": "customer_manager", "description": "Quản lý khách hàng"},
    {"name": "story_manager", "description": "Quản lý story"},
    {"name": "admin", "description": "Quản trị hệ thống"}
] 