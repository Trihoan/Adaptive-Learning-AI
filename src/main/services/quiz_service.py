from sqlalchemy.orm import Session
from src.main.repositories.quiz_repository import QuizRepository
from typing import List, Dict, Any

class QuizService:
    def __init__(self, db: Session):
        self.repo = QuizRepository(db)

    def get_questions_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        # Ánh xạ Topic/Đề sang danh sách các Chapter ID
        topic_map = {
            "nguon_goc": [1],
            "ban_chat": [2],
            "lich_su": [3],
            "nhap_mon": [4],
            "su_menh": [5],
            "thoi_ky_qua_do": [6],
            # Đề tổng hợp
            "de_triet_1": [1, 2, 3], 
            "de_xahoi_1": [4, 5, 6],
            "de_tong_hop": [1, 2, 3, 4, 5, 6]
        }
        
        chapter_ids = topic_map.get(topic, [1])
        all_questions = []

        try:
            for c_id in chapter_ids:
                db_questions = self.repo.get_questions_by_chapter(c_id)
                if db_questions:
                    for q in db_questions:
                        ans_list = q.answers 
                        q_data = {
                            "id": str(q.id),
                            "text": q.content,
                            "chapter_id": c_id, # Lưu lại ID chương để AI phân tích
                            "A": ans_list[0].content if len(ans_list) > 0 else "N/A",
                            "B": ans_list[1].content if len(ans_list) > 1 else "N/A",
                            "C": ans_list[2].content if len(ans_list) > 2 else "N/A",
                            "D": ans_list[3].content if len(ans_list) > 3 else "N/A",
                            "correct": self._get_correct_label(ans_list)
                        }
                        all_questions.append(q_data)
            
            if not all_questions:
                return [{ "id": "sample", "text": "Đang cập nhật câu hỏi...", "A": "A", "correct": "A", "chapter_id": 1 }]

            # Trộn câu hỏi và lấy giới hạn (ví dụ 10 câu mỗi đề)
            import random
            random.shuffle(all_questions)
            return all_questions[:10] 

        except Exception as e:
            print(f"Lỗi QuizService: {e}")
            return []

    def get_correct_answers_for_topic(self, topic: str) -> Dict[str, Any]:
        questions = self.get_questions_by_topic(topic)
        answers_dict = {}
        
        # Ánh xạ ngược từ chapter_id sang tên chương để AI gợi ý
        chapter_names = {
            1: "Vật chất và ý thức", 2: "Phép biện chứng", 3: "Chủ nghĩa duy vật lịch sử",
            4: "Nhập môn CNXH KH", 5: "Sứ mệnh giai cấp công nhân", 6: "Thời kỳ quá độ"
        }

        for q in questions:
            answers_dict[f"q{q['id']}"] = {
                "correct": q["correct"],
                "text": q["text"],
                "topic": chapter_names.get(q["chapter_id"], "Kiến thức chung")
            }
        return answers_dict
