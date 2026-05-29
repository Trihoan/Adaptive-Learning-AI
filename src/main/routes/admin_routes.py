from fastapi import APIRouter, Depends, Form, HTTPException, status, Cookie, UploadFile, File, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.domain.models import User, Question, Answer, Chapter, Course, Quiz
from typing import Optional
import shutil
import os

router = APIRouter(prefix="/admin", tags=["Admin"])

def check_admin(db: Session, user_id: str):
    if not user_id:
        return False
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    return user and user.role == "admin"

@router.get("/questions")
async def get_questions_list(
    chapter_id: Optional[int] = None,
    quiz_id: Optional[int] = None,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=403)

    query = db.query(Question)
    if chapter_id:
        query = query.filter(Question.maChuong == chapter_id)
    if quiz_id:
        query = query.filter(Question.maDeThi == quiz_id)

    questions = query.order_by(Question.maCauHoi.asc()).all()
    return questions

@router.post("/courses/add")
async def add_new_course(
    maMonHoc: str = Form(...),
    tenMonHoc: str = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=403)

    # Kiểm tra xem môn học đã tồn tại chưa
    existing = db.query(Course).filter(Course.maMonHoc == maMonHoc).first()
    if existing:
        return RedirectResponse(url="/admin/content?error=course_exists", status_code=303)

    new_course = Course(maMonHoc=maMonHoc, tenMonHoc=tenMonHoc)
    db.add(new_course)
    db.commit()

    return RedirectResponse(url="/admin/content?course_status=added", status_code=303)

@router.post("/questions/add")
async def add_individual_question(
    noiDung: str = Form(...),
    maChuong: Optional[int] = Form(None),
    maDeThi: Optional[int] = Form(None),
    ans_a: str = Form(...),
    ans_b: str = Form(...),
    ans_c: str = Form(...),
    ans_d: str = Form(...),
    correct: str = Form(...), # "A", "B", "C", or "D"
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=403)

    new_q = Question(
        noiDung=noiDung, 
        maChuong=maChuong, 
        maDeThi=maDeThi,
        doKho=1, 
        loaiCauHoi="single"
    )
    db.add(new_q)
    db.flush()

    answers = [
        Answer(maCauHoi=new_q.maCauHoi, noiDungDapAn=ans_a, laDapAnDung=(correct == "A")),
        Answer(maCauHoi=new_q.maCauHoi, noiDungDapAn=ans_b, laDapAnDung=(correct == "B")),
        Answer(maCauHoi=new_q.maCauHoi, noiDungDapAn=ans_c, laDapAnDung=(correct == "C")),
        Answer(maCauHoi=new_q.maCauHoi, noiDungDapAn=ans_d, laDapAnDung=(correct == "D")),
    ]
    db.add_all(answers)
    db.commit()

    return RedirectResponse(url="/admin/content?q_status=added", status_code=303)

@router.delete("/questions/{q_id}")
async def delete_question(
    q_id: int,
    admin_id: str,
    db: Session = Depends(get_db)
):
    if not check_admin(db, admin_id):
        raise HTTPException(status_code=403)

    q = db.query(Question).filter(Question.maCauHoi == q_id).first()
    if not q:
        raise HTTPException(status_code=404)

    db.delete(q)
    db.commit()
    return {"status": "success"}
  
