from sqlalchemy.orm import Session
from src.main.repositories.quiz_repository import QuizRepository
from typing import List, Dict, Any

class QuizService:
    def __init__(self, db: Session):
        self.repo = QuizRepository(db)

    def get_questions_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        # Chuyển đổi topic thành chapter_id (Trong thực tế bạn có thể map từ tên topic)
        topic_to_chapter_id = {
            "nguon_goc": 1,
            "ban_chat": 2,
            "lich_su": 3
        }
        chapter_id = topic_to_chapter_id.get(topic, 1) # Mặc định là chapter 1

        # Lấy từ Database
        db_questions = self.repo.get_questions_by_chapter(chapter_id)
        
        # Format lại dữ liệu cho Frontend (với các trường A, B, C, D)
        formatted_questions = []
        for q in db_questions:
            # Lấy danh sách đáp án cho câu hỏi này
            ans_list = q.answers 
            
            q_data = {
                "id": str(q.id),
                "text": q.content,
                "A": ans_list[0].content if len(ans_list) > 0 else "",
                "B": ans_list[1].content if len(ans_list) > 1 else "",
                "C": ans_list[2].content if len(ans_list) > 2 else "",
                "D": ans_list[3].content if len(ans_list) > 3 else "",
                "correct": self._get_correct_label(ans_list)
            }
            formatted_questions.append(q_data)
            
        return formatted_questions

    def _get_correct_label(self, answers):
        # Xác định xem đáp án thứ mấy là đúng để trả về label 'A', 'B', 'C' hoặc 'D'
        labels = ['A', 'B', 'C', 'D']
        for idx, ans in enumerate(answers):
            if ans.is_correct and idx < len(labels):
                return labels[idx]
        return 'A'

    def get_correct_answers_for_topic(self, topic: str) -> Dict[str, Any]:
        # Tương tự như lấy câu hỏi, ta lấy danh sách đáp án đúng từ DB
        questions = self.get_questions_by_topic(topic)
        answers_dict = {}
        for q in questions:
            answers_dict[f"q{q['id']}"] = {
                "correct": q["correct"],
                "topic": topic
            }
        return answers_dict
