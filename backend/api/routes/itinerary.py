"""
api/routes/itinerary.py
行程 CRUD + 推薦 API
"""

from flask import Blueprint, request, jsonify, g
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.itinerary_service import recommend_itinerary
from models.itinerary import (
    get_itinerary_by_id,
    get_itineraries_by_user,
    update_itinerary,
    delete_itinerary,
)

itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.route("/recommend", methods=["POST"])
@require_auth
@swag_from("../swagger/itinerary_recommend.yaml")
def recommend():
    """AI 生成行程推薦，並存入 MongoDB"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    result = recommend_itinerary(user_uid=g.user["uid"], params=data)
    return jsonify(result), 201


@itinerary_bp.route("/user/history", methods=["GET"])
@require_auth
@swag_from("../swagger/itinerary_history.yaml")
def user_history():
    """取得使用者所有歷史行程"""
    itineraries = get_itineraries_by_user(user_uid=g.user["uid"])
    return jsonify({"itineraries": itineraries}), 200


@itinerary_bp.route("/<itinerary_id>", methods=["GET"])
@require_auth
@swag_from("../swagger/itinerary_get.yaml")
def get_itinerary(itinerary_id):
    """取得單一行程詳細資料"""
    itinerary = get_itinerary_by_id(itinerary_id, g.user["uid"])
    if not itinerary:
        return jsonify({"error": "行程不存在或無權限存取"}), 404
    return jsonify(itinerary), 200


@itinerary_bp.route("/<itinerary_id>", methods=["PUT"])
@require_auth
@swag_from("../swagger/itinerary_update.yaml")
def update(itinerary_id):
    """更新行程（前端拖拉排序後呼叫）"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    success = update_itinerary(itinerary_id, g.user["uid"], data)
    if not success:
        return jsonify({"error": "更新失敗，行程不存在或無權限"}), 404
    return jsonify({"message": "行程更新成功"}), 200


@itinerary_bp.route("/<itinerary_id>", methods=["DELETE"])
@require_auth
@swag_from("../swagger/itinerary_delete.yaml")
def delete(itinerary_id):
    """刪除行程"""
    success = delete_itinerary(itinerary_id, g.user["uid"])
    if not success:
        return jsonify({"error": "刪除失敗，行程不存在或無權限"}), 404
    return jsonify({"message": "行程已刪除"}), 200
