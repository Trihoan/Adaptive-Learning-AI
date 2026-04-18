# 🎓 Adaptive Learning AI  (ALAS)

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Framework](https://img.shields.io/badge/AI-Scikit--learn-orange)](https://scikit-learn.org/)

## 📝 Giới thiệu dự án
**Adaptive Learning AI System** là một nền tảng học tập trực tuyến thông minh, có khả năng cá nhân hóa lộ trình học tập cho từng sinh viên dựa trên năng lực và hành vi thực tế. Hệ thống sử dụng các thuật toán Học máy (Machine Learning) để phân loại người học và đề xuất tài liệu phù hợp nhất.

Dự án này được xây dựng nhằm giải quyết vấn đề "một giáo án cho tất cả", giúp tối ưu hóa thời gian và hiệu quả tiếp thu kiến thức. Backend được phát triển bằng FastAPI, mang lại hiệu suất cực cao và tài liệu API tự động.
---

## ✨ Các tính năng chính
- **Phân loại người học (Student Clustering):** Sử dụng thuật toán **K-Means** để nhóm sinh viên dựa trên phong cách học tập và trình độ đầu vào.
- **Dự đoán kết quả học tập:** Áp dụng **Decision Tree** hoặc **KNN** để dự báo khả năng hoàn thành khóa học của sinh viên.
- **Lộ trình cá nhân hóa:** Tự động điều chỉnh độ khó của bài tập và gợi ý tài liệu bổ trợ.
- **Dashboard trực quan:** Theo dõi tiến độ học tập thông qua biểu đồ sinh động.
- **RESTful API mạnh mẽ: Cung cấp các endpoint tốc độ cao để giao tiếp với Frontend.
---

### 📊 Mô hình AI sử dụng
Hệ thống sử dụng các mô hình học máy cơ bản nhưng hiệu quả cao cho giáo dục:

- K-Means: Phân nhóm học viên thành các nhóm: Cần hỗ trợ, Khá, Giỏi.

- Decision Tree: Quyết định bước tiếp theo trong lộ trình dựa trên điểm số hiện tại.

- KNN: Tìm kiếm các học viên có hành vi tương tự để đưa ra gợi ý cộng tác.
## 🏗️ Cấu trúc thư mục
```text
Adaptive-Learning-AI/
     ├── data/                       # Thư mục chứa dữ liệu huấn luyện
     │   └── students_data.csv       # File CSV chứa 500 mẫu dữ liệu sinh viên
     ├── models/                     # Thư mục lưu trữ các mô hình AI (.pkl)
     │   ├── kmeans_model.pkl        # Mô hình phân cụm (Giỏi/Khá/TB)
     │   ├── dtree_model.pkl         # Mô hình cây quyết định (Dự đoán Đạt/Trượt)
     │   └── scaler.pkl              # Bộ chuẩn hóa dữ liệu đầu vào
     ├── src/
     │   ├── main/
     │   │   ├── ai/                 
     │   │   │   ├── __init__.py
     │   │   │   └── ai_engine.py    # Chứa logic 3 mô hình K-Means, D-Tree, KNN
     │   │   ├── config/
     │   │   │   └── settings.py     # Cấu hình Database & Secret Key
     │   │   ├── controllers/
     │   │   │   └── auth_controller.py # Xử lý Đăng ký/Đăng nhập (đã sửa maSV)
     │   │   ├── domain/
     │   │   │   ├── models/         # Các Model SQLAlchemy (đã sửa khóa ngoại)
     │   │   │   │   ├── user_model.py
     │   │   │   │   ├── course_model.py
     │   │   │   │   ├── chapter_model.py
     │   │   │   │   └── study_result_model.py
     │   │   │   └── schemas/        # Pydantic Schemas cho API
     │   │   ├── repositories/
     │   │   │   └── user_repository.py # Truy vấn DB người dùng 
     │   │   ├── routes/
     │   │   │   ├── auth_routes.py  # Route Auth 
     │   │   │   ├── system_routes.py 
     │   │   │   └── view_routes.py 
     │   │   ├── services/
     │   │   │   ├── ai_service.py   
     │   │   │   ├── auth_service.py # Logic xác thực bcrypt mới
     │   │   │   └── security_service.py 
     │   │   └── database.py         # Kết nối SQLAlchemy
     │   ├── test/                   # Thư mục dành riêng cho kiểm thử
     │   │   ├── ai_engine.py        
     │   │   ├── seed_user.py        
     │   │   ├── fix_tester.py       # Script sửa lỗi hash mật khẩu
     │   │   └── test_db.py          # Kiểm tra kết nối MySQL
     │   ├── app.py                  # File Flask cũ (chỉ dùng tham khảo)
     │   └── server.py               # [ENTRY POINT] File khởi chạy FastAPI
     ├── static/
     │   ├── css/
     │   │   ├── style.css           # CSS chung
     │   │   ├── home.css            # CSS cho trang chủ
     │   │   ├── result.css          # CSS cho trang kết quả
     │   │   └── AI.css              # [MỚI] CSS riêng cho Chatbot Robot
     │   └── img/                    # Chứa hình ảnh logo, minh họa
     ├── templates/                  # Giao diện HTML (đã sửa url_for path)
     │   ├── home.html               
     │   ├── login.html
     │   ├── register.html           
     │   ├── result.html             
     │   ├── quiz.html
     │   └── course.html
     ├── requirements.txt            # Danh sách thư viện (cần có bcrypt, scikit-learn)
```
## 🛠️ Công nghệ sử dụng
Ngôn ngữ: Python 3.x

AI/Machine Learning: Scikit-learn, Pandas, NumPy

Web Framework: Flask / FastAPI , Unvicorn (ASGI server)

Database & ORM: MySQL , SQLAlchemy

Tools: VS Code, Git

Môi Trường: Virtualenv, Pydantic (Validate dữ liệu)

## 🚀 Hướng dẫn cài đặt
### 1. Clone repository:
```bash
git clone https://github.com/Trihoan/Adaptive-Learning-AI.git
cd Adaptive-Learning-AI
```
### 2. Khởi tạo môi trường ảo (Virtual Environment)
Việc này giúp quản lý thư viện Python riêng biệt cho dự án:
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường (Windows)
venv\Scripts\activate

# Kích hoạt môi trường (macOS/Linux)
source venv/bin/activate
```
### 3. Cài đặt các thư viện cần thiết 
Dự án sử dụng các thư viện AI và Web FrameWork: 
```text
pip install -r requirements.txt
```
### 4. Thiết lập biến môi trường (Environment Variables)
```text
# Ví dụ nội dung file .env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/alas_db
(Lưu ý: Thay thế username, password và tên database bằng thông tin thực tế của bạn).
```
### 5.Khởi động Server FastAPI
Chạy lệnh sau để khởi động server ở chế độ phát triển (tự động reload khi có thay đổi code):
```text
uvicorn src.server:app --reload
```
### 6.Trải nghiệm API (Swagger UI)
FastAPI tự động tạo tài liệu API tương tác cực kỳ trực quan. Mở trình duyệt và truy cập:

Tài liệu Swagger UI: http://127.0.0.1:8000/docs

Tài liệu ReDoc: http://127.0.0.1:8000/redoc
