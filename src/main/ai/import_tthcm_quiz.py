from sqlalchemy.orm import Session
from src.main.database import SessionLocal
from src.main.domain.models import Course, Chapter, Question, Answer

def import_tthcm_data():
    db: Session = SessionLocal()
    try:
        # 1. Kiểm tra Môn học
        course_id = "TTHCM"
        course = db.query(Course).filter(Course.maMonHoc == course_id).first()
        if not course:
            course = Course(
                maMonHoc=course_id,
                tenMonHoc="Tư tưởng Hồ Chí Minh",
                moTa="Môn học về hệ thống quan điểm toàn diện và sâu sắc về những vấn đề cơ bản của cách mạng Việt Nam"
            )
            db.add(course)
            db.flush()

        # 2. Lấy danh sách chương đã có (theo yêu cầu người dùng đã làm 3 chương)
        chapters = db.query(Chapter).filter(Chapter.maMonHoc == course_id).order_by(Chapter.stt).all()
        
        if len(chapters) < 3:
            print(f"⚠️ Chỉ tìm thấy {len(chapters)} chương cho môn TTHCM. Vui lòng kiểm tra lại.")
            return

        ch1, ch2, ch3 = chapters[0], chapters[1], chapters[2]

        # 3. Dữ liệu câu hỏi cho 3 chương
        # Cấu trúc: (Nội dung, Độ khó, [ (Đáp án, Đúng/Sai) ], maChuong)
        QUIZ_DATA = [
            # --- CHƯƠNG 1 ---
            ("Nguồn gốc tư tưởng, lý luận nào đóng vai trò quyết định bước ngoặt trong sự phát triển của Tư tưởng Hồ Chí Minh?", 2, [
                ("Chủ nghĩa Mác - Lênin", True), ("Văn hóa phương Tây", False),
                ("Tinh hoa văn hóa phương Đông", False), ("Truyền thống yêu nước của dân tộc", False)
            ], ch1.maChuong),
            ("Hồ Chí Minh đã tiếp thu giá trị nào của học thuyết Khổng Tử?", 1, [
                ("Tư tưởng về một xã hội bình đẳng", False), ("Triết lý hành động, nhập thế, hành đạo giúp đời", True),
                ("Tư tưởng về quyền con người", False), ("Tất cả các đáp án trên", False)
            ], ch1.maChuong),
            ("Yếu tố nào thuộc về nhân tố chủ quan trong sự hình thành Tư tưởng Hồ Chí Minh?", 2, [
                ("Bối cảnh lịch sử dân tộc", False), ("Sự ra đời của chủ nghĩa Mác", False),
                ("Tư duy độc lập, tự chủ, sáng tạo và lòng yêu nước nhiệt thành của Hồ Chí Minh", True), ("Sự sụp đổ của các phong trào yêu nước cũ", False)
            ], ch1.maChuong),
            ("Thời kỳ tìm thấy con đường cứu nước, giải phóng dân tộc của Hồ Chí Minh diễn ra trong giai đoạn nào?", 2, [
                ("1890 - 1911", False), ("1911 - 1920", True),
                ("1921 - 1930", False), ("1930 - 1945", False)
            ], ch1.maChuong),
            ("Hồ Chí Minh đã đọc 'Sơ thảo lần thứ nhất những luận cương về vấn đề dân tộc và vấn đề thuộc địa' của Lênin vào thời gian nào?", 1, [
                ("Tháng 6/1911", False), ("Tháng 7/1920", True),
                ("Tháng 12/1920", False), ("Tháng 2/1930", False)
            ], ch1.maChuong),
            ("Văn hóa phương Tây mà Hồ Chí Minh tiếp thu có điểm nào nổi bật?", 2, [
                ("Tư tưởng tự do, bình đẳng, bác ái", True), ("Tư tưởng quân chủ chuyên chế", False),
                ("Sự tôn sùng tôn giáo", False), ("Chế độ đẳng cấp", False)
            ], ch1.maChuong),
            ("Một trong những giá trị truyền thống dân tộc Việt Nam là nguồn gốc của TTHCM là gì?", 1, [
                ("Chủ nghĩa yêu nước và ý chí tự lực tự cường", True), ("Tư tưởng đại hán", False),
                ("Sự cam chịu số phận", False), ("Tư tưởng bế quan tỏa cảng", False)
            ], ch1.maChuong),
            ("Hồ Chí Minh rời bến cảng Nhà Rồng ra đi tìm đường cứu nước vào ngày nào?", 1, [
                ("19/5/1890", False), ("5/6/1911", True),
                ("3/2/1930", False), ("2/9/1945", False)
            ], ch1.maChuong),
            ("Trong các nguồn gốc sau, nguồn gốc nào là tiền đề tư tưởng lý luận trực tiếp của TTHCM?", 3, [
                ("Chủ nghĩa Mác - Lênin", True), ("Nho giáo", False),
                ("Phật giáo", False), ("Văn hóa Phục hưng", False)
            ], ch1.maChuong),
            ("Tư tưởng Hồ Chí Minh chính thức được Đảng ta coi là nền tảng tư tưởng, kim chỉ nam cho hành động từ Đại hội mấy?", 3, [
                ("Đại hội VI (1986)", False), ("Đại hội VII (1991)", True),
                ("Đại hội VIII (1996)", False), ("Đại hội IX (2001)", False)
            ], ch1.maChuong),

            # --- CHƯƠNG 2 ---
            ("Theo Hồ Chí Minh, độc lập dân tộc phải gắn liền với?", 1, [
                ("Chủ nghĩa tư bản", False), ("Chủ nghĩa xã hội", True),
                ("Chủ nghĩa dân tộc cực đoan", False), ("Chế độ quân chủ", False)
            ], ch2.maChuong),
            ("Mục tiêu cao nhất của chủ nghĩa xã hội theo Tư tưởng Hồ Chí Minh là gì?", 1, [
                ("Xây dựng nền công nghiệp hiện đại", False), ("Nâng cao đời sống vật chất và tinh thần cho nhân dân", True),
                ("Xóa bỏ hoàn toàn tôn giáo", False), ("Phát triển vũ khí hạt nhân", False)
            ], ch2.maChuong),
            ("Động lực quan trọng nhất của chủ nghĩa xã hội ở Việt Nam theo Hồ Chí Minh là gì?", 2, [
                ("Sự viện trợ từ nước ngoài", False), ("Khoa học kỹ thuật", False),
                ("Con người, mà trước hết là nhân dân lao động", True), ("Vốn đầu tư", False)
            ], ch2.maChuong),
            ("Câu nói nổi tiếng 'Không có gì quý hơn độc lập tự do' được Hồ Chí Minh khẳng định vào năm nào?", 2, [
                ("1945", False), ("1954", False),
                ("1966", True), ("1969", False)
            ], ch2.maChuong),
            ("Theo Hồ Chí Minh, đặc điểm lớn nhất của thời kỳ quá độ lên CNXH ở Việt Nam là gì?", 3, [
                ("Từ một nước nông nghiệp lạc hậu tiến thẳng lên CNXH không kinh qua giai đoạn phát triển TBCN", True),
                ("Từ một nước tư bản chủ nghĩa phát triển", False),
                ("Từ một nước phong kiến lâu đời", False),
                ("Tình trạng chia cắt đất nước", False)
            ], ch2.maChuong),
            ("Nội dung cốt lõi của Tư tưởng Hồ Chí Minh về độc lập dân tộc là gì?", 2, [
                ("Độc lập tự do là quyền thiêng liêng, bất khả xâm phạm của tất cả các dân tộc", True),
                ("Độc lập dân tộc phải đi đôi với chủ nghĩa đế quốc", False),
                ("Độc lập dân tộc chỉ cần về mặt chính trị", False),
                ("Chỉ cần độc lập cho giai cấp công nhân", False)
            ], ch2.maChuong),
            ("Theo Hồ Chí Minh, biện pháp quan trọng nhất để xây dựng CNXH là?", 3, [
                ("Dùng sức mạnh cưỡng chế", False),
                ("Đem tài dân, sức dân, của dân làm lợi cho dân dưới sự lãnh đạo của Đảng", True),
                ("Vay vốn nước ngoài thật nhiều", False),
                ("Ưu tiên phát triển công nghiệp nặng bằng mọi giá", False)
            ], ch2.maChuong),
            ("Hình thức quá độ lên CNXH ở Việt Nam theo TTHCM là gì?", 2, [
                ("Quá độ trực tiếp", False), ("Quá độ gián tiếp", True)
            ], ch2.maChuong),
            ("Độc lập dân tộc theo Hồ Chí Minh bao gồm những nội dung nào?", 2, [
                ("Độc lập thật sự, hoàn toàn", False),
                ("Gắn liền với thống nhất và toàn vẹn lãnh thổ", False),
                ("Độc lập dân tộc gắn liền với tự do, hạnh phúc của nhân dân", False),
                ("Tất cả các phương án trên", True)
            ], ch2.maChuong),
            ("Hồ Chí Minh quan niệm CNXH là một chế độ xã hội như thế nào?", 1, [
                ("Không còn áp bức bóc lột, mọi người đều có việc làm, được ấm no hạnh phúc", True),
                ("Duy trì sự phân biệt giàu nghèo", False),
                ("Mọi người đều có tài sản bằng nhau tuyệt đối", False),
                ("Do quân đội quản lý hoàn toàn", False)
            ], ch2.maChuong),

            # --- CHƯƠNG 3 ---
            ("Đảng Cộng sản Việt Nam là sản phẩm của sự kết hợp giữa chủ nghĩa Mác - Lênin, phong trào công nhân và?", 1, [
                ("Phong trào yêu nước", True), ("Văn hóa dân tộc", False),
                ("Phong trào tư sản", False), ("Sự giúp đỡ quốc tế", False)
            ], ch3.maChuong),
            ("Nguyên tắc tổ chức cơ bản nhất của Đảng Cộng sản Việt Nam theo TTHCM là gì?", 2, [
                ("Tự phê bình và phê bình", False), ("Kỷ luật nghiêm minh, tự giác", False),
                ("Tập trung dân chủ", True), ("Đoàn kết thống nhất", False)
            ], ch3.maChuong),
            ("Hồ Chí Minh quan niệm thế nào về Nhà nước 'của dân'?", 2, [
                ("Mọi quyền lực trong nhà nước và xã hội đều thuộc về nhân dân", True),
                ("Nhân dân đóng thuế cho nhà nước", False),
                ("Nhà nước do nhân dân bầu ra", False),
                ("Nhân dân làm theo lệnh nhà nước", False)
            ], ch3.maChuong),
            ("Theo Hồ Chí Minh, việc 'gốc' của Đảng là gì?", 2, [
                ("Công tác kinh tế", False), ("Công tác cán bộ", True),
                ("Công tác đối ngoại", False), ("Công tác kiểm tra", False)
            ], ch3.maChuong),
            ("Nhà nước Việt Nam Dân chủ Cộng hòa mang bản chất của giai cấp nào?", 1, [
                ("Giai cấp nông dân", False), ("Giai cấp công nhân", True),
                ("Tầng lớp trí thức", False), ("Giai cấp tư sản dân tộc", False)
            ], ch3.maChuong),
            ("Tư tưởng Hồ Chí Minh về xây dựng một nhà nước pháp quyền có đặc điểm gì?", 2, [
                ("Nhà nước quản lý xã hội bằng pháp luật và không ngừng tăng cường pháp chế XHCN", True),
                ("Chỉ cần đạo đức, không cần pháp luật", False),
                ("Pháp luật chỉ dành cho nhân dân", False),
                ("Pháp luật là công cụ của giai cấp thống trị bóc lột", False)
            ], ch3.maChuong),
            ("Muốn cải tạo xã hội cũ thành xã hội mới, theo Hồ Chí Minh, Đảng phải như thế nào?", 2, [
                ("Phải có nhiều đảng viên giàu có", False),
                ("Phải vững vàng về tư tưởng, chặt chẽ về tổ chức và gắn phó máu thịt với dân", True),
                ("Phải có quân đội mạnh", False),
                ("Phải nắm hết tài sản quốc gia", False)
            ], ch3.maChuong),
            ("Trong xây dựng Nhà nước, Hồ Chí Minh đặc biệt nhấn mạnh việc phòng chống 'giặc nội xâm' nào?", 1, [
                ("Tham ô, lãng phí, quan liêu", True), ("Mù chữ", False),
                ("Đói nghèo", False), ("Ngoại xâm", False)
            ], ch3.maChuong),
            ("Đảng lãnh đạo Nhà nước bằng phương thức nào?", 3, [
                ("Bằng đường lối, chủ trương, chính sách", False),
                ("Bằng công tác cán bộ và kiểm tra", False),
                ("Bằng sự gương mẫu của đảng viên", False),
                ("Tất cả các phương án trên", True)
            ], ch3.maChuong),
            ("Khẩu hiệu nào thể hiện sâu sắc tư tưởng Hồ Chí Minh về phục vụ nhân dân của cán bộ?", 1, [
                ("Quan cách mạng", False), ("Công bộc của dân", True),
                ("Chủ của dân", False), ("Người dạy bảo dân", False)
            ], ch3.maChuong),
        ]

        # 4. Thực hiện nạp
        count = 0
        for q_text, difficulty, answers, ma_chuong in QUIZ_DATA:
            existing_q = db.query(Question).filter(Question.noiDung == q_text, Question.maChuong == ma_chuong).first()
            if existing_q:
                continue

            new_q = Question(
                maChuong=ma_chuong,
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
        print(f"✅ Đã nạp thành công {count} câu hỏi mới cho môn TTHCM vào Database!")

    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import_tthcm_data()
