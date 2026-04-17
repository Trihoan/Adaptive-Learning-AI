from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from src.main.database import Base
class Course(Base):
    __tablename__ = "monhoc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    maMonHoc = Column(String(20), unique=True)
    tenMonHoc = Column(String(100), nullable=False)
    moTa = Column(Text)

    # Relationships
    chapters = relationship("Chapter", back_populates="course", cascade="all, delete-orphan")
    learning_paths = relationship("ChiTietLoTrinh", back_populates="course")
    user_skills = relationship("UserSkill", back_populates="course", cascade="all, delete-orphan")

class LoTrinh(Base):
    __tablename__ = "lotrinh"

    maLoTrinh = Column(Integer, primary_key=True, autoincrement=True)
    maSV = Column(String(20), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"))
    tenLoTrinh = Column(String(100))
    ngayBatDau = Column(DateTime)
    trangThai = Column(Integer, default=0)

    user = relationship("User", back_populates="learning_paths")
    details = relationship("ChiTietLoTrinh", back_populates="learning_path", cascade="all, delete-orphan")

class ChiTietLoTrinh(Base):
    __tablename__ = "chitietlotrinh"

    maLoTrinh = Column(Integer, ForeignKey("lotrinh.maLoTrinh", ondelete="CASCADE"), primary_key=True)
    monhoc_id = Column(Integer, ForeignKey("monhoc.id", ondelete="CASCADE"), primary_key=True)
    maMonHoc = Column(String(20))
    thuTuHoc = Column(Integer)
    dkHoanThanh = Column(Float, default=7.0)

    learning_path = relationship("LoTrinh", back_populates="details")
    course = relationship("Course", back_populates="learning_paths")