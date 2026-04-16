"""
services/weather_service.py
天氣服務 — 串接 Open-Meteo（免費，不需 API Key）
流程：城市名 → geocoding → 取得預報 → 計算體感溫度 → 生成衣物建議
"""

import os
import requests
from utils.cache import get_cache, set_cache

OPEN_METEO_BASE = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
GEO_BASE        = "https://geocoding-api.open-meteo.com/v1"


def get_weather_and_clothing(destination: str, date: str | None = None) -> dict:
    """
    查詢目的地天氣與衣物建議
    Returns: {
        "destination": "Tokyo",
        "forecast": [ { "date": "...", "tempMax": 28, "tempMin": 18, "humidity": 70, "feelsLike": 30, "condition": "sunny" } ],
        "clothingSuggestion": "建議穿著短袖上衣搭配輕薄外套，原因：體感溫度 30°C...",
        "alerts": []
    }
    """
    # TODO:
    # 1. 先查 Redis 快取（cache key: f"weather:{destination}:{date}"）
    # 2. 呼叫 Open-Meteo geocoding API 取得經緯度
    # 3. 呼叫 Open-Meteo forecast API 取得 7 天預報
    # 4. 計算體感溫度（Heat Index 或 Wind Chill 依氣溫選擇）
    # 5. 用規則或 GPT 生成衣物建議文字
    # 6. 存入 Redis 快取
    raise NotImplementedError("weather_service 尚未實作")


def _feels_like(temp_c: float, humidity: float, wind_kmh: float) -> float:
    """
    體感溫度計算（Heat Index 公式，> 27°C 時適用）
    TODO: 實作公式
    """
    raise NotImplementedError
