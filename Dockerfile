FROM python:3.12-slim-bookworm

# システムパッケージのインストール
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Pythonライブラリのビルドに必要なパッケージ
    build-essential \
    cmake \
    libboost-all-dev \
    # matplotlibで使うフォント (ゴシックと明朝の両方をインストール)
    fonts-ipafont-gothic \
    fonts-ipafont-mincho \
    fonts-liberation \
    # 不要なキャッシュファイルを削除
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの指定
WORKDIR /app


# Pythonライブラリのインストール
COPY requirements.txt .
# matplotlib_fontjaは削除されていることを確認してください
RUN pip install --no-cache-dir -r requirements.txt
# キャッシュクリアは不要になりますが、念のため残しておきます
RUN rm -rf /root/.cache/matplotlib

# ソースコードのコピー
COPY . .

# ポートの開放
EXPOSE 8501

# アプリケーションの実行
CMD ["streamlit", "run", "app.py"]