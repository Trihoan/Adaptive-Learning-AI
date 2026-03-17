from fastapi import HTTPException
from src.main.services.auth_service import AuthService
from src.main.repositories.user_repository import UserRepository
from src.main.domain.models import User
from src.main.services.security_service import hash_password # Giả sử bạn có hàm hash

class AuthController:
    def __init__(self, db):
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(self.user_repo)

    async def register(self, username, password, confirm_password, fullname, student_id):
        # 1. Kiểm tra mật khẩu khớp nhau
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Mật khẩu xác nhận không khớp")

        # 2. Kiểm tra tên đăng nhập
        if self.user_repo.find_by_username(username):
            raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")

        # 3. Kiểm tra Mã sinh viên
        if self.user_repo.find_by_id(student_id):
            raise HTTPException(status_code=400, detail="Mã sinh viên này đã được đăng ký")

        # 4. Tạo User mới
        new_user = User(
            id=student_id,           # maSV
            username=username, 
            password=hash_password(password), 
            role="student"           # Mặc định là student
            # hoTen=fullname         # Mở comment nếu Model có cột hoTen
        )
        self.user_repo.save_user(new_user)
        return {"status": "success", "message": "Đăng ký thành công!"}

    async def login(self, username, password):
        user = self.auth_service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
        return user