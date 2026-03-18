from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from src.main.database import Base


class User(Base):
    __tablename__ = "nguoihoc"

    # maSV là khóa chính
    maSV = Column(String(20), primary_key=True, index=True, autoincrement=False)
    
    # username ánh xạ vào tenDangNhap
    username = Column("tenDangNhap", String(50), unique=True, nullable=False)
    
    # password ánh xạ vào matKhau
    password = Column("matKhau", String(255), nullable=False)
    
    hoTen = Column("hoTen", String(100), nullable=True)
    email = Column("email", String(100), unique=True, nullable=True)
    role = Column(String(20), default="student")
    ngayTao = Column("ngayTao", DateTime, default=datetime.utcnow)

    # dữ liệu AI
    avg_score = Column(Float, default=0.0)
    total_time = Column(Float, default=0.0)

    results = relationship(
        "StudyResult",
        back_populates="user",
        cascade="all, delete-orphan"
    )


