import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os

class ALEngine:
    def __init__(self):
        self.model_path = 'models/kmeans_model.pkl'
        self.scaler_path = 'models/scaler.pkl'
        self.data_path = 'data/students_data.csv'
        self.kmeans = None
        self.scaler = None

    def train_clustering(self, n_clusters=3):
        """Huấn luyện mô hình K-Means để phân loại sinh viên"""
        if not os.path.exists(self.data_path):
            print(f"❌ Không tìm thấy file {self.data_path}. Hãy chạy script tạo dữ liệu trước!")
            return

        # 1. Đọc dữ liệu
        df = pd.read_csv(self.data_path)
        
        # 2. Chọn các đặc trưng (Features) để phân cụm
        # Chúng ta chọn điểm số và thói quen học tập
        features = ['math_score', 'programming_score', 'study_hours_per_week', 'video_completion_rate']
        X = df[features]

        # 3. Chuẩn hóa dữ liệu (Feature Scaling)
        # K-Means tính khoảng cách nên dữ liệu cần đưa về cùng một thang đo
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # 4. Khởi tạo và huấn luyện K-Means
        # n_clusters=3 tương ứng với: Cần hỗ trợ, Khá, Giỏi
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.kmeans.fit(X_scaled)

        # 5. Lưu mô hình và bộ chuẩn hóa để tái sử dụng
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.kmeans, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

        print(f"✅ Đã huấn luyện và lưu mô hình tại {self.model_path}")
        
        # In ra đặc điểm trung bình của mỗi nhóm để bạn dễ hình dung
        df['group'] = self.kmeans.labels_
        print("\n📊 Đặc điểm trung bình của từng nhóm sinh viên:")
        print(df.groupby('group')[features].mean())

    def predict_student_group(self, math, prog, hours, video):
        """Dự đoán nhóm của một sinh viên mới dựa trên thông tin nhập vào"""
        if self.kmeans is None or self.scaler is None:
            # Load lại model nếu chưa có trong bộ nhớ
            self.kmeans = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)

        # Chuẩn hóa dữ liệu đầu vào giống như lúc huấn luyện
        input_data = np.array([[math, prog, hours, video]])
        input_scaled = self.scaler.transform(input_data)
        
        cluster = self.kmeans.predict(input_scaled)[0]
        
        # Ánh xạ số cụm sang tên nhóm dễ hiểu
        group_names = {0: "Cần hỗ trợ", 1: "Khá", 2: "Giỏi"}
        return group_names.get(cluster, "Không xác định")

# --- Chạy thử nghiệm ---
if __name__ == "__main__":
    engine = ALEngine()
    
    # Bước 1: Huấn luyện
    engine.train_clustering()
    
    # Bước 2: Thử dự đoán cho một sinh viên mới
    # Ví dụ: Toán 8, Code 9, Học 15h, Xem video 90%
    result = engine.predict_student_group(8.0, 9.0, 15.0, 0.9)
    print(f"\n🔍 Kết quả phân tích sinh viên mới: {result}")