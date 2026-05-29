from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.main.database import Base

class Quiz(Base):
    __tablename__ = "dethi"

    maDeThi = Column(Integer, primary_key=True, autoincrement=True)
    tenDeThi = Column(String(255), nullable=False)
    monhoc_id = Column(Integer, ForeignKey("monhoc.id", ondelete="CASCADE"))
    maMonHoc = Column(String(20))
    thoiGianLam = Column(Integer, default=60) # Minutes
    moTa = Column(Text)
    ngayTao = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course")
    questions = relationship("Question", back_populates="quiz")
    exams = relationship("Exam", back_populates="quiz")
    assigned_classes = relationship("Class", secondary="lop_hoc_de_thi", back_populates="assigned_quizzes")

class ClassQuizNew(Base):
    __tablename__ = "lop_hoc_de_thi"

    maLop = Column(Integer, ForeignKey("lop_hoc.id", ondelete="CASCADE"), primary_key=True)
    maDeThi = Column(Integer, ForeignKey("dethi.maDeThi", ondelete="CASCADE"), primary_key=True)
    ngayGiao = Column(DateTime, default=datetime.utcnow)
