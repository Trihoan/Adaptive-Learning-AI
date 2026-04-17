import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hoc-tap-ai-bi-mat-2026'
    
    # Ưu tiên lấy từ biến môi trường (khi lên Render), nếu không có mới dùng localhost (XAMPP)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'mysql+pymysql://root:@localhost:3306/adaptive_learning_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False # Tắt log SQL trên server để tăng tốc