# src/main/repositories/user_repository.py
from sqlalchemy.orm import Session
from src.main.domain.models import User

class UserRepository: 
    def __init__(self, db: Session):
        self.db = db # Nhận session database từ Controller truyền vào

    def find_by_username(self, username: str):
        # Dùng SQLAlchemy thay vì Pandas
        return self.db.query(User).filter(User.username == username).first()

    def save_user(self, user_obj: User):
        # Lưu vào MySQL
        self.db.add(user_obj)
        self.db.commit()
        self.db.refresh(user_obj)
        return user_obj

    def delete_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False