# TravelWise 🌏
### 全齡化旅行適應決策支援平台

> **Group H｜期末專案**  
> 資管四 B10705037 關凱欣　經濟四 B11303045 林鼎鈞　外文二 B13102010 李艾蓁　B12106001 林奕睿　圖資四 B11106054 蔡怡萱　資管三 B12705024 吳宇平

> 📅 最後更新：2026-05-24　｜　✅ 所有 API 測試通過　｜　🐳 Docker 一鍵啟動

---

## 📌 專案簡介

TravelWise 整合 **AI 行程規劃、飛行疲勞生理模型（SAFTE）、即時天氣、景點資料、航班查詢、匯率換算**，讓使用者從輸入航班編號到取得完整旅遊規劃只需一個步驟。

---

## 🏗️ 技術架構

| 層級 | 技術 | 用途 | 費用 |
|------|------|------|------|
| 前端 | Vue 3 + Vite + TailwindCSS | 使用者介面 | 免費 |
| 後端 | Python Flask 3.x | REST API 開發 | 免費 |
| 資料庫 | MongoDB Atlas | 儲存使用者與行程資料 | 免費方案 |
| 快取 | Redis 7 | 快取景點、天氣、匯率資料 | 免費方案 |
| AI | OpenAI GPT-4o-mini | AI 景點推薦與行程生成 | 依使用量計費 |
| 景點 API | OpenTripMap | 景點資訊查詢 | 免費 |
| 天氣 API | Open-Meteo | 天氣資料查詢 | 免費 |
| 身份驗證 | Firebase Admin SDK | 使用者登入驗證 | 免費方案 |
| 航班 API | Aviationstack | 航班編號轉城市／時區資訊 | 免費方案 |
| 匯率 | ExchangeRate-API | 即時匯率查詢與換算 | 免費方案 |
| 容器化 | Docker Compose | 一鍵啟動整個後端環境 | 免費 |

```
travel_wise/
├── docker-compose.yml        ← 一鍵啟動 Redis + Flask 後端
├── frontend/                 ← Vue 3 + Vite（npm run dev）
└── backend/
    ├── Dockerfile            ← python:3.11-slim + gunicorn
    ├── app.py                ← Flask Application Factory
    ├── requirements.txt
    ├── api/routes/           ← 各功能 Blueprint
    ├── services/             ← 業務邏輯層
    ├── models/               ← MongoDB Document 結構
    └── utils/                ← Auth Middleware、Cache、Error Handler
```

---

## 🚀 快速開始（Docker — 推薦所有人使用）

### 前置需求

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 已安裝並啟動
- 向 **林鼎鈞** 取得以下兩個私密檔案（不在 Git 內）：
  - `backend/.env`
  - `backend/firebase_service_account.json`

### Step 1 — Clone & 放置私密檔案

```bash
git clone git@github.com:yukinoshita045/travel_wise.git
cd travel_wise
# 將 .env 和 firebase_service_account.json 放進 backend/ 目錄
```

### Step 2 — 一鍵啟動

```bash
docker compose up --build
```

啟動成功後：

```
✅ 後端 API：  http://localhost:5001
📖 Swagger UI：http://localhost:5001/api/docs
```

> ⚠️ macOS 的 Port 5000 被 AirPlay 佔用，後端統一對外用 **5001**。

### Step 3 — 驗證後端正常

```bash
curl "http://localhost:5001/api/weather?destination=Tokyo"
# 看到 JSON 天氣資料 → 成功 ✅
```

### 常用指令

```bash
docker compose up --build          # 首次或更新後啟動（重新 build）
docker compose up -d               # 背景啟動（已 build 過）
docker compose down                # 停止並移除容器
docker compose logs -f backend     # 即時查看後端 log
git pull && docker compose up --build  # 拉新版並重啟
```

---

## 🐳 Docker 設定說明

### `docker-compose.yml`

```yaml
services:
  redis:
    image: redis:7-alpine
    container_name: travelwise_redis
    ports: ["6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  backend:
    build: ./backend            # 使用 backend/Dockerfile
    container_name: travelwise_backend
    ports: ["5001:5000"]        # Host 5001 → Container 5000
    env_file: ./backend/.env    # 載入所有 API Key
    environment:
      REDIS_URL: redis://redis:6379/0   # 覆蓋 .env 的 localhost 設定
      FLASK_TESTING: "true"             # 開發模式：跳過 Firebase 驗證
    volumes:
      - ./backend/firebase_service_account.json:/app/firebase_service_account.json:ro
    depends_on:
      redis:
        condition: service_healthy
```

