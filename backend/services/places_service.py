"""
services/places_service.py
景點資料服務 — 串接 Google Places API（New）
加入 Redis 快取避免重複打 API（TTL 24 小時）
"""

import os
import requests
from utils.cache import get_cache, set_cache

PLACES_API_KEY  = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_BASE_URL = "https://places.googleapis.com/v1"
CACHE_TTL       = int(os.getenv("PLACES_CACHE_TTL_SECONDS", 86400))


def search_places(query: str, location: str | None = None) -> dict:
    """
    搜尋景點
    Returns: {
        "places": [
            {
                "placeId": "ChIJ...",
                "name": "淺草寺",
                "address": "東京都...",
                "rating": 4.5,
                "userRatingCount": 12000,
                "location": { "lat": 35.7148, "lng": 139.7967 },
                "primaryType": "tourist_attraction"
            }
        ]
    }
    """
    # TODO:
    # 1. 查 Redis 快取（cache key: f"places:search:{query}:{location}"）
    # 2. 呼叫 Google Places Text Search API
    # 3. 解析回應，萃取所需欄位
    # 4. 存入 Redis 快取
    raise NotImplementedError("places_service.search_places 尚未實作")


def get_place_detail(place_id: str) -> dict | None:
    """
    取得景點詳細資料
    Returns: {
        "placeId": "ChIJ...",
        "name": "...",
        "address": "...",
        "rating": 4.5,
        "openingHours": [...],
        "website": "...",
        "phoneNumber": "...",
        "photos": [...],
        "ticketPrice": null,
        "bookingUrl": null
    }
    """
    # TODO:
    # 1. 查 Redis 快取（cache key: f"places:detail:{place_id}"）
    # 2. 呼叫 Google Places Details API
    # 3. 解析欄位，存入快取
    raise NotImplementedError("places_service.get_place_detail 尚未實作")
