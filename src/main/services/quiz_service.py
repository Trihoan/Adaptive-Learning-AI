from sqlalchemy.orm import Session
from src.main.repositories.quiz_repository import QuizRepository
from src.main.domain.schemas.quiz_schema import QuizSubmit, QuizResultResponse
from src.main.domain.models.question_model import Exam
from datetime import datetime
from typing import List

class QuizService:
    def __init__(self):
        self.quiz_repo = QuizRepository()

    def create_exam(self, db: Session, user_id: str, chapter_id: int) -> Exam:
        return self.quiz_repo.create_exam(db, user_id, chapter_id)

    def get_exam_by_id(self, db: Session, exam_id: int) -> Exam:
        return self.quiz_repo.get_exam_by_id(db, exam_id)

    def get_questions_for_exam(self, db: Session, exam_id: int) -> List[any]: # Using 'any' for now, will be Question model
        return self.quiz_repo.get_questions_by_exam(db, exam_id)

    def submit_quiz(self, db: Session, exam_id: int, submit_data: QuizSubmit):
        exam = self.quiz_repo.get_exam_by_id(db, exam_id)
        if not exam:
            return None # Exam not found

        questions = self.quiz_repo.get_questions_by_exam(db, exam_id)
        
        if not questions:
            return None # No questions for this exam
            
        correct_answers_count = 0
        total_questions = len(questions)
        
        for submitted_answer in submit_data.answers:
            question = self.quiz_repo.get_question_with_answers_by_id(db, submitted_answer.question_id)
            if question:
                correct_answer_obj = self.quiz_repo.get_correct_answer_for_question(db, question.id)
                if correct_answer_obj and submitted_answer.answer_id == correct_answer_obj.id:
                    correct_answers_count += 1
                    
        score = (correct_answers_count / total_questions) * 10.0 if total_questions > 0 else 0.0
        
        # Update exam record with score and end time
        updated_exam = self.quiz_repo.update_exam_score(db, exam_id, score, datetime.utcnow())
        
        return QuizResultResponse(
            exam_id=exam_id,
            total_questions=total_questions,
            correct_answers=correct_answers_count,
            score=round(score, 2)
        )
