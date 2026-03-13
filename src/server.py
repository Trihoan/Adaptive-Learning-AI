from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session 
from sqlalchemy import text

# Import từ project của bạn
from src.main.config.settings import Config
from src.main.database import get_db 
from src.main.repositories.user_repository import UserRepository
from src.main.domain.models import User # Đảm bảo đã import Model User

app = FastAPI(title="Adaptive Learning AI API")

# 1. Cấu hình Templates và Static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- ROUTES HIỂN THỊ GIAO DIỆN (GET) ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Trang đăng nhập chính"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Trang đăng ký tài khoản"""
    return templates.TemplateResponse("register.html", {"request": request})

# --- ROUTES XỬ LÝ LOGIC (POST / DELETE) ---

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Xử lý đăng ký và lưu vào MySQL"""
    user_repo = UserRepository(db)
    
    # Kiểm tra xem user đã tồn tại chưa
    existing_user = user_repo.find_by_username(username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
    
    # Tạo object User mới (nhớ hash password nếu làm dự án thật nhé)
    new_user = User(username=username, password=password)
    user_repo.save_user(new_user)
    
    return {"status": "success", "message": "Đăng ký thành công!", "user": username}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """Kiểm tra đăng nhập từ database"""
    user_repo = UserRepository(db)
    user = user_repo.find_by_username(username)
    
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
        
    return {"status": "success", "message": f"Chào mừng {username}!"}

@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Xóa người dùng theo ID"""
    user_repo = UserRepository(db)
    success = user_repo.delete_user(user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy User để xóa")
    
    return {"status": "success", "message": f"Đã xóa User có ID: {user_id}"}

# --- HỆ THỐNG ---

@app.get("/health")
async def system_health_check(db: Session = Depends(get_db)):
    """Đổi tên hàm thành system_health_check để tránh lỗi Duplicate ID"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "online",
            "project": "Adaptive Learning AI",
            "database": "Connected Successfully!"
        }
    except Exception as e:
        return {"status": "error", "database": str(e)}