# TravelWise 🌏
### 全齡化旅行適應決策支援平台

> **Group H｜期末專案**  
> 資管四 B10705037 關凱欣、經濟四 B11303045 林鼎鈞、外文二 B13102010 李艾蓁、B12106001 林奕睿、圖資四 B11106054 蔡怡萱、資管三 B12705024 吳宇平

---

## 📌 專案簡介

TravelWise 是一套整合 **AI 行程規劃、飛行疲勞生理模型、即時天氣、景點資料**的旅遊決策支援平台。  
核心目標：把複雜的生理數據與環境資訊，轉譯為易懂的白話建議與可視化卡片，幫助全年齡使用者規劃最合適的行程。

---

## 🧩 使用者流程（Option 2）

```
步驟 1  登入 / 註冊（Firebase Auth）
步驟 2  選擇旅客人數與年齡區間（選項式，不需打字）
步驟 3  填入航班資料（出發/抵達城市、起降時間、轉機次數）
步驟 4  後端驗證城市名稱可識別（失敗則顯示錯誤提示）
步驟 5  選擇旅遊風格（輕鬆休閒 / 觀光景點）
步驟 6  AI 生成 Day by Day 行程
步驟 7  後端自動計算疲勞分數、時差、年齡加權（前端顯示 loading）
步驟 8  顯示：時差適應指數、體力電池、建議活動開始時間、行程壓力類型
步驟 9  行程總覽確認 → 存入資料庫
```

---

## 🏗️ 技術架構

```
前端 (Frontend)   →  React + Vite + TailwindCSS
後端 (Backend)    →  Python Flask 3.x (REST API, Blueprint 模組化)
資料庫            →  MongoDB Atlas (PyMongo)
快取              →  Redis（景點 24hr / 天氣 1hr）
AI                →  OpenAI gpt-5-mini（Function Calling 自動查景點）
景點資料          →  OpenTripMap（免費 API）
天氣資料          →  Open-Meteo（免費，無需 Key）
身份驗證          →  Firebase Admin SDK（ID Token）
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
| `POST` | `/api/trip/plan` | ⭐ 一站式旅遊規劃（步驟 3~9）|
| `POST` | `/api/itinerary/recommend` | 單獨呼叫 AI 生成行程 |
| `GET`  | `/api/itinerary/user/history` | 我的歷史行程列表 |
| `GET`  | `/api/itinerary/<id>` | 取得單一行程 |
| `PUT`  | `/api/itinerary/<id>` | 更新行程 |
| `DELETE` | `/api/itinerary/<id>` | 刪除行程 |
| `POST` | `/api/fatigue/analyze` | 疲勞分析（隊友模組）|

> 📖 完整 Swagger UI：`http://localhost:5001/api/docs`

---

## 🚀 快速開始

### 環境需求
- Python >= 3.11
- Node.js >= 18
- Redis：`brew install redis && brew services start redis`
- MongoDB Atlas（需將本機 IP 加入白名單）

### 後端啟動
```bash
cd backend
cp .env.example .env          # 填入各 API Key
pip3 install -r requirements.txt
python3 start_server.py
```

```
✅ TravelWise backend running at http://localhost:5001
📖 Swagger UI: http://localhost:5001/api/docs
```

> ⚠️ macOS Port 5000 被 AirPlay 佔用，請改用 **5001**

### 測試用認證 Header
```
Authorization: Bearer TEST_MODE
```

---

## 🔄 主要整合端點

### `POST /api/trip/plan` ⭐

