from sqlalchemy.orm import Session
from src.main.repositories.course_repository import CourseRepository
from src.main.domain.models import Course
from typing import List, Optional

class CourseService:
    def __init__(self, db: Session):
        self.repo = CourseRepository(db)

    def get_all_courses(self) -> List[Course]:
        return self.repo.get_all()

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        return self.repo.get_by_id(course_id)

    def get_course_by_code(self, ma_mon_hoc: str) -> Optional[Course]:
        return self.repo.get_by_code(ma_mon_hoc)

    def create_course(self, ma_mon_hoc: str, ten_mon_hoc: str, mo_ta: str = "") -> Course:
        new_course = Course(
            maMonHoc=ma_mon_hoc,
            tenMonHoc=ten_mon_hoc,
            moTa=mo_ta
        )
        return self.repo.create(new_course)

    def delete_course(self, course_id: int) -> bool:
        return self.repo.delete(course_id)
