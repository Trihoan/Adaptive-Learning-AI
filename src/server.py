from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.main.routes import (
    auth_routes, 
    user_routes, 
    view_routes, 
    system_routes, 
    quiz_routes,
    course_routes
)

app = FastAPI(title="Adaptive Learning AI API")

# Mount thư mục static để phục vụ CSS, hình ảnh...
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. Các Router phục vụ Giao diện (HTML) và Xác thực từ Form
app.include_router(view_routes.router)
app.include_router(auth_routes.router)

# 2. Các Router phục vụ Logic và API (đặt tiền tố /api cho gọn)
app.include_router(quiz_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(system_routes.router, prefix="/api", tags=["System"])
app.include_router(course_routes.router, prefix="/api", tags=["Course"])