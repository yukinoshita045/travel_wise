# TravelWise Backend

Flask + MongoDB + OpenAI Function Calling 的旅遊行程推薦後端。

---

## 📁 專案結構

```
backend/
├── app.py                         # Flask 進入點，所有 Blueprint 在此註冊
├── start_server.py                # 開發用啟動腳本（自動載入 .env）
├── .env                           # 環境變數（不上傳 Git）
├── .env.example                   # 環境變數範本
├── firebase_service_account.json  # Firebase Admin SDK 金鑰（不上傳 Git）
├── requirements.txt               # Python 套件清單
│
├── config/
│   ├── database.py                # MongoDB 單例連線（仿 LibreChat connect.js）
│   └── swagger_config.py         # Swagger UI 全域設定
│
├── api/
│   ├── routes/
│   │   ├── chat.py               # POST /api/chat
│   │   ├── weather.py            # GET  /api/weather
│   │   ├── places.py             # GET  /api/places/search, /api/places/<xid>
│   │   ├── budget.py             # POST /api/budget/calculate
│   │   ├── itinerary.py          # POST /api/itinerary/recommend + CRUD
│   │   └── fatigue.py            # POST /api/fatigue/analyze（他人負責）
│   └── swagger/
│       ├── chat.yaml
│       ├── weather.yaml
│       ├── places_search.yaml
│       ├── places_detail.yaml
│       ├── budget.yaml
│       ├── itinerary_recommend.yaml
│       ├── itinerary_history.yaml
│       ├── itinerary_get.yaml
│       ├── itinerary_update.yaml
│       └── itinerary_delete.yaml
│
├── services/
│   ├── chat_service.py           # OpenAI Function Calling 核心
│   ├── places_service.py         # OpenTripMap 景點搜尋
│   ├── weather_service.py        # Open-Meteo 天氣查詢
│   ├── budget_service.py         # 預算分配計算
│   └── itinerary_service.py      # 行程生成與地理排序
│
├── models/
│   ├── conversation.py           # 對話紀錄 MongoDB CRUD
│   ├── itinerary.py              # 行程 MongoDB CRUD
│   └── user.py                   # 使用者 MongoDB CRUD
│
└── utils/
    ├── auth_middleware.py         # @require_auth Firebase 驗證 Decorator
    ├── cache.py                   # Redis 快取工具（get/set，失敗時靜默忽略）
    └── error_handlers.py          # 統一 HTTP 錯誤格式
```

---

## ⚙️ 環境設定

### 1. 建立 `.env`（複製 `.env.example`）

```env
FLASK_ENV=development
FLASK_DEBUG=true
PORT=5001

MONGO_URI=mongodb+srv://<user>:<password>@cluster0.xxx.mongodb.net/travelwise
REDIS_URL=redis://localhost:6379/0

FIREBASE_SERVICE_ACCOUNT_PATH=./firebase_service_account.json
FIREBASE_PROJECT_ID=wisetrip-31013

OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5-mini

OPENTRIPMAP_API_KEY=...
```

### 2. 安裝套件

```bash
pip3 install flask flask-cors flasgger pymongo certifi redis firebase-admin openai requests python-dotenv pytest
```

### 3. 啟動伺服器

```bash
cd backend
python3 start_server.py
```

成功後會看到：
```
✅ TravelWise backend running at http://localhost:5001
📖 Swagger UI: http://localhost:5001/api/docs
```

> ⚠️ macOS Port 5000 被 AirPlay 佔用，請改用 5001

---

## 🔐 認證機制

所有 API 皆需帶 Firebase ID Token：

```
Authorization: Bearer <Firebase ID Token>
```

**測試時**可用 `TEST_MODE` 跳過 Firebase 驗證（自動注入 `uid: test-user-001`）：

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

### 1. `GET /api/weather` — 天氣查詢

**Input（Query Params）**

| 參數 | 必填 | 類型 | 說明 | 範例 |
|------|------|------|------|------|
| `destination` | ✅ | string | 目的地城市（英文） | `Tokyo` |
| `date` | ❌ | string | 保留參數，目前未使用 | `2026-04-18` |

**curl 範例**
```bash
curl "http://localhost:5001/api/weather?destination=Tokyo" \
  -H "Authorization: Bearer TEST_MODE"
```

