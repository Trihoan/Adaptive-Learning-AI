from sqlalchemy.orm import Session
from src.main.repositories.quiz_repository import QuizRepository
from src.main.domain.models import Exam, Question, Answer, StudyResult
from src.main.domain.schemas.quiz_schema import QuizSubmit, QuizResultResponse
from typing import List, Dict, Any, Optional
from datetime import datetime

class QuizService:
    def __init__(self, db: Session):
        self.repo = QuizRepository(db)
        self.db = db

    def create_exam(self, db: Session, user_id: str, chapter_id: int) -> Exam:
        # Lấy câu hỏi ngẫu nhiên từ chương
        questions = self.repo.get_questions_by_chapter(chapter_id)
        import random
        # Tăng lên 20 câu nếu là đề tổng hợp, hoặc 10 câu nếu đề chương lẻ
        limit = 20 if chapter_id > 100 else 10 # Giả định chapter_id lớn là đề tổng hợp hoặc tùy chỉnh
        selected_questions = random.sample(questions, min(len(questions), limit))

        exam = Exam(
            maSV=user_id,
            maChuong=chapter_id,
            thoiGianBatDau=datetime.utcnow()
        )
        exam.questions = selected_questions
        db.add(exam)
        db.commit()
        db.refresh(exam)
        return exam

    def get_exam_by_id(self, db: Session, exam_id: int) -> Optional[Exam]:
        return db.query(Exam).filter(Exam.maBaiKiemTra == exam_id).first()

    def get_questions_for_exam(self, db: Session, exam_id: int) -> List[Question]:
        exam = self.get_exam_by_id(db, exam_id)
        return exam.questions if exam else []

    def submit_quiz(self, db: Session, exam_id: int, submit_data: QuizSubmit) -> Optional[QuizResultResponse]:
        exam = self.get_exam_by_id(db, exam_id)
        if not exam:
            return None

        correct_count = 0
        total_questions = len(exam.questions)
        
        # Lưu kết quả từng câu
        for answer_data in submit_data.answers:
            question = db.query(Question).filter(Question.maCauHoi == answer_data.maCauHoi).first()
            if not question:
                continue
            
            # Kiểm tra đáp án chọn
            chosen_answer = db.query(Answer).filter(Answer.maDapAn == answer_data.maDapAn).first()
            is_correct = chosen_answer.laDapAnDung if chosen_answer else False
            
            if is_correct:
                correct_count += 1
            
            # 1. Cập nhật maDapAnChon vào bảng trung gian chitietbaikiemtra
            # Chúng ta dùng một câu query update vì SQLAlchemy secondary table mapping khó truy cập trực tiếp từng dòng có sẵn
            from src.main.domain.models.question_model import QuizQuestionAssociation
            db.query(QuizQuestionAssociation).filter(
                QuizQuestionAssociation.maBaiKiemTra == exam_id,
                QuizQuestionAssociation.maCauHoi == answer_data.maCauHoi
            ).update({"maDapAnChon": answer_data.maDapAn})

            # 2. Lưu StudyResult (ketquahoctap) - Bảng lịch sử tổng quát
            new_sr = StudyResult(
                maSV=exam.maSV,
                maCauHoi=answer_data.maCauHoi,
                maDapAnChon=answer_data.maDapAn,
                trangThai=is_correct,
                maBaiKiemTra=exam.maBaiKiemTra
            )
            db.add(new_sr)

        score = (correct_count / total_questions) * 10 if total_questions > 0 else 0
        exam.diem = score
        exam.thoiGianKetThuc = datetime.utcnow()
        db.commit()

        return QuizResultResponse(
            maBaiKiemTra=exam_id,
            total_questions=total_questions,
            correct_answers=correct_count,
            score=score
        )

    def get_questions_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        # Ánh xạ Topic/Đề sang danh sách các Chapter ID (Khớp với home.html mới)
        topic_map = {
            # CNXH KH: Khớp tên tiếng Việt từ home.html
            "Chương 1": [1], "Chương 2": [2], "Chương 3": [3], "Chương 4": [4], 
            "Chương 5": [5], "Chương 6": [6], "Chương 7": [7],
            
            "Tổng hợp 1": [1, 2, 3, 4, 5, 6, 7],
            "Tổng hợp 2": [1, 2, 3, 4, 5, 6, 7],
            "Tổng hợp 3": [1, 2, 3, 4, 5, 6, 7],
            "Tổng hợp 4": [1, 2, 3, 4, 5, 6, 7],

            # TTHCM: Đã chỉnh STT 1-5 ứng với maChuong 8-12
            "TTHCM_Chương 1": [8], "TTHCM_Chương 2": [9], "TTHCM_Chương 3": [10],
            "TTHCM_Chương 4": [11], "TTHCM_Chương 5": [12],
            
            "Tổng hợp TTHCM 1": [8, 9, 10, 11, 12],
            "Tổng hợp TTHCM 2": [8, 9, 10, 11, 12],
            "Tổng hợp TTHCM 3": [8, 9, 10, 11, 12],
            "Tổng hợp TTHCM 4": [8, 9, 10, 11, 12]
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
                            "id": str(q.maCauHoi),
                            "text": q.noiDung,
                            "chapter_id": c_id, 
                            "A": ans_list[0].noiDungDapAn if len(ans_list) > 0 else "N/A",
                            "B": ans_list[1].noiDungDapAn if len(ans_list) > 1 else "N/A",
                            "C": ans_list[2].noiDungDapAn if len(ans_list) > 2 else "N/A",
                            "D": ans_list[3].noiDungDapAn if len(ans_list) > 3 else "N/A",
                            "correct": self._get_correct_label(ans_list)
                        }
                        all_questions.append(q_data)
            
            if not all_questions:
                return [{ "id": "sample", "text": "Đang cập nhật câu hỏi cho chương này...", "A": "Đang cập nhật", "correct": "A", "chapter_id": chapter_ids[0] }]

            # Trộn câu hỏi
            import random
            random.shuffle(all_questions)
            
            # Giới hạn câu hỏi
            if "Tổng hợp" in topic:
                limit = 60
            else:
                limit = 40
                
            return all_questions[:limit] 

        except Exception as e:
            print(f"Lỗi QuizService: {e}")
            return []

    def _get_correct_label(self, ans_list: List) -> str:
        labels = ["A", "B", "C", "D"]
        for idx, ans in enumerate(ans_list):
            if ans.laDapAnDung:
                return labels[idx] if idx < len(labels) else "A"
        return "A"

    def get_correct_answers_for_topic(self, topic: str) -> Dict[str, Any]:
        questions = self.get_questions_by_topic(topic)
        answers_dict = {}
        
        # Ánh xạ ngược từ chapter_id sang tên chương để AI gợi ý
        chapter_names = {
            # CNXHKH
            1: "Nhập môn CNXHKH", 2: "Sứ mệnh giai cấp công nhân", 3: "Thời kỳ quá độ",
            4: "Dân chủ XHCN và Nhà nước", 5: "Cơ cấu xã hội - giai cấp", 
            6: "Dân tộc và tôn giáo", 7: "Vấn đề gia đình",
            # TTHCM
            8: "Cơ sở hình thành TTHCM", 9: "Độc lập dân tộc và CNXH",
            10: "Đảng Cộng sản và Nhà nước", 11: "Đại đoàn kết dân tộc",
            12: "Văn hóa, đạo đức, con người"
        }

        # Cần map nhãn A, B, C, D sang ID đáp án thực tế để lưu DB
        for q in questions:
            if q["id"] == "sample": continue
            # Lấy lại câu hỏi từ DB để có danh sách đáp án gốc (vì q trong questions là dict)
            db_q = self.repo.get_question_by_id(int(q["id"]))
            ans_map = {}
            labels = ["A", "B", "C", "D"]
            for idx, ans in enumerate(db_q.answers):
                if idx < len(labels):
                    ans_map[labels[idx]] = ans.maDapAn

            answers_dict[f"q{q['id']}"] = {
                "correct": q["correct"],
                "text": q["text"],
                "topic": chapter_names.get(q["chapter_id"], "Kiến thức chung"),
                "chapter_id": q["chapter_id"],
                "ans_map": ans_map # Thêm map label -> maDapAn
            }
        return answers_dict

    def get_correct_answers_by_ids(self, q_ids: List[int]) -> Dict[str, Any]:
        answers_dict = {}
        chapter_names = {
            1: "Nhập môn CNXHKH", 2: "Sứ mệnh giai cấp công nhân", 3: "Thời kỳ quá độ",
            4: "Dân chủ XHCN và Nhà nước", 5: "Cơ cấu xã hội - giai cấp", 
            6: "Dân tộc và tôn giáo", 7: "Vấn đề gia đình",
            8: "Cơ sở hình thành TTHCM", 9: "Độc lập dân tộc và CNXH",
            10: "Đảng Cộng sản và Nhà nước", 11: "Đại đoàn kết dân tộc",
            12: "Văn hóa, đạo đức, con người"
        }

        for q_id in q_ids:
            q = self.repo.get_question_by_id(q_id)
            if not q:
                continue
            
            ans_list = q.answers
            ans_map = {}
            labels = ["A", "B", "C", "D"]
            for idx, ans in enumerate(ans_list):
                if idx < len(labels):
                    ans_map[labels[idx]] = ans.maDapAn

            answers_dict[f"q{q.maCauHoi}"] = {
                "correct": self._get_correct_label(ans_list),
                "text": q.noiDung,
                "topic": chapter_names.get(q.maChuong, "Kiến thức chung"),
                "chapter_id": q.maChuong,
                "ans_map": ans_map
            }
        return answers_dict

    def get_questions_by_ids(self, q_ids: List[int]) -> List[Dict[str, Any]]:
        questions = []

        for q_id in q_ids:
            q = self.repo.get_question_by_id(q_id)
            if not q:
                continue

            ans_list = q.answers
            questions.append({
                "id": str(q.maCauHoi),
                "text": q.noiDung,
                "chapter_id": q.maChuong,
                "A": ans_list[0].noiDungDapAn if len(ans_list) > 0 else "N/A",
                "B": ans_list[1].noiDungDapAn if len(ans_list) > 1 else "N/A",
                "C": ans_list[2].noiDungDapAn if len(ans_list) > 2 else "N/A",
                "D": ans_list[3].noiDungDapAn if len(ans_list) > 3 else "N/A",
                "correct": self._get_correct_label(ans_list)
            })

        return questions
