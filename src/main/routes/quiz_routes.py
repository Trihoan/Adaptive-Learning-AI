from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.controllers.quiz_controller import QuizController
from src.main.domain.schemas.quiz_schema import ExamResponse, QuestionResponse, QuizSubmit, QuizResultResponse
from typing import List

router = APIRouter(prefix="/exams", tags=["Exams"]) # Changed prefix to /exams

@router.post("/", response_model=ExamResponse)
def create_exam(user_id: str, chapter_id: int, db: Session = Depends(get_db)):
    controller = QuizController(db)
    return controller.create_exam(user_id, chapter_id)

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam_by_id(exam_id: int, db: Session = Depends(get_db)):
    controller = QuizController(db)
    return controller.get_exam_by_id(exam_id)

@router.get("/{exam_id}/questions", response_model=List[QuestionResponse])
def get_questions_for_exam(exam_id: int, db: Session = Depends(get_db)):
    controller = QuizController(db)
    return controller.get_questions_for_exam(exam_id)

@router.post("/{exam_id}/submit", response_model=QuizResultResponse)
def submit_quiz(exam_id: int, submit_data: QuizSubmit, db: Session = Depends(get_db)):
    controller = QuizController(db)
    return controller.submit_quiz(exam_id, submit_data)