**Output**
```json
{
  "destination": "東京",
  "forecast": [
    {
      "date": "2026-04-18",
      "tempMax": 21.0,
      "tempMin": 8.6,
      "humidity": 75.9,
      "feelsLike": 21.0,
      "windKmh": 7.7,
      "condition": "多雲",
      "precipProb": 0
    }
  ],
  "clothingSuggestion": "氣溫涼爽，建議穿著長袖搭配薄外套；預報有降雨，請攜帶雨傘",
  "alerts": [
    { "date": "2026-04-24", "message": "2026-04-24 降雨機率 76%，請攜帶雨具" }
  ]
}
```

| 欄位 | 說明 |
|------|------|
| `forecast[].condition` | 晴天 / 多雲 / 雨 / 雪 / 雷雨 / 霧 |
| `forecast[].feelsLike` | 體感溫度（>27°C 用 Heat Index，<10°C 用 Wind Chill）|
| `clothingSuggestion` | 依平均體感溫度自動生成衣物建議 |
| `alerts` | 降雨機率 ≥70% 時觸發警告 |

---

### 2. `GET /api/places/search` — 景點搜尋

**Input（Query Params）**

| 參數 | 必填 | 類型 | 預設 | 說明 | 範例 |
|------|------|------|------|------|------|
| `city` | ✅ | string | — | 城市名（英文） | `Tokyo` |
| `preferences` | ❌ | string | 全部 | 逗號分隔偏好類型 | `文化,美食` |
| `radius` | ❌ | integer | 5000 | 搜尋半徑（公尺） | `5000` |
| `limit` | ❌ | integer | 20 | 回傳筆數上限 | `10` |

**preferences 可選值**

| 值 | 對應 OpenTripMap kinds |
|----|----------------------|
| `文化` | cultural |
| `自然` | natural |
| `美食` | foods |
| `購物` | shops |
| `娛樂` | amusements |
| `宗教` | religion |
| `歷史` | historic |

**curl 範例**
```bash
curl "http://localhost:5001/api/places/search?city=Tokyo&preferences=文化,美食&limit=5" \
  -H "Authorization: Bearer TEST_MODE"
```

**Output**
```json
[
  {
    "xid": "Q963514",
    "name": "Tōkaidō",
    "kinds": "cultural,interesting_places",
    "lat": 35.689,
    "lon": 139.691,
    "rate": 3,
    "dist": 11.13
  }
]
```

| 欄位 | 說明 |
|------|------|
| `xid` | OpenTripMap 唯一 ID，用於查詳情 |
| `rate` | 景點評分（1–3，3 最高）|
| `dist` | 距離城市中心（公尺）|

---

### 3. `GET /api/places/<xid>` — 景點詳情

**Input（Path）**

| 參數 | 說明 |
|------|------|
| `xid` | 從 `/places/search` 取得的景點 ID |

**curl 範例**
```bash
curl "http://localhost:5001/api/places/Q963514" \
  -H "Authorization: Bearer TEST_MODE"
```

**Output**
```json
{
  "xid": "Q963514",
  "name": "Tōkaidō",
  "kinds": "cultural,interesting_places",
  "lat": 35.689,
  "lon": 139.691,
  "description": "The Tōkaidō road was the most important...",
  "image": "https://upload.wikimedia.org/...",
  "wikipedia": "https://en.wikipedia.org/wiki/T%C5%8Dkaid%C5%8D",
  "opening_hours": "",
  "address": {
    "city": "新宿區",
    "country": "日本 (Japan)",
    "postcode": "163-8001",
    "road": "議事堂通り"
  }
}
```

---

### 4. `POST /api/budget/calculate` — 預算分配

**分配比例（固定）**

| 類別 | 比例 |
|------|------|
| 住宿（accommodation） | 35% |
| 餐費（food） | 25% |
| 交通（transport） | 15% |
| 活動/景點（activities） | 20% |
| 緊急備用（emergency） | 5% |

**Input（Body JSON）**

