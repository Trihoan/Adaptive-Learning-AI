from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.main.database import Base

class Chapter(Base):
    __tablename__ = "chuonghoc"

    id = Column("maChuong", Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column("maMonHoc", String(20), ForeignKey("MonHoc.maMonHoc"))
    title = Column("tenChuong", String(255), nullable=False)
    order = Column("stt", Integer, default=1) # order field 'stt'

    course = relationship("Course", backref="chapters")
    questions = relationship("Question", back_populates="chapter", cascade="all, delete-orphan")
    quizzes = relationship("Exam", back_populates="chapter", cascade="all, delete-orphan")