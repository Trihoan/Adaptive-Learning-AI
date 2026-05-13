from fastapi import APIRouter, Depends, Form, HTTPException, status, Cookie, UploadFile, File
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.repositories.user_repository import UserRepository
from src.main.domain.models import User, Question, Answer, Chapter, Course
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
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=403)

    query = db.query(Question)
    if chapter_id:
        query = query.filter(Question.maChuong == chapter_id)

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
        return RedirectResponse(url="/admin/users?error=course_exists", status_code=303)

    new_course = Course(maMonHoc=maMonHoc, tenMonHoc=tenMonHoc)
    db.add(new_course)
    db.commit()

    return RedirectResponse(url="/admin/users?course_status=added", status_code=303)

@router.post("/questions/add")
async def add_individual_question(
    noiDung: str = Form(...),
    maChuong: int = Form(...),
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

    new_q = Question(noiDung=noiDung, maChuong=maChuong, doKho=1, loaiCauHoi="single")
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

    return RedirectResponse(url="/admin/users?q_status=added", status_code=303)

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
    user_id: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    if not check_admin(db, user_id):
        raise HTTPException(status_code=403)
    
    course = db.query(Course).filter(Course.maMonHoc == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Tìm STT cao nhất hiện tại cho đề tổng hợp (>= 100)
    from sqlalchemy import func
    max_stt = db.query(func.max(Chapter.stt)).filter(Chapter.monhoc_id == course.id, Chapter.stt >= 100).scalar()
    new_stt = (max_stt if max_stt else 99) + 1
    
    new_chapter = Chapter(
        monhoc_id=course.id,
        maMonHoc=course_id,
        tenChuong=exam_name,
        stt=new_stt
    )
    db.add(new_chapter)
    db.commit()
    
    return RedirectResponse(url="/admin/users?exam_status=added", status_code=303)

@router.post("/users/update")
async def update_user(
    maSV: str = Form(...),
    hoTen: str = Form(...),
    email: str = Form(...),
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
        
        return RedirectResponse(url="/admin/users?import_status=success", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        return RedirectResponse(url=f"/admin/users?import_status=error&detail={str(e)}", status_code=status.HTTP_303_SEE_OTHER)
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
