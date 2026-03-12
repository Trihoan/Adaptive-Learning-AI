import pandas as pd
import numpy as np
import os

# 1. Cấu hình các thông số
np.random.seed(42)  # Giữ kết quả cố định mỗi lần chạy
n_students = 500

# 2. Tạo các Features (Đầu vào)
math_score = np.random.uniform(0, 10, n_students)
prog_score = np.random.uniform(0, 10, n_students)
study_hours = np.random.uniform(2, 20, n_students)
video_rate = np.random.uniform(0, 1, n_students)

# 3. Tạo Logic cho "is_passed" (Mục tiêu cho Decision Tree)
# Giả sử: Đỗ nếu (Điểm trung bình > 5 và học trên 5h) hoặc (Học cực chăm > 15h)
score_avg = (math_score + prog_score) / 2
is_passed = ((score_avg > 5) & (study_hours > 5)) | (study_hours > 15)
is_passed = is_passed.astype(int)

# 4. Tạo DataFrame
df = pd.DataFrame({
    'math_score': np.round(math_score, 1),
    'programming_score': np.round(prog_score, 1),
    'study_hours_per_week': np.round(study_hours, 1),
    'video_completion_rate': np.round(video_rate, 2),
    'is_passed': is_passed
})

# 5. Lưu vào thư mục data/
os.makedirs('data', exist_ok=True)
df.to_csv('data/students_data.csv', index=False)

print("✅ Đã tạo file data/students_data.csv thành công với 500 mẫu!")