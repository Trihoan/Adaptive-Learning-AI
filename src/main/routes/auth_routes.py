from fastapi import APIRouter, Form, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.controllers.auth_controller import AuthController

router = APIRouter(tags=["Auth"])

@router.post("/register")
async def register(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    fullname: str = Form(None),    
    student_id: str = Form(...),  
    db: Session = Depends(get_db)
):
    controller = AuthController(db)
    # 1. Đăng ký tài khoản mới
    user_data = await controller.register(username, password, confirm_password, fullname, student_id)
    
    # 2. Sau khi đăng ký thành công, thực hiện đăng nhập luôn
    user = await controller.login(username, password)
    
    # 3. Chuyển hướng thẳng đến trang home
    redirect_response = RedirectResponse(url="/home", status_code=303)
    redirect_response.set_cookie(key="user_id", value=str(user.maSV), httponly=True, path="/")
    
    return redirect_response

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    controller = AuthController(db)
    user = await controller.login(username, password)
    
    # Tạo RedirectResponse đến trang home
    redirect_response = RedirectResponse(url="/home", status_code=303)
    
    # Lưu phiên đăng nhập vào Cookie của response chuyển hướng với path="/"
    redirect_response.set_cookie(key="user_id", value=str(user.maSV), httponly=True, path="/")
    
    return redirect_response