前端**只需呼叫這一支**，後端自動串接：城市驗證 → 疲勞分析 → AI 生成行程。

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
    "isRedEye": false
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
  },
  "fatigueScore": 50
}
```

> `fatigueScore` 為**選填**。  
> 有帶 → 直接換算成卡片指標。  
> 沒帶 → 後端 placeholder（固定 50），回傳中標記 `"_placeholder": true`。

**Response**
```json
{
  "destination": "Tokyo",
  "fatigue":    { "...": "→ FatigueCard" },
  "itinerary":  { "...": "→ ItineraryCard" },
  "weather":    null
}
```

---

## 🃏 前端卡片 Response Schema

所有 API 依照固定 Schema，前端直接 map 到 HTML 卡片渲染。

---

### 🌤️ WeatherCard — `GET /api/weather`

```json
{
  "destination": "東京",
  "clothingSuggestion": "氣溫涼爽，建議穿著長袖搭配薄外套；預報有降雨，請攜帶雨傘",
  "alerts": [
    { "date": "2026-06-03", "message": "2026-06-03 降雨機率 85%，請攜帶雨具" }
  ],
  "forecast": [
    {
      "date": "2026-06-01",
      "tempMax": 28.5,
      "tempMin": 19.2,
      "feelsLike": 30.1,
      "humidity": 72.0,
      "windKmh": 12.3,
      "condition": "多雲",
      "precipProb": 15
    }
  ]
}
```

| 欄位 | 類型 | 卡片用途 |
|------|------|---------|
| `destination` | string | 卡片標題 |
| `clothingSuggestion` | string | 穿搭建議文字區塊 |
| `alerts[]` | array | 警告 badge（降雨機率 ≥70% 才出現）|
| `forecast[].condition` | string | 天氣 icon（晴天/多雲/雨/雪/雷雨/霧）|
| `forecast[].feelsLike` | number | 主要顯示溫度 |
| `forecast[].precipProb` | integer 0–100 | 雨傘 icon 觸發條件 |

---

### 😴 FatigueCard — `POST /api/trip/plan` → `fatigue`

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
  "_placeholder": true
}
```

| 欄位 | 類型 | 卡片用途 |
|------|------|---------|
| `baseScore` | integer 0–100 | 疲勞指數數字顯示 |
| `level` | string | 標籤 badge（低/中等/高/極高）|
| `energyBattery` | integer 0–100 | 電池進度條 % |
| `jetLagIndex` | integer | 時差適應指數（小時）|
| `suggestedStartTime` | string HH:MM | 建議出發時間 highlight |
| `tripStressType` | string | 行程類型標籤（高壓力行程/一般行程）|
| `recoverHours` | integer | 建議恢復時數 |
| `explanation` | string | 說明段落，直接顯示 |
| `_placeholder` | boolean | `true` → 顯示「⚠️ 疲勞模組整合中」提示 |

**分級對照**

| baseScore | level | energyBattery | suggestedStartTime | tripStressType |
|-----------|-------|--------------|-------------------|----------------|
| 0–29 | 低 | 85% | 09:00 | 一般行程 |
| 30–54 | 中等 | 65% | 10:00 | 一般行程 |
| 55–74 | 高 | 45% | 11:00 | 高壓力行程 |
| 75–100 | 極高 | 25% | 13:00 | 高壓力行程 |

---

### 🗓️ ItineraryCard — `POST /api/trip/plan` → `itinerary`

```json
{
  "itineraryId": "be36f77d-2c0a-4f93-a91b-4f64128efbd3",
  "userId": "test-user-001",
  "title": "3天東京新宿文化・歷史・攝影之旅",
  "days": [
    {
      "dayNumber": 1,
      "theme": "新宿古今巡禮（市政建築、神社、公園）",
      "spots": [
        {
          "xid": "Q3530518",
          "name": "Tokyo City Hall Tower II",
          "description": "新宿區的市政大樓，現代建築代表，適合拍照與認識都廳歷史。",
          "lat": 35.6879,
          "lon": 139.6920,
          "arrivalTime": "09:00",
          "stayDuration": 60,
          "ticketPrice": 0,
          "notes": "建議早上前往拍攝外觀；若要上展望台請事先確認開放規定。"
        }
      ]
    }
  ],
  "budget": {
    "total": 60000,
    "currency": "TWD",
    "breakdown": {}
  },
  "createdAt": "Mon, 04 May 2026 08:45:17 GMT",
  "updatedAt": "Mon, 04 May 2026 08:45:17 GMT"
}
```

| 欄位 | 類型 | 卡片用途 |
|------|------|---------|
| `itineraryId` | string UUID | 儲存後用於 CRUD |
| `title` | string | 行程卡片大標題 |
| `days[].dayNumber` | integer | Day 1 / Day 2 … |
| `days[].theme` | string | 當天副標題 |
| `spots[].name` | string | 景點卡片標題 |
| `spots[].description` | string | 景點說明段落 |
| `spots[].arrivalTime` | string HH:MM | 時間軸顯示 |
| `spots[].stayDuration` | integer 分鐘 | 停留時間標籤 |
| `spots[].ticketPrice` | number | 票價（0 = 免費 badge）|
| `spots[].notes` | string | GPT 提醒事項（小字）|
| `spots[].lat` / `lon` | number | 地圖 pin 座標 |

---

### 💰 BudgetCard — `POST /api/budget/calculate`

