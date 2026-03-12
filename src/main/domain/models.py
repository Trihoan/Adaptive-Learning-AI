from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student') # 'admin' hoặc 'student'
    
    # Dữ liệu cho AI Decision Tree
    avg_score = db.Column(db.Float, default=0.0)
    total_time = db.Column(db.Float, default=0.0)

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255)) # Để hiển thị ảnh môn học cho đẹp

class StudyResult(db.Model):
    __tablename__ = 'study_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    score = db.Column(db.Float)
    time_spent = db.Column(db.Float) # Thời gian làm bài (giây)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)