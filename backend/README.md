# TravelWise Backend 🛠️

Flask 3.x + MongoDB Atlas + OpenAI Function Calling 的旅遊行程推薦後端。

> 前端卡片 Schema 與整合流程請看：[根目錄 README](../README.md)

---

## 📁 專案結構

```
backend/
├── app.py                          # Flask 進入點，所有 Blueprint 在此註冊
├── start_server.py                 # 開發用啟動腳本（自動載入 .env）
├── .env                            # 環境變數（不上傳 Git）
├── .env.example                    # 環境變數範本
├── requirements.txt                # Python 套件清單
│
├── config/
│   ├── database.py                 # MongoDB 單例連線（cached connection pool）
│   └── swagger_config.py          # Swagger UI 全域設定
│
├── api/
│   ├── routes/
│   │   ├── trip.py                 # ⭐ POST /api/trip/plan（一站式整合端點）
│   │   ├── chat.py                 # POST /api/chat
│   │   ├── weather.py              # GET  /api/weather
│   │   ├── places.py               # GET  /api/places/search, /api/places/<xid>
│   │   ├── budget.py               # POST /api/budget/calculate
│   │   ├── itinerary.py            # POST /api/itinerary/recommend + CRUD
│   │   └── fatigue.py              # POST /api/fatigue/analyze（隊友負責）
│   └── swagger/
│       ├── weather.yaml
│       ├── places_search.yaml
│       ├── places_detail.yaml
│       ├── budget.yaml
│       ├── chat.yaml
│       └── fatigue.yaml
│
├── services/
│   ├── chat_service.py             # OpenAI Function Calling 核心（最多 10 輪）
│   ├── places_service.py           # OpenTripMap 景點搜尋 + Redis 快取
│   ├── weather_service.py          # Open-Meteo 天氣查詢 + Redis 快取
│   ├── budget_service.py           # 預算分配計算（五類比例）
│   ├── itinerary_service.py        # 行程生成 + Nearest Neighbor 地理排序
│   └── fatigue_service.py          # 疲勞分析（TODO，隊友實作）
│
├── models/
│   ├── conversation.py             # 對話紀錄 MongoDB CRUD
│   ├── itinerary.py                # 行程 MongoDB CRUD
│   └── user.py                     # 使用者 MongoDB CRUD
│
└── utils/
    ├── auth_middleware.py           # @require_auth Firebase 驗證 Decorator
    ├── cache.py                     # Redis 快取工具（失敗時靜默忽略）
    └── error_handlers.py            # 統一 HTTP 錯誤格式（含 traceback）
```

---

## ⚙️ 環境設定

### 1. 建立 `.env`

```env
FLASK_ENV=development
FLASK_DEBUG=true
PORT=5001

MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxx.mongodb.net/travelwise?retryWrites=true&w=majority
REDIS_URL=redis://localhost:6379/0

FIREBASE_SERVICE_ACCOUNT_PATH=./firebase_service_account.json
FIREBASE_PROJECT_ID=wisetrip-31013

OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5-mini

OPENTRIPMAP_API_KEY=...
```

### 2. 安裝套件

```bash
pip3 install -r requirements.txt
```

### 3. 啟動 Redis

```bash
brew install redis && brew services start redis
redis-cli ping   # → PONG
```

### 4. 啟動 Server

```bash
python3 start_server.py
```

```
✅ TravelWise backend running at http://localhost:5001
📖 Swagger UI: http://localhost:5001/api/docs
```

> ⚠️ macOS Port 5000 被 AirPlay 佔用，請改用 **5001**

---

## 🔐 認證機制

所有 API 皆需帶 Firebase ID Token：

```
Authorization: Bearer <Firebase ID Token>
```

**開發測試**可用 TEST_MODE 跳過 Firebase（自動注入 `uid: test-user-001`）：

```
Authorization: Bearer TEST_MODE
```

---

## 📡 API 完整說明

### Swagger UI
```
http://localhost:5001/api/docs
```

---

### ⭐ `POST /api/trip/plan` — 一站式旅遊規劃

對應使用者流程步驟 3~9，前端只需呼叫這一支。

**內部執行順序：**
```
1. 必填欄位驗證
2. 步驟 4：城市驗證（search_spots 試查，失敗回 422）
3. 步驟 7：疲勞分析
   ├── 有帶 fatigueScore → _build_fatigue_from_score()
   └── 沒帶 → _compute_fatigue()（目前為 placeholder，score=50）
4. 步驟 6：組成 trip_params → recommend_itinerary()（GPT Function Calling）
5. 步驟 8+9：回傳 { destination, fatigue, itinerary, weather }
```

