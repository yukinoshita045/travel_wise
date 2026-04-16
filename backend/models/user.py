"""
models/user.py
User Collection Schema（PyMongo）
對應 LibreChat User model 的設計概念
"""

from datetime import datetime, timezone
from config.database import get_db


COLLECTION = "users"


def get_collection():
    return get_db()[COLLECTION]


def create_user(uid: str, email: str, display_name: str = "") -> dict:
    """
    建立新使用者（Firebase Auth 登入後呼叫）
    若已存在則不重複建立
    """
    col = get_collection()
    existing = col.find_one({"uid": uid})
    if existing:
        return existing

    user_doc = {
        "uid":         uid,
        "email":       email,
        "displayName": display_name,
        "createdAt":   datetime.now(timezone.utc),
        "updatedAt":   datetime.now(timezone.utc),
    }
    col.insert_one(user_doc)
    return user_doc


def get_user_by_uid(uid: str) -> dict | None:
    return get_collection().find_one({"uid": uid}, {"_id": 0})
