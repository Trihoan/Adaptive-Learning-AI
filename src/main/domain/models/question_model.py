from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from src.main.database import Base
from datetime import datetime

# Association Table for Many-to-Many relationship between Exam and Question
class QuizQuestionAssociation(Base):
    __tablename__ = "chitietbaikiemtra"

    exam_id = Column("maBaiKiemTra", Integer, ForeignKey("BaiKiemTra.maBaiKiemTra"), primary_key=True)
    question_id = Column("maCauHoi", Integer, ForeignKey("CauHoi.maCauHoi"), primary_key=True)

class Exam(Base):
    __tablename__ = "BaiKiemTra"

    id = Column("maBaiKiemTra", Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column("maSV", String(20), ForeignKey("NguoiHoc.maSV"))
    chapter_id = Column("maChuong", Integer, ForeignKey("chuonghoc.maChuong"))
    start_time = Column("thoiGianBatDau", DateTime, default=datetime.utcnow)
    end_time = Column("thoiGianKetThuc", DateTime)
    score = Column("diem", Float)

    user = relationship("User", backref="exams")
    chapter = relationship("Chapter", back_populates="quizzes")
    questions = relationship("Question", secondary="chitietbaikiemtra", back_populates="exams")

class Question(Base):
    __tablename__ = "CauHoi"

    id = Column("maCauHoi", Integer, primary_key=True, index=True, autoincrement=True)
    chapter_id = Column("maChuong", Integer, ForeignKey("chuonghoc.maChuong"))
    content = Column("noiDung", Text, nullable=False)
    difficulty = Column("doKho", Integer)

    chapter = relationship("Chapter", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    exams = relationship("Exam", secondary="chitietbaikiemtra", back_populates="questions")

class Answer(Base):
    __tablename__ = "dapan"

    id = Column("maDapAn", Integer, primary_key=True, index=True, autoincrement=True)
    question_id = Column("maCauHoi", Integer, ForeignKey("CauHoi.maCauHoi"))
    content = Column("noiDungDapAn", Text, nullable=False)
    is_correct = Column("laDapAnDung", Boolean, default=False)

    question = relationship("Question", back_populates="answers")
