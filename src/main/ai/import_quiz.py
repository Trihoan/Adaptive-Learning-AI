from sqlalchemy.orm import Session
from src.main.database import SessionLocal
from src.main.domain.models import Course, Chapter, Question, Answer

def import_cnx_kh_data():
    db: Session = SessionLocal()
    try:
        # 1. Khởi tạo Môn học
        course_id = "CNXHKH"
        course = db.query(Course).filter(Course.maMonHoc == course_id).first()
        if not course:
            course = Course(
                maMonHoc=course_id,
                tenMonHoc="Chủ nghĩa xã hội khoa học",
                moTa="Môn học nghiên cứu các quy luật chính trị - xã hội"
            )
            db.add(course)
            db.flush()

        # 2. Khởi tạo Chương học
        chapter_name = "Chương 1: Nhập môn Chủ nghĩa xã hội khoa học"
        chapter = db.query(Chapter).filter(Chapter.tenChuong == chapter_name).first()
        if not chapter:
            chapter = Chapter(
                maMonHoc=course_id,
                tenChuong=chapter_name,
                stt=1
            )
            db.add(chapter)
            db.flush()

        # 3. Dữ liệu 40 câu hỏi
        QUIZ_DATA = [
            ("Đâu là phát kiến vĩ đại của C. Mác và Ph. Ăngghen?", 1, [
                ("Học thuyết giá trị thặng dư", False), ("Học thuyết về chủ nghĩa duy vật lịch sử", False),
                ("Học thuyết về sứ mệnh lịch sử của giai cấp công nhân", False), ("Tất cả các đáp án đều đúng", True)
            ]),
            ("Chọn đáp án SAI: Hạn chế cơ bản của CNXH không tưởng trước C. Mác là:", 2, [
                ("Chưa phát hiện ra được sứ mệnh lịch sử của giai cấp công nhân", False),
                ("Chưa thấy được bản chất bóc lột và quá trình phát sinh, phát triển và diệt vong tất yếu của CNTB", False),
                ("Chưa đưa ra được những luận điểm có giá trị về xã hội trong tương lai", True),
                ("Không dùng bạo lực cách mạng để xóa bỏ chế độ tư bản chủ nghĩa", False)
            ]),
            ("Tác phẩm nào đánh dấu sự ra đời của CNXH khoa học?", 1, [
                ("Chủ nghĩa đế quốc giai đoạn tột cùng của CNTB", False), ("Những nguyên lý của chủ nghĩa cộng sản", False),
                ("Tuyên ngôn của Đảng cộng sản", True), ("Tình cảnh giai cấp lao động ở Anh", False)
            ]),
            ("Tác phẩm đầu tiên mà C.Mác và Ph. Ăngghen viết chung là tác phẩm nào?", 2, [
                ("Gia đình thần thánh", True), ("Hệ tư tưởng Đức", False),
                ("Tuyên ngôn của Đảng cộng sản", False), ("Tình cảnh giai cấp lao động ở Anh", False)
            ]),
            ("Ai là người sáng lập chủ nghĩa xã hội không tưởng - phê phán?", 1, [
                ("Cả 3 tác giả (Owen, Phurie, Xanh-xi-mong)", True), ("Owen", False), ("Phurie", False), ("Xanh-xi-mong", False)
            ]),
            ("Chủ nghĩa xã hội khoa học sử dụng phương pháp luận chung nhất là:", 2, [
                ("Phương pháp duy tâm chủ quan", False), ("Phương pháp luận duy vật biện chứng và duy vật lịch sử", True),
                ("Phương pháp luận siêu hình", False), ("Phương pháp trừu tượng hóa khoa học", False)
            ]),
            ("Đáp án nào KHÔNG phải là phương pháp nghiên cứu của CNXH khoa học?", 2, [
                ("Phương pháp kết hợp lý luận với thực tiễn", False), ("Phương pháp liên ngành", False),
                ("Phương pháp logic và lịch sử", False), ("Phương pháp nghiên cứu định lượng", True)
            ]),
            ("Đối tượng nghiên cứu của CNXH khoa học là gì?", 3, [
                ("Những con đường và hình thức đấu tranh cách mạng của GCCN...", False),
                ("Những quy luật chính trị - xã hội của quá trình hình thành hình thái KT-XH cộng sản...", False),
                ("Cả 2 đáp án trên đều đúng", True)
            ]),
            ("Phát kiến nào là sự khẳng định về mặt triết học sự sụp đổ của CNTB và sự thắng lợi của CNXH?", 2, [
                ("Học thuyết giá trị thặng dư", False), ("Học thuyết sứ mệnh lịch sử của giai cấp công nhân", False),
                ("Học thuyết về chủ nghĩa duy vật biện chứng", False), ("Học thuyết về chủ nghĩa duy vật lịch sử", True)
            ]),
            ("Sự kiện lịch sử nào đã đưa CNXH từ lý luận trở thành hiện thực?", 1, [
                ("Cách mạng tháng Mười Nga", True), ("Công xã Pari", False),
                ("Phong trào công nhân Lion", False), ("Phong trào hiến chương Anh", False)
            ]),
            ("Tác phẩm nào được coi là cương lĩnh chính trị, kim chỉ nam cho phong trào công nhân quốc tế?", 1, [
                ("Bộ “Tư bản\"", False), ("Chống Đuyring", False),
                ("Phê phán cương lĩnh Gôta", False), ("Tuyên ngôn của Đảng cộng sản", True)
            ]),
            ("Tiền đề về tư tưởng lý luận trực tiếp cho sự ra đời của CNXH khoa học là:", 2, [
                ("Chủ nghĩa xã hội không tưởng - phê phán", True), ("Kinh tế chính trị tư sản cổ điển Anh", False),
                ("Triết học cổ điển Đức", False)
            ]),
            ("Với 2 phát kiến nào C.Mác và Ph. Angghen đã đưa CNXH từ không tưởng trở thành khoa học?", 2, [
                ("Học thuyết giá trị thặng dư – sứ mệnh lịch sử GCCN", False),
                ("Chủ nghĩa duy vật lịch sử - Học thuyết giá trị thặng dư", True)
            ]),
            ("Với phát kiến nào C. Mác đã đưa chủ nghĩa xã hội từ lý luận khoa học thành hiện thực sinh động?", 2, [
                ("Học thuyết giá trị thặng dư", False), ("Học thuyết về sứ mệnh lịch sử của giai cấp công nhân", True)
            ]),
            ("Chủ nghĩa xã hội được hiểu là:", 1, [
                ("Một khoa học", False), ("Phong trào thực tiễn", False),
                ("Trào lưu tư tưởng lý luận", False), ("Cả 3 đáp án trên đều đúng", True)
            ]),
            ("Hạn chế của tư tưởng xã hội chủ nghĩa không tưởng phê phán do yếu tố nào?", 2, [
                ("Điều kiện lịch sử", False), ("Hạn chế về thế giới quan nhà tư tưởng", False),
                ("Hạn chế về tầm nhìn", False), ("Tất cả các phương án trên", True)
            ]),
            ("Ai đã nhận xét: “Chủ nghĩa xã hội không tưởng không thể vạch ra được lối thoát thực sự\"?", 2, [
                ("C.Mác", False), ("V.Lênin", True)
            ]),
            ("C.Mác sinh năm bao nhiêu?", 1, [
                ("1818", True), ("1820", False), ("1883", False), ("1918", False)
            ]),
            ("Ai là người đã gắn lý luận của C.Mác với V.I.Lênin thành “Chủ nghĩa Mác - Lenin\"?", 2, [
                ("Hêghen", False), ("J.Xtalin", True), ("L. Phoiobắc", False)
            ]),
            ("Quan điểm chuyên chính vô sản là việc GCCN thực hiện kiểu tổ chức lao động cao hơn TBCN là của ai?", 3, [
                ("C.Mác", False), ("V.Lênin", True)
            ]),
            ("Trong môn học này, Chủ nghĩa xã hội khoa học được nghiên cứu theo nghĩa nào?", 2, [
                ("Nghĩa rộng", False), ("Nghĩa hẹp", True)
            ]),
            ("“Tuyên ngôn của Đảng Cộng sản\" được soạn thảo bởi ai?", 1, [
                ("C.Mác", False), ("C.Mác và Ph.Ăngghen", True), ("Ph.Ăngghen", False)
            ]),
            ("Phát minh nào KHÔNG phải là tiền đề khoa học tự nhiên cho sự ra đời của CNXH khoa học?", 2, [
                ("Học thuyết tiến hóa", False), ("Học thuyết tế bào", False),
                ("Thuyết nguyên tử", True), ("Định luật bảo toàn năng lượng", False)
            ]),
            ("Chủ nghĩa Mác - Lenin được cấu thành từ 3 bộ phận nào?", 2, [
                ("Triết học Mác – Lenin, kinh tế chính trị Mác - Lenin, CNXH khoa học", True)
            ]),
            ("Tư tưởng xã hội chủ nghĩa là gì?", 2, [
                ("Hệ thống quan niệm phản ánh nhu cầu, ước mơ của các giai cấp lao động...", False),
                ("Niềm tin về chế độ không áp bức bóc lột...", False), ("C cả 3 đáp án đều đúng", True)
            ]),
            ("Những yếu tố tư tưởng xã hội chủ nghĩa xuất hiện từ khi nào?", 2, [
                ("Xuất hiện chế độ tư hữu, xuất hiện giai cấp thống trị bóc lột", True)
            ]),
            ("Nhận định GCCN tạo ra lực lượng sản xuất đồ sộ hơn tất cả các thế hệ trước gộp lại là của ai?", 2, [
                ("C.Mác và Ph.Ăngghen", True)
            ]),
            ("Hạn chế của CNXH không tưởng trước Mác là?", 2, [
                ("Chưa chỉ ra con đường đấu tranh", False), ("Chưa thấy sứ mệnh GCCN", False), ("Tất cả đáp án trên", True)
            ]),
            ("Chủ nghĩa xã hội khoa học ra đời vào thời gian nào?", 1, [
                ("Những năm 40 của thế kỉ XIX", True)
            ]),
            ("Triết học của Hêghen có đặc điểm gì?", 3, [
                ("Duy tâm nhưng chứa đựng hạt nhân hợp lý của phép biện chứng", True)
            ]),
            ("Triết học của L. Phoiơbắc có đặc điểm gì?", 3, [
                ("Siêu hình nhưng nội dung thấm nhuần quan niệm duy vật", True)
            ]),
            ("C.Mác và Ph.Ăngghen sáng lập chủ nghĩa duy vật biện chứng dựa trên kế thừa gì?", 2, [
                ("Phép biện chứng của Hêghen và giá trị duy vật của L. Phoiơbắc", True)
            ]),
            ("Trong TBCN, mâu thuẫn kinh tế là mâu thuẫn giữa:", 3, [
                ("LLSX xã hội hóa với QHSX tư nhân TBCN", True)
            ]),
            ("Mâu thuẫn chính trị - xã hội trong TBCN là mâu thuẫn giữa:", 1, [
                ("Tư sản và vô sản", True)
            ]),
            ("Phong trào đấu tranh GCCN những năm 40 thế kỷ XIX chứng minh điều gì?", 2, [
                ("GCCN là một lực lượng chính trị - xã hội độc lập", True)
            ]),
            ("Nhà tư tưởng tiêu biểu của CNXH không tưởng Pháp đầu thế kỷ XIX là?", 1, [
                ("Xanh Ximông, S. Phuriê, R.Owen", True)
            ]),
            ("Phong trào Hiến chương diễn ra ở đâu?", 1, [
                ("Anh", True)
            ]),
            ("Phong trào công nhân dệt 1844 diễn ra ở đâu?", 1, [
                ("Đức", True)
            ]),
            ("Nhận xét sự sụp đổ của LX và Đông Âu là do \"tất yếu logic của CNXH\" là đúng hay sai?", 2, [
                ("Sai", True)
            ]),
            ("CNXH khoa học có chức năng giác ngộ và hướng dẫn GCCN trong mấy thời kỳ?", 2, [
                ("3", True)
            ])
        ]

        # 4. Thực hiện nạp
        count = 0
        for q_text, difficulty, answers in QUIZ_DATA:
            existing_q = db.query(Question).filter(Question.noiDung == q_text).first()
            if existing_q:
                continue

            new_q = Question(
                maChuong=chapter.maChuong,
                noiDung=q_text,
                doKho=difficulty
            )
            db.add(new_q)
            db.flush()

            for a_text, is_correct in answers:
                new_a = Answer(
                    maCauHoi=new_q.maCauHoi,
                    noiDungDapAn=a_text,
                    laDapAnDung=is_correct
                )
                db.add(new_a)
            count += 1

        db.commit()
        print(f"✅ Đã nạp thành công {count} câu hỏi mới vào Database!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_cnx_kh_data()
