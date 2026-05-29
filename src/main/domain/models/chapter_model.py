from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.main.database import Base

class Chapter(Base):
    __tablename__ = "chuonghoc"

    maChuong = Column(Integer, primary_key=True, autoincrement=True)
    monhoc_id = Column(Integer, ForeignKey("monhoc.id"))
    maMonHoc = Column(String(20))
    tenChuong = Column(String(255), nullable=False)
    stt = Column(Integer, default=1)

    course = relationship("Course", back_populates="chapters")
    questions = relationship("Question", back_populates="chapter", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="chapter", cascade="all, delete-orphan")
    assigned_classes = relationship("Class", secondary="lop_hoc_chuong_hoc", back_populates="quizzes")