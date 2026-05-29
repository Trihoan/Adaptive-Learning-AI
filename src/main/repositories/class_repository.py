from sqlalchemy.orm import Session
from src.main.domain.models.class_model import Class, ClassStudent, ClassQuiz
from src.main.domain.models.quiz_model import Quiz, ClassQuizNew
from src.main.domain.models.user_model import User
from src.main.domain.models.chapter_model import Chapter
from typing import List, Optional

class ClassRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_class(self, maLop: str, tenLop: str, maGV: str, monhoc_id: int) -> Class:
        new_class = Class(maLop=maLop, tenLop=tenLop, maGV=maGV, monhoc_id=monhoc_id)
        self.db.add(new_class)
        self.db.commit()
        self.db.refresh(new_class)
        return new_class

    def get_class_by_id(self, class_id: int) -> Optional[Class]:
        return self.db.query(Class).filter(Class.id == class_id).first()

    def get_class_by_code(self, maLop: str) -> Optional[Class]:
        return self.db.query(Class).filter(Class.maLop == maLop).first()

    def get_classes_by_teacher(self, maGV: str) -> List[Class]:
        return self.db.query(Class).filter(Class.maGV == maGV).all()

    def add_student_to_class(self, class_id: int, maSV: str):
        class_student = ClassStudent(maLop=class_id, maSV=maSV)
        self.db.add(class_student)
        self.db.commit()

    def get_students_in_class(self, class_id: int) -> List[User]:
        cls = self.get_class_by_id(class_id)
        return cls.students if cls else []

    def remove_student_from_class(self, class_id: int, maSV: str):
        self.db.query(ClassStudent).filter(
            ClassStudent.maLop == class_id,
            ClassStudent.maSV == maSV
        ).delete()
        self.db.commit()

    def delete_class(self, class_id: int):
        cls = self.get_class_by_id(class_id)
        if cls:
            self.db.delete(cls)
            self.db.commit()
            return True
        return False

    # Quiz Management (Legacy Chapter-based)
    def assign_quiz_to_class(self, class_id: int, maChuong: int):
        existing = self.db.query(ClassQuiz).filter(
            ClassQuiz.maLop == class_id,
            ClassQuiz.maChuong == maChuong
        ).first()
        if not existing:
            new_assign = ClassQuiz(maLop=class_id, maChuong=maChuong)
            self.db.add(new_assign)
            self.db.commit()

    def remove_quiz_from_class(self, class_id: int, maChuong: int):
        self.db.query(ClassQuiz).filter(
            ClassQuiz.maLop == class_id,
            ClassQuiz.maChuong == maChuong
        ).delete()
        self.db.commit()

    def get_quizzes_for_class(self, class_id: int) -> List[Chapter]:
        cls = self.get_class_by_id(class_id)
        return cls.quizzes if cls else []

    # Exam (DeThi) Management
    def assign_dethi_to_class(self, class_id: int, maDeThi: int):
        existing = self.db.query(ClassQuizNew).filter(
            ClassQuizNew.maLop == class_id,
            ClassQuizNew.maDeThi == maDeThi
        ).first()
        if not existing:
            new_assign = ClassQuizNew(maLop=class_id, maDeThi=maDeThi)
            self.db.add(new_assign)
            self.db.commit()

    def remove_dethi_from_class(self, class_id: int, maDeThi: int):
        self.db.query(ClassQuizNew).filter(
            ClassQuizNew.maLop == class_id,
            ClassQuizNew.maDeThi == maDeThi
        ).delete()
        self.db.commit()

    def get_dethis_for_class(self, class_id: int) -> List[Quiz]:
        cls = self.get_class_by_id(class_id)
        return cls.assigned_quizzes if cls else []
