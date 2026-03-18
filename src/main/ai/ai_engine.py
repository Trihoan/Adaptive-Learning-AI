import os
import pandas as pd
import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import NearestNeighbors

class ALEngine:
    def __init__(self):
        # Đường dẫn tương đối từ gốc dự án
        self.model_dir = 'models'
        self.data_path = 'data/students_data.csv'
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.kmeans_path = os.path.join(self.model_dir, 'kmeans_model.pkl')
        self.dtree_path = os.path.join(self.model_dir, 'dtree_model.pkl')
        self.scaler_path = os.path.join(self.model_dir, 'scaler.pkl')
        
        self.kmeans = None
        self.dtree = None
        self.scaler = None
        self.knn = None

    def train_all(self):
        """Huấn luyện bộ 3 mô hình AI: K-Means, Decision Tree, KNN"""
        if not os.path.exists(self.data_path):
            print(f"⚠️ Cảnh báo: Không tìm thấy {self.data_path}. AI sẽ hoạt động ở chế độ cơ bản.")
            return False

        df = pd.read_csv(self.data_path)
        features = ['math_score', 'programming_score', 'study_hours_per_week', 'video_completion_rate']
        X = df[features]
        y = df['is_passed']

        # 1. Chuẩn hóa (Scaler)
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        joblib.dump(self.scaler, self.scaler_path)

        # 2. Phân nhóm (K-Means)
        self.kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.kmeans.fit(X_scaled)
        joblib.dump(self.kmeans, self.kmeans_path)

        # 3. Dự đoán (Decision Tree)
        self.dtree = DecisionTreeClassifier(max_depth=5, random_state=42)
        self.dtree.fit(X, y)
        joblib.dump(self.dtree, self.dtree_path)

        # 4. Tương đồng (KNN)
        self.knn = NearestNeighbors(n_neighbors=5, algorithm='auto')
        self.knn.fit(X_scaled)
        
        print("✅ [AI Engine] Đã huấn luyện xong tất cả mô hình.")
        return True

    def predict_all(self, math, prog, hours, video):
        """Dự đoán toàn diện từ 3 mô hình"""
        try:
            if self.kmeans is None:
                self.kmeans = joblib.load(self.kmeans_path)
                self.dtree = joblib.load(self.dtree_path)
                self.scaler = joblib.load(self.scaler_path)
                
                # KNN cần data để fit lại (vì nó không lưu được trạng thái fit như các model khác)
                df = pd.read_csv(self.data_path)
                X_scaled = self.scaler.transform(df[['math_score', 'programming_score', 'study_hours_per_week', 'video_completion_rate']])
                self.knn = NearestNeighbors(n_neighbors=5).fit(X_scaled)

            input_data = np.array([[math, prog, hours, video]])
            input_scaled = self.scaler.transform(input_data)

            # K-Means
            cluster = self.kmeans.predict(input_scaled)[0]
            group_names = {0: "Cần hỗ trợ", 1: "Khá", 2: "Giỏi"}

            # Decision Tree
            is_passed = self.dtree.predict(input_data)[0]

            # KNN
            distances, indices = self.knn.kneighbors(input_scaled)
            
            return {
                "group": group_names.get(cluster, "Khá"),
                "is_passed": "Đạt" if is_passed == 1 else "Cần cố gắng",
                "similar_students_indices": indices[0].tolist()
            }
        except Exception as e:
            print(f"❌ [AI Engine] Lỗi khi dự đoán: {e}")
            return {"group": "Khá", "is_passed": "Chưa xác định", "similar_students_indices": []}
