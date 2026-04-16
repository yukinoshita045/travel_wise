# TravelWise Backend 🛠️

Python Flask 後端 — 所有 API 以 Swagger UI 呈現

## 技術棧

| 用途 | 套件 |
|------|------|
| Web 框架 | Flask 3 |
| Swagger UI | flasgger |
| 資料庫 | MongoDB（PyMongo）|
| 快取 | Redis |
| 認證 | Firebase Admin SDK |
| AI 對話 | OpenAI GPT-4o |
| 天氣 | Open-Meteo（免費，無需 Key）|
| 景點 | Google Places API |
| 測試 | pytest + pytest-flask |

---

## 📁 後端資料夾結構

```
backend/
├── app.py                  # Flask 進入點，Blueprint 全部在這裡註冊
├── requirements.txt
├── pytest.ini
├── .env.example            # ← 複製為 .env 並填入真實 Key
│
├── config/
│   ├── database.py         # MongoDB cached connection（仿 LibreChat connect.js）
│   └── swagger_config.py   # Swagger UI / flasgger 設定
│
├── api/
│   ├── routes/             # 每個功能一個 Blueprint 檔案
│   │   ├── chat.py         # POST /api/chat
│   │   ├── weather.py      # GET  /api/weather
│   │   ├── fatigue.py      # POST /api/fatigue/analyze
│   │   ├── itinerary.py    # /api/itinerary/* (CRUD + recommend)
│   │   ├── places.py       # GET  /api/places/search | /:place_id
│   │   └── budget.py       # POST /api/budget/calculate
│   └── swagger/            # 每個 API 的 Swagger YAML 規格
│       ├── chat.yaml
│       ├── weather.yaml
│       ├── fatigue.yaml
│       ├── budget.yaml
│       └── ...（itinerary 5 個端點各一份）
│
├── services/               # 商業邏輯層（不直接碰 HTTP）
│   ├── chat_service.py     # GPT-4o 多輪對話 + System Prompt
│   ├── weather_service.py  # Open-Meteo + 體感溫度 + 衣物建議
│   ├── fatigue_service.py  # SAFTE 模型運算
│   ├── itinerary_service.py# 行程推薦邏輯 + 景點排序
│   ├── places_service.py   # Google Places API + Redis 快取
│   └── budget_service.py   # 預算分配計算
│
├── models/                 # MongoDB Collection 操作（仿 LibreChat models/）
│   ├── user.py
│   ├── conversation.py     # Conversation + Message（多輪對話）
│   └── itinerary.py
│
├── utils/
│   ├── auth_middleware.py  # @require_auth decorator（Firebase Token 驗證）
│   ├── cache.py            # Redis get/set 工具
│   └── error_handlers.py   # 統一錯誤格式
│
└── tests/
    ├── conftest.py         # pytest fixtures
    ├── unit/               # 純邏輯單元測試（不需 DB / API）
    │   ├── test_fatigue_service.py
    │   └── test_budget_service.py
    └── integration/        # API 整合測試（Flask test client）
```

---

## 🚀 啟動方式

```bash
cd backend

# 1. 建立虛擬環境
python -m venv venv
source venv/bin/activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 用編輯器填入 MONGO_URI, OPENAI_API_KEY, GOOGLE_PLACES_API_KEY 等

# 4. 啟動
python app.py
```

**Swagger UI：** http://localhost:5000/api/docs

---

## 🔑 API 端點總覽

| Method | 路徑 | 功能 | 需要登入 |
|--------|------|------|---------|
| POST | `/api/chat` | AI 對話 | ✅ |
| GET  | `/api/weather` | 天氣查詢 | ✅ |
| POST | `/api/fatigue/analyze` | 疲勞分析 | ✅ |
| POST | `/api/itinerary/recommend` | AI 生成行程 | ✅ |
| GET  | `/api/itinerary/user/history` | 歷史行程 | ✅ |
| GET  | `/api/itinerary/:id` | 取得行程 | ✅ |
| PUT  | `/api/itinerary/:id` | 更新行程 | ✅ |
| DELETE | `/api/itinerary/:id` | 刪除行程 | ✅ |
| GET  | `/api/places/search` | 景點搜尋 | ✅ |
| GET  | `/api/places/:place_id` | 景點詳情 | ✅ |
| POST | `/api/budget/calculate` | 預算計算 | ✅ |

---

## 🧪 執行測試

```bash
cd backend
pytest
```
