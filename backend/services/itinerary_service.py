"""
services/itinerary_service.py
行程推薦邏輯 — 呼叫 chat_service 取得 AI 行程，排序景點後存入 MongoDB
"""

import math
import logging
from models.itinerary import create_itinerary
from services.chat_service import handle_chat_message

logger = logging.getLogger(__name__)


def recommend_itinerary(user_uid: str, params: dict) -> dict:
    """
    根據使用者偏好，透過 AI 生成行程並存入 MongoDB
    params 範例：
    {
        "destination": "Tokyo",
        "days": 5,
        "travelers": 2,
        "budget": 50000,
        "transportMode": "大眾運輸",
        "maxCommuteMinutes": 30,
        "preferences": ["文化", "美食"],
        "mustVisit": ["淺草寺"],
        "fatigueContext": { "finalScore": 45, "level": "中等", "recoverHours": 6 },
        "conversationId": null
    }
    Returns: { "itineraryId": "...", "title": "...", "days": [...], "budget": {...} }
    """
    destination = params.get("destination", "Tokyo")
    days        = params.get("days", 3)
    travelers   = params.get("travelers", 1)
    budget      = params.get("budget", 0)

    # 組成自然語言 prompt
    prompt = _build_prompt(params)
    logger.info(f"[Itinerary] 開始規劃：{destination} {days}天")

    # 呼叫 AI（含 Function Calling 自動查景點）
    chat_result = handle_chat_message(
        user_uid=user_uid,
        message=prompt,
        conversation_id=params.get("conversationId"),
        trip_params=params,
    )

    reply = chat_result.get("reply", {})

    # 如果 AI 回傳的是行程 JSON，存入 MongoDB
    if reply.get("type") == "itinerary":
        itinerary_data = reply["content"]
        days_data = itinerary_data.get("days", [])

        # 對每天的景點做地理排序
        for day in days_data:
            day["spots"] = _sort_spots_by_location(day.get("spots", []))

        saved = create_itinerary(
            user_uid=user_uid,
            title=itinerary_data.get("title", f"{destination} {days}天行程"),
            days=days_data,
            budget={"total": budget, "currency": "TWD", "breakdown": {}},
        )
        return saved
    else:
        # AI 沒直接給行程 JSON（例如還在問問題），直接回傳對話結果
        return {
            "conversationId": chat_result.get("conversationId"),
            "reply": reply,
        }


def _build_prompt(params: dict) -> str:
    """把 params 轉成自然語言 prompt"""
    destination = params.get("destination", "")
    days        = params.get("days", 3)
    travelers   = params.get("travelers", 1)
    budget      = params.get("budget")
    transport   = params.get("transportMode", "大眾運輸")
    preferences = params.get("preferences", [])
    must_visit  = params.get("mustVisit", [])
    max_commute = params.get("maxCommuteMinutes")

    parts = [f"請幫我規劃 {days} 天的{destination}旅遊行程，共 {travelers} 人"]
    if budget:
        parts.append(f"總預算 {budget} 元")
    if transport:
        parts.append(f"交通方式：{transport}")
    if max_commute:
        parts.append(f"每次移動不超過 {max_commute} 分鐘")
    if preferences:
        parts.append(f"偏好：{', '.join(preferences)}")
    if must_visit:
        parts.append(f"必去景點：{', '.join(must_visit)}")
    parts.append("請先查詢真實景點資料再安排行程，並以 JSON 格式輸出。")

    return "，".join(parts) + "。"


def _sort_spots_by_location(spots: list[dict]) -> list[dict]:
    """
    Nearest Neighbor 演算法：依地理位置排序景點，減少不必要的交通時間
    從第一個景點出發，每次選最近的下一個
    """
    if len(spots) <= 2:
        return spots

    # 過濾掉沒有座標的景點
    with_coords    = [s for s in spots if s.get("lat") and s.get("lon")]
    without_coords = [s for s in spots if not (s.get("lat") and s.get("lon"))]

    if len(with_coords) <= 1:
        return spots

    sorted_spots = [with_coords[0]]
    remaining    = with_coords[1:]

    while remaining:
        last = sorted_spots[-1]
        nearest = min(remaining, key=lambda s: _haversine(
            last["lat"], last["lon"], s["lat"], s["lon"]
        ))
        sorted_spots.append(nearest)
        remaining.remove(nearest)

    return sorted_spots + without_coords


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """計算兩點之間的球面距離（公里）"""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))
