from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Schema for Employee
class EmployeeBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[datetime] = None

class EmployeeCreate(EmployeeBase):
    pass

class Employee(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for User
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    employee: Employee

    class Config:
        from_attributes = True

# Schema for Tokens
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

# Schema for User Session
class UserSessionBase(BaseModel):
    device_info: Optional[str] = None
    ip_address: Optional[str] = None

class UserSessionCreate(UserSessionBase):
    user_id: int
    session_token: str
    expires_at: datetime

class UserSession(UserSessionBase):
    id: int
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True

class UserWithRoles(User):
    roles: List[str] = []

    class Config:
        from_attributes = True 