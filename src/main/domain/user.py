class User:
    def __init__(self, username, password, email, role='student'):
        self.username = username
        self.password = password  # Trong thực tế sẽ là mật khẩu đã mã hóa
        self.email = email
        self.role = role
        