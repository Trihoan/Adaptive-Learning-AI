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
    
    from src.main.domain.models import Exam, StudyResult, Question, Chapter, HanhViHocTap, Quiz

    # 1. LẤY NGỮ CẢNH HỌC TẬP CHI TIẾT
    weak_chapters = []
    recent_results = []
    competency_group = "Chưa xác định"
    
    if user_id:
        try:
            # Lấy 2 chương yếu nhất dựa trên số câu sai
            results = db.query(Chapter.tenChuong, func.count(StudyResult.maKetQua))\
                .select_from(Chapter)\
                .join(Question, (Chapter.maChuong == Question.maChuong))\
                .join(StudyResult, Question.maCauHoi == StudyResult.maCauHoi)\
                .filter(StudyResult.maSV == user_id, StudyResult.trangThai == False)\
                .group_by(Chapter.maChuong, Chapter.tenChuong)\
                .order_by(func.count(StudyResult.maKetQua).desc()).limit(2).all()
            weak_chapters = [r[0] for r in results]

            # Lấy 3 bài làm gần nhất (bao gồm cả đề thi và chương)
            exams = db.query(Exam).filter(Exam.maSV == user_id).order_by(Exam.thoiGianKetThuc.desc()).limit(3).all()
            for ex in exams:
                target_name = ""
                if ex.maDeThi:
                    qz = db.query(Quiz).filter(Quiz.maDeThi == ex.maDeThi).first()
                    target_name = f"Đề: {qz.tenDeThi}" if qz else "Đề ôn tập"
                elif ex.maChuong:
                    ch = db.query(Chapter).filter(Chapter.maChuong == ex.maChuong).first()
                    target_name = f"Chương: {ch.tenChuong}" if ch else "Bài ôn tập"
                
                recent_results.append(f"{target_name} ({ex.diem}/10)")

            # Lấy nhóm năng lực từ AI Engine
            behavior = db.query(HanhViHocTap).filter(HanhViHocTap.maSV == user_id).first()
            if behavior and behavior.nangLuc:
                competency_group = behavior.nangLuc
        except Exception as e:
            print(f"Error fetching student context: {e}")

    # 2. XÂY DỰNG PROMPT CHUYÊN SÂU
    if client:
        try:
            ai_identity = f"""
            BẠN LÀ: 'ALAS Assistant' - Gia sư AI cá nhân hóa.
            NGỮ CẢNH SINH VIÊN:
            - Tên: {user.hoTen if user else 'Người dùng'}.
            - Nhóm năng lực (AI phân loại): {competency_group}.
            - Điểm trung bình hệ thống: {user.avg_score if user else 0}/10.
            - Tổng thời gian học: {user.total_time if user else 0} giờ.
            - Các bài làm gần đây: {', '.join(recent_results) if recent_results else 'Chưa có'}.
            - Lỗ hổng kiến thức (Chương yếu nhất): {', '.join(weak_chapters) if weak_chapters else 'Chưa xác định'}.

            NHIỆM VỤ: 
            - Phân tích dữ liệu trên để đưa ra lời khuyên 'thấu hiểu hoàn cảnh'.
            - Nếu sinh viên chào hỏi hoặc hỏi dạo này thế nào, hãy chủ động nhắc đến kết quả gần đây và khuyên họ tập trung vào chương yếu.
            - Nếu sinh viên hỏi kiến thức, hãy giải thích dễ hiểu và liên hệ với các chương họ đã học.

            PHONG CÁCH: Thân thiện như một người bạn đồng hành (xưng 'Mình' - 'Bạn' hoặc gọi tên). Khích lệ sự tiến bộ.
            QUY TẮC: Trả lời ngắn gọn (3-4 câu), không dùng ngôn ngữ máy móc.
            """

            full_prompt = f"{ai_identity}\n\nNgười dùng hỏi: {user_message}"

            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    max_output_tokens=600
                )
            )
            
            if response and response.text:
                return {"reply": response.text.strip()}
        except Exception as e:
            print(f"Gemini SDK Error: {str(e)}")

    # 3. CHẾ ĐỘ DỰ PHÒNG (NẾU AI LỖI HOẶC CHƯA CẤU HÌNH API KEY)
    if not client:
        print("⚠️ Cảnh báo: GOOGLE_API_KEY chưa được cấu hình. AI đang chạy ở chế độ dự phòng hạn chế.")
    
    # Xử lý hỏi lộ trình/chương yếu
    advice_keywords = ["học gì", "lộ trình", "tư vấn", "dạo này", "hỏi", "giúp", "chương", "yếu", "kết quả", "ôn tập", "thế nào"]
    if any(k in user_message_lower for k in advice_keywords):
        if recent_results:
            msg = f"Chào {user.hoTen if user else 'bạn'}, qua phân tích {len(recent_results)} bài làm gần nhất (như {recent_results[0]}), mình thấy bạn nên tập trung vào: **{', '.join(weak_chapters) if weak_chapters else 'các nội dung mới'}**. Bạn muốn mình giải thích lý thuyết phần nào không?"
        else:
            msg = f"Chào {user.hoTen if user else 'bạn'}, mình chưa thấy dữ liệu bài làm của bạn. Hãy thử hoàn thành một bài ôn tập để mình có thể phân tích và tư vấn chính xác nhé!"
        return {"reply": msg}

    # Xử lý các câu hỏi chào hỏi/tên
    if any(k in user_message_lower for k in ["chào", "hi", "hello", "tên gì", "là ai"]):
        return {"reply": f"Chào {user.hoTen if user else 'bạn'}, mình là trợ lý AI của ALAS. Bạn có thể hỏi mình về 'kết quả học tập', 'phần kiến thức còn yếu' hoặc nhờ mình giải thích một khái niệm nào đó nhé!"}

    # Phản hồi mặc định khi không hiểu (thay vì lặp lại câu chào)
    return {"reply": "Mình nghe đây! Hiện tại mình đang tập trung hỗ trợ bạn về ôn tập các môn Lý luận chính trị. Bạn có muốn mình phân tích kết quả bài làm gần nhất của bạn không? (Gợi ý: Hãy thử bấm nút 'Phần mình còn yếu' ở trên)"}
