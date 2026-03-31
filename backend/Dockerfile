FROM python:3.11-slim

# ตั้งค่า Environment ให้ Python ไม่สร้างไฟล์ .pyc และแสดง log ทันที
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# ติดตั้ง System Dependencies ที่จำเป็นสำหรับ psycopg2 (ตัวเชื่อม Postgres)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง Python Library
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก๊อปปี้โค้ด
COPY . .

# สั่งรัน (ใช้ Uvicorn สำหรับ Local / Gunicorn สำหรับ Server)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
