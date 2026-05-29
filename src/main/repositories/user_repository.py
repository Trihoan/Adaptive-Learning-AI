from sqlalchemy.orm import Session
from src.main.domain.models import User

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_username(self, username: str):
        return self.db.query(User).filter(User.tenDangNhap == username).first()

    def find_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def find_by_id(self, user_id: str): 
        return self.db.query(User).filter(User.maSV == user_id).first()

    def save_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: str): 
        user = self.find_by_id(user_id)

        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def get_all_users(self):
        return self.db.query(User).all()

def get_ai_metrics(user_id: str = None):
    import os, json
    ai_chart_file = f"ai_clusters_{user_id}.png" if user_id else "ai_clusters.png"
    static_img_dir = os.path.join("static", "img")
    
    # Base path for models/ai_metrics.json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    metrics_path = os.path.join(base_dir, 'models', 'ai_metrics.json')
    
    if user_id and not os.path.exists(os.path.join(static_img_dir, ai_chart_file)):
        ai_chart_file = "ai_clusters.png"

    ai_metrics = {
        "accuracy": 0, 
        "precision": 0, 
        "clusters": 0, 
        "status": "Chưa có dữ liệu",
        "last_train": "Chưa xác định",
        "class_name": "text-danger",
        "chart_file": ai_chart_file
    }
    
    try:
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ai_metrics.update(data)
                if ai_metrics.get("accuracy", 0) > 70:
                    ai_metrics["class_name"] = "text-success"
                else:
                    ai_metrics["class_name"] = "text-danger"
    except Exception as e:
        print(f"Lỗi đọc file AI metrics: {e}")
        
    return ai_metrics
