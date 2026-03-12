from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.main.config.settings import Config

app = FastAPI(title="Adaptive Learning AI API")

# Cấu hình để FastAPI biết tìm file HTML ở đâu
# Giả sử thư mục templates của bạn nằm ở thư mục gốc của project
templates = Jinja2Templates(directory="templates")
    
# Nếu bạn có thư mục static cho CSS/JS (tùy chọn)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Hiển thị trang đăng nhập"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Hiển thị trang đăng ký"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...)):
    """Xử lý dữ liệu đăng ký từ form"""
    # Sau này bạn có thể gọi User Repository ở đây để lưu vào Database
    # db_uri = Config.SQLALCHEMY_DATABASE_URI
    return {"message": "Register success", "user": username}

@app.get("/health")
async def health_check():
    """Kiểm tra trạng thái hệ thống và kết nối DB"""
    return {
        "status": "ready",
        "project": "Adaptive Learning AI",
        "database_configured": Config.SQLALCHEMY_DATABASE_URI is not None
    }