### `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app:create_app()"]
```

**重點設計：**
- `python:3.11-slim`：體積小、安全性高
- `gunicorn` 取代 Flask dev server，生產等級穩定性
- `--timeout 300`：避免 OpenAI 長請求被中斷
- `FLASK_TESTING=true`：開發中跳過 Firebase Token 驗證，不需帶 Authorization header

---

## 🔐 環境變數 & 私密檔案

| 檔案 | 是否在 Git | 取得方式 |
|------|-----------|---------|
| `backend/.env` | ❌ 不在 Git | 向林鼎鈞索取 |
| `backend/firebase_service_account.json` | ❌ 不在 Git | 向林鼎鈞索取 |
| `backend/.env.example` | ✅ 在 Git | 範本，不含真實 Key |

`.env` 必填項目：

```bash
MONGO_URI=mongodb+srv://...
OPENAI_API_KEY=sk-...
OPENTRIPMAP_API_KEY=...
AVIATIONSTACK_API_KEY=...    # 航班查詢
# FLASK_TESTING 由 docker-compose.yml 設定，不在 .env
```

---

## 📡 API 總覽

| Method | 路由 | 說明 |
|--------|------|------|
| `GET`  | `/api/weather` | 7 天天氣預報 + 衣物建議 |
| `GET`  | `/api/places/search` | 城市景點搜尋 |
| `GET`  | `/api/places/<xid>` | 景點詳情 |
| `POST` | `/api/budget/calculate` | 預算分配計算 |
| `POST` | `/api/chat` | AI 對話（含 Function Calling）|
| `POST` | `/api/trip/plan` | ⭐ 一站式旅遊規劃 |
| `POST` | `/api/itinerary/recommend` | 單獨呼叫 AI 生成行程 |
| `GET`  | `/api/itinerary/user/history` | 我的歷史行程列表 |
| `GET`  | `/api/itinerary/<id>` | 取得單一行程 |
| `PUT`  | `/api/itinerary/<id>` | 更新行程 |
| `DELETE` | `/api/itinerary/<id>` | 刪除行程 |
| `POST` | `/api/fatigue/analyze` | 疲勞分析（SAFTE 模型）|
| `GET`  | `/api/flight/info` | 航班編號查詢（自動填入表單）|
| `GET`  | `/api/currency/rates` | 取得即時匯率列表 |
| `POST` | `/api/currency/convert` | 金額換算（11 種幣別）|

> 📖 完整互動文件：[http://localhost:5001/api/docs](http://localhost:5001/api/docs)（需先啟動 Docker）

---

## 🔄 核心端點：`POST /api/trip/plan` ⭐

前端**只需呼叫這一支 API**，後端自動串接：  
**航班自動填入 → 城市驗證 → SAFTE 疲勞計算 → AI 行程生成**

**Request Body**

```json
{
  "flight": {
    "departureCity": "Taipei",
    "arrivalCity": "Tokyo",
    "departureTime": "2026-06-01T08:00:00",
    "arrivalTime": "2026-06-01T12:30:00",
    "departureTz": "Asia/Taipei",
    "arrivalTz": "Asia/Tokyo",
    "flightDurationHours": 3.5,
    "layoverCount": 0,
    "isRedEye": false,
    "hasNapped": false
  },
  "travelers": [
    { "ageGroup": "adult",  "fitnessLevel": "medium" },
    { "ageGroup": "senior", "fitnessLevel": "low" }
  ],
  "trip": {
    "days": 3,
    "budget": 60000,
    "travelStyle": "觀光景點",
    "transportMode": "大眾運輸",
    "mustVisit": ["淺草寺"]
  }
}
```

**Response 結構**

```json
{
  "destination": "Tokyo",
  "fatigue":   { "...疲勞卡片資料" },
  "itinerary": { "...行程卡片資料" },
  "weather":   null
}
```

### 🛫 航班自動填入流程

使用者在前端輸入航班編號（如 `CI100`），前端先打：

```
GET /api/flight/info?flightNum=CI100
```

回傳：

```json
{
  "flightNumber": "CI100",
  "airline": "China Airlines",
  "departure": { "city": "Taipei", "country": "Taiwan", "timezone": "Asia/Taipei", "time": "08:00" },
  "arrival":   { "city": "Tokyo",  "country": "Japan",  "timezone": "Asia/Tokyo",  "time": "11:30" },
  "flightDurationHours": 3.5
}
```

前端用這份資料自動填入 `/api/trip/plan` 的 `flight` 欄位，使用者不需手動輸入時區與飛行時長。

---

## 🃏 前端卡片 Response Schema

### 😴 FatigueCard

```json
{
  "baseScore": 50,
  "level": "中等",
  "energyBattery": 65,
  "jetLagIndex": 3,
  "suggestedStartTime": "10:00",
  "tripStressType": "一般行程",
  "recoverHours": 6,
  "explanation": "疲勞指數 50，屬於中等壓力，建議第一天活動從 10:00 開始。",
  "_placeholder": false
}
```

| baseScore | level | energyBattery | suggestedStartTime |
|-----------|-------|---------------|--------------------|
| 0–29 | 低 | 85% | 09:00 |
| 30–54 | 中等 | 65% | 10:00 |
| 55–74 | 高 | 45% | 11:00 |
| 75–100 | 極高 | 25% | 13:00 |

> `_placeholder: false` → SAFTE 真實計算；`true` → 前端顯示「⚠️ 疲勞模組計算中」提示

### 🌤️ WeatherCard

```json
{
  "destination": "東京",
  "clothingSuggestion": "建議穿著長袖搭配薄外套；預報有降雨，請攜帶雨傘",
  "alerts": [{ "date": "2026-06-03", "message": "降雨機率 85%，請攜帶雨具" }],
  "forecast": [
    {
      "date": "2026-06-01",
      "tempMax": 28.5, "tempMin": 19.2, "feelsLike": 30.1,
      "humidity": 72.0, "windKmh": 12.3,
      "condition": "多雲", "precipProb": 15
    }
  ]
}
```

### 🗓️ ItineraryCard

```json
{
  "itineraryId": "be36f77d-...",
  "title": "3天東京新宿文化・歷史・攝影之旅",
  "days": [
    {
      "dayNumber": 1,
      "theme": "新宿古今巡禮",
      "spots": [
        {
          "xid": "Q3530518",
          "name": "Tokyo City Hall",
          "description": "現代建築代表，適合拍照。",
          "lat": 35.6879, "lon": 139.6920,
          "arrivalTime": "09:00",
          "stayDuration": 60,
          "ticketPrice": 0,
          "notes": "建議早上前往拍攝外觀。"
        }
      ]
    }
  ],
  "budget": { "total": 60000, "currency": "TWD" }
}
```

### 💰 BudgetCard

```json
{
  "totalBudget": 60000, "currency": "TWD",
  "perPerson": 30000, "isOverBudget": false,
  "breakdown": {
    "accommodation": { "total": 21000, "ratio": 0.35 },
    "food":          { "total": 15000, "ratio": 0.25 },
    "transport":     { "total": 9000,  "ratio": 0.15 },
    "activities":    { "total": 12000, "ratio": 0.20 },
    "emergency":     { "total": 3000,  "ratio": 0.05 }
  }
}
```

### 💱 匯率 API

```bash
# 取得以 TWD 為基準的所有匯率
GET /api/currency/rates?base=TWD

