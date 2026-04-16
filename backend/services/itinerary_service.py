"""
services/itinerary_service.py
行程推薦邏輯 — 解析 AI 回傳 JSON、排序景點、存入 MongoDB
"""

from models.itinerary import create_itinerary
from services.chat_service import handle_chat_message


def recommend_itinerary(user_uid: str, params: dict) -> dict:
    """
    根據使用者偏好，透過 AI 生成行程並存入 MongoDB
    params 範例：
    {
        "totalBudget": 50000,
        "days": 5,
        "travelers": 2,
        "destination": "東京",
        "preferences": ["美食", "文化", "拍照"],
        "mustVisit": ["淺草寺", "新宿御苑"],
        "conversationId": null
    }
    Returns: { "itineraryId": "...", "title": "...", "days": [...], "budget": {...} }
    """
    # TODO:
    # 1. 把 params 轉成自然語言 prompt（例如：「幫我規劃 5 天東京行程，預算 5 萬...」）
    # 2. 呼叫 handle_chat_message()，取得 AI 行程 JSON
    # 3. 驗證並解析行程 JSON 格式
    # 4. 呼叫 _sort_spots_by_location() 優化景點順序
    # 5. 呼叫 budget_service.calculate_budget() 生成預算表
    # 6. 呼叫 create_itinerary() 存入 MongoDB
    # 7. 回傳完整行程資料
    raise NotImplementedError("itinerary_service 尚未實作")


def _sort_spots_by_location(spots: list) -> list:
    """
    依地理位置排序景點，減少不必要的交通時間
    TODO: 用景點經緯度計算 nearest-neighbor 排序
    """
    raise NotImplementedError
