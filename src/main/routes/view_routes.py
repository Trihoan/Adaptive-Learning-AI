from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.services.ai_service import AIService
from typing import Optional

router = APIRouter(tags=["Views"])

templates = Jinja2Templates(directory="templates")
ai_service = AIService()

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
    # Logic giả lập giống trong app.py
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
async def quiz_page(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})

@router.post("/result", response_class=HTMLResponse)
async def result_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    q1: Optional[str] = Form(None),
    q2: Optional[str] = Form(None),
    q3: Optional[str] = Form(None)
):
    user_fullname = "Người dùng"
    user_obj = None
    if user_id:
        user_repo = UserRepository(db)
        user_obj = user_repo.find_by_id(user_id)
        if user_obj:
            user_fullname = user_obj.hoTen if user_obj.hoTen else user_obj.username

    score = 0
    total = 3

    # Đáp án đúng
    answers = {"q1": "A", "q2": "B", "q3": "C"}

    if q1 == answers["q1"]: score += 1
    if q2 == answers["q2"]: score += 1
    if q3 == answers["q3"]: score += 1

    # Lấy gợi ý từ AI (Dựa trên kết quả thực tế của người dùng)
    # Giả sử chúng ta dùng điểm số này làm math_score và prog_score
    current_score_rate = (score / total) * 10
    ai_rec = ai_service.get_recommendation(
        math_score=current_score_rate, 
        prog_score=current_score_rate,
        study_hours=user_obj.total_time if user_obj else 5.0,
        video_rate=0.8
    )

    return templates.TemplateResponse(
        "result.html", 
        {
            "request": request, 
            "score": score, 
            "total": total, 
            "user_fullname": user_fullname,
            "ai_rec": ai_rec
        }
    )

@router.get("/result", response_class=HTMLResponse)
async def result_page_get(request: Request, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    user_fullname = "Người dùng"
    if user_id:
        user_repo = UserRepository(db)
        user = user_repo.find_by_id(user_id)
        if user:
            user_fullname = user.hoTen if user.hoTen else user.username

    return templates.TemplateResponse("result.html", {"request": request, "score": 0, "total": 0, "user_fullname": user_fullname})