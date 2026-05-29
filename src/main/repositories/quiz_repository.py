from sqlalchemy.orm import Session
from src.main.domain.models.question_model import Question, Answer, Exam
from typing import List

class QuizRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_questions_by_chapter(self, chapter_id: int) -> List[Question]:
        # Lấy câu hỏi kèm theo các đáp án (Eager loading answers)
        return self.db.query(Question).filter(Question.maChuong == chapter_id).all()

    def get_questions_by_quiz(self, quiz_id: int) -> List[Question]:
        return self.db.query(Question).filter(Question.maDeThi == quiz_id).all()

    def get_question_by_id(self, question_id: int) -> Question:
        return self.db.query(Question).filter(Question.maCauHoi == question_id).first()

    def save_exam_result(self, exam: Exam):
        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)
        return exam
