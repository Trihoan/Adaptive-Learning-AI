from sqlalchemy.orm import Session
from src.main.services.course_service import CourseService
from src.main.domain.models import Course
from typing import List, Optional
from fastapi import HTTPException

class CourseController:
    def __init__(self, db: Session):
        self.course_service = CourseService(db)

    def get_all_courses(self) -> List[Course]:
        return self.course_service.get_all_courses()

    def get_course_by_id(self, course_id: int) -> Course:
        course = self.course_service.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course

    def get_course_by_code(self, ma_mon_hoc: str) -> Course:
        course = self.course_service.get_course_by_code(ma_mon_hoc)
        if not course:
            raise HTTPException(status_code=404, detail=f"Course with code {ma_mon_hoc} not found")
        return course

    def delete_course(self, course_id: int) -> dict:
        success = self.course_service.delete_course(course_id)
        if not success:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"message": "Course deleted successfully"}
