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
- **RESTful API mạnh mẽ:** Cung cấp các endpoint tốc độ cao để giao tiếp với Frontend.
---

### 📊 Mô hình AI sử dụng
Hệ thống sử dụng các mô hình học máy cơ bản nhưng hiệu quả cao cho giáo dục:

- K-Means: Phân nhóm học viên thành các nhóm: Cần hỗ trợ, Khá, Giỏi.

- Decision Tree: Quyết định bước tiếp theo trong lộ trình dựa trên điểm số hiện tại.

- KNN: Tìm kiếm các học viên có hành vi tương tự để đưa ra gợi ý cộng tác.

## 🏗️ Cấu trúc thư mục
```text
Adaptive-Learning-AI/
├── data/                       # Dữ liệu huấn luyện
│   └── students_data.csv       # File CSV mẫu dữ liệu sinh viên
├── models/                     # Các mô hình AI đã huấn luyện (.pkl)
│   ├── kmeans_model.pkl        # Phân cụm năng lực
│   ├── dtree_model.pkl         # Dự đoán kết quả
│   ├── scaler.pkl              # Chuẩn hóa dữ liệu
│   └── ai_metrics.json         # Chỉ số đánh giá mô hình
├── src/                        # Mã nguồn chính
│   ├── server.py               # [ENTRY POINT] Khởi chạy FastAPI
│   ├── app.py                  # Flask App (Tham khảo)
│   └── main/                   
│       ├── database.py         # Kết nối cơ sở dữ liệu
│       ├── ai/                 # Logic xử lý AI (ai_engine, ai_trainer)
│       ├── config/             # Cấu hình hệ thống (settings)
│       ├── controllers/        # Điều hướng logic nghiệp vụ
│       ├── domain/             # SQLAlchemy Models & Pydantic Schemas
│       ├── repositories/       # Thao tác trực tiếp với Database
│       ├── routes/             # Định nghĩa các Endpoint API
│       └── services/           # Xử lý logic trung gian
├── static/                     # Tài nguyên tĩnh (CSS, JS, Images)
│   ├── css/                    # Các file stylesheet
│   └── img/                    # Hình ảnh, logo
├── templates/                  # Giao diện HTML (Jinja2)
├── index.html                  # File điều hướng cho GitHub Pages
├── requirements.txt            # Danh sách thư viện phụ thuộc
└── Procfile                    # Cấu hình triển khai trên Render
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

### 7. Link Demo (GitHub Pages)
Truy cập bản demo trực tuyến tại: [https://trihoan.github.io/Adaptive-Learning-AI/](https://trihoan.github.io/Adaptive-Learning-AI/)
