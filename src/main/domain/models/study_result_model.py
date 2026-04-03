from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from src.main.database import Base


class StudyResult(Base):
    __tablename__ = "ketquahoctap"

    maKetQua = Column(Integer, primary_key=True, autoincrement=True)
    maSV = Column(String(20), ForeignKey("nguoihoc.maSV", ondelete="CASCADE"))
    maCauHoi = Column(Integer, ForeignKey("cauhoi.maCauHoi", ondelete="CASCADE"))
    maDapAnChon = Column(Integer, ForeignKey("dapan.maDapAn"))
    thoiGianLam = Column(DateTime, default=datetime.utcnow)
    trangThai = Column(Boolean)
    maBaiKiemTra = Column(Integer, ForeignKey("baikiemtra.maBaiKiemTra", ondelete="CASCADE"))

    user = relationship("User", back_populates="results")
    question = relationship("Question", back_populates="results")
    chosen_answer = relationship("Answer", back_populates="results")
    exam = relationship("Exam", back_populates="results")