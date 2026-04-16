"""
models/conversation.py
Conversation & Message Collection Schema（PyMongo）
仿照 LibreChat /api/models/Conversation.js + Message.js 的結構設計
"""

import uuid
from datetime import datetime, timezone
from config.database import get_db

CONV_COLLECTION = "conversations"
MSG_COLLECTION  = "messages"


def get_conv_col():
    return get_db()[CONV_COLLECTION]

def get_msg_col():
    return get_db()[MSG_COLLECTION]


# ── Conversation ──────────────────────────────────────────

def create_conversation(user_uid: str, title: str = "新對話") -> dict:
    """
    建立新的對話 session（每次使用者開啟新的 AI 對話）
    """
    doc = {
        "conversationId": str(uuid.uuid4()),
        "userId":         user_uid,
        "title":          title,
        "createdAt":      datetime.now(timezone.utc),
        "updatedAt":      datetime.now(timezone.utc),
    }
    get_conv_col().insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


def get_conversations_by_user(user_uid: str, limit: int = 20) -> list:
    """
    取得使用者最近的對話列表
    """
    cursor = (
        get_conv_col()
        .find({"userId": user_uid}, {"_id": 0})
        .sort("updatedAt", -1)
        .limit(limit)
    )
    return list(cursor)


# ── Message ───────────────────────────────────────────────

def save_message(conversation_id: str, user_uid: str, role: str, content: str) -> dict:
    """
    儲存一則訊息（role: "user" | "assistant"）
    仿照 LibreChat saveMessage 函式
    """
    doc = {
        "messageId":      str(uuid.uuid4()),
        "conversationId": conversation_id,
        "userId":         user_uid,
        "role":           role,      # "user" 或 "assistant"
        "content":        content,
        "createdAt":      datetime.now(timezone.utc),
    }
    get_msg_col().insert_one(doc)
    # 同步更新 conversation.updatedAt
    get_conv_col().update_one(
        {"conversationId": conversation_id},
        {"$set": {"updatedAt": datetime.now(timezone.utc)}}
    )
    return {k: v for k, v in doc.items() if k != "_id"}


def get_messages_by_conversation(conversation_id: str) -> list:
    """
    取得指定對話的所有訊息（依時間排序），供多輪對話 history 使用
    """
    cursor = (
        get_msg_col()
        .find({"conversationId": conversation_id}, {"_id": 0})
        .sort("createdAt", 1)
    )
    return list(cursor)
