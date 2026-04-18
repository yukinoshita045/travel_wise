"""
api/routes/places.py
GET /api/places/search — 景點搜尋（Google Places API）
GET /api/places/<place_id> — 景點詳細資料
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.places_service import search_spots, get_spot_detail

places_bp = Blueprint("places", __name__)


@places_bp.route("/search", methods=["GET"])
@require_auth
@swag_from("../swagger/places_search.yaml")
def search():
    """
    搜尋景點（OpenTripMap）
    Query params: city (城市名), preferences (逗號分隔), radius (公尺), limit (筆數)
    """
    city        = request.args.get("city")
    preferences = request.args.get("preferences", "").split(",") if request.args.get("preferences") else []
    radius      = int(request.args.get("radius", 5000))
    limit       = int(request.args.get("limit", 20))

    if not city:
        return jsonify({"error": "缺少 city 參數"}), 400

    result = search_spots(city=city, preferences=preferences, radius_m=radius, limit=limit)
    return jsonify(result), 200


@places_bp.route("/<xid>", methods=["GET"])
@require_auth
@swag_from("../swagger/places_detail.yaml")
def place_detail(xid):
    """
    取得景點詳細資料（OpenTripMap xid）
    """
    result = get_spot_detail(xid=xid)
    if not result:
        return jsonify({"error": "景點不存在"}), 404
    return jsonify(result), 200
