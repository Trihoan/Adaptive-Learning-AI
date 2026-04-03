from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from src.main.database import Base

class NhatKyHeThong(Base):
    __tablename__ = "nhatkyhethong"

    maLog = Column(Integer, primary_key=True, autoincrement=True)
    maAdmin = Column(String(20), ForeignKey("nguoihoc.maSV"))
    hanhDong = Column(String(255))
    thoiGian = Column(DateTime, default=datetime.utcnow)
