from src.main.database import SessionLocal
from src.main.domain.models import Course, Chapter

def init_cnxh():
    db = SessionLocal()
    try:
        course = db.query(Course).filter(Course.maMonHoc == 'CNXHKH').first()
        if not course:
            course = Course(
                maMonHoc='CNXHKH', 
                tenMonHoc='Chủ nghĩa xã hội khoa học', 
                moTa='Môn học nghiên cứu các quy luật chính trị - xã hội'
            )
            db.add(course)
            db.flush()
        
        chapters = [ 
            'Chương 1: Nhập môn CNXHKH', 
            'Chương 2: Sứ mệnh lịch sử của giai cấp công nhân', 
            'Chương 3: Chủ nghĩa xã hội và thời kỳ quá độ', 
            'Chương 4: Dân chủ xã hội chủ nghĩa và nhà nước', 
            'Chương 5: Cơ cấu xã hội - giai cấp và liên minh', 
            'Chương 6: Vấn đề dân tộc và tôn giáo', 
            'Chương 7: Vấn đề gia đình trong thời kỳ quá độ' 
        ]
        
        for i, name in enumerate(chapters):
            existing = db.query(Chapter).filter(Chapter.tenChuong == name, Chapter.maMonHoc == 'CNXHKH').first()
            if not existing:
                db.add(Chapter(
                    monhoc_id=course.id, 
                    maMonHoc='CNXHKH', 
                    tenChuong=name, 
                    stt=i+1
                ))
        
        db.commit()
        print(' Đã khởi tạo môn học và đủ 7 chương CNXHKH trong database.')
    except Exception as e:
        db.rollback()
        print(f'Lỗi: {e}')
    finally:
        db.close()

if __name__ == "__main__":
    init_cnxh()
