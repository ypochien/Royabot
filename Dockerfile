FROM python:3.12-slim

# 安裝系統依賴（TA-Lib 需要）
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 安裝 TA-Lib C 庫
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# 安裝 uv
RUN pip install uv

# 設定工作目錄
WORKDIR /app

# 複製專案文件
COPY pyproject.toml uv.lock* README.md ./

# 安裝 Python 依賴
RUN uv sync --frozen

# 複製應用程式碼
COPY src/ ./src/
COPY .env* ./

# 創建必要的目錄
RUN mkdir -p downloads

# 設定時區
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 設定環境變量
ENV PYTHONPATH=/app/src
ENV UV_PYTHON=python3.12

# 執行應用程式
CMD ["uv", "run", "python", "-m", "royabot.bot"]