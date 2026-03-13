from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.main.config.settings import Config

# 1. Tạo Engine (Động cơ kết nối)
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# 2. Tạo SessionLocal (Nơi thực hiện các truy vấn)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Lớp cơ sở để định nghĩa các bảng (Models)
Base = declarative_base()

# Hàm bổ trợ để lấy DB cho mỗi request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()