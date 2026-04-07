from fastapi import APIRouter, Depends, HTTPException, Form, Cookie
from fastapi.responses import RedirectResponse
from typing import Optional
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.services.auth_service import AuthService

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,     # Đổi từ int sang str cho khớp maSV
    admin_id: str,    # Đổi từ int sang str
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)

    # Tìm tài khoản admin đang thực hiện lệnh
    current_admin = user_repo.find_by_id(admin_id)

    if not current_admin:
        raise HTTPException(status_code=401, detail="Tài khoản thực hiện không tồn tại")

    success, message = auth_service.remove_user(user_id, current_admin)

    if not success:
        status_code = 403 if "quyền" in message else 404
        raise HTTPException(status_code=status_code, detail=message)

    return {"status": "success", "message": message}

@router.post("/users/update")
async def update_user(
    maSV: str = Form(...),
    hoTen: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    admin_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    
    # Kiểm tra quyền admin
    admin = user_repo.find_by_id(admin_id)
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Không có quyền thực hiện")
        
    user = user_repo.find_by_id(maSV)
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")
        
    user.hoTen = hoTen
    user.email = email
    user.role = role
    
    db.commit()
    return RedirectResponse(url="/admin/users", status_code=303)