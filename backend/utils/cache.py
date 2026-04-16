"""
utils/cache.py
Redis 快取工具 — 供 weather_service 和 places_service 使用
"""

import os
import json
import redis
import logging

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(url, decode_responses=True)
    return _redis_client


def get_cache(key: str):
    """
    取得快取值，若不存在或 Redis 連線失敗回傳 None
    """
    try:
        value = _get_redis().get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.warning(f"Redis get 失敗（key={key}）: {e}")
    return None


def set_cache(key: str, value: dict, ttl_seconds: int = 3600):
    """
    寫入快取，Redis 連線失敗時靜默忽略（不影響主流程）
    """
    try:
        _get_redis().setex(key, ttl_seconds, json.dumps(value, ensure_ascii=False))
    except Exception as e:
        logger.warning(f"Redis set 失敗（key={key}）: {e}")