**Request**
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
    "isRedEye": false
  },
  "travelers": [
    { "ageGroup": "adult", "fitnessLevel": "medium" }
  ],
  "trip": {
    "days": 3,
    "budget": 60000,
    "travelStyle": "觀光景點",
    "transportMode": "大眾運輸",
    "mustVisit": ["淺草寺"]
  },
  "fatigueScore": 50
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `flight.arrivalCity` | ✅ | 目的地（英文）|
| `flight.flightDurationHours` | ✅ | 飛行時數 |
| `travelers[].ageGroup` | ✅ | child / adult / senior |
| `travelers[].fitnessLevel` | ✅ | low / medium / high |
| `trip.days` | ✅ | 旅遊天數 |
| `trip.travelStyle` | ✅ | 輕鬆休閒 / 觀光景點 |
| `fatigueScore` | ❌ | 0–100，由隊友模組計算後帶入 |

**travelStyle → preferences 對照**

| travelStyle | 自動對應偏好 |
|-------------|------------|
| 輕鬆休閒 | 自然、美食、購物 |
| 觀光景點 | 文化、歷史、宗教、拍照 |

**城市驗證失敗回傳（422）**
```json
{
  "error": "無法識別目的地城市，請確認城市名稱（建議使用英文）",
  "field": "flight.arrivalCity"
}
```

**curl 測試範例**
```bash
curl -X POST "http://localhost:5001/api/trip/plan" \
  -H "Authorization: Bearer TEST_MODE" \
  -H "Content-Type: application/json" \
  -d '{
    "flight": {"departureCity":"Taipei","arrivalCity":"Tokyo","flightDurationHours":3.5,"layoverCount":0,"isRedEye":false,"departureTz":"Asia/Taipei","arrivalTz":"Asia/Tokyo"},
    "travelers": [{"ageGroup":"adult","fitnessLevel":"medium"}],
    "trip": {"days":3,"budget":60000,"travelStyle":"觀光景點","transportMode":"大眾運輸"}
  }'
```

---

### `GET /api/weather` — 天氣查詢

**Query Params**

| 參數 | 必填 | 說明 |
|------|------|------|
| `destination` | ✅ | 城市名（英文），如 `Tokyo` |

```bash
curl "http://localhost:5001/api/weather?destination=Tokyo" \
  -H "Authorization: Bearer TEST_MODE"
```

**Response Schema → WeatherCard**（詳見根目錄 README）

---

### `GET /api/places/search` — 景點搜尋

**Query Params**

| 參數 | 必填 | 預設 | 說明 |
|------|------|------|------|
| `city` | ✅ | — | 城市名（英文）|
| `preferences` | ❌ | 全部 | 逗號分隔：文化,歷史,美食,自然,購物,娛樂,宗教 |
| `radius` | ❌ | 5000 | 搜尋半徑（公尺）|
| `limit` | ❌ | 20 | 回傳筆數 |

```bash
curl "http://localhost:5001/api/places/search?city=Tokyo&preferences=文化,美食&limit=5" \
  -H "Authorization: Bearer TEST_MODE"
```

---

### `GET /api/places/<xid>` — 景點詳情

```bash
curl "http://localhost:5001/api/places/Q963514" \
  -H "Authorization: Bearer TEST_MODE"
```

---

### `POST /api/budget/calculate` — 預算分配

**預算五類比例（固定）**

| 類別 | 比例 |
|------|------|
| 住宿 | 35% |
| 餐費 | 25% |
| 交通 | 15% |
| 活動/景點票價 | 20% |
| 緊急備用 | 5% |

**Request**
```json
{
  "totalBudget": 60000,
  "days": 3,
  "travelers": 2,
  "currency": "TWD",
  "spots": [
    { "name": "晴空塔", "ticketPrice": 2100 },
    { "name": "淺草寺", "ticketPrice": 0 }
  ]
}
```

---

### `POST /api/chat` — AI 對話

GPT 自動呼叫工具：

| 工具 | 說明 |
|------|------|
| `search_spots` | 搜尋城市景點（OpenTripMap）|
| `get_spot_detail` | 取得景點詳情（含圖片、Wikipedia）|

**Request**
```json
{
  "message": "幫我規劃 3 天東京行程，喜歡文化和美食",
  "conversationId": null,
  "tripParams": {
    "destination": "Tokyo",
    "days": 3,
    "travelers": 2,
    "preferences": ["文化", "美食"]
  }
}
```

---

### `POST /api/itinerary/recommend` — AI 生成行程

**內部流程：**
```
1. 組成自然語言 prompt
2. GPT Function Calling（最多 10 輪）
3. 解析行程 JSON
4. Nearest Neighbor 地理排序景點
5. 存入 MongoDB
6. 回傳 ItineraryCard
```

**Request**
```json
{
  "destination": "Tokyo",
  "days": 3,
  "travelers": 2,
  "budget": 60000,
  "transportMode": "大眾運輸",
  "preferences": ["文化", "美食"],
  "mustVisit": ["淺草寺"],
  "fatigueContext": {
    "finalScore": 50,
    "level": "中等",
    "recoverHours": 6
  }
}
```

---

### 行程 CRUD

| Method | 路由 | 說明 |
|--------|------|------|
| `GET` | `/api/itinerary/user/history` | 我的所有行程 |
| `GET` | `/api/itinerary/<id>` | 取得單一行程 |
| `PUT` | `/api/itinerary/<id>` | 更新行程（拖拉排序後呼叫）|
| `DELETE` | `/api/itinerary/<id>` | 刪除行程 |

