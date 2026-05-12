from fastapi import APIRouter, Depends, Cookie
from sqlalchemy.orm import Session
from sqlalchemy import text, func
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
        return {"status": "online", "database": "Connected Successfully!"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

from google import genai
from src.main.config.settings import Config
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or Config.GOOGLE_API_KEY

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception:
        client = None
else:
    client = None

@router.post("/chat")
async def chat_with_ai(
    message_data: Dict[str, str],
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    user_message = message_data.get("message", "")
    user_message_lower = user_message.lower()
    
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    from src.main.domain.models import Exam, StudyResult, Question, Chapter

    exam_count = db.query(Exam).filter(Exam.maSV == user_id).count() if user_id else 0
    weak_chapters = []
    if user_id:
        try:
            results = db.query(Chapter.tenChuong, func.count(StudyResult.maKetQua))\
                .select_from(Chapter)\
                .join(Question, Chapter.maChuong == Question.maChuong)\
                .join(StudyResult, Question.maCauHoi == StudyResult.maCauHoi)\
                .filter(StudyResult.maSV == user_id, StudyResult.trangThai == False)\
                .group_by(Chapter.maChuong, Chapter.tenChuong)\
                .order_by(func.count(StudyResult.maKetQua).desc()).limit(2).all()
            weak_chapters = [r[0] for r in results]
        except Exception: pass

    # 1. THỬ DÙNG GEMINI
    if client:
        try:
            # Gửi kèm ngữ cảnh cực kỳ chi tiết cho AI
            system_instruction = f"""
            Bạn là 'AI Cố vấn học tập thông minh'.
            Thông tin người học: {user.hoTen if user else 'Người học'}.
            Điểm TB: {user.avg_score if user else 'Chưa có'}.
            Số bài đã làm: {exam_count}.
            Các chương học yếu (cần ôn tập gấp): {', '.join(weak_chapters) if weak_chapters else 'Chưa xác định'}.
            
            Quy tắc:
            - Luôn xưng hô thân thiện, gọi tên người học.
            - Trả lời bằng tiếng Việt tự nhiên như người thật.
            - Không trả lời quá dài (tối đa 4 câu).
            - Nếu họ hỏi về lộ trình, hãy dùng dữ liệu 'Chương học yếu' ở trên để tư vấn cụ thể.
            """
            
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=user_message,
                config={'system_instruction': system_instruction}
            )
            
            if response and response.text:
                return {"reply": f"{response.text.strip()}\n\n(🤖 Trả lời bởi Gemini AI)"}
        except Exception as e:
            print(f"🔥 LỖI GEMINI: {str(e)}")

    # 2. CHẾ ĐỘ DỰ PHÒNG (NẾU AI LỖI)
    if any(k in user_message_lower for k in ["học gì", "lộ trình", "tư vấn", "dạo này"]):
        if weak_chapters:
            msg = f"Chào {user.hoTen if user else 'bạn'}, dựa trên dữ liệu thật, bạn đang gặp khó ở: **{', '.join(weak_chapters)}**. Bạn hãy ôn lại các chương này trước khi làm đề mới nhé!"
        else:
            msg = "Chào bạn, hiện tại tôi chưa thấy dữ liệu bài làm của bạn. Bạn hãy thử làm một vài bài kiểm tra để tôi có thể tư vấn lộ trình nhé!"
        return {"reply": f"{msg}\n\n(📝 Chế độ dự phòng)"}

    return {"reply": "Tôi đã nhận được tin nhắn của bạn. Bạn có muốn biết mình nên tập trung ôn tập chương nào không?\n\n(📝 Chế độ dự phòng)"}
