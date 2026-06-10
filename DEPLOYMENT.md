# TravelWise — 短期部署指南（Vercel + Render）

> 架構：**前端 Vue SPA → Vercel**、**後端 Flask API → Render**、MongoDB Atlas / Firebase 沿用既有雲端服務。

---

## 0. 先備清單

部署前先把這些值準備好（之後要貼到 Render / Vercel）：

| 項目 | 從哪來 |
|------|--------|
| `MONGO_URI` | MongoDB Atlas 連線字串 |
| Firebase service account JSON | `backend/firebase_service_account.json` 整份內容 |
| `OPENAI_API_KEY` | OpenAI |
| `RAPIDAPI_KEY` | RapidAPI（航班 API） |
| Firebase Web 設定 | `frontend/.env.example` 內已有（公開值，可直接用） |

> ⚠️ MongoDB Atlas → Network Access 要把 `0.0.0.0/0` 加進白名單（Render 免費方案 IP 不固定），否則後端連不到 DB。

---

## 1. 後端部署到 Render

repo 根目錄已有 [render.yaml](render.yaml)，採 Blueprint 一鍵部署。

1. 把這個分支 push 到 GitHub。
2. Render Dashboard → **New → Blueprint** → 選這個 repo → Apply。
   它會建立兩個服務：`travelwise-backend`（web）與 `travelwise-redis`（keyvalue）。
3. 進 `travelwise-backend` 的 **Environment**，填入標記為「需手動」的變數：

   | 變數 | 值 |
   |------|----|
   | `MONGO_URI` | 你的 Atlas 連線字串 |
   | `FIREBASE_SERVICE_ACCOUNT_JSON` | 貼入 `firebase_service_account.json` **整份內容**（單行，貼上去即可，不用自己壓成一行） |
   | `FIREBASE_PROJECT_ID` | `wisetrip-31013` |
   | `OPENAI_API_KEY` | 你的 key |
   | `RAPIDAPI_KEY` | 你的 key |
   | `CORS_ORIGINS` | 先留空，等 Vercel 網域出來後回填（見步驟 3） |

   `REDIS_URL` 由 Render 自動注入，不用填。
4. 部署完成後，後端網址類似 `https://travelwise-backend.onrender.com`。
   開 `https://travelwise-backend.onrender.com/healthz` 應回 `{"status":"ok"}`。

> 免費方案閒置 15 分鐘會休眠，下一個請求會冷啟動（約 30–60 秒），屬正常現象。

---

## 2. 前端部署到 Vercel

前端已有 [frontend/vercel.json](frontend/vercel.json)（含 Vue Router history 模式所需的 SPA rewrite）。

1. Vercel → **Add New → Project** → 選同一個 repo。
2. **Root Directory** 設為 `frontend`（重要，否則抓不到 package.json）。
   Framework 會自動偵測為 Vite。
3. **Environment Variables** 填入（照抄 `frontend/.env.example`，只改 `VITE_API_URL`）：

   | 變數 | 值 |
   |------|----|
   | `VITE_API_URL` | 步驟 1 拿到的 Render 後端網址（**結尾不要加 `/api`**） |
   | `VITE_FIREBASE_API_KEY` | 見 `.env.example` |
   | `VITE_FIREBASE_AUTH_DOMAIN` | 見 `.env.example` |
   | `VITE_FIREBASE_PROJECT_ID` | 見 `.env.example` |
   | `VITE_FIREBASE_STORAGE_BUCKET` | 見 `.env.example` |
   | `VITE_FIREBASE_MESSAGING_SENDER_ID` | 見 `.env.example` |
   | `VITE_FIREBASE_APP_ID` | 見 `.env.example` |
   | `VITE_FIREBASE_MEASUREMENT_ID` | 見 `.env.example` |

4. Deploy。完成後得到前端網址，如 `https://travel-wise.vercel.app`。

---

## 3. 把兩邊接起來（CORS + Firebase 授權網域）

1. **回填 CORS**：到 Render `travelwise-backend` 的 `CORS_ORIGINS` 填入 Vercel 網址
   （例：`https://travel-wise.vercel.app`，多個用逗號分隔），存檔會自動重新部署。
2. **Firebase 授權網域**：Firebase Console → Authentication → Settings →
   Authorized domains，加入你的 Vercel 網域，否則前端登入會被擋。

---

## 4. 驗收

1. 開 Vercel 前端網址 → 應出現 Firebase 登入畫面。
2. 用共用開發帳號登入：`dev@travelwise.com` / `TravelWiseDev2026!`
   （或自行註冊新帳號）。
3. 登入後應能看到旅程列表、進入行程、AI 聊天等功能正常打到 Render 後端。

---

## 疑難排解

| 症狀 | 原因 / 解法 |
|------|------------|
| 前端 API 全部 CORS error | `CORS_ORIGINS` 沒填或拼錯 Vercel 網域；網址結尾不要帶 `/` |
| 重新整理某頁面變 404 | `vercel.json` 的 rewrite 沒生效 → 確認 Root Directory 設成 `frontend` |
| 後端 500、log 顯示 MongoDB 連不到 | Atlas 沒開 `0.0.0.0/0` 白名單，或 `MONGO_URI` 錯 |
| 登入後 API 回 401 | 1) `FLASK_TESTING` 應為 `false`；2) `FIREBASE_SERVICE_ACCOUNT_JSON` 內容貼錯；3) ID Token 約 1 小時過期，重新登入 |
| 前端登入彈窗報 `auth/unauthorized-domain` | Firebase Authorized domains 沒加 Vercel 網域 |
| Render build 失敗在 pip | 確認 `backend/requirements.txt` 為 UTF-8（本次已修正，原為 UTF-16 會失敗） |
| 後端第一個請求很慢 | 免費方案冷啟動，正常 |

---

## 純展示模式（不想設 Firebase）

只想 demo、不接真實登入：把 Render 的 `FLASK_TESTING` 設為 `true`，
後端會跳過 token 驗證、所有人共用 `test-user-001`。前端登入畫面仍在，
但 API 不再驗證 token（適合臨時展示，正式上線請設回 `false`）。
