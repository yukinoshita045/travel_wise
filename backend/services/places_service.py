"""
services/places_service.py
景點資料服務 — 串接 OpenTripMap API（免費）
Redis 快取避免重複打 API（TTL 24 小時）
"""

import os
import requests
import logging
from utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)

OTM_KEY   = os.getenv("OPENTRIPMAP_API_KEY")
OTM_BASE  = "https://api.opentripmap.com/0.1/en"
CACHE_TTL = int(os.getenv("PLACES_CACHE_TTL_SECONDS", 86400))

# 使用者偏好 → OpenTripMap kinds 對應
PREFERENCE_KINDS = {
    "文化":   "cultural",
    "自然":   "natural",
    "美食":   "foods",
    "拍照":   "interesting_places",
    "購物":   "shops",
    "宗教":   "religion",
    "娛樂":   "amusements",
    "歷史":   "historic",
}


def geocode_city(city: str) -> tuple[float, float]:
    """
    城市名稱 → (lat, lon)
    使用 OpenTripMap geoname API
    """
    cache_key = f"geo:{city}"
    cached = get_cache(cache_key)
    if cached:
        return cached["lat"], cached["lon"]

    resp = requests.get(
        f"{OTM_BASE}/place/geoname",
        params={"name": city, "apikey": OTM_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if "lat" not in data:
        raise ValueError(f"找不到城市：{city}")

    result = {"lat": data["lat"], "lon": data["lon"]}
    set_cache(cache_key, result, ttl_seconds=CACHE_TTL)
    return result["lat"], result["lon"]


def search_spots(
    city: str,
    preferences: list[str],
    radius_m: int = 5000,
    limit: int = 20,
) -> list[dict]:
    """
    搜尋城市內的景點
    preferences: ["文化", "美食", ...] → 轉成 OpenTripMap kinds
    Returns: [
        {
            "xid": "W123456",
            "name": "淺草寺",
            "lat": 35.71,
            "lon": 139.79,
            "kinds": "historic,religion",
            "rate": 7,
            "dist": 1200.0
        }, ...
    ]
    """
    kinds = ",".join(
        [PREFERENCE_KINDS.get(p, "interesting_places") for p in preferences]
    ) or "interesting_places"

    cache_key = f"spots:{city}:{kinds}:{radius_m}"
    cached = get_cache(cache_key)
    if cached:
        logger.info(f"[Cache HIT] {cache_key}")
        return cached

    lat, lon = geocode_city(city)

    resp = requests.get(
        f"{OTM_BASE}/places/radius",
        params={
            "radius": radius_m,
            "lon":    lon,
            "lat":    lat,
            "kinds":  kinds,
            "rate":   "3",      # 只拿評分 ≥ 3（1~7）
            "format": "json",
            "limit":  limit,
            "apikey": OTM_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    spots = resp.json()

    result = [
        {
            "xid":   s.get("xid"),
            "name":  s.get("name", "未知景點"),
            "lat":   s.get("point", {}).get("lat"),
            "lon":   s.get("point", {}).get("lon"),
            "kinds": s.get("kinds", ""),
            "rate":  s.get("rate", 0),
            "dist":  s.get("dist", 0),
        }
        for s in spots
        if s.get("name")
    ]

    set_cache(cache_key, result, ttl_seconds=CACHE_TTL)
    logger.info(f"[OpenTripMap] {city} 找到 {len(result)} 個景點")
    return result


def get_spot_detail(xid: str) -> dict | None:
    """
    取得單一景點詳細資訊（名稱、描述、地址、圖片、Wikipedia 連結）
    """
    cache_key = f"spot_detail:{xid}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    resp = requests.get(
        f"{OTM_BASE}/places/xid/{xid}",
        params={"apikey": OTM_KEY},
        timeout=10,
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    d = resp.json()

    result = {
        "xid":           d.get("xid"),
        "name":          d.get("name", ""),
        "description":   d.get("wikipedia_extracts", {}).get("text", ""),
        "lat":           d.get("point", {}).get("lat"),
        "lon":           d.get("point", {}).get("lon"),
        "address":       d.get("address", {}),
        "url":           d.get("url", ""),
        "wikipedia":     d.get("wikipedia", ""),
        "image":         d.get("preview", {}).get("source", ""),
        "opening_hours": d.get("opening_hours", ""),
        "kinds":         d.get("kinds", ""),
    }

    set_cache(cache_key, result, ttl_seconds=CACHE_TTL)
    return result
