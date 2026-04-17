from src.main.database import SessionLocal
from src.main.domain.models import User, Exam
from datetime import datetime, timedelta

def simulate():
    db = SessionLocal()
    try:
        # Lấy user admin (tài khoản bạn đang dùng)
        user = db.query(User).filter(User.role == 'admin').first()
        if not user:
            print("❌ Không tìm thấy user admin.")
            return

        masv = user.maSV
        print(f"🔄 Đang tạo dữ liệu giả lập cho: {masv}...")

        # Xóa các bài thi cũ
        db.query(Exam).filter(Exam.maSV == masv).delete()

        # Tạo 5 bài thi thể hiện sự tiến bộ
        # Điểm: 5.5, 6.5, 7.5, 8.5, 9.5
        # Thời gian học: tăng dần từ 2h lên 6h
        for i in range(5):
            score = 5.5 + i
            start_time = datetime.utcnow() - timedelta(hours=2+i)
            end_time = datetime.utcnow()
            db.add(Exam(
                maSV=masv,
                maChuong=i+1,
                diem=score,
                thoiGianBatDau=start_time,
                thoiGianKetThuc=end_time
            ))
        
        # Cập nhật thông số học tập thực tế cho User
        user.avg_score = 7.5
        user.total_time = 4.5 # Giờ học trung bình
        
        db.commit()
        print(f"✅ Đã giả lập xong. Hiện tại {masv} đang có điểm trung bình là 7.5 và 4.5h học.")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    simulate()
