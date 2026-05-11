from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class AnswerBase(BaseModel):
    maDapAn: int
    noiDungDapAn: str

class AnswerResponse(AnswerBase):
    laDapAnDung: bool
    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    maCauHoi: int
    maChuong: int
    noiDung: str
    doKho: int

class QuestionResponse(QuestionBase):
    answers: List[AnswerBase] = [] # Only show answer content, not if it's correct
    class Config:
        from_attributes = True

class ExamBase(BaseModel):
    maBaiKiemTra: int
    maSV: Optional[str] = None # Can be None if quiz is not started by user yet
    maChuong: int
    thoiGianBatDau: Optional[datetime] = None
    thoiGianKetThuc: Optional[datetime] = None
    diem: Optional[float] = None

class ExamResponse(ExamBase):
    questions: List[QuestionResponse] = []
    class Config:
        from_attributes = True

class QuizAnswer(BaseModel):
    maCauHoi: int
    maDapAn: int # User submits the ID of the chosen answer

class QuizSubmit(BaseModel):
    answers: List[QuizAnswer]

class QuizResultResponse(BaseModel):
    maBaiKiemTra: int
    total_questions: int
    correct_answers: int
    score: float

class QuizDraftSchema(BaseModel):
    topic: str
    question_ids: List[int]
    answers: dict
    seconds_elapsed: int
    current_question: int

class QuizDraftResponse(QuizDraftSchema):
    maSV: str
    updated_at: datetime
    class Config:
        from_attributes = True