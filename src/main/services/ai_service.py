import os
import joblib
import numpy as np
import pandas as pd
from src.main.ai.ai_engine import ALEngine

class AIService:
    def __init__(self):
        self.engine = ALEngine()
        self.dtree_path = 'models/dtree_model.pkl'

    def get_recommendation(self, math_score, prog_score, study_hours, video_rate):
        try:
            # 1. Đảm bảo mô hình đã được huấn luyện
            if not os.path.exists(self.dtree_path):
                self.engine.train_all()

            # 2. Lấy phân tích từ cả 3 mô hình
            analysis = self.engine.predict_all(math_score, prog_score, study_hours, video_rate)
            
            group = analysis["group"]
            is_passed = analysis["is_passed"]
            similar_indices = analysis["similar_students_indices"]

            # 3. Lấy thông tin về tài liệu từ những học viên tương đồng (KNN logic)
            # Giả lập: Lấy ngẫu nhiên các tài liệu mà nhóm tương đồng đã học
            suggested_docs = ["Giáo trình Triết học Mác-Lênin (NXB Chính trị quốc gia)", "Bài giảng CNXH Khoa học", "Tài liệu ôn tập trắc nghiệm lý luận chính trị"]
            peer_suggestion = suggested_docs[np.random.randint(0, len(suggested_docs))]

            # 4. Tổng hợp lời khuyên
            recommendations = {
                "Giỏi": {
                    "status": f"Xuất sắc! Dự đoán kết quả kỳ thi: {is_passed}.",
                    "action": [
                        "Thử sức với các đề thi tổng hợp 60 câu",
                        f"Học viên cùng trình độ thường tham khảo: {peer_suggestion}"
                    ],
                    "next_step": "Chương tiếp theo hoặc Ôn tập tổng hợp"
                },
                "Khá": {
                    "status": f"Tốt! Dự đoán kết quả kỳ thi: {is_passed}.",
                    "action": [
                        "Xem lại các câu hỏi bị sai trong phần lịch sử triết học",
                        f"Gợi ý tài liệu bổ sung: {peer_suggestion}"
                    ],
                    "next_step": "Ôn tập lại các khái niệm cơ bản của Chương 2"
                },
                "Cần hỗ trợ": {
                    "status": f"Cần cố gắng hơn! Dự đoán kết quả kỳ thi: {is_passed}.",
                    "action": [
                        "Đọc kỹ giáo trình và ghi chú các từ khóa quan trọng",
                        "Xem lại các video bài giảng tóm tắt chương"
                    ],
                    "next_step": "Học lại kiến thức nền tảng của Chương 1"
                }
            }


            return recommendations.get(group, recommendations["Khá"])

        except Exception as e:
            print(f"❌ Lỗi AI Service: {e}")
            return {"status": "AI đang bảo trì", "action": ["Học tập bình thường"], "next_step": "Tiếp tục"}
