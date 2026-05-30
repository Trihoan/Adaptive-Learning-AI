from fastapi import APIRouter, Request, Form, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.services.ai_service import AIService
from src.main.services.quiz_service import QuizService
from typing import Optional
from urllib.parse import quote
import json
import os

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
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    
    if user and user.role == "teacher":
        return RedirectResponse(url="/teacher/dashboard", status_code=303)
    
    fullname = get_fullname(db, user_id)
    
    # 1. Lấy danh sách môn học và chương từ DB
    db_courses = db.query(Course).all()
    
    # Lấy danh sách maChuong và maDeThi đã được giao cho các lớp mà sinh viên tham gia
    assigned_quiz_ids = []
    assigned_dethi_ids = []
    if user_id and user.role == "student":
        from src.main.domain.models import ClassStudent, ClassQuiz, ClassQuizNew
        # Tìm các lớp sinh viên tham gia
        user_classes = db.query(ClassStudent.maLop).filter(ClassStudent.maSV == user_id).all()
        class_ids = [c.maLop for c in user_classes]
        if class_ids:
            # Tìm các đề ôn tập (chương) được giao
            assigned_quizzes = db.query(ClassQuiz.maChuong).filter(ClassQuiz.maLop.in_(class_ids)).all()
            assigned_quiz_ids = [q.maChuong for q in assigned_quizzes]
            
            # Tìm các đề thi được giao
            assigned_dethis = db.query(ClassQuizNew.maDeThi).filter(ClassQuizNew.maLop.in_(class_ids)).all()
            assigned_dethi_ids = [d.maDeThi for d in assigned_dethis]

    dynamic_courses = {}
    course_names = {}
    for c in db_courses:
        course_names[c.maMonHoc] = c.tenMonHoc
        
        # 1. Lọc chương học/đề ôn tập (stt < 100 hoặc được giao)
        db_chapters = db.query(Chapter).filter(
            Chapter.monhoc_id == c.id
        ).filter(
            (Chapter.stt < 100) | (Chapter.maChuong.in_(assigned_quiz_ids))
        ).order_by(Chapter.stt).all()
        
        # 2. Lấy các đề thi được giao
        from src.main.domain.models import Quiz
        db_quizzes = db.query(Quiz).filter(
            Quiz.monhoc_id == c.id,
            Quiz.maDeThi.in_(assigned_dethi_ids)
        ).all()
        
        dynamic_courses[c.maMonHoc] = []
        for ch in db_chapters:
            # Đếm số câu hỏi thực tế của chương này
            from src.main.domain.models import Question as QuestionModel
            q_count = db.query(QuestionModel).filter(QuestionModel.maChuong == ch.maChuong).count()
            
            dynamic_courses[c.maMonHoc].append({
                "id": ch.maChuong,
                "type": "chapter",
                "title": ch.tenChuong,
                "topic": ch.tenChuong,
                "is_general": ch.stt >= 100,
                "is_assigned": ch.maChuong in assigned_quiz_ids,
                "question_count": q_count
            })
            
        for qz in db_quizzes:
            # Đếm số câu hỏi thực tế của đề thi này
            from src.main.domain.models import Question as QuestionModel
            q_count = db.query(QuestionModel).filter(QuestionModel.maDeThi == qz.maDeThi).count()

            dynamic_courses[c.maMonHoc].append({
                "id": qz.maDeThi,
                "type": "quiz",
                "title": qz.tenDeThi,
                "topic": qz.tenDeThi,
                "is_general": True,
                "is_assigned": True,
                "time_limit": qz.thoiGianLam,
                "question_count": q_count
            })

    # Lấy thống kê thực tế từ DB
    stats = {}
    if user_id:
        from sqlalchemy import func, text
        from src.main.domain.models import Exam, Chapter as ChapterModel
        
        # Nhóm theo maChuong, đếm số lần làm và tính tổng số giây
        results = db.query(
            Exam.maChuong, 
            func.count(Exam.maBaiKiemTra).label("count"),
            func.sum(func.timestampdiff(text('SECOND'), Exam.thoiGianBatDau, Exam.thoiGianKetThuc)).label("total_seconds")
        ).filter(Exam.maSV == user_id).group_by(Exam.maChuong).all()
        
        # Ánh xạ từ maChuong sang tên chương (topic)
        for r in results:
            ch_obj = db.query(ChapterModel).filter(ChapterModel.maChuong == r.maChuong).first()
            if ch_obj:
                def format_time(seconds):
                    if not seconds: return "0 phút"
                    minutes = round(seconds / 60, 1)
                    return f"{minutes} phút"
                
                stats[ch_obj.tenChuong] = {
                    "count": r.count, 
                    "time": format_time(r.total_seconds)
                }

    return templates.TemplateResponse(
        "home.html", 
        {
            "request": request, 
            "user_fullname": fullname,
            "db_stats": stats,
            "dynamic_courses": dynamic_courses,
            "course_names": course_names,
            "is_admin": check_admin(db, user_id)
        }
    )

from src.main.domain.models import Chapter, Course