```json
{
  "totalBudget": 50000,
  "days": 5,
  "travelers": 2,
  "currency": "TWD",
  "spots": [
    { "name": "淺草寺", "ticketPrice": 0 },
    { "name": "東京晴空塔", "ticketPrice": 2100 },
    { "name": "teamLab", "ticketPrice": 3200 }
  ]
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `totalBudget` | ✅ | 總預算（數字）|
| `days` | ✅ | 天數 |
| `travelers` | ✅ | 人數 |
| `spots` | ✅ | 景點清單（空陣列也可）|
| `currency` | ❌ | 幣別，預設 TWD |

**curl 範例**
```bash
curl -X POST "http://localhost:5001/api/budget/calculate" \
  -H "Authorization: Bearer TEST_MODE" \
  -H "Content-Type: application/json" \
  -d '{
    "totalBudget": 50000,
    "days": 5,
    "travelers": 2,
    "spots": [
      {"name": "晴空塔", "ticketPrice": 2100},
      {"name": "teamLab", "ticketPrice": 3200}
    ]
  }'
```

**Output**
```json
{
  "totalBudget": 50000,
  "currency": "TWD",
  "perPerson": 25000,
  "days": 5,
  "travelers": 2,
  "breakdown": {
    "accommodation": { "total": 17500, "perPersonPerNight": 2187.5, "ratio": 0.35 },
    "food":          { "total": 12500, "perPersonPerDay": 1250.0,   "ratio": 0.25 },
    "transport":     { "total": 7500,  "ratio": 0.15 },
    "activities": {
      "total": 10000,
      "ticketTotal": 10600,
      "spotCosts": [
        { "name": "晴空塔", "pricePerPerson": 2100, "subtotal": 4200 },
        { "name": "teamLab", "pricePerPerson": 3200, "subtotal": 6400 }
      ],
      "ratio": 0.20
    },
    "emergency": { "total": 2500, "ratio": 0.05 }
  },
  "warnings": ["景點票價合計 10600 超過活動預算 10000，建議增加總預算或減少付費景點"],
  "isOverBudget": true
}
```

> ⚠️ 景點票價合計 > activities 預算時，`isOverBudget: true`，`warnings` 會有說明

---

### 5. `POST /api/chat` — AI 對話（含 Function Calling）

GPT 會自動決定是否呼叫以下工具：

| 工具名稱 | 說明 |
|---------|------|
| `search_spots` | 搜尋城市附近景點（OpenTripMap）|
| `get_spot_detail` | 取得景點詳細資料（含描述、圖片、Wikipedia）|

**Input（Body JSON）**

```json
{
  "message": "東京有哪些好玩的文化景點？",
  "conversationId": null,
  "tripParams": {
    "destination": "Tokyo",
    "days": 3,
    "travelers": 2,
    "budget": 50000,
    "transportMode": "大眾運輸",
    "maxCommuteMinutes": 30,
    "preferences": ["文化", "美食"],
    "mustVisit": ["淺草寺"]
  }
}
```

| 欄位 | 必填 | 說明 |
|------|------|------|
| `message` | ✅ | 使用者輸入的訊息 |
| `conversationId` | ❌ | 繼續舊對話（null = 開新對話）|
| `tripParams` | ❌ | 旅遊條件，注入 GPT system context |
| `tripParams.preferences` | ❌ | 文化 / 自然 / 美食 / 購物 / 娛樂 / 宗教 / 歷史 |

**curl 範例**
```bash
curl -X POST "http://localhost:5001/api/chat" \
  -H "Authorization: Bearer TEST_MODE" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "幫我規劃 3 天東京行程，喜歡文化和美食",
    "tripParams": {
      "destination": "Tokyo",
      "days": 3,
      "travelers": 2,
      "preferences": ["文化", "美食"]
    }
  }'
