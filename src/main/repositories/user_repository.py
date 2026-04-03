from sqlalchemy.orm import Session
from src.main.domain.models import User

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def find_by_username(self, username: str):
        return self.db.query(User).filter(User.tenDangNhap == username).first()

    def find_by_id(self, user_id: str): 
        return self.db.query(User).filter(User.maSV == user_id).first()

    def save_user(self, user: User):
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: str): 
        user = self.find_by_id(user_id)

        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True

    def get_all_users(self):
        return self.db.query(User).all()