import os
import pandas as pd
from sqlalchemy.orm import Session
from src.main.database import SessionLocal
from src.main.domain.models import Course, Chapter, Question, Answer

# Trước khi lấy 
def import_from_excel(file_path, course_id, chapter_name, stt=1):
    """
    Import câu hỏi từ file Excel (.xlsx) vào Database.
    Cấu trúc file Excel cần có các cột:
    - question: Nội dung câu hỏi
    - a, b, c, d: Nội dung các đáp án
    - correct: Đáp án đúng (ghi chữ A, B, C, hoặc D)
    """
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return

    db: Session = SessionLocal()
    try:
        # 1. Kiểm tra/Tạo Môn học
        course = db.query(Course).filter(Course.maMonHoc == course_id).first()
        if not course:
            course = Course(maMonHoc=course_id, tenMonHoc=course_id)
            db.add(course)
            db.flush()

        # 2. Kiểm tra/Tạo Chương
        chapter = db.query(Chapter).filter(Chapter.tenChuong == chapter_name, Chapter.maMonHoc == course_id).first()
        if not chapter:
            chapter = Chapter(monhoc_id=course.id, maMonHoc=course_id, tenChuong=chapter_name, stt=stt)
            db.add(chapter)
            db.flush()

        # 3. Đọc file Excel
        print(f"📖 Đang đọc file Excel: {file_path}...")
        df = pd.read_excel(file_path)
        
        # Chuyển tên cột về chữ thường để tránh lỗi gõ hoa/thường
        df.columns = [c.lower().strip() for c in df.columns]

        for index, row in df.iterrows():
            q_text = str(row['question']).strip()
            if not q_text or q_text == 'nan': continue

            # Lưu câu hỏi
            new_q = Question(
                maChuong=chapter.maChuong,
                noiDung=q_text,
                doKho=1,
                loaiCauHoi="single"
            )
            db.add(new_q)
            db.flush()

            # Lưu các đáp án
            ans_map = {
                'A': str(row['a']).strip(),
                'B': str(row['b']).strip(),
                'C': str(row['c']).strip(),
                'D': str(row['d']).strip()
            }
            
            correct_ans = str(row['correct']).strip().upper()

            for label, content in ans_map.items():
                is_correct = (label == correct_ans)
                new_ans = Answer(
                    maCauHoi=new_q.maCauHoi,
                    noiDungDapAn=content,
                    laDapAnDung=is_correct
                )
                db.add(new_ans)
            
            print(f"  + Row {index+2}: Đã thêm '{q_text[:30]}...'")

        db.commit()
        print("✅ Đã hoàn tất nhập dữ liệu từ Excel.")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Script này dùng để import dữ liệu từ file Excel (.xlsx).")
    print("Yêu cầu file có các cột: question, a, b, c, d, correct")
    # Ví dụ: import_from_excel("data/quiz_toan.xlsx", "TOAN1", "Chương 1: Đạo hàm")
