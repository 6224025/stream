FROM python:3.12-slim-bookworm

# Install build dependencies (Debian系の場合、apkではなくapt-getを使用)
# build-essential は C/C++コンパイラを含みます
# cmake や boost など、pyarrow が明示的に要求するものは残す必要があるかもしれません
# ただし、多くの場合、manylinux wheel が使われればこれらも不要になります。
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libboost-all-dev \
    # 他に pyarrow のドキュメントで Debian系での依存として挙げられているものがあれば追加
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app
# Copy the requirements file into the container
COPY requirements.txt .

# requirements.txt に pyarrow を含めた状態でインストールを試みる
# (PYARROW_BUNDLE_ARROW_CPPなどの環境変数は一旦削除してシンプルに試す)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py"]