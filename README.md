# TravelWise 🌏
### 全齡化旅行適應決策支援平台

> Group H｜期末專案  
> 資管四 B10705037 關凱欣、經濟四 B11303045 林鼎鈞、外文二 B13102010 李艾蓁、B12106001 林奕睿、圖資四 B11106054 蔡怡萱、資管三 B12705024 吳宇平

---

## 📌 專案簡介

TravelWise 是一套整合 AI 對話、疲勞生理模型、即時天氣、Google Maps 的旅遊決策支援平台。  
目標是將複雜的環境數據與生理模型，轉譯為易懂的白話建議，幫助使用者規劃最適合自己的行程。

---

## 🧩 核心功能

| 功能 | 說明 |
|------|------|
| ✈️ 飛行疲勞分析 | SAFTE 模型計算疲勞指數，考量時差、轉機、紅眼航班 |
| 🌤️ 天氣 & 衣物建議 | 串接 Open-Meteo，提供體感溫度與穿搭建議 |
| 🗺️ 卡片式行程規劃 | AI 對話生成行程，支援拖拉排序 |
| 📍 景點資料整合 | Google Places API 提供評分、營業時間、訂票連結 |
| 💰 預算分配計算 | 依人數、天數、景點票價自動生成預算表 |
| 🔐 用戶認證與歷史行程 | Firebase Auth + Firestore 儲存歷史紀錄 |

---

## 🏗️ 技術架構

```
前端 (Frontend)   →  React + Vite + TailwindCSS + dnd-kit
後端 (Backend)    →  Python Flask (REST API)
資料庫 (Database) →  Firebase Firestore + Firebase Auth
外部 API          →  OpenAI GPT-4o / Google Maps & Places / Open-Meteo
```

---

## 🚀 快速開始

### 環境需求
- Node.js >= 18
- Python >= 3.11
- Firebase 專案（需自行建立）

### 前端啟動
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 後端啟動
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

---

## 📁 專案結構

```
travel_wise/
├── frontend/        # React 前端
├── backend/         # Python Flask 後端
├── database/        # Firebase 設定 & Firestore Schema
└── docs/            # 文件、API Reference、功能規格書
```

詳細說明請見 [`docs/architecture.md`](docs/architecture.md)

---

## 🔑 API Key 安全規範

- 所有 Key 存於後端 `.env`，**前端不持有任何 Key**
- `.env` 已加入 `.gitignore`，由後端組員統一管理
- 部署時使用環境變數注入，不寫死在程式碼中
