import pandas as pd
import numpy as np
import os

def generate_sample_data(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    np.random.seed(42)
    n_samples = 500
    
    # Sinh dữ liệu ngẫu nhiên có logic: 
    # math_score: 0-10, programming_score: 0-10, study_hours: 0-40, video_rate: 0-1
    math_score = np.random.uniform(2, 10, n_samples)
    prog_score = np.random.uniform(2, 10, n_samples)
    study_hours = np.random.uniform(1, 30, n_samples)
    video_rate = np.random.uniform(0.1, 1, n_samples)
    
    # logic pass/fail giả định: điểm trung bình > 5 và học > 5 tiếng
    avg = (math_score + prog_score) / 2
    is_passed = ((avg > 5) & (study_hours > 5)).astype(int)
    
    df = pd.DataFrame({
        'math_score': math_score,
        'programming_score': prog_score,
        'study_hours_per_week': study_hours,
        'video_completion_rate': video_rate,
        'is_passed': is_passed
    })
    
    df.to_csv(file_path, index=False)
    print(f"✅ Đã tạo dữ liệu mẫu tại: {file_path}")

if __name__ == "__main__":
    generate_sample_data('data/students_data.csv')
