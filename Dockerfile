# 咫尺天涯社交平台 — 容器化部署（可选方案：Render / Fly.io / 自有服务器 / Hugging Face Spaces）
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# Pillow 依赖的运行时库（官方 wheel 通常已自带，保留以防万一）
RUN apt-get update \
    && apt-get install -y --no-install-recommends libjpeg62-turbo zlib1g \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 确保上传目录存在
RUN mkdir -p static/uploads/avatars static/uploads/posts \
             static/uploads/videos static/uploads/attachments \
             static/uploads/thumbnails

EXPOSE 8000

CMD ["sh", "-c", "gunicorn wsgi:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120"]
