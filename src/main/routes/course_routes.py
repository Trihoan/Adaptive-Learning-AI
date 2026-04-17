from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.controllers.course_controller import CourseController
from src.main.domain.schemas.course_schema import CourseResponse
from typing import List

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseResponse])
async def get_courses(db: Session = Depends(get_db)):
    controller = CourseController(db)
    return controller.get_all_courses()

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course_by_id(course_id: int, db: Session = Depends(get_db)):
    controller = CourseController(db)
    return controller.get_course_by_id(course_id)

@router.get("/code/{ma_mon_hoc}", response_model=CourseResponse)
async def get_course_by_code(ma_mon_hoc: str, db: Session = Depends(get_db)):
    controller = CourseController(db)
    return controller.get_course_by_code(ma_mon_hoc)

@router.delete("/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    controller = CourseController(db)
    return controller.delete_course(course_id)
