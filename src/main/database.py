from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.main.config.settings import Config


connect_args = {}
if "tidbcloud.com" in Config.SQLALCHEMY_DATABASE_URI:
    connect_args["ssl"] = {"fake_flag_to_enable_tls": True}


engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
