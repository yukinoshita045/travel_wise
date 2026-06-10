# TravelWise — Project Overview for Claude

> 最後更新：2026-06-03  
> 整合狀態：`main` 後端 + `frontend-adjust` 前端已合併完畢  
> ⚠️ 本文件新增了「Section 13 前後端串聯清單」與「Section 14 假資料標注」，供 Opus 審查後執行

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

### ✅ 已完成：Firebase 真實認證（2026-06-08）
- `Auth.vue` 已接 Firebase Authentication（Email/密碼註冊 + 登入），登入後存真實 ID Token 至 `localStorage.authToken`
- 後端 `FLASK_TESTING=false` 時正式驗證 token，各使用者旅程依 `uid` 隔離（詳見下方「開發者注意事項」）

### 待處理 / 已知限制（詳見 Section 13 & 14）

- 🔴 `ChatPanel.vue:177-189` MOCK 擋住 `/api/chat`（刪掉即可啟用）
- ❌ `FlightPage` 沒有「新增/查詢航班」UI；`/api/flight/info` 後端已就緒但前端未串
- ❌ `TripPlan.vue` 走 ChatPanel（`/api/chat`），`/api/trip/plan` 沒有前端入口
- ❌ `/api/budget`、`/api/places`（前端獨立呼叫）完全未串聯
- ⚠️  `ChatPanel.vue` tripParams 已改為讀真實 trip 資料（舊問題已修）
- ⚠️  後端 MongoDB 相關 API（itinerary、trip、chat）需 `MONGO_URI`，無連線時回 500

### 🔑 開發者注意事項（認證上線後，組員必讀）

開啟真實認證後，**整個前端被 Firebase 登入畫面擋住**，組員開發前需先設定：

1. **前端設定**：`cd frontend && cp .env.example .env`
   （`.env.example` 已含可直接使用的 Firebase web 設定，apiKey 為公開值）

2. **共用開發帳號**（免自己註冊，登入畫面直接輸入即可）：
   - 帳號：`dev@travelwise.com`
   - 密碼：`TravelWiseDev2026!`
   - ⚠️ 共用帳號 = 共用資料，多人同時用會看到彼此的旅程；要獨立資料請各自用 app 註冊新帳號

3. **認證模式切換**（`backend/.env` 的 `FLASK_TESTING`，不再寫死在 docker-compose）：
   - `FLASK_TESTING=false`（預設）→ 正式驗證 token，依 `uid` 隔離各使用者資料
   - `FLASK_TESTING=true` → 跳過驗證、所有人共用 `test-user-001`（純後端 API / 單機開發用）
   - 純打後端 API（Swagger / curl）可用 `Authorization: Bearer TEST_MODE` 跳過，無需 token

4. **已知限制**：
   - Firebase ID Token 約 **1 小時過期**，目前未自動續期，掛太久後 API 會回 401 需重新登入
   - `backend/firebase_service_account.json` 的 private key 目前無法做 Admin **寫入**操作（`create_user` 等會回 `Invalid JWT Signature`）；但**驗證 token（登入）不受影響**。若日後需要 Admin 寫入功能，需到 Firebase 主控台重新產生 service account 金鑰

---

## 13. 前後端串聯清單（完整）

> 圖例：✅ 已串聯  ⚠️ 部分串聯／有問題  ❌ 完全未串聯  🔴 MOCK（假資料擋住真實呼叫）

### 13-A. 認證（Auth）

| 項目 | 前端檔案 | 後端機制 | 狀態 |
|------|----------|----------|------|
| Firebase 登入 | `Auth.vue` | Firebase Admin SDK `@require_auth` | 🔴 **MOCK** — `Auth.vue` 只是 alert + emit，完全沒有呼叫 Firebase SDK；登入後 `localStorage` 沒有真實 ID Token |
| axios 帶 Token | `api/client.js:8` | `Authorization: Bearer <token>` | ⚠️ fallback 為 `'TEST_MODE'`（`FLASK_TESTING=true` 時有效，正式環境會 401） |
| 啟動時同步旅程 | `main.js:8` `loadTripsFromApi()` | `GET /api/trips` | ⚠️ 在使用者登入前就執行，Token 永遠是 `TEST_MODE` |

**需要做的事：**
1. 在 `Auth.vue` 中整合 Firebase SDK（`signInWithEmailAndPassword` / `createUserWithEmailAndPassword`）
2. 登入成功後把 `await user.getIdToken()` 存入 `localStorage.setItem('authToken', token)`
3. 把 `loadTripsFromApi()` 移到登入成功後觸發，或加入 token 守衛

---

