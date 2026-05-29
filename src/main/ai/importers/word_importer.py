import os
import re
from docx import Document
from sqlalchemy.orm import Session
from src.main.database import SessionLocal
from src.main.domain.models import Course, Chapter, Question, Answer

import random

def import_from_word(file_path, course_id, default_chapter_name=None, dry_run=False, is_exam=False):
    """
    Import câu hỏi từ file Word (.docx) vào Database.
    - is_exam: Nếu True, câu hỏi sẽ được gắn vào một Đề ôn tập (Quiz model) thay vì Chương.
    """
    if not os.path.exists(file_path):
        print(f"Không tìm thấy file: {file_path}")
        return

    db: Session = SessionLocal()
    try:
        # 1. Kiểm tra/Tạo Môn học
        course = db.query(Course).filter(Course.maMonHoc == course_id).first()
        if not course and not dry_run:
            course = Course(maMonHoc=course_id, tenMonHoc=course_id)
            db.add(course)
            db.flush()

        # 2. Xử lý target (Quiz hoặc Chapter)
        target_quiz_id = None
        current_chapter = None

        if is_exam:
            from src.main.domain.models import Quiz
            # Tạo một đề ôn tập mới dựa trên tên file hoặc ngày tháng
            quiz_name = default_chapter_name or f"Đề nhập từ Word ({os.path.basename(file_path)})"
            if not dry_run:
                new_quiz = Quiz(tenDeThi=quiz_name, monhoc_id=course.id, maMonHoc=course_id)
                db.add(new_quiz)
                db.flush()
                target_quiz_id = new_quiz.maDeThi
                print(f"📝 Đã tạo đề ôn tập mới: {quiz_name}")
        elif default_chapter_name:
            if not dry_run:
                current_chapter = db.query(Chapter).filter(
                    Chapter.tenChuong == default_chapter_name, 
                    Chapter.maMonHoc == course_id
                ).first()
                if not current_chapter:
                    current_chapter = Chapter(monhoc_id=course.id, maMonHoc=course_id, tenChuong=default_chapter_name, stt=1)
                    db.add(current_chapter)
                    db.flush()

        doc = Document(file_path)
        current_q = None
        answers_list = []
        correct_label = None

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text: continue

            # A. Nhận diện tiêu đề CHƯƠNG (Chỉ dùng nếu không phải import vào Đề thi)
            if not is_exam:
                chapter_match = re.match(r'^(Chương|Chapter)\s*(\d+)[:.-]\s*(.*)', text, re.I)
                if chapter_match:
                    if current_q and answers_list and correct_label:
                        save_question(db, current_chapter.maChuong if current_chapter else 0, None, current_q, answers_list, correct_label, dry_run)
                        current_q = None

                    ch_no = chapter_match.group(2)
                    ch_name = text
                    if not dry_run:
                        current_chapter = db.query(Chapter).filter(Chapter.tenChuong == ch_name, Chapter.maMonHoc == course_id).first()
                        if not current_chapter:
                            current_chapter = Chapter(monhoc_id=course.id, maMonHoc=course_id, tenChuong=ch_name, stt=int(ch_no))
                            db.add(current_chapter)
                            db.flush()
                    continue

            # B. Nhận diện CÂU HỎI
            if re.match(r'^(Câu|Question)\s*\d+[:.]', text, re.I):
                if current_q and answers_list and correct_label:
                    save_question(db, current_chapter.maChuong if current_chapter else None, target_quiz_id, current_q, answers_list, correct_label, dry_run)
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
            save_question(db, current_chapter.maChuong if current_chapter else None, target_quiz_id, current_q, answers_list, correct_label, dry_run)

        if not dry_run:
            db.commit()
            print(f"✅ Đã hoàn tất nhập dữ liệu.")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

def save_question(db, chapter_id, quiz_id, q_text, ans_list, correct_label, dry_run=False):
    """Lưu 1 câu hỏi và các đáp án với độ khó ngẫu nhiên"""
    if dry_run: return

    # Random độ khó từ 1 đến 3 nếu không xác định
    diff_level = random.randint(1, 3)

    new_q = Question(
        maChuong=chapter_id, 
        maDeThi=quiz_id,
        noiDung=q_text, 
        doKho=diff_level, 
        loaiCauHoi="single"
    )
    db.add(new_q)
    db.flush()

    for ans in ans_list:
        is_correct = (ans["label"] == correct_label)
        new_ans = Answer(maCauHoi=new_q.maCauHoi, noiDungDapAn=ans["text"], laDapAnDung=is_correct)
        db.add(new_ans)


if __name__ == "__main__":
    # Ví dụ cách dùng:
    # import_from_word("data/test_quiz.docx", "TTHCM", "Chương 1: Cơ sở hình thành")
    print("Script này dùng để import dữ liệu từ file Word (.docx).")
    print("Bạn cần cài đặt: pip install python-docx")
