# 🎓 Adaptive Learning AI  (ALAS)

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![AI Framework](https://img.shields.io/badge/AI-Scikit--learn-orange)](https://scikit-learn.org/)

## 📝 Giới thiệu dự án
**Adaptive Learning AI System** là một nền tảng học tập trực tuyến thông minh, có khả năng cá nhân hóa lộ trình học tập cho từng sinh viên dựa trên năng lực và hành vi thực tế. Hệ thống sử dụng các thuật toán Học máy (Machine Learning) để phân loại người học và đề xuất tài liệu phù hợp nhất.

Dự án này được xây dựng nhằm giải quyết vấn đề "một giáo án cho tất cả", giúp tối ưu hóa thời gian và hiệu quả tiếp thu kiến thức.

---

## ✨ Các tính năng chính
- **Phân loại người học (Student Clustering):** Sử dụng thuật toán **K-Means** để nhóm sinh viên dựa trên phong cách học tập và trình độ đầu vào.
- **Dự đoán kết quả học tập:** Áp dụng **Decision Tree** hoặc **KNN** để dự báo khả năng hoàn thành khóa học của sinh viên.
- **Lộ trình cá nhân hóa:** Tự động điều chỉnh độ khó của bài tập và gợi ý tài liệu bổ trợ.
- **Dashboard trực quan:** Theo dõi tiến độ học tập thông qua biểu đồ sinh động.

---

📊 Mô hình AI sử dụng
Hệ thống sử dụng các mô hình học máy cơ bản nhưng hiệu quả cao cho giáo dục:

- K-Means: Phân nhóm học viên thành các nhóm: Cần hỗ trợ, Khá, Giỏi.

- Decision Tree: Quyết định bước tiếp theo trong lộ trình dựa trên điểm số hiện tại.

- KNN: Tìm kiếm các học viên có hành vi tương tự để đưa ra gợi ý cộng tác.
## 🏗️ Cấu trúc thư mục
```text
├── data/               # Chứa tập dữ liệu huấn luyện (Dataset)
├── models/             # Lưu trữ các model AI đã được huấn luyện (.pkl)
├── notebooks/          # File Jupyter Notebook để phân tích dữ liệu (EDA)
├── src/                # Mã nguồn chính của ứng dụng
│   ├── app.py          # File chạy chính (Backend Flask/FastAPI)
│   ├── ai_engine.py    # Logic xử lý thuật toán AI
│   └── templates/      # Giao diện người dùng (HTML/CSS)
├── .gitignore          # Các file không đẩy lên GitHub (venv, .pyc...)
├── requirements.txt    # Danh sách thư viện cần cài đặt
└── README.md           # Tài liệu hướng dẫn dự án
```
🛠️ Công nghệ sử dụng
Ngôn ngữ: Python 3.x

AI/ML: Scikit-learn, Pandas, NumPy

Web Framework: Flask / FastAPI (Tùy chọn)

Database: MySQL / SQLite

Tools: VS Code, Git

🚀 Hướng dẫn cài đặt
### 1. Clone repository:
```bash
git clone [https://github.com/Trihoan/Adaptive-Learning-AI.git](https://github.com/Trihoan/Adaptive-Learning-AI.git)
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
### 4. Chạy ứng dụng 
Sau khi cài đặt xong, bạn có thể khởi động server local:
```text
python src/app.py
```
Sau đó truy cập địa chỉ http://127.0.0.1:5000 trên trình duyệt.
