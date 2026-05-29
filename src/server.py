from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import asyncio
from src.main.ai.training.ai_trainer import train_and_evaluate

from src.main.routes import (
    auth_routes, 
    user_routes, 
    view_routes, 
    system_routes, 
    quiz_routes,
    course_routes,
    admin_routes,
    teacher_routes
)

app = FastAPI(title="Adaptive Learning AI API")

# --- TỰ ĐỘNG HUẤN LUYỆN AI MỖI 24 GIỜ ---
async def scheduled_ai_training():
    while True:
        try:
            print("[AI Auto-Trainer] Bắt đầu chu kỳ huấn luyện định kỳ...")
            train_and_evaluate("SYSTEM_AUTO")
            print("[AI Auto-Trainer] Đã cập nhật mô hình AI thành công.")
        except Exception as e:
            print(f"AI Auto-Trainer] Lỗi khi huấn luyện tự động: {e}")
        
        # Chờ 24 giờ cho lần huấn luyện tiếp theo
        await asyncio.sleep(24 * 3600)

@app.on_event("startup")
async def startup_event():
    # Chạy huấn luyện lần đầu sau khi khởi động server 10 giây
    async def delayed_start():
        await asyncio.sleep(10)
        asyncio.create_task(scheduled_ai_training())
    
    asyncio.create_task(delayed_start())

# Mount thư mục static để phục vụ CSS, hình ảnh...
app.mount("/static", StaticFiles(directory="static"), name="static")

# 1. Các Router phục vụ Giao diện (HTML) và Xác thực từ Form
app.include_router(view_routes.router)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router) 
app.include_router(teacher_routes.router) 

# 2. Các Router phục vụ Logic và API (đặt tiền tố /api cho gọn)
app.include_router(quiz_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")
app.include_router(system_routes.router, prefix="/api", tags=["System"])
app.include_router(course_routes.router, prefix="/api", tags=["Course"])