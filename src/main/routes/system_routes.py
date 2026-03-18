from fastapi import APIRouter, Depends, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict

from src.main.database import get_db
from src.main.services.ai_service import AIService
from src.main.repositories.user_repository import UserRepository

router = APIRouter()
ai_service = AIService()

@router.get("/health")
async def system_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "online",
            "database": "Connected Successfully!"
        }
    except Exception as e:
        return {"status": "error", "database": str(e)}

@router.post("/chat")
async def chat_with_ai(
    message_data: Dict[str, str],
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    user_message = message_data.get("message", "").lower()

    # 1. Lấy thông tin người dùng để AI phân tích
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id) if user_id else None

    # 2. Logic trả lời đơn giản (có thể mở rộng sau này)
    if "học gì" in user_message or "chương nào" in user_message or "lộ trình" in user_message:
        # Gọi AI Service để lấy lời khuyên thực tế
        # Nếu chưa có điểm (user mới), giả lập điểm trung bình
        math = user.avg_score if user and user.avg_score > 0 else 5.0
        prog = user.avg_score if user and user.avg_score > 0 else 5.0
        hours = user.total_time if user and user.total_time > 0 else 5.0

        rec = ai_service.get_recommendation(math, prog, hours, 0.7)

        response = f"Chào bạn! Dựa trên phân tích từ AI, trạng thái của bạn là: **{rec['status']}**. "
        response += f"Tôi khuyên bạn nên tập trung vào: **{rec['next_step']}**. "
        response += "Ngoài ra, bạn nên: " + ", ".join(rec['action']) + "."

        return {"reply": response}

    elif "chào" in user_message or "hi" in user_message:
        name = user.hoTen if user and user.hoTen else "bạn"
        return {"reply": f"Xin chào {name}! Tôi là AI cố vấn học tập. Bạn cần tôi tư vấn về lộ trình học hay chương tiếp theo không?"}

    else:
        return {"reply": "Tôi chưa hiểu ý bạn lắm. Bạn có thể hỏi về 'Lộ trình học' hoặc 'Tôi nên học chương gì?' để AI tư vấn nhé!"}