### 13-B. 旅程 CRUD（Trips）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 啟動載入旅程 | `travelStore.js:116` `loadTripsFromApi()` | `GET /api/trips` | ✅ 已串聯（但 Token 問題見 13-A） |
| 新增旅程 | `TravelDashboard.vue` → `addTrip()` | `POST /api/trips` | ✅ 已串聯 |
| 更新旅程（含編輯表單） | `TravelDashboard.vue` → `updateTrip()` | `PUT /api/trips/:id` | ✅ 已串聯 |
| 刪除旅程 | `TripCard.vue`（三點選單）→ `deleteTrip()` | `DELETE /api/trips/:id` | ✅ 已串聯 |
| 行程 items 儲存（新增/編輯/刪除 item） | `ItineraryPage.vue` → `saveTripChanges()` | `PUT /api/trips/:id` | ✅ 已串聯 |
| 批次同步（localStorage → 後端） | `travelStore.js:131` `apiSyncTrips()` | `POST /api/trips/sync` | ✅ 已串聯 |

---

### 13-C. 航班（Flight）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 查詢航班即時資料 | 無（尚未實作） | `GET /api/flight/info?flightNum=&date=` | ❌ **完全未串聯** — 後端 API 就緒，前端沒有任何 UI 或呼叫 |
| 顯示航班 | `FlightPage.vue:16` `trip.value.flights` | （不呼叫後端） | 🔴 **全靠 travelStore 本地資料**（來自 travelData.json mock 或手動加入） |
| 新增航班到旅程 | 無對應 UI | — | ❌ **FlightPage 沒有「新增航班」按鈕** |
| TripModal 轉機資料 | `TripModal.vue` → `layovers[]` | — | ⚠️ `layovers[]` 只存城市/小時/航班號，**從未呼叫 `/api/flight/info` 自動帶入真實資料**，也不填入 `trip.flights[]` |

**需要做的事：**
1. 在 FlightPage 或 TripModal 新增「查詢航班」功能，呼叫 `GET /api/flight/info?flightNum=&date=`
2. 把查詢結果寫入 `trip.flights[]` 並 `saveTripChanges()`
3. 新增 `frontend/src/api/flight.js` 封裝此呼叫

---

### 13-D. AI 聊天（Chat）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 傳送訊息 | `ChatPanel.vue:196` `sendChat()` | `POST /api/chat` | 🔴 **MOCK 擋住** — `handleSend()` 第 179-189 行有 hardcoded 假回應 + `return`，永遠不會到達真實 API 呼叫 |
| 傳遞旅程上下文 | `ChatPanel.vue:111` `getTripParams()` | 作為 `tripParams` 傳送 | ✅ 已改為讀取真實 trip 資料（舊版寫死 Tokyo 的問題已修） |
| 對話歷史 | `conversationId.value` | MongoDB 存對話 | ✅ 邏輯正確，但被 MOCK 擋住無法驗證 |

**需要做的事：**
1. **刪除 `ChatPanel.vue` 177-189 行的 mock 程式碼**（有明確備註「OpenAI key 修好後請刪掉這整段」）
2. 確保 `OPENAI_API_KEY` 在後端 `.env` 中正確設定

---

### 13-E. AI 行程規劃（TripPlan）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 一站式行程規劃 | `api/trip.js:3` `planTrip()` | `POST /api/trip/plan` | ❌ **完全未串聯** — `planTrip()` 函式定義了但沒有任何元件呼叫它 |
| TripPlan 頁面 | `TripPlan.vue` | — | ⚠️ 只是包裝 `ChatPanel`，走 `/api/chat` 而非 `/api/trip/plan` |

**需要做的事：**
- 決定 `TripPlan.vue` 的定位：要改成呼叫 `/api/trip/plan` 的專用規劃頁，還是保持用 ChatPanel？目前兩者功能重疊

---

### 13-F. 天氣（Weather）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 查詢每日天氣 | `travelStore.js:380` `refreshWeatherForTrip()` | `GET /api/weather?destination=` | ✅ 已串聯 |
| TripOverviewPage 觸發 | `TripOverviewPage.vue:191` `onMounted` | — | ✅ 頁面載入時自動更新 |

---

### 13-G. 匯率（Currency）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 查詢匯率 | `travelStore.js:326` `refreshCurrencyForTrip()` | `GET /api/currency/rates?base=TWD` | ✅ 已串聯 |
| 幣別推斷 | `currency.js:22` `inferCurrencyFromDestination()` | （前端純邏輯） | ✅ 支援中英文目的地 |
| 金額換算 | `currency.js:11` `convertCurrency()` | `POST /api/currency/convert` | ⚠️ API 已定義，但沒有元件呼叫（UI 無換算功能） |

---

### 13-H. 疲勞指數（Fatigue）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| 疲勞分析 | `travelStore.js:409` `refreshFatigueForTrip()` | `POST /api/fatigue/analyze` | ✅ 已串聯 |
| FlightPage 顯示 | `FlightPage.vue:23` `trip._fatigueDetail` | — | ✅ 讀取 store 已更新的值 |
| 觸發時機 | `FlightPage.vue:78` / `TripOverviewPage.vue:191` `onMounted` | — | ✅ 頁面載入時自動更新 |

---

### 13-I. 行程 API（Itinerary Blueprint）

