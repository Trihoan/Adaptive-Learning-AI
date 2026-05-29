from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.main.database import Base

class Class(Base):
    __tablename__ = "lop_hoc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maLop = Column(String(20, collation='utf8mb4_general_ci'), unique=True, nullable=False)
    tenLop = Column(String(100, collation='utf8mb4_general_ci'), nullable=False)
    maGV = Column(String(20, collation='utf8mb4_general_ci'), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"))
    monhoc_id = Column(Integer, ForeignKey("monhoc.id", ondelete="CASCADE"))
    ngayTao = Column(DateTime, default=datetime.utcnow)

    # Relationships
    teacher = relationship("User", back_populates="classes_taught")
    course = relationship("Course")
    students = relationship("User", secondary="sinh_vien_lop_hoc", back_populates="classes_joined")
    quizzes = relationship("Chapter", secondary="lop_hoc_chuong_hoc", back_populates="assigned_classes")
    assigned_quizzes = relationship("Quiz", secondary="lop_hoc_de_thi", back_populates="assigned_classes")

class ClassStudent(Base):
    __tablename__ = "sinh_vien_lop_hoc"

    maLop = Column(Integer, ForeignKey("lop_hoc.id", ondelete="CASCADE"), primary_key=True)
    maSV = Column(String(20, collation='utf8mb4_general_ci'), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"), primary_key=True)
    ngayThamGia = Column(DateTime, default=datetime.utcnow)

class ClassQuiz(Base):
    __tablename__ = "lop_hoc_chuong_hoc"

    maLop = Column(Integer, ForeignKey("lop_hoc.id", ondelete="CASCADE"), primary_key=True)
    maChuong = Column(Integer, ForeignKey("chuonghoc.maChuong", ondelete="CASCADE"), primary_key=True)
    ngayGiao = Column(DateTime, default=datetime.utcnow)
