from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.services.ai_service import AIService
from src.main.services.quiz_service import QuizService
from typing import Optional
import json

router = APIRouter(tags=["Views"])

templates = Jinja2Templates(directory="templates")

# Hàm lấy tên đầy đủ thực tế từ Database dựa trên maSV (user_id)
def get_fullname(db: Session, user_id: str):
    if not user_id:
        return "Người dùng"
    
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    
    if user:
        # 1. Lấy họ tên và viết hoa chữ cái đầu mỗi từ (.title())
        raw_name = user.hoTen if user.hoTen else user.username
        formatted_name = raw_name.title()
        
        # 2. Lấy MASV và viết hoa toàn bộ (.upper())
        masv = user.maSV.upper() if user.maSV else ""
        
        # Trả về định dạng: Nguyen Van A - B21DCCN001
        return f"{formatted_name} - {masv}"
        
    return "Người dùng"

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    fullname = get_fullname(db, user_id)
    
    # Lấy thống kê thực tế từ DB
    stats = {}
    if user_id:
        from sqlalchemy import func
        from src.main.domain.models.study_result_model import StudyResult
        
        # Nhóm theo topic và đếm số lần làm, cộng tổng thời gian
        results = db.query(
            StudyResult.topic, 
            func.count(StudyResult.id).label("count"),
            func.sum(StudyResult.time_taken).label("total_time")
        ).filter(StudyResult.user_id == user_id).group_by(StudyResult.topic).all()
        
        for r in results:
            minutes = round(r.total_time / 60, 1) if r.total_time else 0
            stats[r.topic] = {"count": r.count, "time": f"{minutes} phút"}

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request, 
            "user_fullname": fullname,
            "db_stats": stats # Truyền thống kê vào template
        }
    )

@router.get("/course/{course_name}", response_class=HTMLResponse)
async def course_page(request: Request, course_name: str, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    fullname = get_fullname(db, user_id)
    chapters = []
    course_title = "Unknown"

    if course_name == "triethoc":
        chapters = [
            "Chương 1: Vật chất và ý thức",
            "Chương 2: Phép biện chứng",
            "Chương 3: Chủ nghĩa duy vật lịch sử"
        ]
        course_title = "Triết học Mác - Lênin"
    elif course_name == "xahoi":
        chapters = [
            "Chương 1: Nhập môn CNXH KH",
            "Chương 2: Sứ mệnh lịch sử của giai cấp công nhân",
            "Chương 3: Chủ nghĩa xã hội và thời kỳ quá độ"
        ]
        course_title = "Chủ nghĩa xã hội khoa học"

    return templates.TemplateResponse(
        "course.html", 
        {"request": request, "course_title": course_title, "chapters": chapters, "user_fullname": fullname}
    )

@router.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request, topic: Optional[str] = "default", user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    fullname = get_fullname(db, user_id)
    quiz_service = QuizService(db)
    questions = quiz_service.get_questions_by_topic(topic)
    
    topic_map = {
        "nguon_goc": "Nguồn gốc Triết học",
        "ban_chat": "Bản chất Triết học",
        "lich_su": "Lịch sử Triết học",
        "default": "Ôn tập tổng hợp"
    }
    display_topic = topic_map.get(topic, topic.replace("_", " ").capitalize())

    return templates.TemplateResponse(
        "quiz.html", 
        {
            "request": request, 
            "questions": questions, 
            "topic": topic, 
            "display_topic": display_topic,
            "user_fullname": fullname
        }
    )

@router.post("/result", response_class=HTMLResponse)
async def process_result(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    topic: Optional[str] = Form("default")
):
    fullname = get_fullname(db, user_id)
    quiz_service = QuizService(db)
    ai_service = AIService()
    form_data = await request.form()
    
    user_repo = UserRepository(db)
    user_obj = user_repo.find_by_id(user_id) if user_id else None
    study_hours = user_obj.total_time if user_obj and user_obj.total_time else 2.5

    answers = quiz_service.get_correct_answers_for_topic(topic)
    score = 0
    result_data = []
    
    for key, info in answers.items():
        user_val = form_data.get(key)
        is_correct = user_val == info["correct"]
        if is_correct: score += 1
        result_data.append({
            "id": key, "text": info["text"], "topic": info["topic"], "correct": is_correct,
            "user_answer": user_val, "correct_answer": info["correct"]
        })
    
    total = len(answers) if answers else 3
    score_rate = (score / total) * 10 if total > 0 else 0
    
    ai_rec = ai_service.get_recommendation(
        math_score=score_rate, 
        prog_score=user_obj.avg_score if user_obj and user_obj.avg_score else score_rate,
        study_hours=study_hours,
        video_rate=0.8
    )

    # LƯU KẾT QUẢ VÀO DATABASE
    if user_id:
        from src.main.domain.models.study_result_model import StudyResult
        new_result = StudyResult(
            user_id=user_id,
            score=score_rate,
            time_taken=float(form_data.get("time_taken", 0)), # Lấy thời gian từ form
            topic=topic,
            course_id="triethoc" if topic.startswith("de_triet") or topic in ["nguon_goc", "ban_chat", "lich_su"] else "xahoi"
        )
        db.add(new_result)
        db.commit()
    
    # Dữ liệu rút gọn để truyền qua URL (tránh lỗi 414 Request-URI Too Large)
    # Chỉ giữ lại thông tin cần thiết cho logic phân tích kiến thức hổng ở trang recommend
    short_result_data = [
        {"topic": item["topic"], "correct": item["correct"]} 
        for item in result_data
    ]
    
    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, "score": score, "total": total, 
            "user_fullname": fullname, "ai_rec": ai_rec,
            "result_data": result_data, 
            "short_result": short_result_data
        }
    )

@router.get("/recommend", response_class=HTMLResponse)
async def recommend_page(request: Request, data: Optional[str] = None, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    fullname = get_fullname(db, user_id)
    ai_service = AIService()
    result_data = []
    ai_recommendation = None
    
    if data:
        try:
            result_data = json.loads(data)
            correct_count = sum(1 for item in result_data if item["correct"])
            score_rate = (correct_count / len(result_data)) * 10 if result_data else 0
            
            user_repo = UserRepository(db)
            user = user_repo.find_by_id(user_id) if user_id else None
            study_hours = user.total_time if user and user.total_time else 2.5
            
            ai_recommendation = ai_service.get_recommendation(
                math_score=score_rate, 
                prog_score=user.avg_score if user and user.avg_score else score_rate,
                study_hours=study_hours,
                video_rate=0.7
            )
        except:
            result_data = []
            
    return templates.TemplateResponse(
        "recommend.html", 
        {"request": request, "resultData": result_data, "ai_rec": ai_recommendation, "user_fullname": fullname}
    )
