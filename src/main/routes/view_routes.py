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

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/home", response_class=HTMLResponse)
async def home_page(request: Request, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user_fullname = "Người dùng"
    if user_id:
        user_repo = UserRepository(db)
        user = user_repo.find_by_id(user_id)
        if user:
            user_fullname = user.hoTen if user.hoTen else user.username

    return templates.TemplateResponse("home.html", {"request": request, "user_fullname": user_fullname})

@router.get("/course/{course_name}", response_class=HTMLResponse)
async def course_page(request: Request, course_name: str):
    chapters = []
    course_title = "Unknown"

    if course_name == "triethoc":
        chapters = [
            "Chương 1: Vật chất và ý thức",
            "Chương 2: Phép biện chứng",
            "Chương 3: Chủ nghĩa duy vật lịch sử"
        ]
        course_title = "Triết học Mác - Lênin"

    return templates.TemplateResponse(
        "course.html", 
        {"request": request, "course_title": course_title, "chapters": chapters}
    )

@router.get("/quiz", response_class=HTMLResponse)
async def quiz_page(request: Request, topic: Optional[str] = "default", db: Session = Depends(get_db)):
    quiz_service = QuizService(db)
    questions = quiz_service.get_questions_by_topic(topic)
    return templates.TemplateResponse("quiz.html", {"request": request, "questions": questions, "topic": topic})

@router.post("/result", response_class=HTMLResponse)
async def process_result(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    topic: Optional[str] = Form("default")
):
    quiz_service = QuizService(db)
    ai_service = AIService() # Khởi tạo ai_service
    form_data = await request.form()
    
    user_fullname = "Người dùng"
    user_obj = None
    study_hours = 2.5
    
    if user_id:
        user_repo = UserRepository(db)
        user_obj = user_repo.find_by_id(user_id)
        if user_obj:
            user_fullname = user_obj.hoTen if user_obj.hoTen else user_obj.username
            study_hours = user_obj.total_time if user_obj.total_time else 2.5

    answers = quiz_service.get_correct_answers_for_topic(topic)
    score = 0
    result_data = []
    
    for key, info in answers.items():
        user_val = form_data.get(key)
        is_correct = user_val == info["correct"]
        if is_correct:
            score += 1
            
        result_data.append({
            "id": key,
            "topic": info["topic"],
            "correct": is_correct,
            "user_answer": user_val,
            "correct_answer": info["correct"]
        })
    
    total = len(answers) if answers else 3
    score_rate = (score / total) * 10 if total > 0 else 0
    
    ai_rec = ai_service.get_recommendation(
        math_score=score_rate, 
        prog_score=user_obj.avg_score if user_obj and user_obj.avg_score else score_rate,
        study_hours=study_hours,
        video_rate=0.8
    )
    
    result_json = json.dumps(result_data)
    
    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, 
            "score": score, 
            "total": total, 
            "user_fullname": user_fullname,
            "ai_rec": ai_rec,
            "result_data": result_data,
            "result_json": result_json
        }
    )

@router.get("/recommend", response_class=HTMLResponse)
async def recommend_page(request: Request, data: Optional[str] = None, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    ai_service = AIService() # Khởi tạo ai_service
    result_data = []
    ai_recommendation = None
    user_fullname = "Người dùng" # Mặc định
    
    # 1. Lấy thông tin người dùng thực tế từ DB
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id) if user_id else None
    
    study_hours = 2.5
    if user:
        user_fullname = user.hoTen if user.hoTen else user.username
        study_hours = user.total_time if user.total_time else 2.5
    
    if data:
        try:
            result_data = json.loads(data)
            correct_count = sum(1 for item in result_data if item["correct"])
            score_rate = (correct_count / len(result_data)) * 10 if result_data else 0
            
            # 2. GỌI AI SERVICE với dữ liệu thực tế
            ai_recommendation = ai_service.get_recommendation(
                math_score=score_rate, 
                prog_score=user.avg_score if user and user.avg_score else score_rate,
                study_hours=study_hours,
                video_rate=0.7
            )
        except Exception as e:
            print(f"Lỗi phân tích AI: {e}")
            result_data = []
            
    return templates.TemplateResponse(
        "recommend.html", 
        {
            "request": request, 
            "resultData": result_data, 
            "ai_rec": ai_recommendation,
            "user_fullname": user_fullname
        }
    )
