# ── Stage 1: Build Vue app ──────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# 先複製 package.json 利用 Docker layer cache
COPY package.json package-lock.json ./
RUN npm ci

# 複製所有前端程式碼
COPY . .

# 注入後端 API URL（對應 docker-compose 的 backend service）
ARG VITE_API_URL=http://localhost:5001
ENV VITE_API_URL=$VITE_API_URL

# Build production 靜態檔案
RUN npm run build

# ── Stage 2: Serve with Nginx ────────────────────────────────
FROM nginx:alpine

# 複製 Nginx 設定（支援 Vue Router history mode）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 複製 build 產出的靜態檔案
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
