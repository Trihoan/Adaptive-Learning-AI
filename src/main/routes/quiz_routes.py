from fastapi import APIRouter, Depends, Cookie
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.main.database import get_db
from src.main.controllers.quiz_controller import QuizController
from src.main.domain.schemas.quiz_schema import ExamResponse, QuestionResponse, QuizSubmit, QuizResultResponse, QuizDraftSchema, QuizDraftResponse
from typing import List, Optional

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

@router.post("/draft/save")
def save_draft(draft_data: QuizDraftSchema, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        return {"status": "error", "message": "User not logged in"}
    
    from src.main.domain.models import QuizDraft
    import json
    
    existing = db.query(QuizDraft).filter(QuizDraft.maSV == user_id, QuizDraft.topic == draft_data.topic).first()
    
    if existing:
        existing.question_ids = ",".join(map(str, draft_data.question_ids))
        existing.answers = json.dumps(draft_data.answers)
        existing.seconds_elapsed = draft_data.seconds_elapsed
        existing.current_question = draft_data.current_question
    else:
        new_draft = QuizDraft(
            maSV=user_id,
            topic=draft_data.topic,
            question_ids=",".join(map(str, draft_data.question_ids)),
            answers=json.dumps(draft_data.answers),
            seconds_elapsed=draft_data.seconds_elapsed,
            current_question=draft_data.current_question
        )
        db.add(new_draft)
    
    db.commit()
    return {"status": "success"}

@router.get("/draft/get/{topic}")
def get_draft(topic: str, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        return {"status": "error", "message": "User not logged in"}
    
    from src.main.domain.models import QuizDraft
    import json
    
    draft = db.query(QuizDraft).filter(QuizDraft.maSV == user_id, QuizDraft.topic == topic).first()
    if not draft:
        return {"status": "not_found"}
    
    return {
        "status": "success",
        "data": {
            "topic": draft.topic,
            "question_ids": [int(x) for x in draft.question_ids.split(",")] if draft.question_ids else [],
            "answers": json.loads(draft.answers) if draft.answers else {},
            "seconds_elapsed": draft.seconds_elapsed,
            "current_question": draft.current_question
        }
    }

@router.delete("/draft/delete/{topic}")
def delete_draft(topic: str, user_id: Optional[str] = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        return {"status": "error", "message": "User not logged in"}
    
    from src.main.domain.models import QuizDraft
    db.query(QuizDraft).filter(QuizDraft.maSV == user_id, QuizDraft.topic == topic).delete()
    db.commit()
    return {"status": "success"}
