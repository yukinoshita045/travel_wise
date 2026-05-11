# ── TravelWise Backend Dockerfile ──
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 先複製 requirements，利用 Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製所有後端程式碼
COPY . .

# 暴露 Flask port
EXPOSE 5000

# 用 gunicorn 啟動（env 變數由 docker compose 注入，不需要 load_dotenv）
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app:create_app()"]
