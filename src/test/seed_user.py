import pymysql
import bcrypt

def check_and_create_user(username, password):
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3306,
            database='adaptive_learning_db'
        )
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT tenDangNhap FROM nguoihoc WHERE tenDangNhap=%s", (username,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Người dùng '{username}' đã tồn tại.")
        else:
            print(f"🛠️ Đang tạo người dùng '{username}'...")
            # Hashing with bcrypt
            salt = bcrypt.gensalt()
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            # Dựa trên model User: maSV (String 20), tenDangNhap, matKhau, role
            cursor.execute(
                "INSERT INTO nguoihoc (maSV, tenDangNhap, matKhau, role) VALUES (%s, %s, %s, %s)",
                ('SV_TESTER', username, hashed_pw, 'student')
            )
            conn.commit()
            print(f"✅ Đã tạo thành công người dùng '{username}' với pass: {password}")
            
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    check_and_create_user('tester', '12345678')
