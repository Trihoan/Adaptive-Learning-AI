# 1. Sử dụng Python bản chính thức, gọn nhẹ
FROM python:3.10-slim

# 2. Thiết lập thư mục làm việc trong container
WORKDIR /app

# 3. Cài đặt các thư viện hệ thống cần thiết cho thư viện đồ họa (Matplotlib) và MySQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 4. Sao chép tệp yêu cầu và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Sao chép toàn bộ mã nguồn vào container
COPY . .

# 6. Mở cổng 10000 (cổng mặc định bạn đang dùng)
EXPOSE 10000

# 7. Lệnh khởi chạy ứng dụng (sử dụng uvicorn)
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "10000"]
