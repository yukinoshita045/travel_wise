"""
config/database.py
MongoDB 連線設定 — 仿照 LibreChat /api/db/connect.js 的 cached connection pool 模式
使用 PyMongo，支援連線池參數（maxPoolSize, minPoolSize 等從 .env 讀取）
"""

import os
import logging
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

logger = logging.getLogger(__name__)

# ── Cached connection（同 LibreChat 的 global.mongoose 模式）──
_cached_client = None
_cached_db = None


def get_db():
    """
    取得 MongoDB database 實例（單例，全域快取）
    Returns: pymongo.database.Database
    """
    global _cached_client, _cached_db

    if _cached_db is not None:
        return _cached_db

    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise EnvironmentError("MONGO_URI 環境變數未設定，請確認 .env 檔案")

    options = {
        "maxPoolSize":              int(os.getenv("MONGO_MAX_POOL_SIZE", 10)),
        "minPoolSize":              int(os.getenv("MONGO_MIN_POOL_SIZE", 2)),
        "serverSelectionTimeoutMS": 5000,
        "tlsCAFile":                certifi.where(),
    }

    logger.info("初始化 MongoDB 連線...")
    logger.info(f"連線選項: {options}")

    _cached_client = MongoClient(mongo_uri, **options)

    # 驗證連線
    try:
        _cached_client.admin.command("ping")
        logger.info("MongoDB 連線成功 ✅")
    except ConnectionFailure as e:
        logger.error(f"MongoDB 連線失敗: {e}")
        raise

    _cached_db = _cached_client["travelwise"]
    return _cached_db


def init_db(app):
    """
    在 Flask app context 中初始化 DB，供 app.py 呼叫
    """
    with app.app_context():
        get_db()
        logger.info("TravelWise DB 初始化完成")
