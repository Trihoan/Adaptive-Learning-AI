from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.services.quiz_service import QuizService
from src.main.domain.schemas.quiz_schema import ExamResponse, QuestionResponse, QuizSubmit, QuizResultResponse
from src.main.domain.models.question_model import Exam, Question
from typing import List

class QuizController:
    def __init__(self, db: Session):
        self.quiz_service = QuizService()
        self.db = db

    def create_exam(self, user_id: str, chapter_id: int) -> Exam:
        return self.quiz_service.create_exam(self.db, user_id, chapter_id)

    def get_exam_by_id(self, exam_id: int) -> Exam:
        exam = self.quiz_service.get_exam_by_id(self.db, exam_id)
        if not exam:
            raise HTTPException(status_code=404, detail="Exam not found")
        return exam

    def get_questions_for_exam(self, exam_id: int) -> List[Question]:
        questions = self.quiz_service.get_questions_for_exam(self.db, exam_id)
        if not questions:
            raise HTTPException(status_code=404, detail="No questions found for this exam")
        return questions

    def submit_quiz(self, exam_id: int, submit_data: QuizSubmit) -> QuizResultResponse:
        result = self.quiz_service.submit_quiz(self.db, exam_id, submit_data)
        if not result:
            raise HTTPException(status_code=404, detail="Exam not found or has no questions")
        return result