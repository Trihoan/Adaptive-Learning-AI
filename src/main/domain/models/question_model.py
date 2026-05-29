from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from src.main.database import Base
from datetime import datetime

# Association Table for Many-to-Many relationship between Exam and Question
class QuizQuestionAssociation(Base):
    __tablename__ = "chitietbaikiemtra"

    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.maBaiKiemTra"), primary_key=True)
    maCauHoi = Column(Integer, ForeignKey("cauhoi.maCauHoi"), primary_key=True)
    maDapAnChon = Column(Integer, ForeignKey("dapan.maDapAn"), nullable=True)

class Exam(Base):
    __tablename__ = "baikiemtra"

    maBaiKiemTra = Column(Integer, primary_key=True, autoincrement=True)
    maSV = Column(String(20), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"))
    maChuong = Column(Integer, ForeignKey("chuonghoc.maChuong", ondelete="CASCADE"), nullable=True)
    maDeThi = Column(Integer, ForeignKey("dethi.maDeThi", ondelete="CASCADE"), nullable=True)
    thoiGianBatDau = Column(DateTime, default=datetime.utcnow)
    thoiGianKetThuc = Column(DateTime)
    diem = Column(Float)

    user = relationship("User", back_populates="exams")
    chapter = relationship("Chapter", back_populates="exams")
    quiz = relationship("Quiz", back_populates="exams")
    questions = relationship("Question", secondary="chitietbaikiemtra", back_populates="exams")
    results = relationship("StudyResult", back_populates="exam")

class Question(Base):
    __tablename__ = "cauhoi"

    maCauHoi = Column(Integer, primary_key=True, autoincrement=True)
    maChuong = Column(Integer, ForeignKey("chuonghoc.maChuong", ondelete="CASCADE"), nullable=True)
    maDeThi = Column(Integer, ForeignKey("dethi.maDeThi", ondelete="CASCADE"), nullable=True)
    noiDung = Column(Text, nullable=False)
    doKho = Column(Integer)
    loaiCauHoi = Column(String(20), default="single")
    giaiThich = Column(Text)

    chapter = relationship("Chapter", back_populates="questions")
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    exams = relationship("Exam", secondary="chitietbaikiemtra", back_populates="questions")
    results = relationship("StudyResult", back_populates="question")

class Answer(Base):
    __tablename__ = "dapan"

    maDapAn = Column(Integer, primary_key=True, autoincrement=True)
    maCauHoi = Column(Integer, ForeignKey("cauhoi.maCauHoi"))
    noiDungDapAn = Column(Text, nullable=False)
    laDapAnDung = Column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")
    results = relationship("StudyResult", back_populates="chosen_answer")

class QuizDraft(Base):
    __tablename__ = "quiz_drafts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maSV = Column(String(20, collation='utf8mb4_general_ci'), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"))
    topic = Column(String(100))
    question_ids = Column(Text) # Comma separated
    answers = Column(Text) # JSON string
    seconds_elapsed = Column(Integer, default=0)
    current_question = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
