from fastapi import APIRouter, Form, Depends, Response
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.controllers.auth_controller import AuthController

router = APIRouter(tags=["Auth"])

@router.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    fullname: str = Form(None),    
    student_id: str = Form(...),  
    db: Session = Depends(get_db)
):
    controller = AuthController(db)
    return await controller.register(username, password, confirm_password, fullname, student_id)

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    controller = AuthController(db)
    user = await controller.login(username, password)
    
    # Lưu phiên đăng nhập
    response.set_cookie(key="user_id", value=str(user.id), httponly=True)
    return {"status": "success", "message": f"Chào mừng {user.username}!", "role": user.role}