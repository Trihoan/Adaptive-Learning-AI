import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hoc-tap-ai-bi-mat-2026'
    
    # 1. Cấu hình kết nối MySQL:
    # Cấu trúc: mysql+pymysql://user:password@host:port/database_name
    # Nếu XAMPP dùng port mặc định (3306) và không có password:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/adaptive_learning_db'
    
    # Nếu bạn đổi XAMPP sang port 3307 do lỗi, hãy dùng dòng dưới đây thay thế:
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3307/adaptive_learning_db'

    # 2. Các cấu hình bổ sung cho SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # Hiện log các câu lệnh SQL ra terminal (rất tốt để test)