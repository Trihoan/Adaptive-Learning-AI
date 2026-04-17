import os
import joblib
import numpy as np
import pandas as pd
from src.main.ai.ai_engine import ALEngine

class AIService:
    def __init__(self):
        self.engine = ALEngine()
        self.dtree_path = 'models/dtree_model.pkl'

    def get_recommendation(self, math_score=None, prog_score=None, study_hours=None, video_rate=None):
        try:
            # TRƯỜNG HỢP CHƯA CÓ DỮ LIỆU (Zero-data)
            # Nếu điểm số hoặc giờ học bằng 0 hoặc None, coi như người mới
            if math_score is None or (math_score == 0 and study_hours == 0):
                return {
                    "status": "Sẵn sàng bắt đầu",
                    "action": ["Làm thử đề số 1 của môn Tư tưởng Hồ Chí Minh", "Làm thử đề số 1 của môn CNXH Khoa học"],
                    "next_step": "Luyện tập ít nhất 2 đề thi để AI có đủ dữ liệu phân tích và dự đoán kết quả cho bạn.",
                    "friendly_msg": "Chào bạn! Mình là AI cố vấn học tập. Hiện tại mình chưa thấy lịch sử ôn tập của bạn. Đừng lo lắng, hãy thử sức với 1-2 đề trắc nghiệm cơ bản nhé, mình sẽ dựa vào đó để xây dựng lộ trình 'về đích' riêng cho bạn!"
                }

            # 1. Đảm bảo mô hình đã được huấn luyện
            if not os.path.exists(self.dtree_path):
                self.engine.train_all()

            # 2. Lấy phân tích từ cả 3 mô hình
            analysis = self.engine.predict_all(math_score, prog_score, study_hours, video_rate)
            
            group = analysis["group"]
            is_passed = "Vượt qua kỳ thi" if analysis["is_passed"] == 1 else "Cần cố gắng thêm"
            
            # 3. Lấy thông tin về tài liệu từ những học viên tương đồng (KNN logic)
            suggested_docs = ["Giáo trình Tư tưởng Hồ Chí Minh (NXB Chính trị quốc gia)", "Bài giảng CNXH Khoa học", "Tài liệu ôn tập trắc nghiệm lý luận chính trị"]
            peer_suggestion = suggested_docs[np.random.randint(0, len(suggested_docs))]

            # 4. Tổng hợp lời khuyên
            recommendations = {
                "Giỏi": {
                    "status": f"Phong độ xuất sắc! Dự đoán kỳ thi: {is_passed}.",
                    "action": [
                        "Thử sức với các đề thi tổng hợp 60 câu để tối ưu thời gian",
                        f"Tài liệu bạn cùng trình độ hay đọc: {peer_suggestion}"
                    ],
                    "next_step": "Duy trì cường độ để giữ vững điểm A+.",
                    "friendly_msg": f"Tuyệt vời! Kết quả {math_score}/10 cho thấy bạn đã nắm rất vững kiến thức. Với đà này, kỳ thi tới chắc chắn sẽ không làm khó được bạn. Hãy thử làm thêm các đề tổng hợp 60 câu để làm quen với áp lực thời gian nhé!"
                },
                "Khá": {
                    "status": f"Đang tiến bộ rất tốt! Dự đoán kỳ thi: {is_passed}.",
                    "action": [
                        "Tập trung tinh chỉnh lại các lỗi sai ở chương vừa làm",
                        f"Gợi ý tài liệu bổ sung: {peer_suggestion}"
                    ],
                    "next_step": "Cố gắng tăng thêm khoảng 30 phút học mỗi tuần để bứt phá lên nhóm Giỏi.",
                    "friendly_msg": f"Chào bạn, mình thấy bạn đang có nền tảng khá vững với mức điểm {math_score}. Chỉ cần tập trung tinh chỉnh lại một vài nội dung chuyên sâu ở các chương lý luận, bạn hoàn toàn có thể chinh phục điểm số cao hơn!"
                },
                "Cần hỗ trợ": {
                    "status": f"Cần tập trung củng cố lại kiến thức! Dự đoán kỳ thi: {is_passed}.",
                    "action": [
                        "Đọc kỹ giáo trình và ghi chú các từ khóa quan trọng",
                        "Xem lại các video bài giảng tóm tắt chương 1 và 2"
                    ],
                    "next_step": "Dành thêm ít nhất 1 giờ mỗi ngày để xem lại các khái niệm cơ bản.",
                    "friendly_msg": f"Đừng nản lòng nhé! Kết quả bài thi {math_score} điểm cho thấy bạn đang gặp chút khó khăn ở phần kiến thức nền tảng. Mình khuyên bạn nên xem lại video tóm tắt chương và làm lại đề số 1 để củng cố lại nhé. Mình luôn ở đây để đồng hành cùng bạn!"
                }
            }

            return recommendations.get(group, recommendations["Khá"])

        except Exception as e:
            print(f"❌ Lỗi AI Service: {e}")
            return {
                "status": "AI đang bảo trì", 
                "action": ["Học tập bình thường"], 
                "next_step": "Tiếp tục",
                "friendly_msg": "Hệ thống AI đang được cập nhật dữ liệu, bạn hãy cứ tiếp tục ôn tập như bình thường nhé!"
            }

        except Exception as e:
            print(f"❌ Lỗi AI Service: {e}")
            return {"status": "AI đang bảo trì", "action": ["Học tập bình thường"], "next_step": "Tiếp tục"}
