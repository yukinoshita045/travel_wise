"""
api/routes/chat.py
POST /api/chat — AI 對話 API（GPT-4o 行程推薦）
"""

from flask import Blueprint, request, jsonify, g
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.chat_service import handle_chat_message

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("", methods=["POST"])
@require_auth
@swag_from("../swagger/chat.yaml")
def chat():
    """
    送出使用者訊息，取得 AI 回覆（含行程 JSON 或純文字建議）
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "缺少 message 欄位"}), 400

    user_uid        = g.user["uid"]
    user_message    = data["message"]
    conversation_id = data.get("conversationId")   # 可選，繼續舊對話

    result = handle_chat_message(
        user_uid=user_uid,
        message=user_message,
        conversation_id=conversation_id,
    )
    return jsonify(result), 200
