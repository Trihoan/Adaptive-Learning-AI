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

    # 2. Logic trả lời nâng cao
    if any(k in user_message for k in ["học gì", "chương nào", "lộ trình", "tư vấn", "giúp"]):
        # Kiểm tra xem user đã làm bài nào chưa
        from src.main.domain.models import Exam
        exam_count = db.query(Exam).filter(Exam.maSV == user_id).count() if user_id else 0

        if exam_count == 0:
            # Gọi AI Service với tham số mặc định cho người mới
            rec = ai_service.get_recommendation(None, None, 0, 0)
            return {"reply": rec['friendly_msg']}

        # Lấy điểm thực tế để AI phân tích
        math = user.avg_score if user and user.avg_score > 0 else 5.0
        prog = user.avg_score if user and user.avg_score > 0 else 5.0
        hours = user.total_time if user and user.total_time > 0 else 5.0

        rec = ai_service.get_recommendation(math, prog, hours, 0.7)
        
       
        response = f"{rec['friendly_msg']}\n\n"
        response += f"📌 **Trạng thái hiện tại:** {rec['status']}\n"
        response += f"🎯 **Lời khuyên:** {rec['next_step']}\n"
        response += f"✅ **Hành động ngay:** " + " & ".join(rec['action'])

        return {"reply": response}

    elif "chào" in user_message or "hi" in user_message:
        name = user.hoTen if user and user.hoTen else "bạn"
        return {"reply": f"Xin chào {name}! Tôi là AI cố vấn học tập. Bạn cần tôi tư vấn về lộ trình học hay chương tiếp theo không?"}

    else:
        return {"reply": "Tôi chưa hiểu ý bạn lắm. Bạn có thể hỏi về 'Lộ trình học' hoặc 'Tôi nên học chương gì?' để AI tư vấn nhé!"}