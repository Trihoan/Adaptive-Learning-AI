from sqlalchemy import create_engine, text
from src.main.config.settings import Config

def fix_database():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    
    with engine.begin() as conn: # Sử dụng begin() để tự động commit
        print("--- Đang kiểm tra và cập nhật cấu trúc bảng KetQuaHocTap ---")
        
        # Thêm các cột thiếu vào bảng KetQuaHocTap
        columns_to_add = [
            ("maMonHoc", "VARCHAR(20)"),
            ("diemTB", "FLOAT"),
            ("thoiGianLamBai", "FLOAT DEFAULT 0"),
            ("chuDe", "VARCHAR(100)"),
            ("thoiGianNop", "DATETIME DEFAULT CURRENT_TIMESTAMP")
        ]
        
        for col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE KetQuaHocTap ADD COLUMN {col_name} {col_type}"))
                print(f"✅ Đã thêm cột '{col_name}'")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"ℹ️ Cột '{col_name}' đã tồn tại.")
                else:
                    print(f"⚠️ Không thể thêm cột '{col_name}': {e}")
            
        print("--- Hoàn tất cập nhật ---")

if __name__ == "__main__":
    fix_database()
