import os
import sys
from src.main.ai.importers.word_importer import import_from_word

def run_importer():
    """
    Công cụ hỗ trợ nhập dữ liệu môn học từ file Word (.docx)
    """
    # --- CẤU HÌNH Ở ĐÂY ---
    # 1. Tên file trong thư mục 'data/'
    filename = "test_quiz.docx" 
    
    # 2. Mã môn học (Ví dụ: 'TOAN_01', 'CNXHKH', 'TTHCM')
    course_id = "TEST_SUBJECT"
    
    # 3. Chế độ Chạy thử (True: Chỉ kiểm tra | False: Lưu thật vào Database)
    dry_run = True
    # ----------------------

    # Đường dẫn đầy đủ đến file trong thư mục data/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    file_path = os.path.join(base_dir, "data", filename)

    print("="*60)
    print(f"🚀 CÔNG CỤ NHẬP DỮ LIỆU MÔN HỌC")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"❌ LỖI: Không tìm thấy file tại: {file_path}")
        print(f"💡 Hướng dẫn: Bạn hãy bỏ file Word vào thư mục 'data/' ở gốc dự án.")
        return

    print(f"📂 File nguồn: {file_path}")
    print(f"📚 Mã môn học: {course_id}")
    print(f"⚙️  Chế độ: {'🧪 CHẠY THỬ (An toàn)' if dry_run else '🔥 LƯU THẬT (Ghi vào DB)'}")
    print("-" * 60)

    # Thực hiện import
    import_from_word(file_path, course_id, dry_run=dry_run)

    print("-" * 60)
    if dry_run:
        print("✅ Kết thúc kiểm tra. Nếu mọi thứ OK, hãy sửa 'dry_run = False' để lưu thật.")
    else:
        print("✅ Đã nạp dữ liệu thành công vào Database.")
    print("="*60)

if __name__ == "__main__":
    run_importer()
