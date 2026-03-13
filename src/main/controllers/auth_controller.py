from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.services.auth_service import AuthService

router = APIRouter()

@router.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Khởi tạo các lớp
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    user = auth_service.authenticate_user(username, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
        
    return {"message": "Đăng nhập thành công", "user": user.username}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    
    success = auth_service.remove_user(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng để xóa")
        
    return {"message": f"Đã xóa người dùng có ID {user_id} thành công"}