```

**Output — type: text（GPT 純文字回覆）**
```json
{
  "conversationId": "4ef2c7e8-2466-4160-ad3d-88d3c48e98e8",
  "reply": {
    "type": "text",
    "content": "以下是查詢後挑出的東京景點：\n1) xid: W297192269\n   名稱：明治神宮內苑..."
  }
}
```

**Output — type: itinerary（GPT 輸出完整行程 JSON 時）**
```json
{
  "conversationId": "4ef2c7e8-...",
  "reply": {
    "type": "itinerary",
    "content": {
      "title": "東京 3 天文化美食之旅",
      "days": [
        {
          "day": 1,
          "spots": [
            { "name": "明治神宮", "xid": "W297192269", "lat": 35.676, "lon": 139.699 }
          ]
        }
      ]
    }
  }
}
```

> 💡 `conversationId` 回傳後儲存，下次請求帶入即可繼續同一對話（MongoDB 長期記憶）

---

### 6. `POST /api/itinerary/recommend` — 一鍵生成行程

**內部執行流程：**
```
1. 組成自然語言 prompt
2. 呼叫 handle_chat_message()（含 Function Calling 查景點）
3. 解析 GPT 回傳的行程 JSON
4. Nearest Neighbor 演算法排序景點（減少通勤）
5. 存入 MongoDB
6. 回傳完整行程
```

**Input（Body JSON）**

```json
{
  "destination": "Tokyo",
  "days": 5,
  "travelers": 2,
  "budget": 50000,
  "transportMode": "大眾運輸",
  "maxCommuteMinutes": 30,
  "preferences": ["文化", "美食"],
  "mustVisit": ["淺草寺"],
  "conversationId": null
}
```

**Output**
```json
{
  "_id": "6626ab12cde...",
  "userUid": "firebase-uid",
  "title": "Tokyo 5天行程",
  "days": [
    {
      "day": 1,
      "spots": [
        { "name": "淺草寺", "xid": "N123", "lat": 35.71, "lon": 139.79 }
      ]
    }
  ],
  "budget": { "total": 50000, "currency": "TWD", "breakdown": {} },
  "createdAt": "2026-04-18T11:30:00"
}
```

---

### 7. 行程 CRUD

| Method | 路由 | 說明 | Input |
|--------|------|------|-------|
| `GET` | `/api/itinerary/user/history` | 取得我的所有行程列表 | 無 |
| `GET` | `/api/itinerary/<id>` | 取得單一行程詳情 | Path: MongoDB `_id` |
| `PUT` | `/api/itinerary/<id>` | 更新行程（拖拉排序後呼叫）| Body: `{"days":[...],"title":"..."}` |
| `DELETE` | `/api/itinerary/<id>` | 刪除行程 | Path: MongoDB `_id` |

---

## 🗄️ MongoDB Collections

### `conversations`
```json
{
  "_id": "UUID",
  "userUid": "firebase-uid",
  "createdAt": "2026-04-18T..."
}
```

### `messages`
```json
{
  "_id": "UUID",
  "conversationId": "UUID",
  "userUid": "firebase-uid",
  "role": "user | assistant | tool",
  "content": "訊息內容",
  "createdAt": "2026-04-18T..."
}
```

### `itineraries`
```json
{
  "_id": "UUID",
  "userUid": "firebase-uid",
  "title": "東京 5 天行程",
  "days": [ { "day": 1, "spots": [...] } ],
  "budget": { "total": 50000, "currency": "TWD" },
  "createdAt": "2026-04-18T...",
  "updatedAt": "2026-04-18T..."
}
```

---

## 🔧 技術選型

| 項目 | 技術 | 說明 |
|------|------|------|
| Web 框架 | Flask 3.1 | Blueprint 模組化 |
| API 文件 | Flasgger (Swagger UI) | `/api/docs` |
| 資料庫 | MongoDB Atlas | PyMongo + certifi（修 SSL）|
| 快取 | Redis | 景點 24hr / 天氣 1hr，失敗時靜默忽略 |
| AI | OpenAI gpt-5-mini | Function Calling 自動查景點 |
| 景點資料 | OpenTripMap | 免費，無需信用卡 |
| 天氣資料 | Open-Meteo | 免費，無需 API Key |
| 身份驗證 | Firebase Admin SDK | ID Token 驗證 |
| 跨域 | Flask-CORS | 允許 localhost:5173 |

---

## ✅ API 測試狀態

| API | 狀態 | 備註 |
|-----|------|------|
| `GET /api/weather` | ✅ 正常 | 回傳真實 7 天預報 + 衣物建議 |
| `GET /api/places/search` | ✅ 正常 | OpenTripMap 真實景點資料 |
| `GET /api/places/<xid>` | ✅ 正常 | 含地址、描述、圖片、Wikipedia |
| `POST /api/budget/calculate` | ✅ 正常 | 超預算警告正確觸發 |
| `POST /api/chat` | ✅ 正常 | GPT Function Calling 自動查景點 |
| `POST /api/itinerary/recommend` | ⏳ 未測 | 依賴 Chat，邏輯完整 |
| 行程 CRUD | ⏳ 未測 | MongoDB 操作，需有行程 ID |
