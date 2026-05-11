import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_score
from sklearn.decomposition import PCA
from src.main.ai.core.ai_engine import ALEngine
from src.main.database import SessionLocal
from src.main.domain.models import User
import json
import os

def sync_db_to_csv():
    """Lấy dữ liệu từ DB và cập nhật vào students_data.csv"""
    db = SessionLocal()
    try:
        # Lấy thông tin tổng hợp của tất cả user có điểm
        users = db.query(User).filter(User.avg_score > 0).all()
        if not users:
            return False

        real_data = []
        for u in users:
            # Giả định video_completion_rate là 0.8 nếu không có dữ liệu thực tế
            real_data.append({
                'math_score': u.avg_score,
                'programming_score': u.avg_score, # Tạm thời lấy bằng avg_score
                'study_hours_per_week': u.total_time if u.total_time else 0,
                'video_completion_rate': 0.8,
                'is_passed': 1 if u.avg_score >= 5 else 0
            })
        
        if real_data:
            new_df = pd.DataFrame(real_data)
            # Đọc dữ liệu mẫu cũ (nếu muốn giữ lại làm nền) hoặc tạo mới hoàn toàn
            data_path = 'data/students_data.csv'
            if os.path.exists(data_path):
                old_df = pd.read_csv(data_path)
                # Kết hợp: Dữ liệu mẫu + Dữ liệu thật
                # Lưu ý: Chỉ lấy dữ liệu thật để AI "thông minh" theo thực tế
                combined_df = pd.concat([old_df, new_df], ignore_index=True)
                combined_df.to_csv(data_path, index=False)
                print(f"📊 Đã đồng bộ {len(real_data)} bản ghi từ Database vào {data_path}")
            else:
                new_df.to_csv(data_path, index=False)
            return True
    except Exception as e:
        print(f"⚠️ Lỗi đồng bộ dữ liệu: {e}")
    finally:
        db.close()
    return False

def train_and_evaluate(target_sv=None):
    if target_sv is None:
        target_sv = "ADMIN"
        
    print(f"[Giai đoạn 0] Đồng bộ dữ liệu thực tế...")
    sync_db_to_csv()

    print(f"[Giai đoạn 4] Bắt đầu quá trình huấn luyện và đánh giá cho: {target_sv}...")
    
    # 1. Đọc dữ liệu mẫu từ CSV
    data_path = 'data/students_data.csv'
    if not os.path.exists(data_path):
        print(f"Không tìm thấy file dữ liệu: {data_path}")
        return "ai_clusters.png"
        
    df = pd.read_csv(data_path)
    features = ['math_score', 'programming_score', 'study_hours_per_week', 'video_completion_rate']
    X = df[features]
    y = df['is_passed']
    
    # 2. Huấn luyện ALEngine
    engine = ALEngine()
    engine.train_all()
    
    # 3. Đánh giá (Metrics)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    y_pred = engine.dtree.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='macro')

    # Lưu metrics vào JSON
    metrics = {
        "accuracy": round(acc * 100, 1),
        "precision": round(prec, 2),
        "clusters": 3,
        "status": "Ổn định" if acc > 0.7 else "Cần huấn luyện lại",
        "last_train": pd.Timestamp.now().strftime("%H:%M:%S %d/%m/%Y")
    }
    with open('models/ai_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)
    
    # 4. LẤY DỮ LIỆU THẬT TỪ DATABASE ĐỂ VẼ BIỂU ĐỒ
    db = SessionLocal()
    real_users = db.query(User).filter(User.avg_score > 0).all()
    db.close()

    real_data_list = []
    for u in real_users:
        real_data_list.append({
            'maSV': u.maSV,
            'math_score': u.avg_score,
            'programming_score': u.avg_score,
            'study_hours_per_week': u.total_time if u.total_time else 0,
            'video_completion_rate': 0.8, # Giả lập tỷ lệ xem video
            'is_real': True
        })

    # 5. TRỰC QUAN HÓA (K-Means + PCA)
    try:
        X_csv = df[features]
        X_real = pd.DataFrame(real_data_list)[features] if real_data_list else pd.DataFrame(columns=features)
        
        X_combined = pd.concat([X_csv, X_real], ignore_index=True)
        X_scaled = engine.scaler.transform(X_combined)
        
        # Phân cụm
        clusters = engine.kmeans.predict(X_scaled)
        
        # PCA giảm về 2 chiều
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(X_scaled)
        
        plt.figure(figsize=(12, 7))
        
        # Vẽ dữ liệu mẫu (các chấm nhỏ mờ)
        n_sample = len(X_csv)
        sns.scatterplot(x=X_pca[:n_sample, 0], y=X_pca[:n_sample, 1], 
                        hue=clusters[:n_sample], palette='viridis', s=50, alpha=0.3, legend=False)
        
        # Vẽ dữ liệu thật (các chấm to hơn)
        if real_data_list:
            X_pca_real = X_pca[n_sample:]
            found_target = False
            for i in range(len(real_data_list)):
                is_target = real_data_list[i]['maSV'] == target_sv
                color = 'red' if is_target else 'black'
                marker = '*' if is_target else 'o'
                size = 400 if is_target else 120
                alpha = 1.0 if is_target else 0.5
                zorder = 10 if is_target else 5
                
                label = f"BẠN ({target_sv})" if is_target else None
                if is_target: found_target = True
                
                plt.scatter(X_pca_real[i, 0], X_pca_real[i, 1], 
                            c=color, marker=marker, s=size, edgecolors='white', 
                            alpha=alpha, zorder=zorder, label=label)
            
            if not found_target:
                print(f"⚠️ Không tìm thấy vị trí của {target_sv} trong tập dữ liệu thực.")

        plt.title(f"BẢN ĐỒ NĂNG LỰC AI\nNgười xem: {target_sv} - Cập nhật: {metrics['last_train']}", fontsize=14, color='darkblue')
        plt.xlabel("Trục năng lực 1 (Kiến thức)", fontsize=12)
        plt.ylabel("Trục năng lực 2 (Kỹ năng/Thời gian)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(loc='upper right')
        
        # Lưu file theo tên User để tránh xung đột
        filename = f'ai_clusters_{target_sv}.png'
        plot_path = os.path.join('static', 'img', filename)
        plt.savefig(plot_path)
        plt.close()
        print(f"✅ Đã cập nhật biểu đồ tại: {plot_path}")
        return filename
        
    except Exception as e:
        print(f"⚠️ Lỗi vẽ biểu đồ: {e}")
        return "ai_clusters.png"

if __name__ == "__main__":
    # Chạy mặc định nếu gọi trực tiếp
    train_and_evaluate()
