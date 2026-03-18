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
            suggested_topics = ["Cấu trúc dữ liệu nâng cao", "Lập trình hướng đối tượng", "Cơ sở dữ liệu SQL"]
            peer_suggestion = suggested_topics[np.random.randint(0, len(suggested_topics))]

            # 4. Tổng hợp lời khuyên
            recommendations = {
                "Giỏi": {
                    "status": f"Xuất sắc! Dự đoán: {is_passed}.",
                    "action": [
                        "Thử sức với các bài tập nâng cao",
                        f"Học viên giống bạn cũng đang học: {peer_suggestion}"
                    ],
                    "next_step": "Chương nâng cao: Tối ưu hóa thuật toán"
                },
                "Khá": {
                    "status": f"Tốt! Dự đoán: {is_passed}.",
                    "action": [
                        "Ôn tập lại các lỗi sai trong bài Quiz",
                        f"Gợi ý tài liệu bổ sung: {peer_suggestion}"
                    ],
                    "next_step": "Chương 3: Cấu trúc dữ liệu"
                },
                "Cần hỗ trợ": {
                    "status": f"Cố lên! Dự đoán: {is_passed}.",
                    "action": [
                        "Xem lại các video bài giảng căn bản",
                        "Tham gia buổi học phụ đạo trực tuyến"
                    ],
                    "next_step": "Học lại Chương 1: Nhập môn"
                }
            }

            return recommendations.get(group, recommendations["Khá"])

        except Exception as e:
            print(f"❌ Lỗi AI Service: {e}")
            return {"status": "AI đang bảo trì", "action": ["Học tập bình thường"], "next_step": "Tiếp tục"}
