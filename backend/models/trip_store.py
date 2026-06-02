"""
models/trip_store.py
Trips Collection Schema（PyMongo）
儲存使用者的完整旅程資料（對應前端 travelStore 的資料結構）
每個 itinerary item 包含 address 欄位
"""

import uuid
from datetime import datetime, timezone
from config.database import get_db

COLLECTION = "trips"


def get_collection():
    return get_db()[COLLECTION]


def _serialize_trip(doc: dict) -> dict:
    """移除 MongoDB 的 _id，轉成可 JSON 序列化的 dict"""
    if doc is None:
        return None
    return {k: v for k, v in doc.items() if k != "_id"}


def create_trip(user_uid: str, trip_data: dict) -> dict:
    """
    建立新旅程
    trip_data 結構（對應前端 travelData.json）：
    {
        "id":          "trip-xxx",
        "title":       "日本東京",
        "destination": "Tokyo, Japan",
        "startDate":   "2026-06-14",
        "endDate":     "2026-06-19",
        "dates":       "2026/06/14-2026/06/19, 共6天",
        "date":        "2026/06",
        "users":       "@xxx, yyy",
        "transfers":   0,
        "layovers":    [],
        "flights":     [...],
        "itinerary": {
            "Day 1": {
                "date": "2026-06-14",
                "weather": "☀",
                "items": [
                    {
                        "id":          "item-uuid",
                        "time":        "09:00",
                        "title":       "淺草寺",
                        "location":    "Asakusa",
                        "address":     "2 Chome-3-1 Asakusa, Taito City, Tokyo, Japan",  # ← 地址欄位
                        "category":    "attraction",
                        "tags":        ["temple"],
                        "stayTime":    2,
                        "cost":        0,
                        "description": "...",
                        "notes":       "...",
                        "image":       "https://..."
                    }
                ]
            }
        },
        "packingItems": { "Day 1": { "date": "...", "items": [...] } },
        "shoppingItems": [{"name": "...", "checked": false}],
        ...
    }
    """
    now = datetime.now(timezone.utc)

    # 確保 address 欄位存在於每個 itinerary item
    itinerary = trip_data.get("itinerary", {})
    for day_key, day_val in itinerary.items():
        for item in day_val.get("items", []):
            item.setdefault("address", "")

    doc = {
        "tripId":       trip_data.get("id", str(uuid.uuid4())),
        "userId":       user_uid,
        "title":        trip_data.get("title", ""),
        "destination":  trip_data.get("destination", ""),
        "date":         trip_data.get("date", ""),
        "startDate":    trip_data.get("startDate", ""),
        "endDate":      trip_data.get("endDate", ""),
        "dates":        trip_data.get("dates", ""),
        "users":        trip_data.get("users", ""),
        "transfers":    int(trip_data.get("transfers", 0)),
        "layovers":     trip_data.get("layovers", []),
        "fatigue":      trip_data.get("fatigue", "-"),
        "weather":      trip_data.get("weather", "-"),
        "budget":       trip_data.get("budget", "TWD"),
        "currencyRate": trip_data.get("currencyRate", "-"),
        "currencyUpdatedAt": trip_data.get("currencyUpdatedAt", ""),
        "isUpcoming":   trip_data.get("isUpcoming", False),
        "coverImage":   trip_data.get("coverImage", ""),
        "note":         trip_data.get("note", ""),
        "type":         trip_data.get("type", "行程規劃"),
        "flights":      trip_data.get("flights", []),
        "itinerary":    itinerary,
        "packingItems": trip_data.get("packingItems", {}),
        "shoppingItems": trip_data.get("shoppingItems", []),
        "createdAt":    now,
        "updatedAt":    now,
    }

    get_collection().insert_one(doc)
    return _serialize_trip(doc)


def get_trip_by_id(trip_id: str, user_uid: str) -> dict | None:
    """取得單一旅程（確認 userId 避免越權）"""
    doc = get_collection().find_one(
        {"tripId": trip_id, "userId": user_uid},
        {"_id": 0}
    )
    return doc


def get_trips_by_user(user_uid: str) -> list:
    """取得使用者所有旅程，依 startDate 降序排列"""
    cursor = (
        get_collection()
        .find({"userId": user_uid}, {"_id": 0})
        .sort("startDate", -1)
    )
    return list(cursor)


def update_trip(trip_id: str, user_uid: str, update_data: dict) -> dict | None:
    """
    更新旅程
    update_data 可以是完整旅程或部分欄位
    確保 itinerary items 的 address 欄位存在
    """
    # 確保 address 欄位存在於每個 itinerary item
    if "itinerary" in update_data:
        for day_key, day_val in update_data["itinerary"].items():
            for item in day_val.get("items", []):
                item.setdefault("address", "")

    update_data["updatedAt"] = datetime.now(timezone.utc)

    # 移除不應由客戶端覆蓋的欄位
    update_data.pop("_id", None)
    update_data.pop("userId", None)

    result = get_collection().find_one_and_update(
        {"tripId": trip_id, "userId": user_uid},
        {"$set": update_data},
        return_document=True,
        projection={"_id": 0}
    )
    return result


def delete_trip(trip_id: str, user_uid: str) -> bool:
    result = get_collection().delete_one(
        {"tripId": trip_id, "userId": user_uid}
    )
    return result.deleted_count > 0


def upsert_trip(user_uid: str, trip_data: dict) -> dict:
    """
    若 tripId 存在則更新，否則建立
    前端同步資料時使用
    """
    trip_id = trip_data.get("id")
    if trip_id:
        existing = get_trip_by_id(trip_id, user_uid)
        if existing:
            return update_trip(trip_id, user_uid, trip_data) or existing
    return create_trip(user_uid, trip_data)
