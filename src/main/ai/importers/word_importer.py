import os
import re
from docx import Document
from sqlalchemy.orm import Session
from src.main.database import SessionLocal
from src.main.domain.models import Course, Chapter, Question, Answer

def import_from_word(file_path, course_id, default_chapter_name=None, dry_run=False):
    """
    Import câu hỏi từ file Word (.docx) vào Database.
    Tự động nhận diện Chương nếu có dòng bắt đầu bằng "Chương X:" hoặc "Chapter X:"
    - dry_run: Nếu True, chỉ in ra kết quả kiểm tra, không lưu vào DB.
    """
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy file: {file_path}")
        return

    if dry_run:
        print("🧪 [CHẾ ĐỘ CHẠY THỬ] - Dữ liệu sẽ KHÔNG được lưu vào Database.")

    db: Session = SessionLocal()
    try:
        # 1. Kiểm tra/Tạo Môn học
        course = None
        if not dry_run:
            course = db.query(Course).filter(Course.maMonHoc == course_id).first()
            if not course:
                course = Course(maMonHoc=course_id, tenMonHoc=course_id)
                db.add(course)
                db.flush()
        else:
            print(f"🔍 Kiểm tra môn học: {course_id}")

        # 2. Đọc file Word
        doc = Document(file_path)
        current_chapter = None
        
        # Nếu có truyền chapter mặc định
        if default_chapter_name:
            if not dry_run:
                current_chapter = db.query(Chapter).filter(
                    Chapter.tenChuong == default_chapter_name, 
                    Chapter.maMonHoc == course_id
                ).first()
                if not current_chapter:
                    current_chapter = Chapter(monhoc_id=course.id, maMonHoc=course_id, tenChuong=default_chapter_name, stt=1)
                    db.add(current_chapter)
                    db.flush()
            else:
                print(f"🔍 Sử dụng chương mặc định: {default_chapter_name}")

        current_q = None
        answers_list = []
        correct_label = None

        print(f"📖 Đang xử lý file: {file_path}...")

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue

            # A. Nhận diện tiêu đề CHƯƠNG
            chapter_match = re.match(r'^(Chương|Chapter)\s*(\d+)[:.-]\s*(.*)', text, re.I)
            if chapter_match:
                if current_q and answers_list and correct_label:
                    save_question(db, current_chapter.maChuong if current_chapter else 0, current_q, answers_list, correct_label, dry_run)
                    current_q = None

                ch_no = chapter_match.group(2)
                ch_name = text
                
                if not dry_run:
                    current_chapter = db.query(Chapter).filter(
                        Chapter.tenChuong == ch_name, 
                        Chapter.maMonHoc == course_id
                    ).first()
                    
                    if not current_chapter:
                        current_chapter = Chapter(monhoc_id=course.id, maMonHoc=course_id, tenChuong=ch_name, stt=int(ch_no))
                        db.add(current_chapter)
                        db.flush()
                        print(f"📁 Đã tạo chương mới: {ch_name}")
                    else:
                        print(f"📂 Đã nhận diện chương cũ: {ch_name}")
                else:
                    print(f"📁 [TEST] Phát hiện chương: {ch_name}")
                continue

            # B. Nhận diện CÂU HỎI
            if re.match(r'^(Câu|Question)\s*\d+[:.]', text, re.I):
                if current_q and answers_list and correct_label:
                    save_question(db, current_chapter.maChuong if current_chapter else 0, current_q, answers_list, correct_label, dry_run)
                
                current_q = re.sub(r'^(Câu|Question)\s*\d+[:.]', '', text, flags=re.I).strip()
                answers_list = []
                correct_label = None

            # C. Nhận diện ĐÁP ÁN
            elif re.match(r'^[A-D][:.]', text, re.I):
                label = text[0].upper()
                content = text[2:].strip()
                answers_list.append({"label": label, "text": content})

            # D. Nhận diện ĐÁP ÁN ĐÚNG
            elif "Đáp án:" in text or "Chọn:" in text:
                match = re.search(r'[A-D]', text.split(":")[-1])
                if match:
                    correct_label = match.group().upper()

        # Lưu câu hỏi cuối cùng
        if current_q and answers_list and correct_label:
            save_question(db, current_chapter.maChuong if current_chapter else 0, current_q, answers_list, correct_label, dry_run)

        if not dry_run:
            db.commit()
            print(f"✅ Đã hoàn tất nhập dữ liệu vào Database.")
        else:
            print(f"✅ [TEST] Kiểm tra hoàn tất. Không có lỗi định dạng.")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

def save_question(db, chapter_id, q_text, ans_list, correct_label, dry_run=False):
    """Lưu 1 câu hỏi và các đáp án"""
    if dry_run:
        print(f"  + [TEST] Câu hỏi: {q_text[:50]}... ({len(ans_list)} đáp án, Đúng: {correct_label})")
        return

    new_q = Question(maChuong=chapter_id, noiDung=q_text, doKho=1, loaiCauHoi="single")
    db.add(new_q)
    db.flush()

    for ans in ans_list:
        is_correct = (ans["label"] == correct_label)
        new_ans = Answer(maCauHoi=new_q.maCauHoi, noiDungDapAn=ans["text"], laDapAnDung=is_correct)
        db.add(new_ans)
    print(f"  + Đã thêm: {q_text[:50]}...")

if __name__ == "__main__":
    # Ví dụ cách dùng:
    # import_from_word("data/test_quiz.docx", "TTHCM", "Chương 1: Cơ sở hình thành")
    print("Script này dùng để import dữ liệu từ file Word (.docx).")
    print("Bạn cần cài đặt: pip install python-docx")
