"""
models/itinerary.py
Itinerary Collection Schema（PyMongo）
儲存使用者規劃的行程，支援拖拉排序後的更新
"""

import uuid
from datetime import datetime, timezone
from config.database import get_db

COLLECTION = "itineraries"


def get_collection():
    return get_db()[COLLECTION]


def create_itinerary(user_uid: str, title: str, days: list, budget: dict) -> dict:
    """
    建立新行程
    days: [
      {
        "dayNumber": 1,
        "date": "2025-10-01",
        "spots": [
          {
            "spotId": "...",
            "placeId": "ChIJ...",
            "name": "淺草寺",
            "address": "...",
            "arrivalTime": "09:00",
            "stayDuration": 90,   # 分鐘
            "rating": 4.5,
            "ticketPrice": 0,
            "bookingUrl": null
          }
        ]
      }
    ]
    budget: { "total": 50000, "breakdown": {...} }
    """
    doc = {
        "itineraryId": str(uuid.uuid4()),
        "userId":      user_uid,
        "title":       title,
        "days":        days,
        "budget":      budget,
        "createdAt":   datetime.now(timezone.utc),
        "updatedAt":   datetime.now(timezone.utc),
    }
    get_collection().insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


def get_itinerary_by_id(itinerary_id: str, user_uid: str) -> dict | None:
    """
    取得單一行程（確認 userId 避免越權存取）
    """
    return get_collection().find_one(
        {"itineraryId": itinerary_id, "userId": user_uid},
        {"_id": 0}
    )


def update_itinerary(itinerary_id: str, user_uid: str, update_data: dict) -> bool:
    """
    更新行程（拖拉後儲存新順序）
    """
    update_data["updatedAt"] = datetime.now(timezone.utc)
    result = get_collection().update_one(
        {"itineraryId": itinerary_id, "userId": user_uid},
        {"$set": update_data}
    )
    return result.modified_count > 0


def get_itineraries_by_user(user_uid: str, limit: int = 20) -> list:
    """
    取得使用者所有歷史行程
    """
    cursor = (
        get_collection()
        .find({"userId": user_uid}, {"_id": 0})
        .sort("updatedAt", -1)
        .limit(limit)
    )
    return list(cursor)


def delete_itinerary(itinerary_id: str, user_uid: str) -> bool:
    result = get_collection().delete_one(
        {"itineraryId": itinerary_id, "userId": user_uid}
    )
    return result.deleted_count > 0
