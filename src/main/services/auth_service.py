from src.main.repositories.user_repository import UserRepository

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username, password):
        user = self.user_repo.get_user_by_username(username)
        if not user or user.password != password:
            return None
        return user
    def remove_user(self, user_id: int):
        # Bạn có thể thêm logic kiểm tra quyền ở đây 
        # (ví dụ: chỉ Admin mới được xóa)
        success = self.user_repo.delete_user(user_id)
        return success