```json
{
  "totalBudget": 60000,
  "currency": "TWD",
  "perPerson": 30000,
  "days": 3,
  "travelers": 2,
  "isOverBudget": false,
  "warnings": [],
  "breakdown": {
    "accommodation": { "total": 21000, "perPersonPerNight": 5250.0, "ratio": 0.35 },
    "food":          { "total": 15000, "perPersonPerDay": 2500.0,   "ratio": 0.25 },
    "transport":     { "total": 9000,  "ratio": 0.15 },
    "activities": {
      "total": 12000,
      "ticketTotal": 3000,
      "spotCosts": [
        { "name": "淺草寺", "pricePerPerson": 0,    "subtotal": 0 },
        { "name": "晴空塔", "pricePerPerson": 2100, "subtotal": 4200 }
      ],
      "ratio": 0.20
    },
    "emergency": { "total": 3000, "ratio": 0.05 }
  }
}
```

| 欄位 | 類型 | 卡片用途 |
|------|------|---------|
| `isOverBudget` | boolean | 紅色警告 banner |
| `warnings[]` | array | 警告文字列表 |
| `perPerson` | number | 每人預算顯示 |
| `breakdown.*` | object | 圓餅圖 / 長條圖資料 |

---

### 📍 SpotSearchCard — `GET /api/places/search`

```json
[
  {
    "xid": "Q963514",
    "name": "Tōkaidō",
    "kinds": "cultural,interesting_places",
    "lat": 35.6894,
    "lon": 139.6917,
    "rate": 3,
    "dist": 11.13
  }
]
```

---

### �� SpotDetailCard — `GET /api/places/<xid>`

```json
{
  "xid": "Q963514",
  "name": "Tōkaidō",
  "kinds": "cultural,interesting_places",
  "lat": 35.6894,
  "lon": 139.6917,
  "description": "The Tōkaidō road was the most important of the Five Routes...",
  "image": "https://upload.wikimedia.org/wikipedia/commons/...",
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

## ✅ API 測試狀態

| API | 狀態 | 備註 |
|-----|------|------|
| `GET /api/weather` | ✅ | 7 天真實預報 + 衣物建議 |
| `GET /api/places/search` | ✅ | OpenTripMap 真實資料 |
| `GET /api/places/<xid>` | ✅ | 含地址、圖片、Wikipedia |
| `POST /api/budget/calculate` | ✅ | 超預算警告正確觸發 |
| `POST /api/chat` | ✅ | GPT Function Calling 自動查景點 |
| `POST /api/trip/plan` | ✅ | 城市驗證 + 疲勞 + AI 行程完整流程 |
| `POST /api/itinerary/recommend` | ✅ | AI 生成行程 + 存 MongoDB |
| `GET /api/itinerary/user/history` | ✅ | MongoDB 正常 |
| `GET /api/itinerary/<id>` | ✅ | MongoDB 正常 |
| `POST /api/fatigue/analyze` | ⏳ | 等隊友疲勞模組完成 |

---

## 👥 分工說明

| 模組 | 負責人 | 狀態 |
|------|--------|------|
| Flask 後端骨架 + 所有 API | 林鼎鈞 | ✅ |
| `POST /api/trip/plan` 整合端點 | 林鼎鈞 | ✅ |
| 前端 React 卡片元件 | 其他組員 | 進行中 |
| `POST /api/fatigue/analyze` 疲勞模組 | 待確認 | ⏳ placeholder 中 |

### ⚙️ 疲勞模組接手說明

完成 `fatigue_service.py` 後，只需修改 `backend/api/routes/trip.py` 中的 `_compute_fatigue()` 一個函式：

```python
def _compute_fatigue(flight_data, travelers):
    from services.fatigue_service import analyze_fatigue
    return analyze_fatigue(
        departure_tz       = flight_data["departureTz"],
        arrival_tz         = flight_data["arrivalTz"],
        flight_duration_hr = flight_data["flightDurationHours"],
        layover_count      = flight_data.get("layoverCount", 0),
        is_red_eye         = flight_data.get("isRedEye", False),
        travelers          = travelers,
    )
```

回傳格式需包含：`baseScore, level, energyBattery, jetLagIndex, suggestedStartTime, tripStressType, recoverHours, explanation`

---

## 🔗 相關連結

- [後端 API 詳細文件](./backend/README.md)
- [Swagger UI](http://localhost:5001/api/docs)（需啟動 server）
- [MongoDB Atlas](https://cloud.mongodb.com)
- [OpenTripMap API Docs](https://opentripmap.io/docs)
- [Open-Meteo API Docs](https://open-meteo.com/en/docs)
