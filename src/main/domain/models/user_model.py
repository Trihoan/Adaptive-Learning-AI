from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from src.main.database import Base


class User(Base):
    __tablename__ = "nguoihoc"

    maSV = Column(String(20), primary_key=True)
    tenDangNhap = Column(String(50), unique=True, nullable=False)
    matKhau = Column(String(255), nullable=False)
    hoTen = Column(String(100))
    email = Column(String(100), unique=True)
    ngayTao = Column(DateTime, default=datetime.utcnow)
    role = Column(String(20), default="student")
    avg_score = Column(Float, default=0.0)
    total_time = Column(Float, default=0.0)

    # Relationships
    results = relationship("StudyResult", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    learning_behaviors = relationship("HanhViHocTap", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LoTrinh", back_populates="user", cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")

class HanhViHocTap(Base):
    __tablename__ = "hanhvihoctap"

    maHanhVi = Column(Integer, primary_key=True, autoincrement=True)
    maSV = Column(String(20), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"))
    tongGioHoc = Column(Float, default=0.0)
    diemTB = Column(Float, default=0.0)
    soBaiDaLam = Column(Integer, default=0)
    nangLuc = Column(String(50))

    user = relationship("User", back_populates="learning_behaviors")

class UserSkill(Base):
    __tablename__ = "user_skill"

    maSV = Column(String(20), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"), primary_key=True)
    maMonHoc = Column(String(20), ForeignKey("monhoc.maMonHoc", ondelete="CASCADE"), primary_key=True)
    skill_level = Column(Float, default=0.0)

    user = relationship("User", back_populates="skills")
    course = relationship("Course", back_populates="user_skills")


