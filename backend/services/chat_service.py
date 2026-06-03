"""
services/chat_service.py
AI 對話服務 — OpenAI Function Calling
GPT 自己決定何時呼叫 search_spots / get_spot_detail
多輪對話 history 從 MongoDB 讀取（長期記憶）
"""

import os
import json
import logging
from openai import OpenAI
from models.conversation import (
    create_conversation,
    get_messages_by_conversation,
    save_message,
)
from services.places_service import search_spots, get_spot_detail

logger = logging.getLogger(__name__)
MODEL  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# 延遲初始化 OpenAI client：避免 import 時就要求 OPENAI_API_KEY，
# 讓未設 key 的環境（如測試、不需 AI 的端點）仍能正常 import / 啟動。
_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

# ── System Prompt ─────────────────────────────────────────
SYSTEM_PROMPT = """你是 TravelWise 的 AI 旅遊顧問，專門幫助使用者規劃最適合的旅遊行程。

## 你的任務
1. 根據使用者的需求（目的地、天數、人數、預算、偏好），規劃合理的每日行程
2. 主動使用工具查詢真實景點資料，不要自己編造景點
3. 考慮使用者的疲勞值、移動距離、停留時間，讓行程節奏合理
4. 回覆使用繁體中文

## 行程輸出格式
當使用者要求規劃行程時，**必須且只能**回傳以下 JSON 格式，包在 ```json ``` 標記中，不要加任何額外說明文字：

```json
{
  "type": "itinerary",
  "title": "5天東京深度文化之旅",
  "days": [
    {
      "dayNumber": 1,
      "theme": "淺草・上野文化散策",
      "spots": [
        {
          "xid": "景點的OpenTripMap ID（必填）",
          "name": "景點名稱（必填）",
          "description": "景點的繁體中文描述，2~3句（必填）",
          "lat": 35.71,
          "lon": 139.79,
          "arrivalTime": "09:00",
          "stayDuration": 90,
          "ticketPrice": 0,
          "notes": "給旅客的繁體中文建議（必填）"
        }
      ]
    }
  ]
}
```

## 欄位規則（務必遵守）
- `xid`：從 search_spots 結果取得，不可自行編造
- `name`：使用原始英文名稱
- `description`：**必須是繁體中文**，2~3 句描述景點特色
- `arrivalTime`：格式 HH:MM（24小時制）
- `stayDuration`：整數，單位為分鐘
- `ticketPrice`：整數，單位為當地貨幣，免費填 0
- `notes`：**必須是繁體中文**，提供實用建議（開放時間、注意事項等）
- `lat` / `lon`：從 search_spots 結果取得，不可為 null

## 工具使用原則
- 先用 search_spots 取得景點清單（一次即可）
- 只對「最終排入行程」的景點呼叫 get_spot_detail（每天最多 2 個）
- 不需要查詢所有景點的 detail，search_spots 結果已足夠規劃行程

## 每日景點數量原則
- 步行：3~4 個景點
- 大眾運輸：4~5 個景點
- 開車：5~6 個景點
- 高齡旅客或疲勞值高：減少 1~2 個並加入休息時間
"""

# ── Function Calling 工具定義 ─────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_spots",
            "description": "搜尋目的地城市的景點，根據偏好類型和移動範圍過濾",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "目的地城市名稱（英文），例如：Tokyo, Paris, Taipei"
                    },
                    "preferences": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "偏好類型，可選：文化、自然、美食、拍照、購物、宗教、娛樂、歷史"
                    },
                    "radius_m": {
                        "type": "integer",
                        "description": "搜尋半徑（公尺）：步行 2000，大眾運輸 5000，開車 15000",
                        "default": 5000
                    },
                    "limit": {
                        "type": "integer",
                        "description": "最多回傳景點數量",
                        "default": 20
                    }
                },
                "required": ["city", "preferences"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_spot_detail",
            "description": "取得單一景點的詳細資訊，包含描述、地址、圖片、Wikipedia 連結",
            "parameters": {
                "type": "object",
                "properties": {
                    "xid": {
                        "type": "string",
                        "description": "景點的 OpenTripMap xid，從 search_spots 結果取得"
                    }
                },
                "required": ["xid"]
            }
        }
    }
]


def _call_tool(name: str, args: dict) -> str:
    """執行 GPT 要求的 function，回傳結果 JSON 字串"""
    try:
        if name == "search_spots":
            result = search_spots(**args)
        elif name == "get_spot_detail":
            result = get_spot_detail(**args)
        else:
            result = {"error": f"未知工具：{name}"}
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Tool {name} 執行失敗: {e}")
        return json.dumps({"error": str(e)})


def _build_context_message(trip_params: dict) -> str:
    """把旅遊條件組成 context 字串，注入 system message"""
    parts = []
    mapping = [
        ("destination",        "目的地"),
        ("days",               "天數"),
        ("travelers",          "出遊人數"),
        ("budget",             "總預算（元）"),
        ("transportMode",      "交通方式"),
        ("maxCommuteMinutes",  "可接受最長通勤時間（分鐘）"),
    ]
    for key, label in mapping:
        if trip_params.get(key):
            parts.append(f"{label}：{trip_params[key]}")
    if trip_params.get("preferences"):
        parts.append(f"偏好：{', '.join(trip_params['preferences'])}")
    if trip_params.get("mustVisit"):
        parts.append(f"必去景點：{', '.join(trip_params['mustVisit'])}")
    if trip_params.get("fatigueContext"):
        fc = trip_params["fatigueContext"]
        parts.append(
            f"疲勞值：{fc.get('finalScore')}（{fc.get('level')}），"
            f"建議恢復 {fc.get('recoverHours', 0)} 小時"
        )
    return "\n".join(parts)


