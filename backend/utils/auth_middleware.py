"""
utils/auth_middleware.py
Firebase ID Token 驗證中介層
仿照 LibreChat 的 JWT 驗證模式，用 decorator 保護 API route
"""

import os
import functools
import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

# ── Firebase Admin SDK 初始化（單例）──
_firebase_initialized = False

def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if not service_account_path:
        raise EnvironmentError("FIREBASE_SERVICE_ACCOUNT_PATH 未設定")
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)
    _firebase_initialized = True
    logger.info("Firebase Admin SDK 初始化完成 ✅")


def require_auth(f):
    """
    Decorator：驗證 Firebase ID Token
    成功後將 user 資訊存入 flask.g.user（uid, email）
    使用方式：
        @require_auth
        def my_route():
            user = g.user  # {"uid": "...", "email": "..."}
    """
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        _init_firebase()
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "缺少 Authorization header", "code": 401}), 401

        id_token = auth_header.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(id_token)
            g.user = {
                "uid":   decoded_token["uid"],
                "email": decoded_token.get("email", ""),
            }
        except Exception as e:
            logger.warning(f"Token 驗證失敗: {e}")
            return jsonify({"error": "Token 無效或已過期", "code": 401}), 401

        return f(*args, **kwargs)
    return decorated
