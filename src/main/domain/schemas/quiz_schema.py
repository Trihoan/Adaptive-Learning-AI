from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnswerBase(BaseModel):
    id: int
    content: str

class AnswerResponse(AnswerBase):
    is_correct: bool
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    id: int
    chapter_id: int
    content: str
    difficulty: int

class QuestionResponse(QuestionBase):
    answers: List[AnswerBase] = [] # Only show answer content, not if it's correct
    class Config:
        from_attributes = True

class ExamBase(BaseModel):
    id: int
    user_id: Optional[str] = None # Can be None if quiz is not started by user yet
    chapter_id: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    score: Optional[float] = None

class ExamResponse(ExamBase):
    questions: List[QuestionResponse] = []
    class Config:
        from_attributes = True

class QuizAnswer(BaseModel):
    question_id: int
    answer_id: int # User submits the ID of the chosen answer

class QuizSubmit(BaseModel):
    answers: List[QuizAnswer]
    
class QuizResultResponse(BaseModel):
    exam_id: int
    total_questions: int
    correct_answers: int
    score: float