@router.post("/general-exams/add")
async def add_general_exam(
    course_id: str = Form(...),
    exam_name: str = Form(...),
    time_limit: int = Form(60),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=403)
    
    course = db.query(Course).filter(Course.maMonHoc == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    new_quiz = Quiz(
        tenDeThi=exam_name,
        monhoc_id=course.id,
        maMonHoc=course_id,
        thoiGianLam=time_limit
    )
    db.add(new_quiz)
    db.commit()
    
    return RedirectResponse(url="/admin/content?exam_status=added", status_code=303)

@router.post("/users/update")
async def update_user(
    maSV: str = Form(...),
    hoTen: str = Form(...),
    email: Optional[str] = Form(None),
    role: str = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(maSV)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hoTen = hoTen
    user.email = email
    user.role = role
    db.commit()
    
    return RedirectResponse(url="/admin/users", status_code=status.HTTP_303_SEE_OTHER)

@router.delete("/users/{target_id}")
async def delete_user(
    target_id: str,
    admin_id: str, # Passed as query param from JS
    db: Session = Depends(get_db)
):
    if not check_admin(db, admin_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    user_repo = UserRepository(db)
    success = user_repo.delete_user(target_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"status": "success", "message": "User deleted"}

@router.post("/ai/train")
async def trigger_training(
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        from src.main.ai.training.ai_trainer import train_and_evaluate
        train_and_evaluate(user_id)
        return {"status": "success", "message": "AI Training completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_data(
    course_id: str = Form(...),
    chapter_name: Optional[str] = Form(None),
    file_type: str = Form(...), # "word" or "excel"
    file: UploadFile = File(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Tạo thư mục temp nếu chưa có
    temp_dir = "temp_uploads"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    file_path = os.path.join(temp_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        if file_type == "word":
            from src.main.ai.importers.word_importer import import_from_word
            import_from_word(file_path, course_id, default_chapter_name=chapter_name)
        elif file_type == "excel":
            from src.main.ai.importers.excel_importer import import_from_excel
            if not chapter_name:
                raise HTTPException(status_code=400, detail="Chapter name is required for Excel import")
            import_from_excel(file_path, course_id, chapter_name)
        
        return RedirectResponse(url="/admin/content?import_status=success", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return RedirectResponse(url=f"/admin/content?import_status=error&detail={str(e)}", status_code=status.HTTP_303_SEE_OTHER)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/users")
async def get_users_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        return RedirectResponse(url="/", status_code=303)

    user_repo = UserRepository(db)
    all_users = user_repo.get_all_users()
    
    students = [u for u in all_users if u.role == "student"]
    teachers = [u for u in all_users if u.role == "teacher"]
    admins = [u for u in all_users if u.role == "admin"]

    # AI Metrics (placeholder or from DB)
    from src.main.repositories.user_repository import get_ai_metrics
    ai_metrics = get_ai_metrics(user_id)

    # Get current user for header
    current_user = user_repo.find_by_id(user_id)
    user_fullname = f"{current_user.hoTen} - {current_user.maSV}" if current_user else "Admin"

    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    
    # Get courses for the "Add Exam" and "Import" modals
    courses = db.query(Course).all()

    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "students": students,
        "teachers": teachers,
        "admins": admins,
        "ai_metrics": ai_metrics,
        "user_fullname": user_fullname,
        "courses": courses,
        "is_admin": True
    })

@router.get("/content")
async def get_content_page(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        return RedirectResponse(url="/", status_code=303)

    user_repo = UserRepository(db)
    current_user = user_repo.find_by_id(user_id)
    user_fullname = f"{current_user.hoTen} - {current_user.maSV}" if current_user else "Admin"

    all_courses = db.query(Course).all()
    all_chapters = db.query(Chapter).all()
    all_quizzes = db.query(Quiz).all()

    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    return templates.TemplateResponse("admin_content.html", {
        "request": request,
        "user_fullname": user_fullname,
        "all_courses": all_courses,
        "all_chapters": all_chapters,
        "all_quizzes": all_quizzes,
        "is_admin": True
    })

@router.get("/users/edit/{target_id}")
async def admin_edit_user_page(
    target_id: str,
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        return RedirectResponse(url="/", status_code=303)
    
    user_repo = UserRepository(db)
    target_user = user_repo.find_by_id(target_id)
    
    if not target_user:
        return RedirectResponse(url="/admin/users")

    # Get current user for header
    current_user = user_repo.find_by_id(user_id)
    user_fullname = f"{current_user.hoTen} - {current_user.maSV}" if current_user else "Admin"
    
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")

    return templates.TemplateResponse(
        "edit_user.html", 
        {
            "request": request, 
            "target_user": target_user, 
            "user_fullname": user_fullname,
            "is_admin": True
        }
    )
