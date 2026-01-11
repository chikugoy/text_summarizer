FROM python:3.11-slim

WORKDIR /app

# ビルド依存パッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    make \
    gcc \
    libffi-dev \
    libssl-dev \
    swig \
    pkg-config \
    libfreetype6-dev \
    libharfbuzz-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    # OpenCV関連の依存パッケージ
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libx11-6 \
    libxcb1 \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# OpenCVを先にインストール
RUN pip install --no-cache-dir opencv-python-headless

# 依存パッケージをインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# アップロードディレクトリを作成
RUN mkdir -p uploads

# 環境変数を設定
ENV PYTHONPATH=/app
ENV PORT=8000

# アプリケーションを実行
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
