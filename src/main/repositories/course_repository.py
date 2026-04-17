from sqlalchemy.orm import Session
from src.main.domain.models import Course
from typing import List, Optional

class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Course]:
        return self.db.query(Course).all()

    def get_by_id(self, course_id: int) -> Optional[Course]:
        return self.db.query(Course).filter(Course.id == course_id).first()

    def get_by_code(self, ma_mon_hoc: str) -> Optional[Course]:
        return self.db.query(Course).filter(Course.maMonHoc == ma_mon_hoc).first()

    def create(self, course: Course) -> Course:
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course_id: int) -> bool:
        course = self.get_by_id(course_id)
        if course:
            self.db.delete(course)
            self.db.commit()
            return True
        return False
