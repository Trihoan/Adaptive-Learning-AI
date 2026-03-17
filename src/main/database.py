from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.main.config.settings import Config

# 1️ Tạo engine kết nối database
engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

# 2️ Session để thao tác DB
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3️ Base class cho các models
Base = declarative_base()


# 4️ Dependency dùng cho FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()