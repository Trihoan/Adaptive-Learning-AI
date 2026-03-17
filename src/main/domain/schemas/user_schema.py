from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    
class UserRegister(BaseModel):
    username: str
    password: str
    confirm_password: str
    fullname: str
    student_id: str