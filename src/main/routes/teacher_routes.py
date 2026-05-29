from fastapi import APIRouter, Depends, Form, HTTPException, status, Cookie, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.repositories.class_repository import ClassRepository
from src.main.services.teacher_service import TeacherService
from src.main.domain.models import Course, User, Quiz
from typing import Optional, List
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/teacher", tags=["Teacher"])
templates = Jinja2Templates(directory="templates")

def check_teacher(db: Session, user_id: str):
    if not user_id:
        return False
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    return user and (user.role == "teacher" or user.role == "admin")

@router.get("/dashboard")
async def teacher_dashboard(
    request: Request,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        return RedirectResponse(url="/", status_code=303)

    teacher_service = TeacherService(db)
    classes = teacher_service.get_teacher_classes(user_id)
    
    user_repo = UserRepository(db)
    teacher = user_repo.find_by_id(user_id)
    courses = db.query(Course).all()

    return templates.TemplateResponse("teacher_dashboard.html", {
        "request": request,
        "teacher": teacher,
        "classes": classes,
        "courses": courses,
        "user_fullname": f"{teacher.hoTen} - {teacher.maSV}",
        "is_admin": teacher.role == "admin"
    })

@router.post("/classes/create")
async def create_class(
    maLop: str = Form(...),
    tenLop: str = Form(...),
    monhoc_id: int = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)

    teacher_service = TeacherService(db)
    teacher_service.create_class(maLop, tenLop, user_id, monhoc_id)
    
    return RedirectResponse(url="/teacher/dashboard", status_code=303)

@router.get("/classes/{class_id}")
async def view_class_details(
    request: Request,
    class_id: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        return RedirectResponse(url="/", status_code=303)

    teacher_service = TeacherService(db)
    cls = teacher_service.get_class_details(class_id)
    if not cls or (cls.maGV != user_id and not check_admin(db, user_id)):
         return RedirectResponse(url="/teacher/dashboard", status_code=303)

    students = teacher_service.get_class_results(class_id)
    assigned_quizzes = teacher_service.get_assigned_quizzes(class_id)
    assigned_dethis = teacher_service.get_assigned_dethis(class_id)
    
    # Get all available chapters for the course of this class
    from src.main.domain.models import Chapter
    available_chapters = db.query(Chapter).filter(Chapter.monhoc_id == cls.monhoc_id).all()
    available_quizzes = db.query(Quiz).filter(Quiz.monhoc_id == cls.monhoc_id).all()
    
    user_repo = UserRepository(db)
    teacher = user_repo.find_by_id(user_id)

    return templates.TemplateResponse("teacher_class_details.html", {
        "request": request,
        "class_info": cls,
        "students": students,
        "assigned_quizzes": assigned_quizzes,
        "assigned_dethis": assigned_dethis,
        "available_chapters": available_chapters,
        "available_quizzes": available_quizzes,
        "user_fullname": f"{teacher.hoTen} - {teacher.maSV}",
        "is_admin": teacher.role == "admin"
    })

@router.post("/classes/{class_id}/quizzes/create-random")
async def create_random_quiz(
    class_id: int,
    quiz_name: str = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    from src.main.domain.models import Class, Quiz
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
         raise HTTPException(status_code=404)

    new_quiz = Quiz(
        monhoc_id=cls.monhoc_id,
        maMonHoc=cls.course.maMonHoc,
        tenDeThi=quiz_name,
        thoiGianLam=60
    )
    db.add(new_quiz)
    db.flush() # Lấy maDeThi

    # Giao đề này cho lớp luôn
    teacher_service = TeacherService(db)
    teacher_service.assign_dethi(class_id, new_quiz.maDeThi)
    db.commit()
    
    return RedirectResponse(url=f"/teacher/classes/{class_id}", status_code=303)

@router.post("/classes/{class_id}/dethis/assign")
async def assign_dethi_to_class(
    class_id: int,
    maDeThi: int = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    teacher_service = TeacherService(db)
    teacher_service.assign_dethi(class_id, maDeThi)
    return RedirectResponse(url=f"/teacher/classes/{class_id}", status_code=303)

@router.delete("/classes/{class_id}/dethis/{maDeThi}")
async def remove_dethi_from_class(
    class_id: int,
    maDeThi: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    teacher_service = TeacherService(db)
    teacher_service.remove_dethi(class_id, maDeThi)
    return {"status": "success"}

@router.delete("/classes/{class_id}/results/{maSV}")
async def delete_student_score(
    class_id: int,
    maSV: str,
    target_id: int, # maDeThi or maChuong
    type: str, # "dethi" or "quiz"
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    from src.main.domain.models import Exam, StudyResult
    query = db.query(Exam).filter(Exam.maSV == maSV)
    if type == "dethi":
        query = query.filter(Exam.maDeThi == target_id)
    else:
        query = query.filter(Exam.maChuong == target_id)
    
    exams = query.all()
    for ex in exams:
        # Xóa các chi tiết liên quan trong StudyResult
        db.query(StudyResult).filter(StudyResult.maBaiKiemTra == ex.maBaiKiemTra).delete()
        db.delete(ex)
    
    db.commit()
    return {"status": "success", "message": "Scores cleared"}


@router.delete("/classes/{class_id}/students/{maSV}")
async def remove_student_from_class(
    class_id: int,
    maSV: str,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    teacher_service = TeacherService(db)
    teacher_service.remove_student_from_class(class_id, maSV)
    return {"status": "success"}

@router.post("/classes/{class_id}/quizzes/assign")
async def assign_quiz_to_class(
    class_id: int,
    maChuong: int = Form(...),
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    teacher_service = TeacherService(db)
    teacher_service.assign_quiz(class_id, maChuong)
    return RedirectResponse(url=f"/teacher/classes/{class_id}", status_code=303)

@router.delete("/classes/{class_id}/quizzes/{maChuong}")
async def remove_quiz_from_class(
    class_id: int,
    maChuong: int,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)
    
    teacher_service = TeacherService(db)
    teacher_service.remove_quiz(class_id, maChuong)
    return {"status": "success"}

def check_admin(db: Session, user_id: str):
    if not user_id:
        return False
    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    return user and user.role == "admin"


@router.post("/classes/{class_id}/add-students")
async def add_students_to_class(
    class_id: int,
    student_ids: str = Form(...), # Comma separated list
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_teacher(db, user_id):
        raise HTTPException(status_code=403)

    teacher_service = TeacherService(db)
    s_ids = [s.strip() for s in student_ids.split(",") if s.strip()]
    teacher_service.add_students_to_class(class_id, s_ids)
    
    return RedirectResponse(url=f"/teacher/classes/{class_id}", status_code=303)

@router.get("/classes/join/{maLop}")
async def join_class_via_qr(
    maLop: str,
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/?error=login_required", status_code=303)

    user_repo = UserRepository(db)
    user = user_repo.find_by_id(user_id)
    if user.role != "student":
        return RedirectResponse(url="/home?error=only_students_can_join", status_code=303)

    class_repo = ClassRepository(db)
    cls = class_repo.get_class_by_code(maLop)
    if not cls:
        raise HTTPException(status_code=404, detail="Lớp học không tồn tại")

    # Check if already in class
    existing_students = class_repo.get_students_in_class(cls.id)
    if user_id not in [s.maSV for s in existing_students]:
        # Check limit 40
        if len(existing_students) >= 40:
            return RedirectResponse(url="/home?error=class_full", status_code=303)
        class_repo.add_student_to_class(cls.id, user_id)

    return RedirectResponse(url="/home?join_status=success", status_code=303)
