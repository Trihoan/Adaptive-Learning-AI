import pymysql

def check_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='', # Để trống nếu dùng XAMPP mặc định
            database='adaptive_learning_db',
            port=3306 
        )
        print("✅ Tuyệt vời! Python đã kết nối thành công tới MySQL Workbench.")
        connection.close()
    except Exception as e:
        print(f"❌ Kết nối thất bại. Lỗi: {e}")

if __name__ == "__main__":
    check_connection()