| 操作 | 前端入口 | 後端端點 | 狀態 |
|------|----------|----------|------|
| AI 推薦行程（存 MongoDB） | `api/trip.js:5` `getItinerary()` | `POST /api/itinerary/recommend` | ❌ `getItinerary()` 是 GET 方法，且沒有任何元件呼叫 |
| 歷史行程列表 | 無 | `GET /api/itinerary/user/history` | ❌ 完全未串聯 |
| 取得單一行程 | `api/trip.js:5` `getItinerary(id)` | `GET /api/itinerary/:id` | ❌ 已定義但從未呼叫 |
| 更新行程 | — | `PUT /api/itinerary/:id` | ❌ 完全未串聯 |
| 刪除行程 | — | `DELETE /api/itinerary/:id` | ❌ 完全未串聯 |

> 注意：前端目前的「行程管理」（ItineraryPage 的每日 items）走 `/api/trips` CRUD，不是 `/api/itinerary`。`/api/itinerary` 的定位是 AI 生成、存 MongoDB 的「行程推薦文件」，與前端日常編輯的行程 items 是兩個不同層級的資料。需釐清使用情境。

---

### 13-J. 預算（Budget）與景點搜尋（Places）

| 功能 | 前端 | 後端端點 | 狀態 |
|------|------|----------|------|
| 預算估算 | 無 `api/budget.js` | `POST /api/budget/estimate` | ❌ **完全未串聯**（無前端呼叫，無 api 封裝） |
| Google Places 搜尋 | 無 | `GET /api/places/search` | ❌ **完全未串聯**（後端使用於 `/api/trip/plan` 內部，但前端沒有景點搜尋 UI） |

---

## 14. 假資料（Mock Data）標注

### 🔴 Level 1：阻擋真實 API 呼叫的 MOCK（最高優先修復）

| 位置 | 描述 | 如何解除 |
|------|------|---------|
| `ChatPanel.vue:177-189` | `handleSend()` 最頂端直接 push 假回應然後 `return`，完全繞過後端 chat API | 刪除該段 mock 程式碼（已有備註說明）；確保 `OPENAI_API_KEY` 設定 |
| `Auth.vue:79-95` | `handleSubmit()` 只做 `alert()` 後 emit，無任何真實認證 | 整合 Firebase SDK；登入後把 ID Token 存入 `localStorage.setItem('authToken', token)` |

### 🟡 Level 2：使用本地假資料但不阻擋 API（次要修復）

| 位置 | 描述 | 影響範圍 |
|------|------|---------|
| `travelData.json` | 初始旅程資料，內含完整 mock trips（CI108 東京航班、行程 items 等） | 若 localStorage 為空 且 `/api/trips` 無資料，這份資料會被當成真實資料顯示 |
| `FlightPage.vue:16` `trip.value.flights` | 航班卡片完全讀自 store，store 的 `flights[]` 只有 travelData.json 的 mock 資料；無 UI 新增/刪除 | FlightPage 呈現假航班，時差計算也以假資料為基礎 |
| `travelStore.js:195-201` | `createTripFromForm()` 中 `coverImage` 寫死為 Unsplash 照片連結 | 新增旅程的封面永遠是同一張預設圖 |
| `TripModal.vue` `layovers[]` | 轉機資料儲存後，航班號不會自動查詢 `/api/flight/info` 填入真實資訊 | 轉機/疲勞計算缺乏真實起降時間與時區 |

### 🟢 Level 3：前端邏輯層的硬編碼（低優先）

| 位置 | 描述 |
|------|------|
| `travelStore.js:362-378` `toEnglishDestination()` | 中文城市名硬編碼對應英文，不在此 map 中的城市無法查天氣 |
| `currency.js:22-93` `inferCurrencyFromDestination()` | 目的地 → 幣別硬編碼對應表，不在列表的地區查不到匯率 |
| `FlightPage.vue:29` `fatigueScore` fallback | 若 `_fatigueDetail` 不存在，fallback 計算 `100 - parseFloat(fatigue)%`，再 fallback 到 `82` |
| `travelStore.js:434` `isRedEye: false` | 疲勞計算中「是否紅眼班機」寫死為 false，不讀 TripModal 的補眠設定 |

---

## 12. 重要開發慣例

1. **後端**：商業邏輯一律寫在 `services/`，`routes/` 只做參數解析與 HTTP 回應
2. **後端**：每個 route 都要掛 `@require_auth`，測試時用 `FLASK_TESTING=true` 或 `Bearer TEST_MODE` 跳過
3. **前端**：所有頁面透過 `travelStore` 存取旅程資料，不要在元件 local state 重複儲存行程主資料
4. **前端**：使用 `getTripOrDefault(route.params.id)` 而非直接 `getTripById`，避免找不到旅程時崩潰
5. **前端**：API 呼叫統一透過 `frontend/src/api/client.js` 的 axios 實例，自動處理 Bearer Token
