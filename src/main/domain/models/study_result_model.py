from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from src.main.database import Base


class StudyResult(Base):
    __tablename__ = "KetQuaHocTap"

    id = Column("maKetQua", Integer, primary_key=True, index=True)

    user_id = Column("maSV", String(20), ForeignKey("nguoihoc.maSV"))
    course_id = Column("maMonHoc", String(20), ForeignKey("MonHoc.maMonHoc"))

    score = Column("diemTB", Float)
    time_spent = Column(Float, default=0.0)
    created_at = Column("thoiGianLam", DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="results")
    course = relationship("Course", back_populates="results")