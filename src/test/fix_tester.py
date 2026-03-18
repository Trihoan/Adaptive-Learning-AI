import pymysql
import bcrypt

def check_and_fix_tester():
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            port=3306,
            database='adaptive_learning_db'
        )
        cursor = conn.cursor()
        
        # 1. Check current hash
        cursor.execute("SELECT matKhau FROM nguoihoc WHERE tenDangNhap='tester'")
        result = cursor.fetchone()
        
        if result:
            current_hash = result[0]
            print(f"🔍 Hash hiện tại: {current_hash}")
            
            # 2. Update to a guaranteed valid bcrypt hash
            password = "12345678"
            salt = bcrypt.gensalt()
            new_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            print(f"🛠️ Đang cập nhật lại hash mới cho 'tester'...")
            cursor.execute(
                "UPDATE nguoihoc SET matKhau=%s WHERE tenDangNhap='tester'",
                (new_hash,)
            )
            conn.commit()
            print(f"✅ Đã cập nhật xong! Hãy thử đăng nhập lại.")
        else:
            print("❌ Không tìm thấy user 'tester'.")
            
        conn.close()
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    check_and_fix_tester()
