# TravelWise Frontend 🖥️

Vue 3 + Vite + TailwindCSS 的旅行規劃前端介面。

> 全端整合說明請看：[根目錄 README](../README.md)

---

## 📁 專案結構

```
frontend/
├── index.html
├── vite.config.js              # Vite 設定（dev proxy → localhost:5001）
├── Dockerfile                  # 多階段 build：Node 20 → nginx:alpine
├── nginx.conf                  # SPA history mode + gzip + /health
├── package.json
│
└── src/
    ├── main.js                 # Vue 入口，掛載前呼叫 loadTripsFromApi()
    ├── App.vue
    ├── router/                 # Vue Router（history mode）
    │
    ├── api/
    │   ├── client.js           # axios 單例，自動帶 Authorization Bearer token
    │   ├── trip.js             # sendChat / planTrip / getItinerary
    │   └── trips.js            # CRUD：fetchTrips / createTrip / updateTripApi...
    │
    ├── data/
    │   └── travelStore.js      # Vue reactive 全域狀態 + API 同步 + localStorage 快取
    │
    ├── pages/
    │   ├── HomePage.vue        # 旅程列表
    │   ├── ItineraryPage.vue   # 每日行程卡片
    │   ├── TripOverviewPage.vue# 行程概覽（打包清單、購物清單）
    │   └── ...
    │
    └── components/
        ├── chat/
        │   ├── ChatPanel.vue   # AI 聊天面板（可拉寬 / 全螢幕）
        │   ├── ChatWindow.vue  # 訊息列表
        │   ├── ChatInput.vue   # 輸入框 + 快捷選項
        │   └── ChatBubble.vue  # 訊息泡泡（支援 **bold** + 換行）
        └── ...
```

---

## 🚀 本機開發

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
```

> `vite.config.js` 已設定 `/api` proxy → `http://localhost:5001`，  
> 開發時不需改任何設定，直接連後端。

---

## 🐳 Docker 啟動（推薦）

從根目錄執行：

```bash
docker compose up --build
```

前端會在 `http://localhost:3000` 提供服務（Nginx 靜態伺服器）。

### Dockerfile 說明（多階段 build）

```dockerfile
# Stage 1：Node 20 build
FROM node:20-alpine AS builder
ARG VITE_API_URL=http://localhost:5001
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2：Nginx serve
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

---

## 🗄️ 狀態管理：`travelStore.js`

| 功能 | 說明 |
|------|------|
| `loadTripsFromApi()` | 啟動時從後端拉資料；後端離線則 fallback localStorage |
| `addTrip(formData)` | 新增旅程，樂觀更新本地 + 背景同步後端 |
| `updateTrip(id, data)` | 更新旅程，同上 |
| `deleteTrip(id)` | 刪除旅程 |
| `saveTripChanges(id)` | 行程項目變更後呼叫，推送給後端 |
| `getTripOrDefault(id)` | 找不到 id 時 fallback 第一筆 |
| `refreshCurrencyForTrip(id)` | 查詢即時匯率並寫入 `trip.currencyRate` |
| `refreshWeatherForTrip(id)` | 查詢 7 天天氣並寫入每日 `itinerary[day].weather` |
| `refreshFatigueForTrip(id)` | 從第一段航班計算 SAFTE 疲勞指數並寫入 `trip.fatigue` |
| `refreshTripLiveData(id)` | 一次呼叫以上三個（TripOverviewPage onMounted 使用）|

資料格式以 `localStorage` 作為離線快取，`apiOnline` 旗標控制是否同步。

---

## � 前後端串接狀況

| 功能 | 頁面 | 後端 API | 狀態 |
|------|------|----------|------|
| AI 行程建議 | ItineraryPage（ChatPanel）| `POST /api/chat` | ✅ |
| 旅程 CRUD | travelStore | `GET/POST/PUT/DELETE /api/trips` | ✅ |
| **即時匯率** | TripOverviewPage | `GET /api/currency/rates` | ✅ |
| **天氣預報** | TripOverviewPage + ItineraryPage | `GET /api/weather` | ✅ |
| **疲勞指數** | FlightPage（時差適應指數卡片）| `POST /api/fatigue/analyze` | ✅ |
| 景點搜尋 | — | `GET /api/places/search` | 後端有，前端未串 |
| 預算計算 | — | `POST /api/budget/calculate` | 後端有，前端未串 |

- 進入任一旅程的「行程規劃」頁面，點擊左下角 **AI 行程建議** 按鈕開啟
- 支援**快捷選項**（文化探索、大眾運輸…）或自由輸入
- 自動帶入當前旅程的目的地、天數、日期作為 AI 上下文
- `conversationId` 在同一個 panel 生命週期內保持，確保對話連貫
- AI 回傳行程 JSON 時自動格式化為 Day / 景點清單顯示

---

## 🔐 認證

`client.js` interceptor 自動帶 `Authorization: Bearer <token>`。  
Token 來源：`localStorage.getItem('authToken')`，若無則預設帶 `TEST_MODE`（開發用）。

目前前端**尚未實作 Firebase 登入頁面**，所有請求都以 `TEST_MODE` 送出，對應後端 `uid: test-user-001`。

---

## 🔗 相關連結

- [根目錄 README（全端）](../README.md)
- [後端 README](../backend/README.md)
- [Swagger UI](http://localhost:5001/api/docs)（需先啟動 Docker）