@router.get("/course/{course_name}", response_class=HTMLResponse)
async def course_page(request: Request, course_name: str, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    fullname = get_fullname(db, user_id)
    
    # Lấy thông tin môn học từ Database
    course = db.query(Course).filter(Course.maMonHoc == course_name).first()
    
    if course:
        # Lấy danh sách chương từ Database
        db_chapters = db.query(Chapter).filter(Chapter.monhoc_id == course.id).order_by(Chapter.stt).all()
        chapters = [f"Chương {c.stt}: {c.tenChuong}" for c in db_chapters]
        course_title = course.tenMonHoc
    else:
        # Fallback nếu không có trong DB
        chapters = []
        course_title = "Unknown Course"

    return templates.TemplateResponse(
        "course.html", 
        {"request": request, "course_title": course_title, "chapters": chapters, "user_fullname": fullname, "is_admin": check_admin(db, user_id)}
    )

@router.get("/quiz", response_class=HTMLResponse)
async def quiz_page(
    request: Request,
    topic: Optional[str] = "default",
    qids: Optional[str] = None,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    fullname = get_fullname(db, user_id)
    quiz_service = QuizService(db)
    questions = []

    if qids:
        try:
            question_ids = [int(q_id) for q_id in qids.split(",") if q_id.strip().isdigit()]
            questions = quiz_service.get_questions_by_ids(question_ids)
        except Exception:
            questions = []

    if not questions:
        questions = quiz_service.get_questions_by_topic(topic, user_id=user_id)
    
    topic_map = {
        "Chương 1": "Chương 1",
        "Chương 2": "Chương 2",
        "Chương 3": "Chương 3",
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
    if question_ids_str and question_ids_str.strip():
        try:
            q_ids = [int(x) for x in question_ids_str.split(",") if x.strip()]
            answers = quiz_service.get_correct_answers_by_ids(q_ids)
        except ValueError:
            answers = quiz_service.get_correct_answers_for_topic(topic)
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
    
    # Xác định các chủ đề yếu (làm sai nhiều nhất)
    weak_topics = []
    topic_errors = {}
    for item in result_data:
        if not item["correct"]:
            t = item["topic"]
            topic_errors[t] = topic_errors.get(t, 0) + 1
    
    # Sắp xếp các chủ đề yếu nhất lên đầu
    sorted_weak = sorted(topic_errors.items(), key=lambda x: x[1], reverse=True)
    weak_topics = [t[0] for t in sorted_weak]

    ai_rec = ai_service.get_recommendation(
        math_score=score_rate, 
        prog_score=user_obj.avg_score if user_obj and user_obj.avg_score else score_rate,
        study_hours=study_hours,
        video_rate=0.8,
        weak_topics=weak_topics
    )

    # LƯU KẾT QUẢ VÀO DATABASE
    if user_id:
        from src.main.domain.models import Exam, StudyResult, Chapter as ChapterModel, Quiz as QuizModel
        from datetime import datetime, timedelta

        # 1. Tìm chapter_id hoặc quiz_id linh hoạt
        chapter_id = None
        quiz_id = None
        
        # Thử tìm trong Quiz trước
        quiz_obj = db.query(QuizModel).filter(QuizModel.tenDeThi == topic).first()
        if quiz_obj:
            quiz_id = quiz_obj.maDeThi
        else:
            # Thử tìm trong Chapter
            ch_obj = db.query(ChapterModel).filter(ChapterModel.tenChuong == topic).first()
            if ch_obj:
                chapter_id = ch_obj.maChuong
            else:
                # Fallback từ câu hỏi đầu tiên
                first_q_key = list(answers.keys())[0] if answers else None
                if first_q_key:
                    q_id = int(first_q_key.replace("q", ""))
                    db_q = db.query(Question).filter(Question.maCauHoi == q_id).first()
                    if db_q:
                        chapter_id = db_q.maChuong
                        quiz_id = db_q.maDeThi
        
        time_taken_seconds = float(form_data.get("time_taken", 0))
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=time_taken_seconds)

        new_exam = Exam(
            maSV=user_id,
            maChuong=chapter_id,
            maDeThi=quiz_id,
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
async def profile_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    saved: Optional[str] = None,
    db: Session = Depends(get_db)
):
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
            "user_fullname": fullname,
            "saved": saved,
            "is_admin": check_admin(db, user_id)
        }
    )

@router.get("/profile/edit", response_class=HTMLResponse)
async def edit_profile_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    fullname = get_fullname(db, user_id)
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)

    if not user:
        return RedirectResponse(url="/")

    return templates.TemplateResponse(
        "edit_profile.html",
        {
            "request": request,
            "user": user,
            "user_fullname": fullname,
            "error": error,
            "is_admin": check_admin(db, user_id)
        }
    )

@router.post("/profile/update")
async def update_profile_email(
    email: str = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)

    if not user:
        return RedirectResponse(url="/", status_code=303)

    email = email.strip().lower()
    if not email:
        return RedirectResponse(url="/profile/edit?error=" + quote("Email không được để trống"), status_code=303)

    existing = user_repo.find_by_email(email)
    if existing and existing.maSV != user.maSV:
        return RedirectResponse(url="/profile/edit?error=" + quote("Email này đã được tài khoản khác sử dụng"), status_code=303)

    user.email = email
    db.commit()
    return RedirectResponse(url="/profile?saved=1", status_code=303)

@router.get("/competency-map", response_class=HTMLResponse)
async def competency_map_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/")
        
    fullname = get_fullname(db, user_id)
    from src.main.repositories.user_repository import get_ai_metrics
    ai_metrics = get_ai_metrics(user_id)

    return templates.TemplateResponse(
        "competency_map.html", 
        {
            "request": request, 
            "user_fullname": fullname,
            "ai_metrics": ai_metrics,
            "is_admin": check_admin(db, user_id)
        }
    )

@router.get("/my-classes", response_class=HTMLResponse)
async def my_classes_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/")
        
    fullname = get_fullname(db, user_id)
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    
    # Lấy danh sách các lớp sinh viên đã tham gia
    joined_classes = user.classes_joined

    return templates.TemplateResponse(
        "my_classes.html", 
        {
            "request": request, 
            "user_fullname": fullname,
            "joined_classes": joined_classes,
            "is_admin": check_admin(db, user_id)
        }
    )

# --- ADMIN VIEWS MOVED TO admin_routes.py ---

def check_admin(db: Session, user_id: str):
    if not user_id:
        return False
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    return user and user.role == "admin"
