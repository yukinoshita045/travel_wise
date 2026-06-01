# TravelWise — Project Overview for Claude

> 最後更新：2026-06-01  
> 整合狀態：`main` 後端 + `frontend-adjust` 前端已合併完畢

---

## 1. 專案簡介

**TravelWise** 是一個 AI 輔助旅遊規劃 Web App。使用者可建立行程、管理每日行程安排、追蹤航班、記帳、查詢天氣與疲勞指數，並透過 AI 聊天面板獲得即時行程建議。

---

## 2. 技術架構

| 層級 | 技術 |
|------|------|
| 前端 | Vue 3 (Composition API) + Vite + Vue Router + Tailwind CSS v3 |
| 後端 | Flask 3 (Blueprint 架構) + Flasgger (Swagger UI) |
| 資料庫 | MongoDB Atlas (PyMongo) |
| 快取 | Redis 7 |
| 認證 | Firebase Admin SDK (ID Token 驗證) |
| 容器化 | Docker Compose (Redis + Flask backend) |
| 航班 API | AeroDataBox (via RapidAPI) |
| AI 聊天 | OpenAI API |

---

## 3. 目錄結構

```
travel_wise/
├── backend/               # Flask API 伺服器
│   ├── app.py             # Flask 進入點，所有 Blueprint 在此註冊
│   ├── start_server.py    # 生產環境啟動腳本
│   ├── requirements.txt   # Python 相依套件
│   ├── Dockerfile
│   ├── api/routes/        # 各功能 Blueprint（一個功能一個檔案）
│   ├── services/          # 商業邏輯層（route 只做路由，邏輯在 service）
│   ├── models/            # MongoDB document 結構定義
│   ├── config/
│   │   ├── database.py    # MongoDB 單例連線池
│   │   └── swagger_config.py
│   ├── utils/
│   │   ├── auth_middleware.py  # Firebase Token 驗證 decorator
│   │   ├── cache.py            # Redis 快取 helper
│   │   └── error_handlers.py
│   └── tests/             # pytest 單元 / 整合測試
│
├── frontend/              # Vue 3 SPA
│   ├── src/
│   │   ├── App.vue        # 根元件，只有 <RouterView />
│   │   ├── main.js        # 掛載 Vue app + Router
│   │   ├── TravelDashboard.vue   # 首頁（行程列表 + 新增旅程）
│   │   ├── router/index.js       # 所有路由定義
│   │   ├── data/
│   │   │   ├── travelStore.js    # Reactive 全域狀態（localStorage 持久化）
│   │   │   └── travelData.json   # 初始 Mock 資料
│   │   ├── api/
│   │   │   ├── client.js         # axios 實例（自動帶 Bearer Token）
│   │   │   └── trip.js           # API 呼叫函式
│   │   ├── pages/         # 路由層級頁面元件
│   │   ├── components/    # 可重用 UI 元件
│   │   └── utils/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── docker-compose.yml     # 一鍵啟動 Redis + Backend
├── database/schema/       # Firestore / MongoDB collection schema 文件
└── docs/feature_specs/    # 功能規格文件
```

---

## 4. 前端路由結構

| 路徑 | 元件 | 說明 |
|------|------|------|
| `/` | `TravelDashboard` | 所有旅程列表、新增/編輯旅程 |
| `/trip/:id` | `TripOverviewPage` | 單次行程總覽（天氣、航班、預算摘要） |
| `/trip/:id/itinerary` | `ItineraryPage` | 每日行程規劃 + AI 聊天面板 |
| `/trip/:id/flights` | `FlightPage` | 航班詳情（轉機、登機門、航廈） |
| `/trip/:id/items` | `ItemPage` | 打包清單 / 購物清單管理 |
| `/trip/:id/plan` | `TripPlan` | AI 行程規劃（生成建議） |

---

## 5. 後端 API 端點

所有 API 路徑皆以 `/api/` 為前綴，並需帶 `Authorization: Bearer <token>` header。
開發/測試模式下可傳 `Bearer TEST_MODE` 或設定 `FLASK_TESTING=true` 跳過驗證。

| Blueprint | 路徑前綴 | 說明 |
|-----------|----------|------|
| `chat_bp` | `/api/chat` | OpenAI 聊天（對話歷史存 MongoDB） |
| `weather_bp` | `/api/weather` | 目的地天氣查詢 |
| `fatigue_bp` | `/api/fatigue` | 依轉機次數計算疲勞指數 |
| `itinerary_bp` | `/api/itinerary` | 行程 CRUD |
| `places_bp` | `/api/places` | Google Places 景點搜尋 / 詳情 |
| `budget_bp` | `/api/budget` | 旅遊預算估算 |
| `trip_bp` | `/api/trip` | 旅程規劃（AI 生成） |
| `flight_bp` | `/api/flight` | 航班查詢（AeroDataBox API） |
| `currency_bp` | `/api/currency` | 匯率查詢 |

### 航班 API（最新版）
```
GET /api/flight/info?flightNum=IT203&date=2026-12-25
```
- 回傳：起降時間（含時區）、航廈、登機門、機場城市/國家
- 資料來源：AeroDataBox（RapidAPI）
- 需設定環境變數：`RAPIDAPI_KEY`

---

## 6. 前端狀態管理（travelStore.js）

使用 Vue `reactive` + `localStorage` 持久化，**不使用 Pinia/Vuex**。

```js
import { travelStore, getTripById, addTrip, updateTrip } from '@/data/travelStore'
```

