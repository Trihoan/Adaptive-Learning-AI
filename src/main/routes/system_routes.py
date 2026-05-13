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
from google.genai import types
from src.main.config.settings import Config
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY") or Config.GOOGLE_API_KEY

# Khởi tạo Client với bản v1beta1 theo đúng kỹ thuật trong video
if api_key:
    try:
        client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1beta1'}
        )
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
    
    user = None
    if user_id:
        user_repo = UserRepository(db)
        user = user_repo.find_by_id(user_id)
    
    from src.main.domain.models import Exam, StudyResult, Question, Chapter

    # Lấy thông tin chương yếu
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

    # 1. THỬ DÙNG GEMINI (PHIÊN BẢN HUẤN LUYỆN CHUYÊN SÂU)
    if client:
        try:
            # BỘ QUY TẮC "HUẤN LUYỆN" CHO AI (PERSONA)
            ai_identity = """
            BẠN LÀ: 'ALAS Assistant' - Hệ thống Cố vấn học tập thông minh dựa trên AI của dự án Adaptive Learning.
            NHIỆM VỤ: Phân tích kết quả học tập và đưa ra lộ trình 'về đích' cá nhân hóa cho từng sinh viên.
            PHONG CÁCH: Thân thiện, khích lệ nhưng chuyên nghiệp. Xưng hô: 'Mình' - 'Bạn' hoặc gọi tên sinh viên.
            KIẾN THỨC CHUYÊN MÔN: 
            - Hiểu rõ môn CNXHKH (Chủ nghĩa xã hội khoa học) và TTHCM (Tư tưởng Hồ Chí Minh).
            - Biết cách tư vấn phương pháp học trắc nghiệm hiệu quả.
            """

            student_context = (
                f"SINH VIÊN ĐANG CHAT: {user.hoTen if user else 'Bạn'}.\n"
                f"DỮ LIỆU THỰC TẾ: Chương đang học yếu nhất: {', '.join(weak_chapters) if weak_chapters else 'Chưa có dữ liệu bài làm'}.\n"
            )

            rules = """
            QUY TẮC PHẢN HỒI:
            1. Nếu sinh viên hỏi 'Bạn là ai?', hãy tự hào giới thiệu mình là trợ lý AI của dự án ALAS.
            2. Nếu sinh viên hỏi về lộ trình, hãy ƯU TIÊN nhắc đến các chương học yếu ở trên.
            3. Luôn kết thúc bằng 1 lời chúc hoặc 1 câu truyền cảm hứng học tập.
            4. Trả lời ngắn gọn, không quá 4 câu.
            """

            full_prompt = f"{ai_identity}\n{student_context}\n{rules}\n\nNgười dùng hỏi: {user_message}"

            #khi có gemini mới 
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            if response and response.text:
                return {"reply": response.text.strip()}
        except Exception as e:
            print(f"Gemini SDK Error: {str(e)}")

    # 2. CHẾ ĐỘ DỰ PHÒNG (NẾU AI LỖI - ĐỐI ĐÁP TỰ NHIÊN HƠN)
    # Xử lý các câu hỏi về danh tính Chatbot
    identity_keywords = ["là ai", "tên gì", "chatbox", "chatbot", "alas"]
    if any(k in user_message_lower for k in identity_keywords):
        return {"reply": f"Chào {user.hoTen if user else 'bạn'}, mình là trợ lý AI của dự án ALAS. Mình ở đây để giúp bạn phân tích kết quả làm bài và chỉ ra những phần kiến thức bạn cần cải thiện. Rất vui được đồng hành cùng bạn!"}

    # Xử lý hỏi lộ trình/chương yếu
    advice_keywords = ["học gì", "lộ trình", "tư vấn", "dạo này", "hỏi", "giúp", "chương", "yếu", "kết quả", "ôn tập"]
    if any(k in user_message_lower for k in advice_keywords):
        if weak_chapters:
            msg = f"Chào {user.hoTen if user else 'bạn'}, qua phân tích các bài làm gần đây, mình thấy bạn nên tập trung ôn lại: **{', '.join(weak_chapters)}**. Đây là những phần bạn hay làm sai nhất. Cố gắng lên, mình tin bạn sẽ làm tốt hơn ở lần tới!"
        else:
            msg = f"Chào {user.hoTen if user else 'bạn'}, hiện tại mình chưa thấy dữ liệu bài làm của bạn. Bạn hãy thử làm một vài đề để mình có dữ liệu tư vấn nhé!"
        return {"reply": msg}

    return {"reply": f"Chào {user.hoTen if user else 'bạn'}! Mình đã nhận được tin nhắn. Bạn có muốn mình tư vấn về lộ trình ôn tập hay xem lại những chương bạn đang gặp khó khăn không?"}
