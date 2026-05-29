from sqlalchemy.orm import Session
from sqlalchemy import text
from src.main.repositories.class_repository import ClassRepository
from src.main.repositories.user_repository import UserRepository
from src.main.domain.models.class_model import Class
from typing import List

class TeacherService:
    def __init__(self, db: Session):
        self.class_repo = ClassRepository(db)
        self.user_repo = UserRepository(db)

    def create_class(self, maLop: str, tenLop: str, maGV: str, monhoc_id: int):
        return self.class_repo.create_class(maLop, tenLop, maGV, monhoc_id)

    def get_teacher_classes(self, maGV: str):
        return self.class_repo.get_classes_by_teacher(maGV)

    def get_class_details(self, class_id: int):
        return self.class_repo.get_class_by_id(class_id)

    def add_students_to_class(self, class_id: int, student_ids: List[str]):
        for sid in student_ids:
            # Check if student exists and not already in class
            student = self.user_repo.find_by_id(sid)
            if student:
                # Check if already in class
                existing_students = self.class_repo.get_students_in_class(class_id)
                if sid not in [s.maSV for s in existing_students]:
                    self.class_repo.add_student_to_class(class_id, sid)

    def get_class_results(self, class_id: int):
        cls = self.class_repo.get_class_by_id(class_id)
        if not cls:
            return []
        
        # Lấy danh sách đề thi và đề ôn tập đã giao cho lớp
        assigned_dethis = self.get_assigned_dethis(class_id)
        assigned_quizzes = self.get_assigned_quizzes(class_id)
        
        students = cls.students
        results = []
        from src.main.domain.models import Exam
        from sqlalchemy import func

        for s in students:
            # Lấy danh sách điểm chi tiết cho từng ĐỀ THI ĐÃ GIAO
            detailed_scores = []
            total_score = 0
            count = 0
            
            for dethi in assigned_dethis:
                latest_exam = self.class_repo.db.query(Exam).filter(
                    Exam.maSV == s.maSV,
                    Exam.maDeThi == dethi.maDeThi
                ).order_by(Exam.thoiGianKetThuc.desc()).first()
                
                if latest_exam:
                    duration_min = (latest_exam.thoiGianKetThuc - latest_exam.thoiGianBatDau).total_seconds() / 60 if latest_exam.thoiGianKetThuc else 0
                    detailed_scores.append({"type": "dethi", "id": dethi.maDeThi, "diem": latest_exam.diem, "time": duration_min})
                    total_score += latest_exam.diem
                    count += 1
                else:
                    detailed_scores.append({"type": "dethi", "id": dethi.maDeThi, "diem": None, "time": 0})

            # Lấy danh sách điểm chi tiết cho từng ĐỀ ÔN TẬP ĐÃ GIAO
            for quiz in assigned_quizzes:
                latest_exam = self.class_repo.db.query(Exam).filter(
                    Exam.maSV == s.maSV,
                    Exam.maChuong == quiz.maChuong
                ).order_by(Exam.thoiGianKetThuc.desc()).first()
                
                if latest_exam:
                    duration_min = (latest_exam.thoiGianKetThuc - latest_exam.thoiGianBatDau).total_seconds() / 60 if latest_exam.thoiGianKetThuc else 0
                    detailed_scores.append({"type": "quiz", "id": quiz.maChuong, "diem": latest_exam.diem, "time": duration_min})
                    total_score += latest_exam.diem
                    count += 1
                else:
                    detailed_scores.append({"type": "quiz", "id": quiz.maChuong, "diem": None, "time": 0})

            results.append({
                "maSV": s.maSV,
                "hoTen": s.hoTen,
                "exam_results": detailed_scores,
                "avg_score": (total_score / count) if count > 0 else 0
            })
        return results

    def remove_student_from_class(self, class_id: int, maSV: str):
        self.class_repo.remove_student_from_class(class_id, maSV)

    def assign_quiz(self, class_id: int, maChuong: int):
        self.class_repo.assign_quiz_to_class(class_id, maChuong)

    def remove_quiz(self, class_id: int, maChuong: int):
        self.class_repo.remove_quiz_from_class(class_id, maChuong)

    def get_assigned_quizzes(self, class_id: int):
        return self.class_repo.get_quizzes_for_class(class_id)

    def assign_dethi(self, class_id: int, maDeThi: int):
        self.class_repo.assign_dethi_to_class(class_id, maDeThi)

    def remove_dethi(self, class_id: int, maDeThi: int):
        self.class_repo.remove_dethi_from_class(class_id, maDeThi)

    def get_assigned_dethis(self, class_id: int):
        return self.class_repo.get_dethis_for_class(class_id)