# 換算金額
POST /api/currency/convert
{ "amount": 60000, "from": "TWD", "to": "JPY" }
```

支援幣別：`TWD USD JPY EUR GBP KRW HKD SGD AUD CNY THB`  
Redis 快取 1 小時，API 失敗時自動 fallback 至內建匯率表。

---

## ✅ API 測試狀態

| API | 狀態 | 備註 |
|-----|------|------|
| `GET /api/weather` | ✅ | Open-Meteo 真實資料 |
| `GET /api/places/search` | ✅ | OpenTripMap 真實資料 |
| `GET /api/places/<xid>` | ✅ | 含圖片、Wikipedia、地址 |
| `POST /api/budget/calculate` | ✅ | 超預算警告正確觸發 |
| `POST /api/chat` | ✅ | GPT Function Calling |
| `POST /api/trip/plan` | ✅ | 完整流程，SAFTE `_placeholder: false` |
| `POST /api/itinerary/recommend` | ✅ | AI 生成 + 存 MongoDB |
| `GET /api/itinerary/user/history` | ✅ | MongoDB 正常 |
| `POST /api/fatigue/analyze` | ✅ | **SAFTE 正式版** |
| `GET /api/flight/info` | ✅ | 需 `AVIATIONSTACK_API_KEY` |
| `GET /api/currency/rates` | ✅ | Redis 快取 1hr |
| `POST /api/currency/convert` | ✅ | 11 種幣別 |

---

## 👥 分工說明

| 模組 | 負責人 | 狀態 |
|------|--------|------|
| Flask 後端骨架 + Docker 容器化 | 林鼎鈞 | ✅ |
| `POST /api/trip/plan` 整合端點 | 林鼎鈞 | ✅ |
| 匯率 API（currency）| 林鼎鈞 | ✅ |
| `POST /api/fatigue/analyze` SAFTE 疲勞模組 | 隊友 | ✅ 已整合 |
| `GET /api/flight/info` 航班查詢 | 隊友 Janet | ✅ 已整合 |
| 前端 Vue 3 元件 + Chat Panel | 其他組員 | 進行中 |

---

## 🔧 本機開發（不用 Docker）

```bash
brew install redis && brew services start redis
cd backend
cp .env.example .env    # 填入各 API Key
pip3 install -r requirements.txt
FLASK_TESTING=true python3 start_server.py
```

> 前端：`cd frontend && npm install && npm run dev`  
> Vite 預設在 `http://localhost:5173`，已預設打 `http://localhost:5001`

---

## 🔗 相關連結

- [後端詳細文件](./backend/README.md)
- [Swagger UI](http://localhost:5001/api/docs)（需先啟動 Docker）
- [MongoDB Atlas](https://cloud.mongodb.com)
- [Aviationstack API Docs](https://aviationstack.com/documentation)
- [ExchangeRate-API Docs](https://www.exchangerate-api.com/docs)
- [Open-Meteo Docs](https://open-meteo.com/en/docs)
