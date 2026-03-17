from src.main.repositories.user_repository import UserRepository
from src.main.domain.models import User
from src.main.services.security_service import verify_password


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str):
        """
        Xác thực đăng nhập
        """
        user = self.user_repo.find_by_username(username)

        if not user:
            return None

        # kiểm tra password
        if not verify_password(password, user.password):
            return None

        return user


    def remove_user(self, user_id_to_delete: int, current_user: User):
        """
        user_id_to_delete: ID của người bị xóa
        current_user: User đang thực hiện hành động
        """

        # 1️⃣ kiểm tra quyền admin
        if current_user.role != "admin":
            return False, "Bạn không có quyền thực hiện hành động này!"

        # 2️⃣ ngăn admin tự xóa chính mình
        if current_user.id == user_id_to_delete:
            return False, "Admin không thể tự xóa chính mình!"

        # 3️⃣ xóa user
        success = self.user_repo.delete_user(user_id_to_delete)

        if success:
            return True, "Xóa người dùng thành công."

        return False, "Không tìm thấy người dùng."