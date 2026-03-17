from sqlalchemy.orm import Session
from src.main.domain.models.question_model import Exam, Question, Answer, QuizQuestionAssociation
from typing import List, Optional
from datetime import datetime

class QuizRepository:

    def create_exam(self, db: Session, user_id: str, chapter_id: int) -> Exam:
        new_exam = Exam(user_id=user_id, chapter_id=chapter_id)
        db.add(new_exam)
        db.commit()
        db.refresh(new_exam)
        return new_exam

    def add_question_to_exam(self, db: Session, exam_id: int, question_id: int):
        association = QuizQuestionAssociation(exam_id=exam_id, question_id=question_id)
        db.add(association)
        db.commit()

    def get_exam_by_id(self, db: Session, exam_id: int) -> Optional[Exam]:
        return db.query(Exam).filter(Exam.id == exam_id).first()

    def get_questions_by_exam(self, db: Session, exam_id: int) -> List[Question]:
        return db.query(Question).join(QuizQuestionAssociation).join(Exam).filter(Exam.id == exam_id).all()

    def get_question_with_answers_by_id(self, db: Session, question_id: int) -> Optional[Question]:
        return db.query(Question).filter(Question.id == question_id).first()

    def get_correct_answer_for_question(self, db: Session, question_id: int) -> Optional[Answer]:
        return db.query(Answer).filter(Answer.question_id == question_id, Answer.is_correct == True).first()

    def update_exam_score(self, db: Session, exam_id: int, score: float, end_time: datetime) -> Exam:
        exam = self.get_exam_by_id(db, exam_id)
        if exam:
            exam.score = score
            exam.end_time = end_time
            db.commit()
            db.refresh(exam)
        return exam