FROM debian:bookworm-slim

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    pipx \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# yt-dlpのインストール
RUN pipx ensurepath && pipx install yt-dlp
RUN pip3 install --break-system-packages flask requests

# PATHを設定
ENV PATH="/root/.local/bin:$PATH"

# 作業ディレクトリの設定
WORKDIR /app

# アプリケーションファイルのコピー
COPY app/ /app/

# ダウンロードディレクトリの作成
RUN mkdir -p /app/downloads

# ポート8080を公開
EXPOSE 8080

# アプリケーションの起動
CMD ["python3", "app.py"]