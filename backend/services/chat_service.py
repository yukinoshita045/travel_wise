"""
services/chat_service.py
AI 對話服務 — 串接 OpenAI GPT-4o
維護多輪對話 history（從 MongoDB 讀取），設計 System Prompt 引導行程推薦
"""

import os
from openai import OpenAI
from models.conversation import (
    create_conversation,
    get_messages_by_conversation,
    save_message,
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL  = os.getenv("OPENAI_MODEL", "gpt-4o")

SYSTEM_PROMPT = """
你是 TravelWise，一個專業的全齡化旅遊規劃助理。
你的職責：
1. 根據使用者輸入的偏好（預算、天數、人數、喜好、必去景點）推薦最佳行程
2. 當使用者明確要求生成行程時，你「必須」回傳結構化 JSON，格式如下：
   {
     "type": "itinerary",
     "title": "行程名稱",
     "days": [
       {
         "dayNumber": 1,
         "date": "YYYY-MM-DD 或 null",
         "spots": [
           {
             "name": "景點名稱",
             "address": "地址",
             "arrivalTime": "09:00",
             "stayDuration": 90,
             "ticketPrice": 0,
             "bookingUrl": null,
             "notes": "備註"
           }
         ]
       }
     ]
   }
3. 若使用者只是問問題，回傳純文字即可，type 設為 "text"
4. 語言：優先繁體中文
5. 對於高齡旅客，主動提醒體力負擔與休息安排
"""


def handle_chat_message(user_uid: str, message: str, conversation_id: str | None = None) -> dict:
    """
    處理使用者訊息，回傳 AI 回覆
    - 若 conversation_id 為 None，自動建立新對話
    - 維護完整對話 history 供多輪對話使用
    Returns: {
        "conversationId": "...",
        "reply": { "type": "text" | "itinerary", "content": "..." | {...} }
    }
    """
    # TODO: 實作 OpenAI 多輪對話邏輯
    # 1. 若無 conversation_id，呼叫 create_conversation()
    # 2. 從 MongoDB 讀取歷史訊息（get_messages_by_conversation）
    # 3. 組成 messages list（system + history + 新訊息）
    # 4. 呼叫 client.chat.completions.create()
    # 5. 儲存使用者訊息與 AI 回覆（save_message x2）
    # 6. 判斷回覆是否為 JSON 行程，解析後回傳
    raise NotImplementedError("chat_service 尚未實作")
