"""
api/routes/trips.py
/api/trips — 使用者旅程 CRUD

GET    /api/trips          → 取得所有旅程
POST   /api/trips          → 建立旅程
GET    /api/trips/:trip_id → 取得單一旅程
PUT    /api/trips/:trip_id → 更新旅程（含行程 items、address 等）
DELETE /api/trips/:trip_id → 刪除旅程
POST   /api/trips/sync     → 前端批次同步（一次上傳多筆旅程）
"""

from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from models.trip_store import (
    create_trip,
    get_trip_by_id,
    get_trips_by_user,
    update_trip,
    delete_trip,
    upsert_trip,
)
import logging

logger = logging.getLogger(__name__)
trips_bp = Blueprint("trips", __name__)


@trips_bp.route("", methods=["GET"])
@require_auth
def list_trips():
    """
    取得目前使用者的所有旅程
    Response: { "trips": [ {...trip}, ... ] }
    """
    trips = get_trips_by_user(user_uid=g.user["uid"])
    return jsonify({"trips": trips}), 200


@trips_bp.route("", methods=["POST"])
@require_auth
def create():
    """
    建立新旅程
    Request Body: 完整的 trip 物件（對應前端 travelData.json 結構）
    包含 itinerary items 的 address 欄位
    Response: { "trip": {...} }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    required = ["title", "destination", "startDate", "endDate"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"缺少必填欄位: {missing}"}), 400

    trip = create_trip(user_uid=g.user["uid"], trip_data=data)
    return jsonify({"trip": trip}), 201


@trips_bp.route("/<trip_id>", methods=["GET"])
@require_auth
def get_trip(trip_id):
    """
    取得單一旅程
    Response: { "trip": {...} }
    """
    trip = get_trip_by_id(trip_id, g.user["uid"])
    if not trip:
        return jsonify({"error": "旅程不存在或無權限"}), 404
    return jsonify({"trip": trip}), 200


@trips_bp.route("/<trip_id>", methods=["PUT"])
@require_auth
def update(trip_id):
    """
    更新旅程（前端每次編輯後同步）
    可傳完整 trip 物件，或只傳要更新的部分欄位。
    itinerary items 中的 address 欄位會自動保留。
    Response: { "trip": {...} }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    updated = update_trip(trip_id, g.user["uid"], data)
    if not updated:
        return jsonify({"error": "旅程不存在或無權限"}), 404
    return jsonify({"trip": updated}), 200


@trips_bp.route("/<trip_id>", methods=["DELETE"])
@require_auth
def delete(trip_id):
    """
    刪除旅程
    Response: { "message": "旅程已刪除" }
    """
    success = delete_trip(trip_id, g.user["uid"])
    if not success:
        return jsonify({"error": "旅程不存在或無權限"}), 404
    return jsonify({"message": "旅程已刪除"}), 200


@trips_bp.route("/sync", methods=["POST"])
@require_auth
def sync_trips():
    """
    前端批次同步多筆旅程（一次上傳 localStorage 中所有資料）
    Request Body: { "trips": [ {...trip}, ... ] }
    Response: { "synced": 3 }
    """
    data = request.get_json()
    if not data or "trips" not in data:
        return jsonify({"error": "缺少 trips 陣列"}), 400

    count = 0
    errors = []
    for trip_data in data["trips"]:
        try:
            upsert_trip(user_uid=g.user["uid"], trip_data=trip_data)
            count += 1
        except Exception as e:
            errors.append({"id": trip_data.get("id"), "error": str(e)})
            logger.warning(f"[Trips] sync 失敗: trip_id={trip_data.get('id')} err={e}")

    result = {"synced": count}
    if errors:
        result["errors"] = errors
    return jsonify(result), 200
