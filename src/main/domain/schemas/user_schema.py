from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    maSV: str
    tenDangNhap: str
    email: Optional[str]
    role: str
    
    class Config:
        from_attributes = True
    
class UserRegister(BaseModel):
    username: str
    password: str
    confirm_password: str
    fullname: str
    student_id: str