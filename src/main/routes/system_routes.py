from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.main.database import get_db

router = APIRouter()

@router.get("/health")
async def system_health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "online",
            "database": "Connected Successfully!"
        }
    except Exception as e:
        return {"status": "error", "database": str(e)}