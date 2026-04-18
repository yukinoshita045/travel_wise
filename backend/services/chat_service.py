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
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL  = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── System Prompt ─────────────────────────────────────────
SYSTEM_PROMPT = """你是 TravelWise 的 AI 旅遊顧問，專門幫助使用者規劃最適合的旅遊行程。

## 你的任務
1. 根據使用者的需求（目的地、天數、人數、預算、偏好），規劃合理的每日行程
2. 主動使用工具查詢真實景點資料，不要自己編造景點
3. 考慮使用者的疲勞值、移動距離、停留時間，讓行程節奏合理
4. 回覆使用繁體中文

## 行程輸出格式
當使用者要求規劃行程時，回傳以下 JSON 格式（包在 ```json ``` 中）：
{
  "type": "itinerary",
  "title": "5天東京深度文化之旅",
  "days": [
    {
      "dayNumber": 1,
      "theme": "淺草・上野文化散策",
      "spots": [
        {
          "xid": "景點ID",
          "name": "景點名稱",
          "description": "簡短描述",
          "lat": 35.71,
          "lon": 139.79,
          "arrivalTime": "09:00",
          "stayDuration": 90,
          "ticketPrice": 0,
          "notes": "建議事項"
        }
      ]
    }
  ]
}

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
    """判斷 GPT 回覆是純文字還是行程 JSON"""
    import re
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if data.get("type") == "itinerary":
                return "itinerary", data
        except json.JSONDecodeError:
            pass
    return "text", text


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

    # ── GPT Function Calling 迴圈（最多 5 輪）──
    for _ in range(5):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.7,
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
        messages.append(gpt_msg)
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