def _parse_reply(text: str) -> tuple[str, object]:
    """
    判斷 GPT 回覆是純文字還是行程 JSON。
    用括號計數法正確處理巢狀 JSON，避免 regex 截斷。
    """
    import re

    # 找到 ```json 區塊的起始位置
    match = re.search(r"```json\s*", text, re.DOTALL)
    if not match:
        return "text", text

    start = match.end()
    # 從第一個 { 開始計數括號，找到完整 JSON
    brace_count = 0
    json_start = None
    json_end = None
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            if json_start is None:
                json_start = i
            brace_count += 1
        elif ch == "}":
            brace_count -= 1
            if brace_count == 0 and json_start is not None:
                json_end = i + 1
                break

    if json_start is None or json_end is None:
        return "text", text

    try:
        data = json.loads(text[json_start:json_end])
    except json.JSONDecodeError as e:
        logger.warning(f"[Parse] JSON 解析失敗: {e}")
        return "text", text

    if data.get("type") != "itinerary":
        return "text", text

    # ── Schema 驗證與自動補全 ──────────────────────────────
    data = _validate_and_fill_itinerary(data)
    return "itinerary", data


def _validate_and_fill_itinerary(data: dict) -> dict:
    """
    驗證並補全行程 JSON，確保每個欄位都符合前端卡片 Schema。
    缺少的欄位填入安全預設值，不會因 GPT 遺漏欄位而 crash。
    """
    data.setdefault("title", "AI 推薦行程")
    data.setdefault("days", [])

    for day in data["days"]:
        day.setdefault("dayNumber", 0)
        day.setdefault("theme", "")
        day.setdefault("spots", [])

        for spot in day["spots"]:
            # 必填欄位補全
            spot.setdefault("xid", "")
            spot.setdefault("name", "未命名景點")
            spot.setdefault("description", "")
            spot.setdefault("lat", None)
            spot.setdefault("lon", None)
            spot.setdefault("arrivalTime", "09:00")
            spot.setdefault("stayDuration", 60)
            spot.setdefault("ticketPrice", 0)
            spot.setdefault("notes", "")

            # 型別強制轉換（GPT 有時輸出字串）
            try:
                spot["stayDuration"] = int(spot["stayDuration"])
            except (ValueError, TypeError):
                spot["stayDuration"] = 60

            try:
                spot["ticketPrice"] = int(spot["ticketPrice"])
            except (ValueError, TypeError):
                spot["ticketPrice"] = 0

            try:
                if spot["lat"] is not None:
                    spot["lat"] = float(spot["lat"])
                if spot["lon"] is not None:
                    spot["lon"] = float(spot["lon"])
            except (ValueError, TypeError):
                spot["lat"] = None
                spot["lon"] = None

    return data


def handle_chat_message(
    user_uid: str,
    message: str,
    conversation_id: str | None = None,
    trip_params: dict | None = None,
) -> dict:
    """
    主要對話處理函式
    Returns: { "conversationId": "...", "reply": { "type": "text"|"itinerary", "content": ... } }
    """
    # 建立或延續對話
    if not conversation_id:
        conv = create_conversation(user_uid)
        conversation_id = conv["conversationId"]

    # 讀取歷史訊息（長期記憶）
    history = get_messages_by_conversation(conversation_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 注入旅遊條件 context
    if trip_params:
        ctx = _build_context_message(trip_params)
        if ctx:
            messages.append({"role": "system", "content": f"## 使用者旅遊條件\n{ctx}"})

    # 加入歷史對話
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # 加入本次使用者訊息
    messages.append({"role": "user", "content": message})
    save_message(conversation_id, user_uid, "user", message)

    # ── GPT Function Calling 迴圈（最多 10 輪）──
    for _ in range(10):
        response = _get_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        gpt_msg = response.choices[0].message

        # 沒有 tool call → 最終回覆
        if not gpt_msg.tool_calls:
            reply_text = gpt_msg.content or ""
            save_message(conversation_id, user_uid, "assistant", reply_text)
            reply_type, reply_content = _parse_reply(reply_text)
            return {
                "conversationId": conversation_id,
                "reply": {"type": reply_type, "content": reply_content},
            }

        # 執行 tool call，把結果加回 messages
        messages.append(gpt_msg.model_dump())  # ChatCompletionMessage → dict
        for tc in gpt_msg.tool_calls:
            args = json.loads(tc.function.arguments)
            logger.info(f"[Tool Call] {tc.function.name}({args})")
            tool_result = _call_tool(tc.function.name, args)
            messages.append({
                "role":         "tool",
                "tool_call_id": tc.id,
                "content":      tool_result,
            })

    return {
        "conversationId": conversation_id,
        "reply": {"type": "text", "content": "抱歉，行程規劃花費時間過長，請稍後再試。"},
    }

