import os
import secrets
import smtplib
import time
from email.message import EmailMessage
from fastapi import APIRouter, Form, Depends, Response, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.controllers.auth_controller import AuthController
from src.main.repositories.user_repository import UserRepository
from src.main.services.security_service import hash_password

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="templates")
reset_tokens = {}


def send_reset_email(to_email: str, reset_link: str):
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM") or smtp_user

    if not smtp_host or not smtp_user or not smtp_password or not smtp_from:
        print(f"[PASSWORD RESET] Link đặt lại mật khẩu: {reset_link}")
        return False

    message = EmailMessage()
    message["Subject"] = "Đặt lại mật khẩu Adaptive Learning AI"
    message["From"] = smtp_from
    message["To"] = to_email
    message.set_content(
        "Bạn vừa yêu cầu đặt lại mật khẩu.\n\n"
        f"Nhấn vào link sau để đặt mật khẩu mới:\n{reset_link}\n\n"
        "Link có hiệu lực trong 30 phút."
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(message)
    return True

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
    
    # Xác định url chuyển hướng dựa trên vai trò
    redirect_url = "/home"
    if user.role == "teacher":
        redirect_url = "/teacher/dashboard"
    elif user.role == "admin":
        redirect_url = "/admin/users"
        
    # Tạo RedirectResponse đến trang tương ứng
    redirect_response = RedirectResponse(url=redirect_url, status_code=303)
    
    # Lưu phiên đăng nhập vào Cookie của response chuyển hướng với path="/"
    redirect_response.set_cookie(key="user_id", value=str(user.maSV), httponly=True, path="/")
    
    return redirect_response


@router.get("/forgot-password")
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@router.post("/forgot-password")
async def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.find_by_email(email.strip().lower())

    if user:
        token = secrets.token_urlsafe(32)
        reset_tokens[token] = {
            "user_id": user.maSV,
            "expires_at": time.time() + 30 * 60
        }
        reset_link = str(request.url_for("reset_password_page")) + f"?token={token}"
        send_reset_email(user.email, reset_link)

    return templates.TemplateResponse(
        "forgot_password.html",
        {
            "request": request,
            "message": "Nếu email tồn tại trong hệ thống, link đặt lại mật khẩu đã được gửi."
        }
    )


@router.get("/reset-password")
async def reset_password_page(request: Request, token: str):
    token_data = reset_tokens.get(token)
    if not token_data or token_data["expires_at"] < time.time():
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": "", "error": "Link đặt lại mật khẩu đã hết hạn hoặc không hợp lệ."}
        )

    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})


@router.post("/reset-password")
async def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    token_data = reset_tokens.get(token)
    if not token_data or token_data["expires_at"] < time.time():
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": "", "error": "Link đặt lại mật khẩu đã hết hạn hoặc không hợp lệ."}
        )

    if password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": "Mật khẩu xác nhận không khớp."}
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": "Mật khẩu cần có ít nhất 6 ký tự."}
        )

    user_repo = UserRepository(db)
    user = user_repo.find_by_id(token_data["user_id"])
    if not user:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": "", "error": "Không tìm thấy tài khoản."}
        )

    user.matKhau = hash_password(password)
    db.commit()
    reset_tokens.pop(token, None)

    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": "", "message": "Đã đặt lại mật khẩu. Bạn có thể đăng nhập bằng mật khẩu mới."}
    )