---

### `POST /api/fatigue/analyze` — 疲勞分析（隊友模組）

> ⚠️ `fatigue_service.py` 的 `analyze_fatigue()` 目前為 `NotImplementedError`，等隊友實作。
> `POST /api/trip/plan` 已預留接口，隊友完成後只需修改 `trip.py` 的 `_compute_fatigue()` 即可。

**Expected Request**
```json
{
  "departureTimezone": "Asia/Taipei",
  "arrivalTimezone": "Asia/Tokyo",
  "flightDurationHours": 3.5,
  "layoverCount": 0,
  "isRedEye": false,
  "travelers": [
    { "ageGroup": "adult", "fitnessLevel": "medium" }
  ]
}
```

**Expected Response → FatigueCard Schema**
```json
{
  "baseScore": 45,
  "level": "中等",
  "energyBattery": 65,
  "jetLagIndex": 3,
  "suggestedStartTime": "10:00",
  "tripStressType": "一般行程",
  "recoverHours": 6,
  "explanation": "跨越 1 個時區，飛行 3.5 小時，整體疲勞屬中等。"
}
```

---

## 🗄️ MongoDB Collections

### `conversations`
```json
{ "_id": "UUID", "userUid": "firebase-uid", "createdAt": "ISO8601" }
```

### `messages`
```json
{
  "_id": "UUID",
  "conversationId": "UUID",
  "userUid": "firebase-uid",
  "role": "user | assistant | tool",
  "content": "訊息內容",
  "createdAt": "ISO8601"
}
```

### `itineraries`
```json
{
  "_id": "UUID",
  "userId": "firebase-uid",
  "title": "3天東京行程",
  "days": [
    {
      "dayNumber": 1,
      "theme": "文化散策",
      "spots": [
        {
          "xid": "Q3530518",
          "name": "景點名稱",
          "lat": 35.68,
          "lon": 139.69,
          "arrivalTime": "09:00",
          "stayDuration": 90,
          "ticketPrice": 0,
          "description": "...",
          "notes": "..."
        }
      ]
    }
  ],
  "budget": { "total": 60000, "currency": "TWD", "breakdown": {} },
  "createdAt": "ISO8601",
  "updatedAt": "ISO8601"
}
```

---

## �� 技術選型

| 項目 | 技術 | 說明 |
|------|------|------|
| Web 框架 | Flask 3.1 | Blueprint 模組化，`app.json.ensure_ascii=False` |
| API 文件 | Flasgger (Swagger UI) | `/api/docs` |
| 資料庫 | MongoDB Atlas | PyMongo + certifi，連線失敗不 crash |
| 快取 | Redis | 景點 24hr / 天氣 1hr，失敗靜默忽略 |
| AI | OpenAI gpt-5-mini | Function Calling，最多 10 輪 |
| 景點資料 | OpenTripMap | 免費，無需信用卡 |
| 天氣資料 | Open-Meteo | 免費，無需 API Key |
| 身份驗證 | Firebase Admin SDK | ID Token，TEST_MODE 跳過 |
| 跨域 | Flask-CORS | 允許 localhost:5173 + production domain |

---

## ✅ API 測試狀態

| API | 狀態 | 備註 |
|-----|------|------|
| `GET /api/weather` | ✅ | 7 天真實預報，Redis 快取 |
| `GET /api/places/search` | ✅ | OpenTripMap，Redis 快取 |
| `GET /api/places/<xid>` | ✅ | 含地址、描述、圖片、Wikipedia |
| `POST /api/budget/calculate` | ✅ | 超預算警告正確觸發 |
| `POST /api/chat` | ✅ | GPT Function Calling 10 輪 |
| `POST /api/trip/plan` | ✅ | 完整流程（城市驗證+疲勞+AI行程）|
| `POST /api/itinerary/recommend` | ✅ | AI 行程 + Nearest Neighbor + MongoDB |
| `GET /api/itinerary/user/history` | ✅ | MongoDB 查詢 |
| `GET /api/itinerary/<id>` | ✅ | MongoDB 查詢 |
| `PUT /api/itinerary/<id>` | ✅ | MongoDB 更新 |
| `DELETE /api/itinerary/<id>` | ✅ | MongoDB 刪除 |
| `POST /api/fatigue/analyze` | ⏳ | 等隊友疲勞模組完成 |

---

## ⚠️ 已知限制與注意事項

1. **MongoDB Atlas IP 白名單**：每換網路環境需至 Atlas → Network Access 加新 IP
2. **gpt-5-mini 不支援 `temperature` 參數**：已移除，勿自行加回
3. **Python 3.13 + OpenSSL 3.0**：Atlas 連線需要 certifi，已在 `database.py` 設定
4. **macOS Port 5000**：被 AirPlay 佔用，固定使用 **5001**
5. **疲勞模組**：`fatigue_service.py` 目前 `raise NotImplementedError`，`/api/fatigue/analyze` 會回 500；但 `/api/trip/plan` 有 placeholder 保護，不受影響
