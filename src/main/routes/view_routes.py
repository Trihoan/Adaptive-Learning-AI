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
        raw_name = user.hoTen if user.hoTen else user.tenDangNhap
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
        from sqlalchemy import func, text
        from src.main.domain.models import Exam
        
        # Nhóm theo maChuong, đếm số lần làm và tính tổng số giây (dùng TIMESTAMPDIFF cho MySQL)
        results = db.query(
            Exam.maChuong, 
            func.count(Exam.maBaiKiemTra).label("count"),
            func.sum(func.timestampdiff(text('SECOND'), Exam.thoiGianBatDau, Exam.thoiGianKetThuc)).label("total_seconds")
        ).filter(Exam.maSV == user_id).group_by(Exam.maChuong).all()
        
        # Ánh xạ ngược từ maChuong sang topic để template nhận diện được
        rev_topic_map = {
            1: "Chương 1", 2: "Chương 2", 3: "Chương 3",
            4: "Chương 4", 5: "Chương 5", 6: "Chương 6",
            7: "Chương 7",
            101: "de_triet_1", 102: "nguon_goc", 103: "ban_chat",
            201: "Tổng hợp 1 ", 202: "Tổng hợp 2", 203: "Tổng hợp 3", 204: "Tổng hợp 4"
        }
        
        def format_time(seconds):
            if not seconds: return "0 phút"
            minutes = round(seconds / 60, 1)
            return f"{minutes} phút"

        for r in results:
            topic_key = rev_topic_map.get(r.maChuong, "default")
            stats[topic_key] = {
                "count": r.count, 
                "time": format_time(r.total_seconds)
            }

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request, 
            "user_fullname": fullname,
            "db_stats": stats, # Truyền thống kê vào template
            "is_admin": check_admin(db, user_id)
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
        {"request": request, "course_title": course_title, "chapters": chapters, "user_fullname": fullname, "is_admin": check_admin(db, user_id)}
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
            "user_fullname": fullname,
            "is_admin": check_admin(db, user_id)
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

    # Lấy danh sách ID câu hỏi từ form để giữ đúng thứ tự và đúng bộ câu hỏi đã làm
    question_ids_str = form_data.get("question_ids")
    if question_ids_str:
        q_ids = [int(x) for x in question_ids_str.split(",")]
        answers = quiz_service.get_correct_answers_by_ids(q_ids)
    else:
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
        from src.main.domain.models import Exam, StudyResult
        from datetime import datetime, timedelta

        # 1. Lưu Exam (baikiemtra)
        # Lấy chapter_id dựa trên topic thực tế
        topic_to_id = {
            "de_triet_1": 101, "nguon_goc": 102, "ban_chat": 103,
            "Chương 1": 1, "Chương 2": 2, "Chương 3": 3, "Chương 4": 4, 
            "Chương 5": 5, "Chương 6": 6, "Chương 7": 7,
            "Tổng hợp 1 ": 201, "Tổng hợp 2": 202, "Tổng hợp 3": 203, "Tổng hợp 4": 204
        }
        chapter_id = topic_to_id.get(topic)
        
        # Fallback nếu không map được
        if not chapter_id:
            first_q_key = list(answers.keys())[0] if answers else None
            chapter_id = answers[first_q_key]["chapter_id"] if first_q_key else 1
        
        time_taken_seconds = float(form_data.get("time_taken", 0))
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=time_taken_seconds)

        new_exam = Exam(
            maSV=user_id,
            maChuong=chapter_id,
            thoiGianBatDau=start_time,
            thoiGianKetThuc=end_time,
            diem=score_rate
        )
        db.add(new_exam)
        db.flush() # Để lấy maBaiKiemTra vừa tạo

        # 2. Lưu từng câu hỏi vào StudyResult (ketquahoctap)
        for key, info in answers.items():
            user_val = form_data.get(key)
            q_id = int(key.replace("q", ""))
            
            # Lấy maDapAnChon từ ans_map
            chosen_ans_id = info["ans_map"].get(user_val)

            new_sr = StudyResult(
                maSV=user_id,
                maCauHoi=q_id,
                maDapAnChon=chosen_ans_id,
                thoiGianLam=end_time,
                trangThai=(user_val == info["correct"]),
                maBaiKiemTra=new_exam.maBaiKiemTra
            )
            db.add(new_sr)
        
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

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    fullname = get_fullname(db, user_id)
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    
    if not user:
        return RedirectResponse(url="/")
        
    return templates.TemplateResponse(
        "profile.html", 
        {
            "request": request, 
            "user": user, 
            "user_fullname": fullname
        }
    )

# --- ADMIN VIEWS ---

def check_admin(db: Session, user_id: str):
    if not user_id:
        user_repo = UserRepository(db)
        return False
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    return user and user.role == "admin"

@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not check_admin(db, user_id):
        return RedirectResponse(url="/home")
    
    fullname = get_fullname(db, user_id)
    user_repo = UserRepository(db)
    all_users = user_repo.get_all_users()
    
    return templates.TemplateResponse(
        "admin_users.html", 
        {
            "request": request, 
            "users": all_users, 
            "user_fullname": fullname
        }
    )

@router.get("/admin/users/edit/{target_id}", response_class=HTMLResponse)
async def admin_edit_user_page(target_id: str, request: Request, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not check_admin(db, user_id):
        return RedirectResponse(url="/home")
    
    fullname = get_fullname(db, user_id)
    user_repo = UserRepository(db)
    target_user = user_repo.find_by_id(target_id)
    
    if not target_user:
        return RedirectResponse(url="/admin/users")
        
    return templates.TemplateResponse(
        "edit_user.html", 
        {
            "request": request, 
            "target_user": target_user, 
            "user_fullname": fullname
        }
    )