| 函式 | 說明 |
|------|------|
| `getTripById(id)` | 依 ID 取得旅程 |
| `getTripOrDefault(id)` | 取得旅程，找不到則回傳第一筆 |
| `addTrip(formData)` | 新增旅程（自動產生每日行程 + 打包清單骨架） |
| `updateTrip(tripId, formData)` | 更新旅程（自動同步日期變動的 dayMap） |
| `resetTravelData()` | 重置為 travelData.json 初始資料 |

---

## 7. 重要元件說明

### `TravelDashboard.vue`
- 顯示旅程卡片列表（`TripCard`）
- 控制 `TripModal`（新增/編輯旅程表單）
- Auth 入口：整合 `Auth.vue`（Firebase 登入/登出）

### `TripCard.vue`
- 點擊整張卡片 → `$emit('open', trip)` → 進入 `TripOverviewPage`
- 點擊三點選單圖示 → `$emit('edit', trip)` → 開啟編輯 Modal

### `TripModal.vue`
- 新增 / 編輯旅程表單
- `v-model.number` 綁定轉機次數，動態渲染轉機點填寫框
- 編輯時自動從 `props.tripData` 預填表單資料

### `Navbar.vue`
- 固定頂部導覽列（`fixed left-0 right-0 top-0`）
- 右上角個人檔案下拉選單
- 登出：清除 `sessionStorage` 的 `travelwise:currentUser`，跳回 `/`

### `ChatPanel.vue`（ItineraryPage 使用）
- 三種狀態：`closed`（浮動按鈕）→ `half`（側邊滑出，可拖拉寬度）→ `full`（全螢幕）
- 透過 `emit('layout-change', { isOpen, width })` 通知父元件調整 main 內容區域寬度
- 呼叫 `POST /api/chat` 傳送訊息，支援對話歷史

### `WeatherIcon.vue`
- 接收天氣字串，回傳對應天氣 emoji 圖示

---

## 8. 環境變數設定

在 `backend/.env` 中設定：

```env
# MongoDB
MONGO_URI=mongodb+srv://<user>:<pass>@cluster.mongodb.net/travelwise

# Firebase
FIREBASE_SERVICE_ACCOUNT_PATH=./firebase_service_account.json

# Redis
REDIS_URL=redis://localhost:6379/0

# 航班 API（AeroDataBox via RapidAPI）
RAPIDAPI_KEY=your_rapidapi_key_here

# OpenAI
OPENAI_API_KEY=your_openai_key_here

# 開發模式：跳過 Firebase Token 驗證
FLASK_TESTING=true

# Flask
FLASK_DEBUG=true
PORT=5000
```

前端 `frontend/.env`：
```env
VITE_API_URL=http://localhost:5001
```

---

## 9. 開發啟動方式

### 後端（含 Redis）
```bash
# 方式一：Docker Compose（推薦）
docker compose up --build

# 方式二：本機直接啟動（需自行啟動 Redis）
cd backend
pip install -r requirements.txt
python app.py
```

後端預設跑在 `http://localhost:5001`，Swagger UI：`http://localhost:5001/api/docs`

### 前端
```bash
cd frontend
npm install
npm run dev
```
前端預設跑在 `http://localhost:5173`

---

## 10. 測試

```bash
cd backend
pytest tests/                      # 跑全部測試
pytest tests/unit/                 # 只跑單元測試
pytest tests/integration/          # 只跑整合測試
```

測試設定在 `backend/pytest.ini`，使用 `conftest.py` 注入 Flask test client。

---

## 11. 目前整合狀態（2026-06-01）

### 已完成
- ✅ `frontend-adjust` 前端（TripOverviewPage、ItineraryPage、ChatPanel、WeatherIcon、TripPlan 等）合併進 `main`
- ✅ `main` 後端（flight service 升級為 AeroDataBox API，新增 terminal/gate/airport 欄位）合併完成
- ✅ 合併衝突已解決（`Navbar.vue`、`TripCard.vue`、`TripModal.vue` 均採用 `frontend-adjust` 最新版本）
- ✅ 前端狀態透過 `travelStore.js` + `localStorage` 串聯各頁面
- ✅ AI 聊天（ChatPanel）整合進 ItineraryPage

### 待處理 / 已知限制
- ⚠️  `ChatPanel.vue` 的 `tripParams` 目前寫死為 `{ destination: 'Tokyo', days: 3, travelers: 1 }`，應替換為當前 trip 的真實資料
- ⚠️  `TravelDashboard` 的 `Auth.vue` Firebase 登入流程需搭配正確的 Firebase 設定才能完整運作（`FLASK_TESTING=true` 可在開發時繞過）
- ⚠️  `FlightPage` 的航班資料目前來自 `travelStore` 本地資料；若要接真實後端 `/api/flight/info`，需在頁面中呼叫 API 並更新 store
- ⚠️  後端 MongoDB 相關 API（itinerary、trip、chat）需 `MONGO_URI` 才能正常運作，本地開發若無 MongoDB 連線，這些 endpoint 會回 500

---

## 12. 重要開發慣例

1. **後端**：商業邏輯一律寫在 `services/`，`routes/` 只做參數解析與 HTTP 回應
2. **後端**：每個 route 都要掛 `@require_auth`，測試時用 `FLASK_TESTING=true` 或 `Bearer TEST_MODE` 跳過
3. **前端**：所有頁面透過 `travelStore` 存取旅程資料，不要在元件 local state 重複儲存行程主資料
4. **前端**：使用 `getTripOrDefault(route.params.id)` 而非直接 `getTripById`，避免找不到旅程時崩潰
5. **前端**：API 呼叫統一透過 `frontend/src/api/client.js` 的 axios 實例，自動處理 Bearer Token
