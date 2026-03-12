from fastapi import FastAPI
from src.main.config.settings import Config # Đường dẫn đã rút gọn, bỏ chữ 'main' thừa

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Dự án Adaptive Learning đã sẵn sàng", "db": Config.SQLALCHEMY_DATABASE_URI}