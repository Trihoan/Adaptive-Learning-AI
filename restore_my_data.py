from sqlalchemy import create_engine, text
import pymysql

# --- CẤU HÌNH KẾT NỐI TIDB CLOUD ---
TIDB_USER = "cDD5zZgTwC6PzXq.root"
TIDB_PASSWORD = "<PASSWORD>" 
TIDB_HOST = "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com"
TIDB_PORT = "4000"
TIDB_DB = "adaptive_learning_db"

TIDB_URI = f"mysql+pymysql://{TIDB_USER}:{TIDB_PASSWORD}@{TIDB_HOST}:{TIDB_PORT}/{TIDB_DB}?ssl_verify_cert=true&ssl_verify_identity=true"

def restore_data():
    try:
        engine = create_engine(TIDB_URI, connect_args={"ssl": {"fake_flag_to_enable_tls": True}})
        with engine.connect() as conn:
            print("--- ĐANG KHÔI PHỤC DỮ LIỆU VỀ MÃ CHƯƠNG 1-5 ---")
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            
            # 1. Dọn đường: Chuyển môn CNXHKH (đang chiếm 1-7) sang mã 101-107
            print("Đang dời môn CNXHKH sang mã tạm...")
            for i in range(1, 8):
                new_id = 100 + i
                conn.execute(text("UPDATE cauhoi SET maChuong = :nid WHERE maChuong = :oid"), {"nid": new_id, "oid": i})
                conn.execute(text("UPDATE chuonghoc SET maChuong = :nid WHERE maChuong = :oid"), {"nid": new_id, "oid": i})

            # 2. Khôi phục 5 chương TTHCM vào mã 1-5
            print("Đang khôi phục 5 chương TTHCM...")
            tthcm_names = [
                (1, "Chương 1: Cơ sở hình thành và phát triển Tư tưởng Hồ Chí Minh"),
                (2, "Chương 2: Tư tưởng Hồ Chí Minh về độc lập dân tộc và Chủ nghĩa xã hội"),
                (3, "Chương 3: Tư tưởng Hồ Chí Minh về Đảng Cộng sản và Nhà nước"),
                (4, "Chương 4: Tư tưởng Hồ Chí Minh về đại đoàn kết dân tộc và đoàn kết quốc tế"),
                (5, "Chương 5: Tư tưởng Hồ Chí Minh về văn hóa, đạo đức, con người")
            ]
            
            # Xóa các bản ghi rác ở 1-5 (nếu có) trước khi chèn lại
            conn.execute(text("DELETE FROM chuonghoc WHERE maChuong BETWEEN 1 AND 5"))
            
            for cid, name in tthcm_names:
                conn.execute(text("INSERT INTO chuonghoc (maChuong, monhoc_id, maMonHoc, tenChuong, stt) VALUES (:id, 3, 'TTHCM', :name, :stt)"),
                           {"id": cid, "name": name, "stt": cid})

            # 3. Dời 200 câu hỏi (hiện đang ở chương 3 hoặc mã chương 8-12) về đúng 1-5
            # Logic: Nếu câu hỏi có từ khóa của chương nào thì về chương đó
            print("Đang dời câu hỏi về đúng 5 chương đầu...")
            # Chương 1
            conn.execute(text("UPDATE cauhoi SET maChuong = 1 WHERE (maChuong = 3 OR maChuong BETWEEN 8 AND 12) AND (noiDung LIKE '%hình thành%' OR noiDung LIKE '%nguồn gốc%')"))
            # Chương 2
            conn.execute(text("UPDATE cauhoi SET maChuong = 2 WHERE (maChuong = 3 OR maChuong BETWEEN 8 AND 12) AND (noiDung LIKE '%độc lập%' OR noiDung LIKE '%cứu nước%')"))
            # Chương 3
            conn.execute(text("UPDATE cauhoi SET maChuong = 3 WHERE (maChuong = 3 OR maChuong BETWEEN 8 AND 12) AND (noiDung LIKE '%Đảng%' OR noiDung LIKE '%Nhà nước%')"))
            # Chương 4
            conn.execute(text("UPDATE cauhoi SET maChuong = 4 WHERE (maChuong = 3 OR maChuong BETWEEN 8 AND 12) AND (noiDung LIKE '%đoàn kết%' OR noiDung LIKE '%Mặt trận%')"))
            # Chương 5
            conn.execute(text("UPDATE cauhoi SET maChuong = 5 WHERE (maChuong = 3 OR maChuong BETWEEN 8 AND 12) AND (noiDung LIKE '%văn hóa%' OR noiDung LIKE '%đạo đức%')"))

            # 4. Trả môn CNXHKH về mã 6-12 (để không trùng 1-5)
            print("Đang sắp xếp lại môn CNXHKH...")
            for i in range(1, 8):
                old_temp_id = 100 + i
                new_final_id = 5 + i # Sẽ là 6, 7, 8, 9, 10, 11, 12
                conn.execute(text("UPDATE cauhoi SET maChuong = :nid WHERE maChuong = :oid"), {"nid": new_final_id, "oid": old_temp_id})
                conn.execute(text("UPDATE chuonghoc SET maChuong = :nid WHERE maChuong = :oid"), {"nid": new_final_id, "oid": old_temp_id})

            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()
            print("--- PHỤC HỒI THÀNH CÔNG ---")
            print("TTHCM: Chương 1-5 | CNXHKH: Chương 6-12")

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    restore_data()
