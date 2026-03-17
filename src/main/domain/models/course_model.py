from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from src.main.database import Base
class Course(Base):
    __tablename__ = "MonHoc" # Đổi từ 'courses' thành 'MonHoc'

    # Ánh xạ: id -> maMonHoc (String)
    id = Column("maMonHoc", String(20), primary_key=True, index=True)
    title = Column("tenMonHoc", String(100), nullable=False)
    description = Column("moTa", Text)
    
    # Lưu ý: Bảng MonHoc trong SQL của bạn không có image_url
    # image_url = Column(String(255)) 

    results = relationship("StudyResult", back_populates="course")